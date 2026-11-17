from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, session, redirect, url_for
from app.models import User, Examination, Slot, Course, Booking, Examiner_Profile
from app.models import Examination_Rubric
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
        return redirect(url_for("main.student_login_Successfull"))
    return render_template("auth/register.html")

@main.route("/examiner/pending_area", methods=["GET", "POST"])
def examiner_pending_area():
    return render_template("auth/examiner_pending.html")


@main.route("/student/login successfull", methods=['GET',  'POST'])
def student_login_Successfull():
    return render_template("auth/student_registration_success.html")

@main.route("/student/book/<int:slot_id>", methods=["POST"])
def book_slot(slot_id):

    # 1. Verify logged-in student
    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("main.login"))

    user = db.session.get(User, user_id)

    if user is None or user.role != "student" or not user.is_active:
        return "Access denied", 403

    # 2. Find the selected slot
    slot = db.session.get(Slot, slot_id)

    if slot is None or not slot.is_active:
        return "Slot not found or inactive.", 404

    # 3. Find the examination
    exam = db.session.get(Examination, slot.exam_id)

    if exam is None:
        return "Examination not found.", 404

    # 4. Check the booking window
    now = datetime.now()

    if not (
        exam.Slot_Booking_booking_start <= now
        <= exam.Slot_Booking_booking_end
    ):
        return "The booking window is not currently open.", 400

    # 5. Check slot availability
    if slot.Available_Seats <= 0 or slot.Status.strip().lower() != "available":
        return "This slot is already full or unavailable.", 400

    # 6. Prevent duplicate bookings for the same examination
    existing_booking = Booking.query.filter_by(
        exam_id=exam.id,
        Student_id=user.id
    ).first()

    if existing_booking:
        return "You already have a booking record for this examination.", 400

    try:
        # 7. Reduce available seats using a conditional database update
        updated = (
            db.session.query(Slot)
            .filter(
                Slot.id == slot_id,
                Slot.is_active.is_(True),
                Slot.Available_Seats > 0,
                Slot.Status == slot.Status
            )
            .update(
                {
                    Slot.Available_Seats: Slot.Available_Seats - 1
                },
                synchronize_session=False
            )
        )

        if updated != 1:
            db.session.rollback()
            return "This slot is no longer available.", 400

        # 8. Create the booking
        new_booking = Booking(
            exam_id=exam.id,
            slot_id=slot.id,
            Student_id=user.id,
            Status="Booked"
        )

        db.session.add(new_booking)

        # 9. Update slot status if it is now full
        db.session.flush()

        db.session.expire(slot)
        db.session.refresh(slot)

        if slot.Available_Seats == 0:
            slot.Status = "Full "

        db.session.commit()

        return redirect(url_for("main.student_dashboard"))

    except Exception:
        db.session.rollback()
        return "Booking failed. Please try again.", 400
    

@main.route("/student/profile", methods=["GET", "POST"])
def student_profile():

    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("main.login"))

    user = db.session.get(User, user_id)

    if user is None or user.role != "student" or not user.is_active:
        return "Access denied", 403

    if request.method == "POST":

        new_email = request.form.get("email", "").strip()

        if not new_email:
            return "Email cannot be empty.", 400

        existing_email = User.query.filter(
            User.email == new_email,
            User.id != user.id
        ).first()

        if existing_email:
            return "This email is already registered.", 400

        user.email = new_email

        db.session.commit()

        return redirect(url_for("main.student_profile"))

    return render_template(
        "auth/student_profile.html",
        user=user
    )


@main.route("/admin", methods=["GET"])
def admin_dashboard():

    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("main.login"))

    user = db.session.get(User, user_id)

    if user is None or user.role != "admin" or not user.is_active:
        return "Access denied", 403

    pending_examiners = User.query.filter_by(
        role="examiner",
        is_active=False
    ).all()

    examiner_info = User.query.filter_by(
        role="examiner"
    ).all()

    student_info = User.query.filter_by(
        role="student"
    ).all()

    courses = Course.query.all()
    examinations = Examination.query.all()
    rubrics = Examination_Rubric.query.all()

    rubrics_by_exam = {}

    for rubric in rubrics:
        rubrics_by_exam.setdefault(rubric.Exam_id, []).append(rubric)
        all_rubrics = Examination_Rubric.query.all()

        print("ALL RUBRICS:", [
            (r.Rubic_id, r.Exam_id, r.Criterion_Name)
            for r in all_rubrics
            ])

        for exam in examinations:
            exam_rubrics = Examination_Rubric.query.filter_by(
            Exam_id=exam.id
            ).all()

    print("EXAM ID:", examinations)
    print("MATCHING RUBRICS:", Examination_Rubric)

    return render_template(
        "auth/admin_dashboard.html",
    user=user,
    courses=courses,
    examinations=examinations,
    pending_examiners=pending_examiners,
    examiner_info=examiner_info,
    student_info=student_info,
    rubrics_by_exam=rubrics_by_exam
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
    
@main.route("/approve-examiner/<int:examiner_id>", methods=["POST"])
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

@main.route("/del-examiner/<int:examiner_id>", methods=["POST"])
def del_examiner(examiner_id):
    admin_id = session.get("user_id")
    admin = db.session.get(User, admin_id)

    if admin is None or admin.role != "admin":
        return "Access denied", 403

    examiner = db.session.get(User, examiner_id)

    if examiner is None or examiner.role != "examiner":
        return "Examiner not found", 404

    examiner.is_active = False
    db.session.commit()
    return redirect(url_for("main.admin_dashboard"))


@main.route("/course-edit/<int:course_id>", methods=["POST"])
def course_edit(course_id):
    admin_id = session.get("user_id")
    admin = db.session.get(User, admin_id)
    
    if admin is None or admin.role != "admin":
        return "Access denied", 403
    
    course = Course.query.get(course_id)

    if course is None:
        return "Course not found", 404
    course.code = request.form.get("code", course.code)
    course.name = request.form.get("name", course.name)
    course.description = request.form.get("description", course.description)
    course.is_active = request.form.get("status", course.is_active)
    db.session.commit()
    return redirect(url_for("main.admin_dashboard"))

@main.route("/course-del/<int:course_id>", methods=["POST"])
def course_del(course_id):
    admin_id = session.get("user_id")
    admin = db.session.get(User, admin_id)
    
    if admin is None or admin.role != "admin":
        return "Access denied", 403
    
    course = Course.query.get(course_id)

    if course is None:
        return "Course not found", 404
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for("main.admin_dashboard"))


