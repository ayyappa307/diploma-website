from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Student, Faculty, Branch

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')

@faculty_bp.before_request
@login_required
def require_faculty():
    if current_user.role != 'faculty':
        return "Unauthorized", 403

@faculty_bp.route('/')
def dashboard():
    faculty_profile = current_user.faculty_profile
    return render_template('faculty/dashboard.html', faculty=faculty_profile)

@faculty_bp.route('/students')
def view_students():
    students = Student.query.all()
    return render_template('faculty/view_students.html', students=students)

@faculty_bp.route('/take_attendance')
def take_attendance():
    branches = Branch.query.all()
    return render_template('faculty/take_attendance.html', branches=branches)

@faculty_bp.route('/get_student_faces')
def get_student_faces():
    import json
    branch_id = request.args.get('branch_id')
    students = Student.query.filter_by(branch_id=branch_id).all()
    
    student_data = []
    for s in students:
        if s.face_data:
            student_data.append({
                'hall_ticket': s.hall_ticket,
                'face_data': json.loads(s.face_data)
            })
            
    return {'students': student_data}

@faculty_bp.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    from datetime import date
    from models import Attendance
    
    data = request.get_json()
    hall_ticket = data.get('hall_ticket')
    
    student = Student.query.filter_by(hall_ticket=hall_ticket).first()
    if not student:
        return {'success': False, 'error': 'Student not found'}
        
    today = date.today()
    # Check if already marked
    existing = Attendance.query.filter_by(student_id=student.id, date=today).first()
    if existing:
        return {'success': True, 'msg': 'Already marked'}
        
    new_attendance = Attendance(date=today, student_id=student.id, status='Present', method='Face')
    db.session.add(new_attendance)
    db.session.commit()
    
    return {'success': True}
