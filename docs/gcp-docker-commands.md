# Instructions to run docker containers alone using the `scraper` container as an example

#### These won't be necessary most of the time, as the `docker-compose.yml` will run all four containers.

### Here are instructions for the individual scraper container. Run these from the `src/scraper` folder.

### Build the docker container from Dockerfile

```sh
sudo docker build -t scraper -f Dockerfile .
```

### Check image for scraper was created
```sh
sudo docker images
```

### Run the container and start with base
```sh
sudo docker run -it scraper bash
```

### Run the program
```sh
python scraper.py
```
To open up a shell into a running Docker container, you can use the `docker exec` command followed by the container ID or name, and the shell executable you want to run (commonly `/bin/bash`).

```sh
docker exec -it [container-id-or-name] /bin/bash
```

Follow these steps:

1. First, you can list the running containers to get the container ID or name:

```sh
docker ps
```

2. From the output of the `docker ps` command, note the container ID or name of the container you want to connect to.

3. Then, run the `docker exec` command with the `-it` flags (to keep STDIN open and allocate a pseudo-tty):

```sh
docker exec -it [your-container-id-or-name] /bin/bash
```

Replace `[your-container-id-or-name]` with the actual container ID or name.

Once you run the above command, you should be inside the container's shell, where you can execute commands as if you're inside the container.

### To give the container access to the GCS Bucket

The directory `gcsbucket` is just a mount point in the Docker container. To actually see the contents of your GCS bucket inside that directory, you need to use `gcsfuse` to mount the bucket to that directory after starting the container.

1. **Run your container**:

    ```bash
    sudo docker run -it --privileged scraper bash
    ```

    Use `--privileged` to allow the container to have necessary permissions to mount filesystems. The `docker-compose` has already set the `llama_index` and `finetuned_bert` to run as privileged if launched this way.

2. **Inside the container, mount the GCS bucket**:

    If your GCE instance has appropriate IAM permissions to access the bucket, you can simply run:

    ```bash
    gcsfuse ac215_scraper_bucket /app/gcsbucket
    ```

    Now, if you list the contents of `/app/gcsbucket`, you should see the contents of your GCS bucket.

Every time you start a new container instance, you'll need to remount the GCS bucket to see its contents in `/app/gcsbucket`. We will likely create a startup script to handle this.