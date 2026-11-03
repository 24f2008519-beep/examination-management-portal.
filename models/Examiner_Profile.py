from app import db

class Examiner_Profile(db.Model):
    __tablename__ = "examiner" 
    id = db.Column(db.Integer, primary_key=True, nullable=False)


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        unique=True
    )


    name = db.Column(db.String(120), nullable=False)
    contact_details = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="pending")
