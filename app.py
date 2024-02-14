from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from helpers import login_required

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL("sqlite:///database.db")

@app.route("/")
@login_required
def index():
    data = db.execute("SELECT * FROM posts ORDER BY created_at DESC")
    return render_template("index.html", data=data)

@app.route("/post/<int:post_id>", methods=["GET"])
def view_post(post_id):
    user = db.execute("SELECT username FROM users WHERE id = :post_id", post_id=post_id)
    post = db.execute("SELECT * FROM posts WHERE post_id = :post_id", post_id=post_id)
    return render_template("postById.html", post=post, user=user)

@app.route("/delete/<int:post_id>", methods=["GET", "POST"])
def delete_post(post_id):
    if request.method == "POST":
        db.execute("DELETE FROM likes WHERE post_id = :post_id", post_id=post_id)
        db.execute("DELETE FROM dislikes WHERE post_id = :post_id", post_id=post_id)
        db.execute("DELETE FROM posts WHERE post_id = :post_id AND user_id = :user_id", post_id=post_id, user_id=session.get('user_id'))
        return redirect("/profile")
    else:       
        return render_template("profile.html", error="Couldn't delete post")



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
    
@app.route("/post", methods=["GET", "POST"])
@login_required
def make_post():
    if request.method == "POST":
        title = request.form.get("postTitle")
        content = request.form.get("post")
        user_id = session.get('user_id')
        if not content or user_id is None:
            return render_template("post.html", error="Please enter the content of your post")
        db.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", title, content, user_id)
        return redirect("/")
    else:
        return render_template("post.html")

@app.route("/like", methods=["POST"])
@login_required
def like_post():
    if request.method == "POST":
        post_id = request.form.get("post_id")
        user_id = session.get("user_id")
        action = request.form.get("action")

        if action == "like":
            print('post id: ', post_id,'user id: ', user_id,'action: ', action)
            liked = db.execute("SELECT * FROM likes WHERE user_id = ? AND post_id = ?", user_id, post_id)
            if len(liked) != 0:
                print("Previously liked:", liked)
                # return redirect("/")
            else:
                db.execute("DELETE FROM dislikes WHERE post_id = ? AND user_id = ?", post_id, user_id)
                disliked = db.execute("SELECT * FROM dislikes WHERE user_id = ? AND post_id = ?", user_id, post_id)
                if len(disliked) == 0:
                    db.execute("UPDATE posts SET likes = (likes + 1) WHERE post_id = ?", post_id)
                    db.execute("INSERT INTO likes (post_id, user_id) VALUES (?, ?)", post_id, user_id)
                    return redirect("/")
                
        elif action == "dislike":
            print('post id: ', post_id,'user id: ', user_id,'action: ', action)
            disliked = db.execute("SELECT * FROM dislikes WHERE user_id = ? AND post_id = ?", user_id, post_id)
            if len(disliked) != 0:
                print("Previously disliked", disliked)
                # return redirect("/")
            else:
                db.execute("DELETE FROM likes WHERE user_id = ? AND post_id = ?", user_id, post_id)
                liked = db.execute("SELECT * FROM likes WHERE user_id = ? AND post_id = ?", user_id, post_id)
                if len(liked) == 0:
                    db.execute("UPDATE posts SET likes = (likes - 1) WHERE post_id = ?", post_id)
                    db.execute("INSERT INTO dislikes (user_id, post_id) VALUES(?, ?)", user_id, post_id)
                    return redirect("/")
                
    data = db.execute("SELECT * FROM posts ORDER BY created_at DESC")
    return render_template("index.html", data=data)    


# @app.route("/like", methods=["POST"])
# def like_post():
#     if request.method == "POST":
#         post_id = request.form.get("post_id")
#         user_id = session.get('user_id')
#         action = request.form.get("action")

#         if action == "like":
#             print("like")
#             liked = db.execute("SELECT * FROM likes WHERE post_id = ? AND user_id = ?", 
#                                post_id, user_id)
#             if liked:
#                 return redirect("/")
#             else:
#                 disliked = db.execute("SELECT * FROM dislikes WHERE post_id = ? AND user_id = ?", post_id, user_id)
#                 if disliked:
#                     db.execute("DELETE FROM dislikes WHERE post_id = ? AND user_id = ?", post_id, user_id)
#                     db.execute("UPDATE posts SET likes = (likes + 1) WHERE post_id = ?", post_id)
#                 else:
#                     db.execute("INSERT INTO likes (post_id, user_id) VALUES (?, ?)", post_id, user_id)
#                     db.execute("UPDATE posts SET likes = (likes + 1) WHERE post_id = ?", post_id)
#                 return redirect("/")  
        
#         if action == "dislike":
#             print("Dislike")
#             disliked = db.execute("SELECT * FROM dislikes WHERE post_id = ? AND user_id = ?", post_id, user_id)
#             if disliked:
#                 return redirect("/")
#             else:
#                 liked = db.execute("SELECT * FROM likes WHERE post_id = ? AND user_id = ?", post_id, user_id)
#                 if liked:
#                     db.execute("DELETE FROM likes WHERE post_id = ? AND user_id = ?", post_id, user_id)
#                     db.execute("UPDATE posts SET likes = (likes - 1) WHERE post_id = ?", post_id)
#                 else:
#                     db.execute("INSERT INTO dislikes (post_id, user_id) VALUES (?, ?)", post_id, user_id)
#                     db.execute("UPDATE posts SET likes = (likes - 1) WHERE post_id = ?", post_id)   
#                 return redirect("/")  
#     else:
#         return redirect("/")

@app.route("/profile")
@login_required
def profile():
    user_id = session.get('user_id')
    posts = db.execute("SELECT * FROM posts WHERE user_id = ? ORDER BY created_at DESC", user_id)
    user = db.execute("SELECT * FROM users WHERE id = ? LIMIT 1", session.get('user_id'))
    return render_template("profile.html", posts=posts, user=user)

@app.route("/logout")
def logout():
    session.clear()
    redirect("/")
    return render_template("login.html")


if __name__ == '__main__':
    app.run(debug=True)