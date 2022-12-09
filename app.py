import os
import time

from flask import Flask, render_template, url_for, send_from_directory, send_file
from flask import request, session, redirect
from database import MysqlPool
from flask import g

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'media'
DB = MysqlPool()
ctx=app.app_context()
ctx.push()

@app.before_request
def before():
    url = request.path  # 当前请求的URL
    white_urls = ["/login", '/logout', '/register']
    if url.startswith('/static'):
        return
    if url in white_urls:
        return
    prev_url = ['/person/bio/upload/', '/uploads/']
    for prev in prev_url:
        if url.startswith(prev):
            return
    else:
        login_status = session.get("login_status", False)
        if not login_status:
            return redirect(url_for('login_html'))
        else:
            pass


@app.route('/login', methods=["GET", "POST"])
def login_html():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        person = DB.fetch_one("select * from `person` where `username` = %s and `password` = %s", (username, password))
        if person is None:
            person = DB.fetch_one("select * from `hr` where `username` = %s and `password` = %s", (username, password))
            if person is None:
                return render_template('login.html', **{
                    "msg": "用户名或密码错误"
                })
            else:
                session["login_status"] = True
                session["login_role"] = "hr"
                session["login_person"] = person
                return redirect(url_for('hr_index'))
        else:
            session["login_status"] = True
            session["login_role"] = "person"
            session["login_person"] = person
            return redirect(url_for("person_index"))


@app.route('/register')
def register_html():
    return render_template("register.html")


@app.route('/logout')
def logout():
    session.pop("login_status")
    session.pop("login_role")
    return redirect(url_for("index_html"))


@app.route('/')
def index_html():
    login_role = session.get("login_role", None)
    if login_role == "hr":
        return redirect(url_for('hr_index'))
    else:
        return redirect(url_for('person_index'))


@app.route("/hr/index")
def hr_index():

    jobs = DB.fetch_all("""
    select * from job 
    order by id desc
    """, None)
    page_size = int(request.args.get('page_size', 9))
    current_page = int(request.args.get('current_page', 1))
    jobs = DB.pagination(jobs, page_size, current_page)
    return render_template("hr/index.html", **{
        "jobs": jobs,
        "hr_id": session.get("login_person").get("id")
    })

@app.route("/hr/job_record/<int:job_id>", methods=["GET", "POST"])
def hr_job_record(job_id):
    if request.method == "GET":
        job_records = DB.fetch_all("""
        select bio_record.*, person.* from bio_record 
        left join person on bio_record.person_id = person.id
        where job_id = %s
        order by bio_record.id desc
        """, (job_id,))

        # print(job_records)

        job = DB.fetch_one("""
        select * from job where id = %s
        """, (job_id,))

        return render_template("hr/job_record.html", **{
            "job_records": job_records,
            "job": job
        })

@app.route("/hr/job_edit/<int:job_id>", methods=["GET", "POST"])
def hr_job_edit(job_id):
    if request.method == "GET":
        job = DB.fetch_one("select * from job where id = %s", (job_id,))
        return render_template("hr/job_edit.html", **{
            "job": job
        })
    else:
        try:
            hr_id = session.get("login_person").get("id")
            name = request.form.get("name")
            desc = request.form.get("desc")
            city = request.form.get("city")
            degree = request.form.get("degree")
            salary_low = request.form.get("salary_low")
            salary_high = request.form.get("salary_high")

            DB.update("update job set `name` = %s, `desc` = %s, `city` = %s, `degree` = %s, `salary_low` = %s, "
                      "`salary_high` = %s where id = %s", (name, desc, city, degree, salary_low, salary_high, job_id))
            job = DB.fetch_one("select * from job where id = %s", (job_id,))

            return render_template("hr/job_edit.html", **{
                "type": "success",
                "msg": "修改成功",
                "job": job
            })
        except Exception as e:
            job = DB.fetch_one("select * from job where id = %s", (job_id,))

            return render_template("hr/job_edit.html", **{
                "type": "danger",
                "msg": "参数错误",
                "job": job
            })

