# Use an official Python runtime as a parent image for the backend
FROM python:3.12-slim

# Set the working directory for the backend
WORKDIR /app/backend

# Copy the backend code
COPY ./ ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports for Flask
EXPOSE 8000

CMD gunicorn app:app --bind 0.0.0.0:8000