"""Face Recognition Attendance System - Web Application"""
import os
from datetime import datetime, date, timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from config import Config
from models import db, User, Attendance
from face_utils import get_face_encoding_from_image, verify_face

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def ensure_dirs():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)


@app.before_request
def before_request():
    ensure_dirs()


@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '')
        if not user_id or not password:
            flash('Please enter user ID and password.', 'error')
            return render_template('login.html')
        user = User.query.filter_by(user_id=user_id).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next') or url_for('index')
            return redirect(next_page)
        flash('Invalid user ID or password.', 'error')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ---------- Student routes ----------

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    return render_template('student/dashboard.html')


@app.route('/student/mark-attendance')
@login_required
def mark_attendance_page():
    if current_user.is_admin():
        return redirect(url_for('admin_dashboard'))
    if not current_user.face_image_path or not os.path.exists(current_user.face_image_path):
        flash('Your face has not been registered. Please contact admin.', 'error')
        return redirect(url_for('student_dashboard'))
    return render_template('student/mark_attendance.html')


@app.route('/api/mark-attendance', methods=['POST'])
@login_required
def api_mark_attendance():
    if current_user.is_admin():
        return jsonify({'success': False, 'message': 'Admins cannot mark attendance.'}), 403
    
    if not current_user.face_image_path or not os.path.exists(current_user.face_image_path):
        return jsonify({'success': False, 'message': 'Face not registered.'}), 400
    
    # Expect base64 image in JSON: { "image": "data:image/jpeg;base64,..." }
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({'success': False, 'message': 'No image provided.'}), 400
    
    try:
        img_data = data['image']
        if ',' in img_data:
            img_data = img_data.split(',', 1)[1]
        import base64
        image_bytes = base64.b64decode(img_data)
    except Exception as e:
        return jsonify({'success': False, 'message': 'Invalid image data.'}), 400
    
    known_encoding = get_face_encoding_from_image(current_user.face_image_path)
    if not verify_face(image_bytes, known_encoding):
        return jsonify({'success': False, 'message': 'Face not recognized. Please try again with better lighting.'}), 400
    
    today = date.today()
    existing = Attendance.query.filter_by(user_id=current_user.id, date=today).first()
    if existing:
        return jsonify({'success': True, 'message': 'Attendance already marked today.', 'already_marked': True})
    
    att = Attendance(user_id=current_user.id, date=today, time=datetime.now().time())
    db.session.add(att)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Attendance marked successfully!'})


@app.route('/api/my-attendance')
@login_required
def api_my_attendance():
    if current_user.is_admin():
        return jsonify({'error': 'Use admin routes'}), 403
    
    year = request.args.get('year', type=int) or date.today().year
    month = request.args.get('month', type=int) or date.today().month
    
    start = date(year, month, 1)
    end = date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1)
    records = Attendance.query.filter_by(user_id=current_user.id).filter(
        Attendance.date >= start, Attendance.date < end
    ).order_by(Attendance.date).all()
    
    days = [r.date.day for r in records]
    return jsonify({'year': year, 'month': month, 'present_days': days, 'records': [
        {'date': r.date.isoformat(), 'time': r.time.strftime('%H:%M')} for r in records
    ]})


# ---------- Admin routes ----------

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.filter_by(role='student').order_by(User.name).all()
    return render_template('admin/dashboard.html', users=users)


@app.route('/admin/users/<int:user_id>')
@login_required
@admin_required
def admin_user_detail(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin():
        flash('Cannot view admin user.', 'error')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/user_detail.html', target_user=user)


@app.route('/api/admin/users/<int:user_id>/attendance')
@login_required
@admin_required
def api_admin_user_attendance(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin():
        return jsonify({'error': 'Invalid'}), 403
    
    year = request.args.get('year', type=int) or date.today().year
    month = request.args.get('month', type=int) or date.today().month
    
    start = date(year, month, 1)
    end = date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1)
    records = Attendance.query.filter_by(user_id=user_id).filter(
        Attendance.date >= start, Attendance.date < end
    ).order_by(Attendance.date).all()
    
    return jsonify({
        'year': year, 'month': month,
        'present_days': [r.date.day for r in records],
        'records': [{'date': r.date.isoformat(), 'time': r.time.strftime('%H:%M')} for r in records]
    })


@app.route('/uploads/face/<int:user_id>')
@login_required
@admin_required
def serve_face_image(user_id):
    """Serve face image for admin view."""
    user = User.query.get_or_404(user_id)
    if not user.face_image_path or not os.path.exists(user.face_image_path):
        return '', 404
    ext = os.path.splitext(user.face_image_path)[1].lower()
    mimetype = 'image/png' if ext == '.png' else 'image/jpeg'
    return send_file(user.face_image_path, mimetype=mimetype)


@app.route('/admin/add-user', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_user():
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        face_file = request.files.get('face_image')
        
        if not user_id or not name or not password:
            flash('User ID, name and password are required.', 'error')
            return redirect(url_for('admin_add_user'))
        
        if User.query.filter_by(user_id=user_id).first():
            flash(f'User ID "{user_id}" already exists.', 'error')
            return redirect(url_for('admin_add_user'))
        
        if not face_file or face_file.filename == '':
            flash('Face image is required for students.', 'error')
            return redirect(url_for('admin_add_user'))
        
        ext = os.path.splitext(secure_filename(face_file.filename))[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png']:
            flash('Face image must be JPG or PNG.', 'error')
            return redirect(url_for('admin_add_user'))
        
        filename = f"{user_id}_{int(datetime.now().timestamp())}{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        face_file.save(filepath)
        
        # Verify face is detectable
        enc = get_face_encoding_from_image(filepath)
        if enc is None:
            os.remove(filepath)
            flash('No face detected in the image. Please use a clear front-facing photo.', 'error')
            return redirect(url_for('admin_add_user'))
        
        user = User(user_id=user_id, name=name, role='student', face_image_path=filepath)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f'User "{name}" added successfully.', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/add_user.html')


# Init DB and seed admin
def init_db():
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(user_id='admin', name='Administrator', role='admin')
            admin.set_password('admin123')
            admin.face_image_path = None
            db.session.add(admin)
            db.session.commit()
            print('Created default admin: user_id=admin, password=admin123')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