@app.route('/hr/job/status_change/<int:job_id>', methods=["POST"])
def hr_job_status_change(job_id):
    DB.update("""
    update job set is_done = abs(is_done-1)  where id = %s
    """, (job_id,))
    return "success"

@app.route("/hr/publish", methods=['GET', 'POST'])
def hr_publish_job():
    if request.method == "GET":
        return render_template("hr/publish.html")
    else:
        try:
            name = f'{request.form.get("name")}'
            salary_low = float(request.form.get("salary_low"))
            salary_high = float(request.form.get("salary_high"))
            city = f'{request.form.get("city")}'
            experience = int(request.form.get("experience"))
            degree = int(request.form.get("degree"))
            desc = f'{request.form.get("desc")}'
            hr_id = int(session.get("login_person").get("id"))

            DB.insert("""
                 insert into job (`name`, `salary_low`, `salary_high`, `city`, `experience`, `degree`, `desc`, `hr_id`)
                 values (%s, %r, %r, %s, %r, %r, %s, %r)
                 """, (name, salary_low, salary_high, city, experience, degree, desc, hr_id))
            return render_template("hr/publish.html", **{
                "msg": "发布成功",
                "type": "success"
            })

        except Exception as e:
            return render_template("hr/publish.html", **{
                "msg": "参数错误",
                "type": "danger"
            })

@app.route('/hr/send_interview/<int:record_id>')
def hr_send_interview(record_id):
    return render_template("hr/send_interview.html", **{
        "record_id": record_id
    })


@app.route('/hr/my_job')
def hr_my_job():
    my_jobs = DB.fetch_all("""
    select * from job
    where hr_id = %s
    order by id desc
    """, (session.get("login_person").get("id"),))

    page_size = int(request.args.get('page_size', 9))
    current_page = int(request.args.get('current_page', 1))
    my_jobs = DB.pagination(my_jobs, page_size, current_page)


    return render_template("hr/my_job.html", **{
        "my_jobs": my_jobs
    })

@app.route('/hr/detail/<int:job_id>/')
def hr_detail(job_id):
    job = DB.fetch_one("""
    select * from job
    where id = %r
    """, (job_id, ))

    if job is None:
        return redirect(code=404, location=url_for('index_html'))

    person_id = session.get("login_person").get("id")
    if person_id == job.get("hr_id"):
        records = DB.fetch_all("""
        select * from bio_record
        where job_id = %r
        """, (job_id))
    else:
        records = []

    return render_template("hr/detail.html", **{
        "job": job,
        "records": records
    })
@app.route('/person/index')
def person_index():
    jobs = DB.fetch_all("""
    select job.*, star.id as star_id from job
    left join `recruit-system`.star
    on job.id = star.job_id
    and star.person_id = %s
    where job.is_done = 1
    order by job.id desc
    """, (session["login_person"]["id"],))
    page_size = int(request.args.get('page_size', 9))
    current_page = int(request.args.get('current_page', 1))
    jobs = DB.pagination(jobs, page_size, current_page)

    return render_template("person/index.html", **{
        "jobs": jobs
    })


@app.route("/person/star")
def person_star():
    stars = DB.fetch_all("""
    select job.*, star.id as star_id from job
    inner join `recruit-system`.star
    on job.id = star.job_id
    and star.person_id = %s
    order by star.id desc
    """, (session["login_person"]["id"],))

    page_size = int(request.args.get('page_size', 9))
    current_page = int(request.args.get('current_page', 1))
    stars = DB.pagination(stars, page_size, current_page)

    return render_template("person/star.html", **{
        "stars": stars
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    af_filename = request.args.get('af_filename', filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename,as_attachment=True, attachment_filename=af_filename)

@app.route('/person/bio/upload/<int:person_id>/<int:job_id>/', methods=["POST"])
def person_bio_upload(job_id, person_id):
    file = request.files.get("file")
    # 文件名由 job_id + session里的用户id + 时间戳 + 文件后缀名组成
    filename = str(job_id) + "_" + str(person_id) + "_" + str(int(time.time())) + "." + file.filename.split(".")[-1]
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    DB.insert("""
    insert into bio_record (person_id, job_id, url)
    value (%s, %s, %s)
    """, (person_id, job_id, url_for('uploaded_file', filename=filename)))

    return {
        "valid": True
    }


@app.route('/person/detail/<int:job_id>/')
def person_detail(job_id):
    job = DB.fetch_one("""
    select job.*, star.id as star_id from job
    left join `recruit-system`.star
    on job.id = star.job_id
    and star.person_id = %s
    where job.id = %s
    """, (session["login_person"]["id"], job_id))

    bio_records = DB.fetch_all("""
    select * from bio_record
    where job_id = %r and person_id = %r
    """, (job_id, session["login_person"]["id"]))



    # job = DB.fetch_one("select * from job where id = %r", (int(job_id),))
    if job is None:
        return redirect(code=404, location=url_for('index_html'))

    return render_template("person/detail.html", **{
        "job": job,
        "bio_records": bio_records
    })


@app.template_filter('route_active_cut')
def route_active_cut(url):
    if request.path == url:
        return "ax-active"
    else:
        return ""

degree_list = ['不限', '初中及以下', '中专', '高中', '大专', '本科', '硕士研究生', '博士研究生']
expr_list = ['不限', '在校生', '应届生', '1年以内', '1-3年', '3-5年', '5-10年']
bio_record_list = ['未处理', 'hr已发送面试', '应聘者拒绝面试', '应聘者接受面试', 'hr已发送offer',\
'应聘者拒绝offer', '应聘者接受offer', 'hr已发送入职', '应聘者拒绝入职', '应聘者接受入职']

@app.template_global('get_bio_record_list')
def get_bio_record_list():
    return bio_record_list

@app.template_global('get_degree_list')
def get_degree_list():
    return degree_list

@app.template_global('get_expr_list')
def get_expr_list():
    return expr_list

@app.template_global('url_filename_func')
def url_filename_cut(url, download_name):
    filename = url.split("/")[-1]
    suffix = filename.split(".")[-1]
    # 获取当前时间戳
    timestamp = str(int(time.time()))
    return f'{url}?af_filename={download_name}-{timestamp}.{suffix}'


@app.template_filter('bio_record_cut')
def bio_record_cut(value):
    value = int(value)
    return bio_record_list[value] if value <= len(bio_record_list) else 'None'


@app.template_filter('degree_cut')
def degree_cut(value):
    value = int(value)
    return degree_list[value] if value <= len(degree_list) else 'None'

@app.template_filter('gender_cut')
def get_gender_cut(value):
    value = int(value)
    if value == 0:
        return "男"
    elif value == 1:
        return "女"
    else:
        return "不限"
@app.template_filter('expr_cut')
def expr_cut(value):
    value = int(value)
    return expr_list[value] if value <= len(expr_list) else 'None'


@app.template_filter('star_status_for_job_cut')
def star_status_for_job_cut(value):
    if value is None:
        return "收藏"
    else:
        return "已收藏"
@app.template_filter('job_is_done_cut')
def job_is_done_cut(value):
    value = int(value)
    if value == 1:
        return "checked"
    else:
        return " "


@app.route('/star/<int:job_id>/', methods=['post'])
def star(job_id):
    person = session.get("login_person", None)
    if person is None:
        return redirect(url_for('login_html'))
    else:
        person_id = person['id']
    star = DB.fetch_one("select * from star where job_id = %r and person_id = %r", (job_id, person_id))
    if star is None:
        DB.insert(r"insert into star (`job_id`, `person_id`) values (%r, %r)", (job_id, person_id))
    else:
        DB.delete(r"delete from star where id = %r", (star.get("id"),))
    return {
        "success": True
    }


if __name__ == '__main__':
    app.run(debug=True)
