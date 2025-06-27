# syntax=docker/dockerfile:1

# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
# We do this separately to leverage Docker's layer caching.
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application's code into the container
COPY . /app

# Expose the port the app runs on
EXPOSE 8000

# Run the application
# The command will be something like: uvicorn core.users.main:app --host 0.0.0.0 --port 8000
# We will set the final command in docker-compose.yml 