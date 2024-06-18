# Use an official Node.js runtime as a parent image for building the frontend
FROM node:22.3-alpine as frontend-builder

# Set the working directory
WORKDIR /app/frontend

# Copy the frontend code
COPY frontend/index.html ./
COPY frontend/package.json ./
COPY frontend/vite.config.js ./
COPY frontend/public ./public
COPY frontend/src ./src

# Install dependencies and build the frontend
RUN npm install
RUN npm run build

# Use an official Python runtime as a parent image for the backend
FROM python:3.12-slim

# Set the working directory for the backend
WORKDIR /app/backend

# Copy the backend code
COPY backend/ ./

# Copy the frontend build output to the appropriate directory for Nginx
COPY --from=frontend-builder /app/frontend/dist /var/www/html

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY run.sh ./
COPY run-service.sh ./
COPY run-worker.sh ./

# Expose ports for Flask
EXPOSE 5000

CMD ./run.sh