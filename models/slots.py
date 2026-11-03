from app import db
from datetime import datetime

AVAILABLE = "Available "
FULL = "Full "
CANCELLED = "Cancelled "
COMPLETED = "Completed"


class Slot(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    
    #student exam info
    exam_id = db.Column(
              db.Integer, 
              db.ForeignKey("examination.id"), 
              nullable = False)
    examiner_id = db.Column(
                  db.Integer, 
                  db.ForeignKey("examiner.id"), 
                  nullable = False)
    
    #Exam slot booking time
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    max_capacity = db.Column(db.Integer, nullable=False)

    #Student Seat Availablity
    Available_Seats = db.Column(
                      db.Integer,
                      nullable=False)
    

    Status = db.Column(
             db.String(30), 
             default = AVAILABLE,
             nullable=False)
    is_active = db.Column(
                db.Boolean, 
                default=True, 
                nullable=False)