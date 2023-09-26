FROM python:3.9-slim

ENV VAR1=10

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install wget and remove unnecessary folder:
RUN apt-get update \
  && apt-get install -y --no-install-recommends wget gcc \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install pipenv:
RUN pip install pipenv

# Copy directory into container and set it as working directory:
COPY src/scraper /app
WORKDIR /app

# Install dependencies with pipenv:
RUN pipenv install --deploy --ignore-pipfile

# Creates a non-root user and adds permission to access the scraper folder:
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Run the appropriate Python module command:
CMD ["python", "scraper.py"]
