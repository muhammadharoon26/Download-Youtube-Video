# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# # Install ffmpeg
# RUN apt-get update && apt-get install -y ffmpeg

# # Install the dependencies
# RUN pip install --no-cache-dir \
#     ffmpeg==1.4 \
#     ffmpeg-python==0.2.0 \
#     fastapi==0.95.1 \
#     uvicorn==0.21.1 \
#     yt-dlp==2024.5.27

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code
COPY . /app

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]