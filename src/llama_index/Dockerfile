
FROM python:3.9-slim

ENV VAR1=10

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install wget and remove unnecessary folder:
RUN  apt-get update \
  && rm -rf /var/lib/apt/lists/*

# Install pipenv, gcc and build-essential:
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
&& apt-get install build-essential -y

# Copy directory into container and set it as working directory:
COPY . /llama_index
WORKDIR /llama_index

# Install dependencies with pipenv:
RUN pipenv install --deploy --system

# Creates a non-root user and adds permission to access acrophily sims folder:
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /llama_index
USER appuser

#start the container from bash:
CMD ["pipenv", "run", "python", "build_query.py"]
