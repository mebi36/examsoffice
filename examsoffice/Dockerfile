# Use an official Python runtime as a parent image
FROM python:3.9.5

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY . /app
# COPY /home/Documents/examsoffice/requirements_latest.txt /app/
RUN pip install --upgrade pip && pip install -r /app/requirements_latest.txt

# # Copy project
# COPY /home/Documents/examsoffice/* /app/


# Expose port (optional, depending on your settings)
EXPOSE 8000

WORKDIR /app/examsoffice

# Run Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

