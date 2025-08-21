@echo off
cd /d D:\task_scheduler
call venv\Scripts\activate
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
