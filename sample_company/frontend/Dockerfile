# Use an official Node.js runtime as a parent image for building the frontend
FROM node:22.3-alpine

# Set the working directory
WORKDIR /app/frontend

# Copy the frontend code
COPY index.html ./
COPY package.json ./
COPY vite.config.js ./
COPY public ./public
COPY src ./src

# Install dependencies and build the frontend
RUN npm install

CMD npm run build
