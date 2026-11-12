from app import db
from datetime import datetime
DRAFT = "Draft"
SUBMITTED = "Submitted"
PUBLISHED = "Published"
class evalution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"), nullable=False)
    max_marks = db.Column(db.Float, nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey("examiner.id"), nullable=False)
    remark = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default=DRAFT)
    evalutuated_at = db.Column(db.DateTime,
                               default = datetime.now,
                               nullable=False)
    published_at = db.Column(db.String(120), nullable=True)