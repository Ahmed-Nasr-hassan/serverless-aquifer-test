# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies first (for better build caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (excluding what's in .dockerignore)
COPY . .

# Default command (can be overridden at runtime)
CMD ["python3", "main.py"]
