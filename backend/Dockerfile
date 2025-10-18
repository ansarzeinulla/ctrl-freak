# Use a newer, compatible version of Python
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from the root context and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code into the container
COPY ./backend/ .

# Expose the port the server runs on
EXPOSE 8000