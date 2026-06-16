from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Student, Faculty, Branch

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def require_admin():
    if current_user.role != 'admin':
        return "Unauthorized", 403

@admin_bp.route('/')
def dashboard():
    stats = {
        'total_students': Student.query.count(),
        'total_faculty': Faculty.query.count(),
        'total_branches': Branch.query.count(),
    }
    return render_template('admin/dashboard.html', stats=stats)

# --- Students ---
@admin_bp.route('/students')
def manage_students():
    students = Student.query.all()
    branches = Branch.query.all()
    return render_template('admin/manage_students.html', students=students, branches=branches)

@admin_bp.route('/students/add', methods=['POST'])
def add_student():
    name = request.form.get('name')
    hall_ticket = request.form.get('hall_ticket')
    branch_id = request.form.get('branch_id')
    semester = request.form.get('semester')
    
    # 1. Create User
    if User.query.filter_by(username=hall_ticket).first():
        flash('Hall Ticket already exists.', 'error')
        return redirect(url_for('admin.manage_students'))
        
    user = User(username=hall_ticket, role='student')
    user.set_password('student123') # Default password
    db.session.add(user)
    db.session.commit()
    
    # 2. Create Student
    student = Student(user_id=user.id, name=name, hall_ticket=hall_ticket, branch_id=branch_id, semester=semester)
    db.session.add(student)
    db.session.commit()
    
    flash('Student added successfully.', 'success')
    return redirect(url_for('admin.manage_students'))

@admin_bp.route('/students/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    user = User.query.get(student.user_id)
    db.session.delete(student)
    db.session.delete(user)
    db.session.commit()
    flash('Student deleted.', 'success')
    return redirect(url_for('admin.manage_students'))

# --- Faculty ---
@admin_bp.route('/faculty')
def manage_faculty():
    faculty = Faculty.query.all()
    return render_template('admin/manage_faculty.html', faculty=faculty)

@admin_bp.route('/faculty/add', methods=['POST'])
def add_faculty():
    name = request.form.get('name')
    emp_id = request.form.get('emp_id')
    department = request.form.get('department')
    
    if User.query.filter_by(username=emp_id).first():
        flash('Employee ID already exists.', 'error')
        return redirect(url_for('admin.manage_faculty'))
        
    user = User(username=emp_id, role='faculty')
    user.set_password('faculty123') # Default password
    db.session.add(user)
    db.session.commit()
    
    fac = Faculty(user_id=user.id, name=name, emp_id=emp_id, department=department)
    db.session.add(fac)
    db.session.commit()
    
    flash('Faculty added successfully.', 'success')
    return redirect(url_for('admin.manage_faculty'))

@admin_bp.route('/faculty/delete/<int:id>')
def delete_faculty(id):
    fac = Faculty.query.get_or_404(id)
    user = User.query.get(fac.user_id)
    db.session.delete(fac)
    db.session.delete(user)
    db.session.commit()
    flash('Faculty deleted.', 'success')
    return redirect(url_for('admin.manage_faculty'))

# --- Branches ---
@admin_bp.route('/branches')
def manage_branches():
    branches = Branch.query.all()
    return render_template('admin/manage_branches.html', branches=branches)

# --- Timetable ---
@admin_bp.route('/timetable', methods=['GET', 'POST'])
def manage_timetable():
    from models import Timetable
    import os
    from werkzeug.utils import secure_filename
    from flask import current_app
    
    if request.method == 'POST':
        branch_id = request.form.get('branch_id')
        semester = request.form.get('semester')
        file = request.files.get('file')
        
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Store relative path for static serving
            rel_path = f"uploads/{filename}"
            
            tt = Timetable(branch_id=branch_id, semester=semester, file_path=rel_path)
            db.session.add(tt)
            db.session.commit()
            flash('Timetable uploaded successfully.', 'success')
        else:
            flash('Invalid file. Only PDF is allowed.', 'error')
            
        return redirect(url_for('admin.manage_timetable'))
        
    timetables = Timetable.query.all()
    branches = Branch.query.all()
    return render_template('admin/manage_timetable.html', timetables=timetables, branches=branches)

# --- Reports ---
@admin_bp.route('/reports')
def view_reports():
    from models import Attendance
    from sqlalchemy import func
    
    # Simple report: count of present/absent per student
    # Note: Requires raw SQL or advanced SQLAlchemy for pivot, MVP uses python processing
    attendances = Attendance.query.all()
    return render_template('admin/reports.html', attendances=attendances)
