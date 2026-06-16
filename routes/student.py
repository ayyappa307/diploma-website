from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Student, Faculty, Branch

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.before_request
@login_required
def require_student():
    if current_user.role != 'student':
        return "Unauthorized", 403

@student_bp.route('/')
def dashboard():
    student_profile = current_user.student_profile
    return render_template('student/dashboard.html', student=student_profile)

@student_bp.route('/profile')
def view_profile():
    student_profile = current_user.student_profile
    return render_template('student/profile.html', student=student_profile)

@student_bp.route('/register_face')
def register_face():
    return render_template('student/register_face.html')

@student_bp.route('/save_face', methods=['POST'])
def save_face():
    import json
    data = request.get_json()
    descriptor = data.get('face_descriptor')
    
    if not descriptor:
        return {'success': False, 'error': 'No face data provided'}, 400
        
    student = current_user.student_profile
    student.face_data = json.dumps(descriptor)
    db.session.commit()
    
    return {'success': True}

@student_bp.route('/results')
def view_results():
    return render_template('student/results.html')

@student_bp.route('/timetable')
def view_timetable():
    from models import Timetable
    student = current_user.student_profile
    timetables = Timetable.query.filter_by(branch_id=student.branch_id, semester=student.semester).all()
    return render_template('student/timetable.html', timetables=timetables)
