# Task Scheduler Web Application

## Problem Statement
Many users struggle to manage tasks with deadlines using simple notes or reminders.  
This project provides a secure, multi-user task management web application that helps users create, update, and track tasks so important work is not missed.

---

## Features
- User Registration and Login with secure password hashing
- Multi-user support — each user sees only their own tasks
- Create, edit, and delete tasks
- Assign deadlines to tasks
- Automatic task status handling (pending / completed / overdue)
- Flash messages for user feedback
- Secure URL protection — unauthorized access returns 404
- Persistent data storage using MySQL
- Web-based interface accessible through a browser

---

## Tech Stack
- **Backend:** Python, Flask, Flask-Login, Flask-SQLAlchemy
- **Frontend:** HTML, CSS, JavaScript
- **Database:** MySQL (Railway)
- **Deployment:** Render

---

## Application Architecture
```
Browser (HTML / CSS / JavaScript)
↓
Flask Routes (@login_required)
↓
MySQL Database (Railway)
↓
Render Deployment
```

---

## Data Model

**Users**
- `id` – Primary Key
- `username` – Unique username
- `email` – Unique email
- `password` – Hashed password (Werkzeug)
- `created_at` – Timestamp

**Tasks**
- `id` – Primary Key
- `user_id` – Foreign Key → users.id
- `task` – Task description
- `due_datetime` – Task deadline
- `status` – pending / completed / overdue
- `created_at` – Timestamp

---

## Security
- Passwords hashed using Werkzeug `generate_password_hash`
- Sessions managed with Flask-Login
- Ownership validation on every task operation — users cannot access other users' tasks
- Secret key and database credentials stored in environment variables

---

## Setup Instructions
1. Clone the repository
2. Install dependencies using `pip install -r requirements.txt`
3. Set up MySQL database and update `.env` file
4. Run `python app.py` to start the Flask server

---

## Live Demo
Live URL: https://task-scheduler-fa2u.onrender.com/

---

## Notes
Push notifications and PWA features were added as experimental enhancements and are not part of the core functionality of the application.