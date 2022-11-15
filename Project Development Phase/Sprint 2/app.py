from flask import Flask,render_template, request,redirect,url_for,session
import ibm_db
import re
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#initializing session
Session(app)

app.secret_key = 'a'

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=125f9f61-9715-46f9-9399-c8177b21803b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30426;Security=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=xmg49931;PWD=YKecpnUZRCObKLe2;","","")

print(conn)

@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=['GET','POST'])
def login():
    global userName;
    global userID;
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT * FROM USERS WHERE USER_NAME=? AND PASSWORD=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            session['user']=username;
            return redirect(url_for("dashboard", uid=username))
        else:
            return render_template("login.html", msg="Invalid username or password!")
    elif request.method == "GET":
        return render_template("login.html")

@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        
        sql = "SELECT * FROM USERS WHERE USER_NAME=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            return render_template("register.html", msg = "Username already taken! try another")
        else:
            sql = "INSERT INTO USERS (user_name,first_name,last_name,email,password) VALUES(?,?,?,?,?)"
            stmt = ibm_db.prepare(conn,sql)
            ibm_db.bind_param(stmt,1,username)
            ibm_db.bind_param(stmt,2,firstname)
            ibm_db.bind_param(stmt,3,lastname)
            ibm_db.bind_param(stmt,4,email)
            ibm_db.bind_param(stmt,5,password)
            ibm_db.execute(stmt)
            return redirect(url_for("login"))
    elif request.method == "GET":
        return render_template("register.html")

@app.route("/dashboard", methods=['GET','POST'])
def dashboard():
  if request.method == "GET":
    sql="select * from products where uid in (select uid from users where user_name = ?);"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,session['user'])
    ibm_db.execute(stmt)

    products = []
    entry = ibm_db.fetch_assoc(stmt)
    while entry != False:
        products.append(entry)
        entry = ibm_db.fetch_assoc(stmt)
    return render_template("view_inventory.html",username=session['user'],products=products);

@app.route("/sellItem",methods=['POST'])
def sell():
    pname = request.form["p_name"]
    stock = request.form["stock"]
    if(int(stock)==0):
        return redirect(url_for("dashboard"))
    stock = int(stock) - 1;

    sql = "UPDATE PRODUCTS SET STOCK_COUNT=? WHERE PRODUCT_NAME=?"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,stock)
    ibm_db.bind_param(stmt,2,pname)
    ibm_db.execute(stmt)
    return redirect(url_for("dashboard"))

@app.route("/epd")
def epd():
    sql="select * from products where uid in (select uid from users where user_name = ?);"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,session['user'])
    ibm_db.execute(stmt)
    products = []
    entry = ibm_db.fetch_assoc(stmt)
    while entry != False:
        products.append(entry)
        entry = ibm_db.fetch_assoc(stmt)
    return render_template("edit_product.html",username=session['user'],products=products)

@app.route("/editproduct",methods=["POST"])
def edit_product():
    pname = request.form["p_name"]
    stock = request.form["stock"]
    price = request.form["price"]
    m_stock = request.form["mstock"]
    sql = "UPDATE PRODUCTS SET STOCK_COUNT=?, PRICE_PER_UNIT= ?, MINIMUM_STOCK=? WHERE PRODUCT_NAME=?"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,stock)
    ibm_db.bind_param(stmt,2,price)
    ibm_db.bind_param(stmt,3,m_stock)
    ibm_db.bind_param(stmt,4,pname)
    ibm_db.execute(stmt)
    return redirect(url_for("epd"))

@app.route("/adp")
def adp():
    return render_template("add_product.html")

@app.route("/addproduct",methods=['POST'])
def add_product():
    pname = request.form["p_name"]
    stock = request.form["stock"]
    price = request.form["price"]
    m_stock = request.form["minimum_stock"]

    sql = "SELECT UID FROM USERS WHERE USER_NAME = ?"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,session['user'])
    ibm_db.execute(stmt)
    uid = ibm_db.fetch_assoc(stmt)
    print(uid)
    uid = int(uid['UID'])
    print(uid)

    sql = "INSERT INTO PRODUCTS (UID,PRODUCT_NAME,STOCK_COUNT,PRICE_PER_UNIT,MINIMUM_STOCK) VALUES (?,?,?,?,?)"
    
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,uid)
    ibm_db.bind_param(stmt,2,pname)
    ibm_db.bind_param(stmt,3,stock)
    ibm_db.bind_param(stmt,4,price)
    ibm_db.bind_param(stmt,5,m_stock)
    ibm_db.execute(stmt)
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True);