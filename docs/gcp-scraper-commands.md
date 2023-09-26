# Instructions to run the scraper docker container alone

#### These won't be necessary most of the time, as the `docker-compose.yml` will run both containers.

### Here are instructions for the individual scraper container. Run these from the `src/scraper` folder.

### Build the docker container from Dockerfile

```sh
sudo docker build -t scraper-app -f Dockerfile .
```

### Check image for scraper-app was created
```sh
sudo docker images
```

### Run the container and start with base
```sh
sudo docker run -it scraper-app bash
```

### Run the program
```sh
python milestone2_main.py
```