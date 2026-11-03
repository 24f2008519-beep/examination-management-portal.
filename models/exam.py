from app import db
from datetime import datetime

DRAFT = 'Draft '
SLOT_CREATION = 'Slot Creation'
BOOKING_OPEN = 'Booking open'
CLOSED = 'Closed '
COMPLETE = 'Completed'

class Examination(db.Model):
    
    # Examination details
    id =  db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    Type = db.Column(db.String(30), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    Max_Marks = db.Column(db.Float, nullable=False)
    user_id = db.Column(
              db.Integer, 
              db.ForeignKey("user.id"), 
              unique = True,
              nullable=False)
    #Relation with course
    course_id = db.Column(
        db.Integer, 
        db.ForeignKey('course.id'), 
        nullable=False)  
    
    #Student slot booking period  
    Slot_Booking_booking_start = db.Column(
                                 db.DateTime, 
                                 nullable=False)
    Slot_Booking_booking_end = db.Column(
                               db.DateTime, 
                               nullable=False)

    #slot creation
    slot_creation_start = db.Column(    
                          db.DateTime, 
                          nullable=False)
    slot_creation_end = db.Column(
                        db.DateTime, 
                        nullable=False)

    #Exam status

    status = db.Column(db.String(40), 
                       default=DRAFT, 
                       nullable=False)
    created_at = db.Column(db.DateTime, 
                           default=datetime.now, 
                           nullable=False)
