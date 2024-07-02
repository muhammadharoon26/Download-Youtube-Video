# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory
WORKDIR /api

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code
COPY . /app

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "8000"]