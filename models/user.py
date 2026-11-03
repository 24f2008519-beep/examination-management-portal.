from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)

    
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


    role = db.Column(db.String(20), nullable=False, default="student")  # 'admin' or 'user'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
