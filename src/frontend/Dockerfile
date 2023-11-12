FROM node:14.9.0-buster-slim

# Update baseline and ensure we don't run the app as root.
RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends openssl && \
    npm install -g http-server && \
    useradd -ms /bin/bash app -d /home/app -G sudo -u 2000 -p "$(openssl passwd -1 Passw0rd)" && \
    mkdir -p /app && \
    chown app:app /app

EXPOSE 8080

# Switch to the new user
USER app
WORKDIR /app

ENTRYPOINT ["/bin/bash"]