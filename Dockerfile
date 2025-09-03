# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements file first (to leverage Docker cache)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY . .

# Expose the port
EXPOSE 8000

# Run FastAPI app from hellow.py
CMD ["uvicorn", "hellow:app", "--host", "0.0.0.0", "--port", "8000"]
