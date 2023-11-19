# Use the official Ubuntu image as the base
FROM ubuntu:20.04

# Set the environment variable for non-interactive installations
ENV DEBIAN_FRONTEND=noninteractive

# Install required dependencies
RUN apt-get update && \
    apt-get install -y curl apt-transport-https ca-certificates gnupg lsb-release openssh-client

# Add the Google Cloud SDK repository
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

# Docker
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
RUN chmod a+r /etc/apt/keyrings/docker.gpg
RUN echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install packages
RUN apt-get update && \
    apt-get install -y google-cloud-sdk google-cloud-sdk-gke-gcloud-auth-plugin jq docker-ce

# Kubernetes & Ansible
RUN curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg && \
    echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | tee /etc/apt/sources.list.d/kubernetes.list  && \
    curl https://baltocdn.com/helm/signing.asc | apt-key add -&& \
    echo "deb https://baltocdn.com/helm/stable/debian/ all main" | tee /etc/apt/sources.list.d/helm-stable-debian.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends kubectl helm python3 python3-pip && \
    pip install openshift ansible docker apache-libcloud

RUN useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 passw0rd)" && \
    usermod -aG docker app && \
    mkdir -p /app && \
    chown app:app /app


# Set the working directory
WORKDIR /app
ADD --chown=app:app . /app

# Install ansible dependencies
RUN set -ex; \
    ansible-galaxy collection install community.general community.kubernetes

# Start a new shell to use the installed SDK
ENTRYPOINT ["/bin/bash","./docker-entrypoint.sh"]