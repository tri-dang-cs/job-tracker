# Use an official Python runtime as a parent image for the backend
FROM python:3.12-slim

# Set the working directory for the backend
WORKDIR /app/backend

# Copy the backend code
COPY ./ ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

# Expose ports for Flask
EXPOSE 8000

CMD gunicorn backend.run:app --bind 0.0.0.0:8000