@main.route("/exam-edit/<int:examination_id>", methods=["GET", "POST"])
def exam_edit(examination_id):

    admin = db.session.get(User, session.get("user_id"))

    if admin is None or admin.role != "admin" or not admin.is_active:
        return "Access denied", 403

    exam = db.session.get(Examination, examination_id)

    if exam is None:
        return "Examination not found", 404

    course_id = request.form.get("course_id", type=int)
    course = db.session.get(Course, course_id)

    if course is None:
        return "Invalid course", 400

    exam.course_id = course.id
    exam.name = request.form.get("name")
    exam.Type = request.form.get("type")
    exam.duration_minutes = request.form.get("duration_minutes", type=int)
    exam.Max_Marks = request.form.get("max_marks", type=float)

    db.session.commit()

    return redirect(url_for("main.admin_dashboard"))

@main.route("/rubric-add/<int:exam_id>", methods=["POST"])
def add_rubric(exam_id):

    user_id = session.get("user_id")
    user = db.session.get(User, user_id)

    if user is None or user.role != "admin":
        return "Access denied", 403

    exam = db.session.get(Examination, exam_id)

    if exam is None:
        return "Examination not found", 404

    criterion_name = request.form.get("criterion_name")
    max_marks = request.form.get("max_marks")
    weightage = request.form.get("weightage")
    description = request.form.get("description")

    if not criterion_name or not max_marks or not weightage:
        return "Please fill all required fields."

    try:
        max_marks = float(max_marks)
        weightage = float(weightage)

        if max_marks <= 0 or weightage <= 0:
            return "Marks and weightage must be positive."

        rubric = Examination_Rubric(
            Exam_id=exam_id,
            Criterion_Name=criterion_name,
            Max_marks=max_marks,
            Weightage=weightage,
            Description=description
        )

        db.session.add(rubric)
        db.session.commit()

    except ValueError:
        db.session.rollback()
        return "Invalid marks or weightage."
    except Exception:
        db.session.rollback()
        raise

    return redirect(url_for("main.admin_dashboard"))

@main.route("/examiner/view/<int:examiner_id>", methods=["POST"])
def view_examiner(examiner_id):

    admin_id = session.get("user_id")
    admin = db.session.get(User, admin_id)

    if admin is None or admin.role != "admin":
        return "Access denied", 403

    # Get selected course
    examiner_id = request.form.get("examiner_id", type=int)
    examiner = db.session.get(User, examiner_id)

    

    # Update examination details
    examiner.Name = examiner.id
    examiner.name = request.form.get("name")
    examiner.Type = request.form.get("type")
    examiner.duration_minutes = request.form.get("duration_minutes", type=int)
    

    db.session.commit()

    return redirect(url_for("main.admin_dashboard"))


@main.route("/exam-del/<int:exam_id>", methods=["POST"])
def del_exam(exam_id):

    admin = db.session.get(User, session.get("user_id"))

    if admin is None or admin.role != "admin":
        return "Access denied", 403

    exam = db.session.get(Examination, exam_id)

    if exam is None:
        return "Examination not found", 404

    db.session.delete(exam)
    db.session.commit()

    return redirect(url_for("main.admin_dashboard"))


@main.route("/exam-rubrics/<int:exam_id>", methods=["GET"])
def exam_rubrics(exam_id):
    admin = db.session.get(User, session.get("user_id"))

    if admin is None or admin.role != "admin":
        return "Access denied", 403

    exam = db.session.get(Examination, exam_id)

    if exam is None:
        return "Examination not found", 404

    rubrics = Examination_Rubric.query.filter_by(Exam_id=exam_id).all()

    return render_template(
        "auth/exam_rubrics.html",
        exam=exam,
        rubrics=rubrics
    )


@main.route("/rubric-edit/<int:rubric_id>", methods=["POST"])
def edit_rubric(rubric_id):
    admin = db.session.get(User, session.get("user_id"))

    if admin is None or admin.role != "admin" or not admin.is_active:
        return "Access denied", 403

    rubric = db.session.get(Examination_Rubric, rubric_id)

    if rubric is None:
        return "Rubric not found", 404

    criterion_name = request.form.get("criterion_name", "").strip()
    max_marks = request.form.get("max_marks", type=float)
    weightage = request.form.get("weightage", type=float)
    description = request.form.get("description", "").strip()

    if not criterion_name or max_marks is None or weightage is None:
        return "Please enter valid rubric details.", 400

    if max_marks <= 0 or weightage < 0:
        return "Invalid marks or weightage.", 400

    rubric.Criterion_Name = criterion_name
    rubric.Max_marks = max_marks
    rubric.Weightage = weightage
    rubric.Description = description

    db.session.commit()

    return redirect(url_for("main.admin_dashboard"))



