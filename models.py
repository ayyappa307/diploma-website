from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False) # Hall ticket or Emp ID or admin
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'faculty', 'student'
    
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade="all, delete-orphan")
    faculty_profile = db.relationship('Faculty', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False) # e.g., CME, ECE
    
    students = db.relationship('Student', backref='branch_ref', lazy=True)
    timetables = db.relationship('Timetable', backref='branch_ref', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    hall_ticket = db.Column(db.String(20), unique=True, nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(10))
    face_data = db.Column(db.Text) # JSON string of face descriptors
    profile_photo = db.Column(db.String(255))
    
    attendances = db.relationship('Attendance', backref='student', lazy=True)

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    emp_id = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(50))
    
    # Simple comma-separated list for simplicity in MVP, could be a join table
    subjects_handling = db.Column(db.String(255)) 

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False) # 'Present', 'Absent', 'Late'
    method = db.Column(db.String(20), default='Manual') # 'Manual', 'Face'

class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())
