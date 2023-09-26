FROM python:3.9-slim

ENV VAR1=10

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip and other dependencies:
RUN apt-get update \
  && apt-get install -y --no-install-recommends gcc \
  && rm -rf /var/lib/apt/lists/*

# Install pipenv:
RUN pip install pipenv

# Copy directory into container and set it as working directory:
COPY . /app
WORKDIR /app

# Install dependencies with pipenv:
RUN pipenv install --deploy --system

# Creates a non-root user and adds permission to access the app folder:
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Run scraper module command:
CMD ["python", "scraper.py"]
