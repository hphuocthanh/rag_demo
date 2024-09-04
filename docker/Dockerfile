# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies required for faiss and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  cmake \
  libblas-dev \
  liblapack-dev \
  wget \
  curl \
  netcat-traditional \
  && rm -rf /var/lib/apt/lists/*

## Install Ollama using curl
#RUN curl -fsSL https://ollama.com/install.sh | bash

# Copy the current directory contents into the container at /app
COPY . .

# Upgrade pip
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8906 available to the world outside this container
EXPOSE 8906

# Define environment variable
ENV FLASK_APP=app.py
# Copy the wait-for-it script into the container
COPY wait-for-it.sh /wait-for-it.sh

# Make the wait-for-it script executable
RUN chmod +x /wait-for-it.sh

# Default entrypoint
ENTRYPOINT ["/wait-for-it.sh", "ollama-container", "11434", "--"]
## Run app.py when the container launches
CMD ["python", "app.py"]
