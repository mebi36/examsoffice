@echo off
cmd /k "C:\examsoffice\examsoffice\env222\Scripts\activate & start chrome --app=http://localhost:8000 & python C:\examsoffice\examsoffice\manage.py runserver & pause