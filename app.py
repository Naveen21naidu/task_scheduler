from flask import Flask, render_template, request, jsonify
from pywebpush import webpush, WebPushException

app = Flask(__name__)

# 🔐 VAPID Keys for Web Push
VAPID_PUBLIC_KEY  = "BBiVJi8--fMfDeRDHI4RRYzv_CFlzDFqL7o3ahnFH_hWDl0q-mxcLpWoWwKL3eyF4OwYPYV1YmDMg4lngmyLkNE="
VAPID_PRIVATE_KEY = "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZytiZ3lyeDdwTXdTOU43bG0KejQzVzYySGo3ZUJZUmZkcEVnMUoyTU9uY2hlaFJBTkNBQVFZbFNZdlB2bnpIdzNrUXh5T0VVV003L3doWmN3eAphaSs2TjJvWnhSLzRWZzVkS3Zwc1hDNlZxRnNDaTkzc2hlRHNHRDJGZFdKZ3pJT0paNEpzaTVEUgotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tCg=="
VAPID_EMAIL       = "mailto:your@email.com"

# 📦 In-Memory Subscription Store
SUBSCRIPTIONS = []

# 🌐 Routes

## Home Page — Task List
@app.route('/')
def home():
    return render_template('home.html')

## Add Task Page
@app.route('/add')
def add_task():
    return render_template('add_task.html')

## Edit Task Page
@app.route('/edit')
def edit_task():
    return render_template('edit_task.html')

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
        try:
            webpush(
                subscription_info=sub,
                data=message,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_EMAIL}
            )
            results.append({'endpoint': sub.get('endpoint'), 'status': 'sent'})
        except WebPushException as ex:
            print("❌ Push failed:", repr(ex))
            results.append({'endpoint': sub.get('endpoint'), 'status': 'failed'})
    return jsonify(results)

## Optional: Test Notification
@app.route('/notify')
def notify():
    return jsonify({
        "title": "🔔 Task Scheduler",
        "body": "Push notifications are active!",
        "icon": "/static/icons/icon-192.png",
        "badge": "/static/icons/icon-96.png"
    })

# 🚀 Run the App
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
