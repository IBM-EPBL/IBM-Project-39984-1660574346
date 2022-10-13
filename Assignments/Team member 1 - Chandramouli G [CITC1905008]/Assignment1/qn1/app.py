from flask import Flask, render_template,url_for,request,redirect

app = Flask(__name__)


@app.route("/", methods = ['GET'])
def register():
    return render_template("register.html")

@app.route("/welcome", methods = ['POST'])
def welcome():
    usrname = request.form["usrname"]
    email = request.form["email"]
    phno = request.form["phno"]
    return render_template("welcome.html", usrname=usrname, phno=phno, email=email)




if __name__ == "__main__":
    app.run(debug=True)