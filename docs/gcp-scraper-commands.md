# Instructions to run the scraper docker container alone

#### These won't be necessary most of the time, as the `docker-compose.yml` will run both containers.

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
