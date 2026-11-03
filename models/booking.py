from app import db
from datetime import datetime

BOOKED = "Booked"
CANCELLED = "Cancelled "
COMPLETED = "Completed"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    exam_id = db.Column(
              db.Integer, 
              db.ForeignKey("examination.id"),
              nullable=False)
    slot_id = db.Column(
              db.Integer, 
              db.ForeignKey("slot.id"), 
              nullable=False)
    Student_id = db.Column(
                 db.Integer, 
                 db.ForeignKey("user.id"), 
                 nullable=False)
    booking_date = db.Column(
              db.DateTime,
              default = datetime.now,
              nullable=False)
    #Booking status

    Status = db.Column(
             db.String(20), 
             default = BOOKED, 
             nullable=False)
    
    #Stops duplicates 
    __table_args__ = (
        db.UniqueConstraint(
            'exam_id',
            'Student_id',
            name='unique_student_exam_booking'),)
        
    