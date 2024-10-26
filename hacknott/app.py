import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import math
import subprocess
from functools import wraps


app = Flask(__name__)

#configures session to use filesystem instead of signed cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = SQL("sqlite:///scores.db")



@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")
    

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return render_template("error.html",message="No Username Entered")
        password = request.form.get("password")
        confirmed = request.form.get("confirmed")
        if not password:
            return render_template("error.html",message="No Password Entered")
        if len(password) <= 7:
            return render_template("error.html",message="Password must be atleast 8 characters")
        if password != confirmed:
            return render_template("error.html",message="Passwords do not match")


        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
            
        except ValueError:
                return render_template("error.html", message="Username Taken")
        return redirect("/login")
    else:
        return render_template("register.html")







@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html",message="No Username Entered")
        # Ensure password was submitted
        if not request.form.get("password"):
            return render_template("error.html",message="No Password Entered")

        rows = db.execute("SELECT * FROM users WHERE username = ?",request.form.get("username"))
        id = db.execute("SELECT id FROM users WHERE username = ?",request.form.get("username"))

        password = request.form.get("password")

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return render_template("error.html",message="Username And/Or Password Is Incorrect")

        # Remember which user has logged in
        id=id[0]
        id = id['id']
        session["user_id"] = id

        check = db.execute("SELECT * FROM profile WHERE user_id = ?", id)
        if not check:
            skill = 'unkown'
            db.execute("INSERT INTO highscores (user_id, memory, typing, threedee, aim) VALUES (?, ?, ?, ?, ?)", session["user_id"], 0, 0, 0, 0)
            db.execute("INSERT INTO profile (user_id, teststaken, bestskill) VALUES (?, ?, ?)",session["user_id"], 0, skill)

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("login.html")
    
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def run_game(game_script, session_id):
    # Use subprocess to run the game script, passing session_id as an argument
    try:
        subprocess.Popen(['python3', os.path.join('games', game_script), str(session_id)])  # Convert session_id to a string
    except Exception as e:
        print(f"Error running game: {e}")
    
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


@app.route("/test", methods=["GET", "POST"])
@login_required
def test():
    return render_template("test.html")



@app.route("/play", methods = ["POST"])
@login_required
def type():
    run_game('type.py', session['user_id'])
    return redirect("/")

@app.route("/highscores", methods =["GET","POST"])
@login_required
def high():
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    username = username[0]
    username = username['username']
   
    highscores = db.execute("SELECT * FROM highscores WHERE user_id = ?", session["user_id"])
    highscores = highscores[0]
    return render_template("highscores.html",highscores=highscores, username=username)


@app.route("/leaderboard", methods=["GET", "POST"])
@login_required
def leaderboard():
    memory = db.execute("SELECT score, username FROM memory ORDER BY score DESC")
    aim = db.execute("SELECT score, username FROM aim ORDER BY score DESC")
    threedee = db.execute("SELECT score, username FROM threedee ORDER BY score DESC")
    type = db.execute("SELECT score, username FROM type ORDER BY score DESC")

    return render_template("leaderboard.html",memory=memory, aim=aim, threedee=threedee, type=type)