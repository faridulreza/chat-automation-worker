# Use Python 3.11 slim as base image
# The slim variant is smaller than the default and has fewer unnecessary packages
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
# - PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files
# - PYTHONUNBUFFERED: Ensures Python output is sent straight to terminal without buffering
# - PORT: Default port for the application (can be overridden at runtime)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install system dependencies
# Include any system packages your application needs here
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry for dependency management
# Poetry provides better dependency management than pip
RUN pip install --no-cache-dir poetry==1.6.1

# Configure Poetry to not create a virtual environment inside the container
# This is not needed in Docker as the container itself is isolated
RUN poetry config virtualenvs.create false

# Copy only the dependency files first
# This allows Docker to cache the installed dependencies
COPY pyproject.toml poetry.lock* ./

# Install dependencies
# --no-interaction: Do not ask any interactive questions
# --no-ansi: Do not output ANSI color codes
RUN poetry install --no-interaction --no-ansi --no-root --only main

# Copy the rest of the application
COPY . .

# Create a non-root user to run the application
# This improves security by not running as root
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Expose the port the app will run on
EXPOSE $PORT

# Command to run the application
# uvicorn is the ASGI server that will run the FastAPI application
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT