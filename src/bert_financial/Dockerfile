FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

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

# Switch to non-root user
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# By default, the container does nothing when it starts
CMD ["tail", "-f", "/dev/null"]
