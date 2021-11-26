@echo off
cmd /k "cd env\Scripts & activate & cd .. & cd .. & start chrome --app=http://localhost:8000 & cd examsoffice & python manage.py runserver & pause