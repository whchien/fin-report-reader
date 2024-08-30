# backend/Dockerfile
FROM python:3.9-slim

LABEL authors="willchien"

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file
COPY src /app/src
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Set the environment variables
ENV PYTHONPATH /app
ENV OPENAI_API_KEY your_key

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["bash", "-c", "uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"]
