import email
from datetime import datetime
from flask import Blueprint, render_template, request, session, redirect, url_for
from app.models import User, Examination, Slot, Course, Booking, Examiner_Profile
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
        #if user:
            #print("Entered password:", repr(password))
            #print("Stored password:", repr(user.password))
            #print("Password match:", user.password == password)
            #print("Role", user.role)
        #checking admin

        
        #0.Check if the user exists
        if not user:
            return "Account not found."

        # 1. Check whether the user exists and password is correct
        if user.password != password:
            return "Invalid username or password."

        #2. Checks whether the user is active or not
        if not user.is_active:
            return "Your account is waitng for approval. Please contact the administrator."

        session.clear()
        session["user_id"] = user.id
        print("Logged-in user:", user.username)
        print("Logged-in role:", user.role)
        print("Session user ID:", session.get("user_id"))
        
        if user.role == "admin":
            return redirect(url_for("main.admin_dashboard"))

        if user.role == "student":
            return redirect(url_for("main.student_dashboard"))

        if user.role == "examiner":
            return redirect(url_for("main.examiner_dashboard"))
        
        return "Invalid user role."
    
    return render_template("auth/login.html")


@main.route("/logout", methods=['GET',  'POST'])
def logout():
    #1. Clear the user ID from the session to log the user out
    session.pop("user_id", None)
    session.clear()
    return redirect(url_for("main.login"))
    

@main.route("/profile", methods=['GET',  'POST'])
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

@main.route("/register/examiner", methods=["GET", "POST"])

@main.route("/register/examiner", methods=["GET", "POST"])
def register_examiner():

    #print("ROUTE CALLED:", request.method)

    if request.method == "POST":
        #print("EXAMINER FORM SUBMITTED")

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        contact = request.form.get("contact")
        department = request.form.get("department")

        # Check whether username or email already exists
        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email)
            ).first()

        if existing_user:
            return "Username or email already registered."

        # Create examiner user account
        new_user = User(
            username=username,
            email=email,
            password=password,
            is_active=False,
            role="examiner"
        )

        # Save user account
        db.session.add(new_user)
        db.session.commit()

        print("Registered role:", new_user.role)
        print("Registered user ID:", new_user.id)
        print("Account active:", new_user.is_active)

        return redirect(url_for("main.examiner_pending_area"))

    return render_template("auth/examiner_register.html")



@main.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter(
           (User.username == username) |
           (User.email == email)
        ).first()

        if existing_user:
            return render_template("auth/login.html")

        new_user = User(username = username, 
                        email = email, password=password, 
                        role ='student')
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("student_registration_success.html"))
    return render_template("auth/register.html")

@main.route("/examiner/pending_area", methods=["GET", "POST"])
def examiner_pending_area():
    return render_template("auth/examiner_pending.html")


@main.route("/student/login successfull", methods=['GET',  'POST'])
def student_login_Successfull():
    return render_template("auth/student_registration_success.html")

@main.route("/admin", methods=['GET',  'POST'])
def admin_dashboard(): 
    
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("main.login"))


    user = User.query.get(user_id)

    admin = User.query.filter_by(role="admin").first()

    print("Admin:", admin.username if admin else None)
    print("Role:", admin.role if admin else None)
    print("Active:", admin.is_active if admin else None)
    if user is None:
        return "User not found."
    print("Session user ID:", user_id)
    print("Logged-in user:", user.username if user else None)
    print("Logged-in role:", repr(user.role) if user else None)
    print("Is admin:", user.role == "admin" if user else False)



    if not user or user.role != "admin":
        return "Access denied. You are not authorized to access this page.", 403
    

    

    pending_examiners = User.query.filter_by(
        role="examiner",
        is_active=False
     ).all()


    courses = Course.query.all()    
    

    return render_template(
    "auth/admin_dashboard.html",
        user=user,
        pending_examiners=pending_examiners,
        courses=courses
    )

@main.route("/student/dashboard")
def student_dashboard():
    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("main.login"))
    
    user = User.query.get(user_id)
    

    if user is None or user.role != "student":
        return "Access denied",403

    if not user.is_active :
        return "Your account is inactive",403

    now = datetime.now()

    available_slots = (db.session.query(Examination)
                                .join(Slot, Slot.exam_id == Examination.id)
                                .filter(
                                     Slot.is_active == True,
                                     Slot.Available_Seats > 0,
                                     Slot.start_time >= now 

                                )
                                .distinct()
                                .all()
                                )
    upcoming_exams = (db.session.query(Slot,Booking,Examination)
                                .join(Examination, Booking.exam_id
                                      == Examination.id)
                                .join(Slot,Booking.slot_id == Slot.id)
                                .filter(
                                     Booking.Student_id == user.id,
                                     Booking.Status == "Booked",
                                     Slot.start_time > now
                                )
                                .distinct()
                                .all()
                                )
    return render_template(
    "auth/student_dashboard.html",
    user=user,
    available_slots=available_slots,
    upcoming_exams=upcoming_exams
)

@main.route("/examiner/dashboard", methods=['GET',  'POST'])
def examiner_dashboard():
    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("main.login"))

    user = User.query.get(user_id)

    if user is None or user.role != "examiner":
        return "Access denied", 403

    if not user.is_active:
        return "Your account is inactive"

    

    return render_template(
        "auth/examiner_dashboard.html"
    )
    
@main.route("/admin/approve-examiner/<int:examiner_id>", methods=["POST"])
def approve_examiner(examiner_id):
    admin_id = session.get("user_id")
    admin = db.session.get(User, admin_id)

    if admin is None or admin.role != "admin":
        return "Access denied", 403

    examiner = db.session.get(User, examiner_id)

    if examiner is None or examiner.role != "examiner":
        return "Examiner not found", 404

    examiner.is_active = True
    db.session.commit()

    return redirect(url_for("main.admin_dashboard"))

