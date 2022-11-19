
from flask import Flask, render_template, request, redirect, url_for;
import ibm_db
import re
userName = ''
userID = 0
app = Flask(__name__)

app.secret_key = 'a'

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b0aebb68-94fa-46ec-a1fc-1c999edb6187.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=31249;Security=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=hcn73641;PWD=ME8ltnAYFqNgUJMh;","","")

print(conn)

@app.route("/")
def home():
    return "HOME"

@app.route("/addItem", methods=['POST'])
def addItem():
    pname = request.form["pname"]
    price = request.form["price"]
    qty = request.form["qty"]

    sql = "INSERT INTO PRODUCT (PNAME, PRICE, QTY) VALUES (?,?,?)"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,pname)
    ibm_db.bind_param(stmt,2,price)
    ibm_db.bind_param(stmt,3,qty)
    ibm_db.execute(stmt)

    sql = "SELECT MAX(PID) FROM PRODUCT"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.execute(stmt)
    pid = ibm_db.fetch_assoc(stmt)
    pid = int(pid['1'])

    sql = "INSERT INTO INVENTORY (AID, PID) VALUES (?,?)"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,userID)
    ibm_db.bind_param(stmt,2,pid)
    ibm_db.execute(stmt)

    return redirect(url_for("dashboard", uid=userName))


@app.route("/dashboard/<uid>",methods=['GET','POST'])
def dashboard(uid=''):
    print(uid)
    if(uid!=userName):
        return redirect(url_for("login"))
    if request.method == "POST":
        pass;
    elif request.method == "GET":
        sql = "select * from product where pid in (select pid from inventory where aid = (select aid from account where usrname=?))"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,uid)
        ibm_db.execute(stmt)

        products = []
        entry = ibm_db.fetch_assoc(stmt)
        while entry != False:
            products.append(entry)
            entry = ibm_db.fetch_assoc(stmt)
        print(products)
        return render_template("supplier_page.html",usrname=uid,products=products)


@app.route("/login", methods=['GET','POST'])
def login():
    global userName;
    global userID;
    if request.method == "POST":
        usrname = request.form["usrname"]
        pwd = request.form["pwd"]
        sql = "SELECT * FROM ACCOUNT WHERE usrname=? AND pwd=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,usrname)
        ibm_db.bind_param(stmt,2,pwd)
        ibm_db.execute(stmt)

        account = ibm_db.fetch_assoc(stmt)
        if account:
            userName = usrname;
            userID = account["AID"]
            print(usrname)
            return redirect(url_for("dashboard", uid=usrname))
        else:
            return render_template("login_page.html", msg="Invalid username or password!")
    elif request.method == "GET":
        return render_template("login_page.html")


@app.route("/register", methods=['GET','POST'])
def register():

    if request.method == "POST":
        usrname = request.form["usrname"]
        pwd = request.form["pwd"]
        email = request.form["email"]

        sql = "SELECT * FROM ACCOUNT WHERE usrname=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt, 1,usrname)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            return render_template("register_page.html", msg = "Username already taken! try another")
        else:
            sql = "INSERT INTO ACCOUNT (email,usrname,pwd) VALUES(?,?,?)"
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,email)
            ibm_db.bind_param(stmt,2,usrname)
            ibm_db.bind_param(stmt,3,pwd)
            ibm_db.execute(stmt)
            return redirect(url_for("login"))
    elif request.method == "GET":
        return render_template("register_page.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True);