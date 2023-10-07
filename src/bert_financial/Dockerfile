# Use Python 3.9-slim as the base image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    wget \
    apt-transport-https \
    ca-certificates \
    gnupg \
    curl \
    lsb-release \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Add gcsfuse repo and install gcsfuse
RUN echo "deb http://packages.cloud.google.com/apt gcsfuse-$(lsb_release -c -s) main" | tee /etc/apt/sources.list.d/gcsfuse.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && \
    apt-get install -y gcsfuse && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Set environment variables
ENV VAR1=10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install pipenv 
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install Python dependencies
RUN pipenv install --deploy --system

# Copy rest of the source code
# Now copying everything from current directory 
COPY . .

# Create a directory that will be used as a mount point (if needed)
RUN mkdir /app/gcsbucket

# Switch to non-root user
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser
