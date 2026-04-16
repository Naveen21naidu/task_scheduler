from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_scheduler.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ─────────────────────────────────────
# MODELS
# ─────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    tasks = db.relationship('Task', backref='owner', lazy=True)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task = db.Column(db.String(200), nullable=False)
    due_datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ─────────────────────────────────────
# ROUTES
# ─────────────────────────────────────

@app.route('/')
@login_required
def home():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    now = datetime.now()
    for task in tasks:
        if task.status == 'pending' and task.due_datetime < now:
            task.status = 'overdue'
    db.session.commit()
    return render_template('home.html', tasks=tasks)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered! Please login.', 'danger')
            return redirect(url_for('register'))
        password = generate_password_hash(request.form['password'])
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid email or password!', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        task = Task(
            user_id=current_user.id,
            task=request.form['task'],
            due_datetime=datetime.strptime(request.form['due_datetime'], '%Y-%m-%dT%H:%M'),
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('add_task.html')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        task.task = request.form['task']
        task.due_datetime = datetime.strptime(request.form['due_datetime'], '%Y-%m-%dT%H:%M')
        db.session.commit()
        flash('Task updated!', 'success')
        return redirect(url_for('home'))
    return render_template('edit_task.html', task=task)

@app.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted!', 'success')
    return redirect(url_for('home'))

@app.route('/complete/<int:task_id>')
@login_required
def complete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.status = 'completed'
    db.session.commit()
    flash('Task completed! 🎉', 'success')
    return redirect(url_for('home'))

@app.route('/undo/<int:task_id>')
@login_required
def undo_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.status = 'pending'
    db.session.commit()
    flash('Task marked as pending!', 'success')
    return redirect(url_for('home'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
