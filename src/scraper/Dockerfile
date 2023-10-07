# Use the official Debian-hosted Python image
FROM python:3.9-slim-buster

# Tell pipenv where the shell is.
# This allows us to use "pipenv shell" as a container entry point.
ENV PYENV_SHELL=/bin/bash

# Ensure we have an up to date baseline, install dependencies
RUN set -ex; \
 apt-get update && \
 apt-get upgrade -y && \
 apt-get install -y --no-install-recommends build-essential git nano && \
 pip install --no-cache-dir --upgrade pip && \
 pip install pipenv

#Install google-chrome
RUN apt-get install -y xvfb gnupg wget curl unzip
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update -y && \
    apt-get install -y google-chrome-stable


RUN apt-get install -y wget
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt-get update && apt-get -y install google-chrome-stable


# Add Pipfile, Pipfile.lock + python code
COPY . /app
WORKDIR /app


# Install dependencies with pipenv:
RUN pipenv install --deploy --system

# Creates a non-root user and adds permission to access the app folder:
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser


## Entry point
#ENTRYPOINT ["/bin/bash"]
# Get into the pipenv shell
CMD ["pipenv", "run", "python", "scraper.py"]
