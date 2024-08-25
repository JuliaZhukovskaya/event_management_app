# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set environment variables to ensure Python outputs stdout and stderr
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock /app/

# Install pipenv and dependencies
RUN pip install pipenv && pipenv install --deploy --ignore-pipfile

# Copy the rest of the application code
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["pipenv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]