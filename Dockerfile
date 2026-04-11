# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main Python script
COPY main.py .

# Run the script unbuffered so print statements show up in Docker logs immediately
ENV PYTHONUNBUFFERED=1

# Command to run when the container starts
CMD ["python", "main.py"]