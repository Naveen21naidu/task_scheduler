from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from pywebpush import webpush, WebPushException

app = Flask(__name__)

# 🔐 VAPID Keys for Web Push
VAPID_PUBLIC_KEY  = "BBiVJi8--fMfDeRDHI4RRYzv_CFlzDFqL7o3ahnFH_hWDl0q-mxcLpWoWwKL3eyF4OwYPYV1YmDMg4lngmyLkNE="
VAPID_PRIVATE_KEY = "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZytiZ3lyeDdwTXdTOU43bG0KejQzVzYySGo3ZUJZUmZkcEVnMUoyTU9uY2hlaFJBTkNBQVFZbFNZdlB2bnpIdzNrUXh5T0VVV003L3doWmN3eAphaSs2TjJvWnhSLzRWZzVkS3Zwc1hDNlZxRnNDaTkzc2hlRHNHRDJGZFdKZ3pJT0paNEpzaTVEUgotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tCg=="
VAPID_EMAIL       = "mailto:your@email.com"

# 📦 In-Memory Subscription Store
SUBSCRIPTIONS = []

# 🗂️ Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 📋 Task Model
class Task(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    task         = db.Column(db.String(200), nullable=False)
    due_datetime = db.Column(db.DateTime, nullable=False)
    status       = db.Column(db.String(20), default='pending')  # pending, completed, overdue

# 🛠️ Create DB Tables
with app.app_context():
    db.create_all()

# ⏰ Background Job: Mark Overdue Tasks
def check_task_status():
    with app.app_context():
        now   = datetime.now()
        tasks = Task.query.filter(Task.status != 'completed').all()
        for t in tasks:
            if t.due_datetime < now:
                t.status = 'overdue'
        db.session.commit()

# 🔁 Start Scheduler (runs every 1 minute)
scheduler = BackgroundScheduler()
scheduler.add_job(check_task_status, 'interval', minutes=1)
scheduler.start()

# 📬 Web Push Helper
def send_push_to_user(subscription_info, message_body):
    try:
        webpush(
            subscription_info=subscription_info,
            data=message_body,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_EMAIL}
        )
        return True
    except WebPushException as ex:
        print("❌ Push failed:", repr(ex))
        return False

# 🌐 Routes

## Home: List Tasks
@app.route('/')
def home():
    check_task_status()
    tasks = Task.query.order_by(Task.due_datetime).all()
    return render_template('home.html', tasks=tasks)

## Add Task
@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        name = request.form['task']
        due  = datetime.strptime(request.form['due_datetime'], '%Y-%m-%dT%H:%M')
        db.session.add(Task(task=name, due_datetime=due))
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_task.html')

## Edit Task
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == 'POST':
        task.task         = request.form['task']
        task.due_datetime = datetime.strptime(request.form['due_datetime'], '%Y-%m-%dT%H:%M')
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit_task.html', task=task)

## Delete Task
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    t = Task.query.get_or_404(task_id)
    db.session.delete(t)
    db.session.commit()
    return redirect(url_for('home'))

## Complete Task
@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    t = Task.query.get_or_404(task_id)
    t.status = 'completed'
    db.session.commit()
    return redirect(url_for('home'))

## Undo Completion
@app.route('/undo/<int:task_id>')
def undo_task(task_id):
    t = Task.query.get_or_404(task_id)
    if t.status == 'completed':
        t.status = 'pending'
        db.session.commit()
    return redirect(url_for('home'))

## Save Push Subscription
@app.route('/subscribe', methods=['POST'])
def subscribe():
    subscription = request.get_json()
    if subscription and subscription not in SUBSCRIPTIONS:
        SUBSCRIPTIONS.append(subscription)
        print("📬 New subscription saved:", subscription)
    return jsonify({'success': True})

## Send Push to All Subscribers
@app.route('/send_push', methods=['POST'])
def send_push():
    message = request.get_json().get('message', '🔔 You have a new task reminder!')
    results = []

    for sub in SUBSCRIPTIONS:
        success = send_push_to_user(sub, message)
        results.append({'endpoint': sub.get('endpoint'), 'status': 'sent' if success else 'failed'})

    return jsonify(results)

# 🚀 Run the App
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

