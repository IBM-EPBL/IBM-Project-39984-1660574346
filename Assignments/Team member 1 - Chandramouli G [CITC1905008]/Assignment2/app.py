
from flask import Flask, render_template, request, redirect, url_for;
import ibm_db
import re
userName = ''
userID = 0
app = Flask(__name__)

app.secret_key = 'a'

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=31249;Security=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=hcn73641;PWD=ME8ltnAYFqNgUJMh;","","")


@app.route("/home")
def home():
    usrname = request.args.get('usrname')
    return  render_template("welcome.html",usrname=usrname)

@app.route("/login", methods=['GET','POST'])
def login():
    global userName;
    global userID;
    if request.method == "POST":
        usrname = request.form["usrname"]
        pwd = request.form["pwd"]
        sql = "SELECT * FROM assign2_user WHERE usrname=? AND pwd=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,usrname)
        ibm_db.bind_param(stmt,2,pwd)
        ibm_db.execute(stmt)

        account = ibm_db.fetch_assoc(stmt)
        if account:
            userName = usrname;
            return redirect(url_for("home", usrname=usrname))
        else:
            return render_template("login_page.html", msg="Invalid username or password!")
    elif request.method == "GET":
        return render_template("login_page.html")


@app.route("/", methods=['GET','POST'])
def register():

    if request.method == "POST":
        usrname = request.form["usrname"]
        pwd = request.form["pwd"]
        email = request.form["email"]
        rollno = request.form["rollno"]

        sql = "SELECT * FROM assign2_user WHERE usrname=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt, 1,usrname)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            return render_template("register_page.html", msg = "Username already taken! try another")
        else:
            sql = "INSERT INTO assign2_user (email,usrname,pwd,rollno) VALUES(?,?,?,?)"
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,email)
            ibm_db.bind_param(stmt,2,usrname)
            ibm_db.bind_param(stmt,3,pwd)
            ibm_db.bind_param(stmt,4,rollno)
            ibm_db.execute(stmt)
            return redirect(url_for("login"))
    elif request.method == "GET":
        return render_template("register_page.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True);