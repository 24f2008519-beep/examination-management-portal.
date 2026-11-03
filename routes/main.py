import email
from flask import Blueprint, render_template, request, session, redirect, url_for
from app.models import User
from app import db
main = Blueprint('main', __name__)


@main.route("/home")
def home():
    
    return render_template("home.html")

@main.route("/", methods=["GET", "POST"])

def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()

        #checking admin

        if user and user.role == "admin" and user.password == password:
            session["user_id"] = user.id
            return redirect(url_for("main.admin_dashboard"))
        #0.Check if the user exists
        if not user:
            return "Account not found."

        # 1. Check whether the user exists and password is correct
        if user and user.password != password:
            return "Invalid username or password."

        #2. Checks whether the user is active or not
        if not user.is_active:
            return "Your account is waitng for approval. Please contact the administrator."

        #3. If the user exists and is active, store the user ID in the session and redirect to the profile page
        session["user_id"] = user.id
        return redirect(url_for("main.profile"))
    return render_template("auth/login.html")


@main.route("/logout")
def logout():
    #1. Clear the user ID from the session to log the user out
    session.pop("user_id", None)
    return redirect(url_for("main.home"))

@main.route("/profile")
def profile():
    #1. Retrieve the user ID from the session if User is None, return a message 
    # indicating that the user is not found and prompt them to log in first
    user_id = session.get("user_id")
    if user_id is None:
        return "User not found. Please log in first."
    
    #2. Query the database for the user with the retrieved user ID        
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return "User not found."


    return render_template("auth/profile.html", user=user)

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()

        if existing_user:
            return "Username or email already registered."

        
        new_user = User(username = username, 
                        email = email, password = password, 
                        role = 'student')
        db.session.add(new_user)
        db.session.commit()

        
        return redirect(url_for("main.home")) 
    return render_template("auth/register.html")


@main.route("/examiner/register", methods=["GET", "POST"])
def examiner_register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter(
           (User.username == username) |
           (User.email == email)
        ).first()

        if existing_user:
            return render_template("auth/examiner_pending.html")

        new_user = User(username = username, 
                        email = email, password=password, 
                        role ='examiner')
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("main.examiner_pending_area"))
    return render_template("auth/examiner_register.html")

@main.route("/examiner_pending_area", methods=["GET", "POST"])
def examiner_pending_area():
    return render_template("auth/examiner_pending.html")


@main.route("/admin")
def admin_dashboard(): 
    #1. Retrieve the user ID from the session
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("main.login"))

    #2. Query the database for the user with the retrieved user ID
    user = User.query.get(user_id)
    if user is None:
        return "User not found."

    #3. Check's if the user is an admin
    if not user or user.role != "admin":
        return "Access denied. You are not authorized to access this page.", 403
    

    #4. pending_examiners checkbox.

    pending_examiners = User.query.filter_by(role="examiner",
                                             is_active=False).all()

    return render_template("auth/admin_dashboard.html", user=user)

    
    

    

            