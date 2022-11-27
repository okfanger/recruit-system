import os

from flask import Flask, render_template, url_for
from flask import request, session, redirect
from database import MysqlPool

app = Flask(__name__)
app.secret_key = os.urandom(24)
DB = MysqlPool()


# 中间件
@app.before_request
def before():
    url = request.path  # 当前请求的URL
    white_urls = ["/login"]
    if url.startswith('/static'):
        return
    if url in white_urls:
        pass
    else:
        _id = session.get("_id", None)
        if not _id:
            return redirect(url_for('login_html'))
        else:
            pass


@app.route('/')
def index_html():  # put application's code here
    return redirect(url_for('index'))


@app.route('/hr/index')
def hr_index():
    return render_template("hr/index.html")


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
                return redirect(url_for('login_html'))

        return "123"


def index_html():
    pass


def register_html():
    return render_template("register.html")


if __name__ == '__main__':
    app.run(debug=True)
