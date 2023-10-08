## Dockerfile and entrypoint.sh Explanation

### Dockerfile

This Dockerfile is used to build a Docker image based on Python 3.9-slim, a minimalistic version of Python 3.9. It was quite a challenge to get it to work so that it would automatically connect to the GCS bucket upon launch!

![Image above shows how we launch all containers with `docker-compose`, then use `docker exec` to enter the container, where we can see the GCS bucket has been automatically mounted and the data shown.](../img/docker-gcsfuse.jpg)

#### Note: Inside the folders for the containers there is a folder called `gcsbucket`. This does not hold any data; rather, it is a mount point for the GCS bucket when the Docker container is run.

1. **Base Image**:
   ```docker
   FROM python:3.9-slim
   ```
   This uses the Python 3.9 slim image from DockerHub as the base image.

2. **Install System Dependencies**:
   Necessary system packages are installed using `apt-get`. After installation, the apt package list is removed to save space.
   
3. **Install gcsfuse**:
   The Google Cloud Storage FUSE adapter is installed, allowing the user to mount a GCS bucket as a filesystem.
   
4. **Set Working Directory**:
   The working directory inside the container is set to `/app`.
   
5. **Environment Variables**:
   Some environment variables are set, e.g., disabling Python from writing `.pyc` files and ensuring Python's stdout and stderr are unbuffered.
   
6. **Install pipenv**:
   `pipenv` is installed for dependency management.
   
7. **Copy Dependencies & Install**:
   The `Pipfile` and `Pipfile.lock` are copied into the container, and then the Python dependencies are installed.
   
8. **Copy Source Code**:
   All files in the current directory are copied into the container.
   
9. **Modify fuse.conf**:
   The `user_allow_other` option is added to `fuse.conf` to allow non-root users to specify the `allow_other` or `allow_root` mount options.
   
10. **Entrypoint Script**:
   The `entrypoint.sh` script is copied into the container, made executable, and set as the default entry point.
   
11. **Add User**:
   A non-root user `appuser` is added to the container, given sudo privileges, and set as the owner of the `/app` directory. This is for security reasons, ensuring the container doesn't run applications as the root user.
   
12. **Set User and Entry Point**:
   The default user is set to `appuser`, and the entry point for the container is set to the `entrypoint.sh` script.

### entrypoint.sh

This script serves as the initial command that's run when the container starts.

1. **Mount GCS Bucket**:
   The Google Cloud Storage bucket named `ac215_scraper_bucket` is mounted to `/app/gcsbucket` using `gcsfuse`.

2. **Execute Command**:
   The script will then execute whatever command is passed to the container at runtime. If no command is provided, it defaults to running a shell.
