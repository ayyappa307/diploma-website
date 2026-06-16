from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from models import db, User, Branch, Student, Faculty
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os

app = Flask(__name__)
app.config.from_object(Config)

# Register Blueprints
from routes.admin import admin_bp
from routes.faculty import faculty_bp
from routes.student import student_bp

app.register_blueprint(admin_bp)
app.register_blueprint(faculty_bp)
app.register_blueprint(student_bp)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Setup Database and initial data ---
def setup_database():
    with app.app_context():
        db.create_all()
        # Seed Admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Seed Branches
            branches = [
                Branch(name='Computer Engineering', code='CME'),
                Branch(name='Electronics & Communication', code='ECE'),
                Branch(name='Electrical & Electronics', code='EEE'),
                Branch(name='Mechanical Engineering', code='MECH'),
                Branch(name='Civil Engineering', code='CIVIL')
            ]
            db.session.add_all(branches)
            db.session.commit()
            print("Database initialized with admin and branches.")

setup_database()

# --- Routes ---

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'faculty':
            return redirect(url_for('faculty.dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5000)
