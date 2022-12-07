import os
import time

from flask import Flask, render_template, url_for, send_from_directory
from flask import request, session, redirect
from database import MysqlPool

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'media'
DB = MysqlPool()


@app.before_request
def before():
    url = request.path  # 当前请求的URL
    white_urls = ["/login", '/logout', '/register']
    if url.startswith('/static'):
        return
    if url in white_urls:
        return
    prev_url = ['/person/bio/upload/']
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


@app.route('/person/index')
def person_index():
    jobs = DB.fetch_all("""
    select job.*, star.id as star_id from job
    left join `recruit-system`.star
    on job.id = star.job_id
    and star.person_id = %s
    order by job.id desc
    """, (session["login_person"]["id"],))
    page_size = int(request.args.get('page_size', 9))
    current_page = int(request.args.get('current_page', 1))
    jobs = DB.pagination(jobs, page_size, current_page)

    print(jobs)
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
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

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


@app.template_filter('degree_cut')
def degree_cut(value):
    format_list = ['不限', '初中及以下', '中专', '高中', '大专', '本科', '硕士研究生', '博士研究生']
    return format_list[value] if value <= len(format_list) else 'None'


@app.template_filter('expr_cut')
def expr_cut(value):
    format_list = ['不限', '在校生', '应届生', '1年以内', '1-3年', '3-5年', '5-10年']
    return format_list[value] if value <= len(format_list) else 'None'


@app.template_filter('star_status_for_job_cut')
def star_status_for_job_cut(value):
    if value is None:
        return "收藏"
    else:
        return "已收藏"


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
