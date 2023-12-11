# Use the official Debian-hosted Python image
FROM python:3.9-slim-buster
ENV CLOUDSDK_PYTHON=/usr/local/bin/python3.9
#ARG CHROME_VERSION="119.0.6045.105-1"
ARG DEBIAN_PACKAGES="build-essential git curl wget unzip gzip xvfb gnupg"

# Prevent apt from showing prompts
ENV DEBIAN_FRONTEND=noninteractive

# Python wants UTF-8 locale
ENV LANG=C.UTF-8

# Tell pipenv where the shell is. This allows us to use "pipenv shell" as a
# container entry point.
ENV PYENV_SHELL=/bin/bash

# Tell Python to disable buffering so we don't lose any logs.
ENV PYTHONUNBUFFERED=1

# Ensure we have an up to date baseline, install dependencies and
# create a user so we don't run the app as root
RUN set -ex; \
    for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends $DEBIAN_PACKAGES && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip && \
    pip install pipenv && \
    useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 Passw0rd)" && \
    mkdir -p /app && \
    mkdir -p /persistent && \
    chown app:app /persistent && \
    chown app:app /app


# Install any needed dependencies for Chrome
RUN apt-get update && apt-get install -y \
    xvfb gnupg wget curl unzip \
    libnss3 \
    libxss1 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    libgbm1 \
    xdg-utils \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Download and Install Google Chrome
RUN wget --verbose -P /tmp/ https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chrome-linux64.zip

# Check the integrity and list contents of the ZIP file
RUN unzip -t /tmp/chrome-linux64.zip
RUN unzip -l /tmp/chrome-linux64.zip

# Unzip the file to /opt/chrome and list contents
RUN unzip /tmp/chrome-linux64.zip -d /opt/chrome
RUN ls -la /opt/chrome/chrome-linux64/

# This makes chrome executable, and sets a symoblic link of chrome to google-chrome
RUN chmod +x /opt/chrome/chrome-linux64/chrome
RUN ln -s /opt/chrome/chrome-linux64/chrome /usr/bin/google-chrome

# Add the Cloud SDK distribution URI as a package source
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Import the Google Cloud public key
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

# Update and install the Cloud SDK
# RUN apt-get update && apt-get install -y google-cloud-sdk

###################
# New Section 
###################

# Add the Cloud SDK distribution URI as a package source
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Import the Google Cloud public key
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

# Update the sources listing
RUN apt-get update

# Now instead of using apt-get install, we'll download and run Google's install.sh script
RUN curl https://sdk.cloud.google.com | bash

# Add the Google Cloud SDK to the path (or source the path file provided)
ENV PATH $PATH:/home/app/google-cloud-sdk/bin

###################

# Expose port of API service
EXPOSE 9000

# Create a directory for downloads and give ownership to the app user
RUN mkdir -p /home/downloads && chown app:app /home/downloads

# Switch to the new user
USER app
WORKDIR /app

# Install python packages
ADD --chown=app:app Pipfile Pipfile.lock /app/

RUN pipenv sync

# Add the rest of the source code. This is done last so we don't invalidate all
# layers when we change a line of code.
ADD --chown=app:app . /app

# Entry point
ENTRYPOINT ["/bin/bash","./docker-entrypoint.sh"]