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
    sudo  && \ 
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Add gcsfuse repo and install gcsfuse
RUN echo "deb https://packages.cloud.google.com/apt gcsfuse-$(lsb_release -c -s) main" | tee /etc/apt/sources.list.d/gcsfuse.list && \
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

# Enable user_allow_other in fuse.conf
RUN echo 'user_allow_other' >> /etc/fuse.conf

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Make the script executable
RUN chmod +x /entrypoint.sh

# Add appuser to sudo group and disable password prompts for sudo commands
RUN adduser -u 5678 --disabled-password --gecos "" appuser \
    && adduser appuser sudo \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
    && chown -R appuser /app

USER appuser

# Use the entry script as the entry point
ENTRYPOINT ["/entrypoint.sh"]

CMD ["/bin/bash"]