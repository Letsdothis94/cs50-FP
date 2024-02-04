from flask import Flask, render_template, request, session, redirect
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL("sqlite:///database.db")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return render_template("login.html", error="Enter username and password")
        data = db.execute("SELECT * FROM users WHERE username =?", username)
        if not data or not check_password_hash(data[0]["hash"], password):
            return render_template("login.html", error="User not found")
        session["user_id"] = data[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")
        
@app.route("/signup", methods=["GET", "POST"])
def signup():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return render_template("signup.html", error="Please fill in the form")
        elif password != confirmation:
            return render_template("signup.html", error="Passwords do not match")
        data = db.execute("SELECT * FROM users WHERE username = ?", username)
        if data:
            return render_template("signup.html", error="Username already exists")
        hashed = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed)
        data = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = data[0]["id"]
        return redirect("/login")
    else:
        return render_template("signup.html")


if __name__ == '__main__':
    app.run(debug=True)