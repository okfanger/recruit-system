import os

from flask import Flask, render_template, url_for
from flask import request, session, redirect
from database import MysqlPool

app = Flask(__name__)
app.secret_key = os.urandom(24)
DB = MysqlPool()


@app.before_request
def before():
    url = request.path  # 当前请求的URL
    white_urls = ["/login"]
    if url.startswith('/static'):
        return
    if url in white_urls:
        pass
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
                return redirect(url_for('hr_index'))
        else:
            session["login_status"] = True
            session["login_role"] = "person"
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


@app.route('/hr/index')
def hr_index():
    return render_template("hr/index.html")


@app.route('/person/index')
def person_index():
    jobs = DB.fetch_all("select * from job", None)
    return render_template("person/index.html", **{
        "jobs": jobs
    })


if __name__ == '__main__':
    app.run(debug=True)
