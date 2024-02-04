from flask import Flask, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    return render_template("signup.html")


if __name__ == '__main__':
    app.run(debug=True)