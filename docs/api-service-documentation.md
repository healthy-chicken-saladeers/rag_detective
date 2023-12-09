# FastAPI Service

This repository contains a Dockerized FastAPI service which is intended to be deployed with Google Cloud Platform. It calls endpoints which access our Weaviate server as well as our Google Vertex AI deployed BERT model's API.

## Files

The repository `/src/api_service` folder includes the following files:

- `Dockerfile`: This file defines the steps to create a Docker image for hosting the FastAPI application.
- `docker-shell.sh`: A shell script used to build the image defined in the Dockerfile and run a container from it.
- `docker-entrypoint.sh`: A shell script that runs when a Docker container is started from the image. This script kickstarts the Uvicorn server which serves the FastAPI app.
- `api/service.py`: This is the main FastAPI application file. It defines the endpoints (routes) of the API and the logic of what they do when called.
- `api/helper.py`: Contains helper functions that assist with the functionality of the FastAPI routes in the `service.py` file.
- `README.txt`: Contains basic instructions for building the Docker image, running the Docker container, and interacting with the FastAPI application.

### Dockerfile

The `Dockerfile` defines a series of steps for creating a Docker image. The Docker image will be based on a slim Debian host with Python 3.9 installed. The `Dockerfile` includes scripts for updating and upgrading Debian packages, installing needed libraries, creating a new user to avoid running the app as root, and copying and installing requirements from our `Pipfile`.

```Dockerfile
FROM python:3.9-slim-buster
...
EXPOSE 9000
USER app
WORKDIR /app
...
ADD --chown=app:app Pipfile Pipfile.lock /app/
RUN pipenv sync
ADD --chown=app:app . /app
ENTRYPOINT ["/bin/bash","./docker-entrypoint.sh"]
```

### docker-shell.sh

`docker-shell.sh` is used to build the image and run a container from it. It creates a container on localhost's port 9000 from our Docker Image and maps some local directories to directories within the Docker container.

```bash
docker build -t $IMAGE_NAME --platform=linux/arm64/v8 -f Dockerfile .
...
docker run --rm --name "$IMAGE_NAME" -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-v "$PERSISTENT_DIR":/persistent \
-p 9000:9000 \
-e DEV=1 \
-e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
-e OPENAI_APIKEY=$OPENAI_APIKEY \
$IMAGE_NAME
```

### docker-entrypoint.sh

`docker-entrypoint.sh` is the script that runs when a container is created using our Docker image. This script starts the Uvicorn server which serves the FastAPI app.

```bash
uvicorn_server() {
    uvicorn api.service:app --host 0.0.0.0 --port 9000 --log-level debug --reload --reload-dir api/ "$@"
}
...
if [ "${DEV}" = 1 ]; then
  pipenv shell
else
  uvicorn_server_production
fi
```

## Instructions

In the cloned git repo cd into the `api_service` directory:

```bash
cd src/api_service
sh docker-shell.sh
```

Once the Docker container is up and running, you can test the startup of the FastAPI app by running:

```bash
uvicorn api.service:app --host 0.0.0.0 --port 9000 --log-level debug --reload --reload-dir api/ "$@"
```

Open your browser and navigate to http://0.0.0.0:9000/ to access the API service.

Explore the API documentation by visiting http://0.0.0.0:9000/docs. This page provides comprehensive information about the API, including available endpoints, request and response examples, and interactive testing capabilities.

# API Endpoints

### api/service.py

`service.py` is where the FastAPI application is setup and where request routes are defined.

```python
@app.get("/")  
async def get_index():
    return {"message": "Welcome to the RAG Detective App!"}

@app.get("/streaming")
async def streaming_endpoint():
...

@app.post("/rag_query")
async def rag_query(request: Request, background_tasks: BackgroundTasks):
...

@app.get("/websites", response_model=List[str])
def read_websites():
    return helper.get_website_addresses(app.state.weaviate_client)

@app.get("/timestamps/{website_address}", response_model=List[str])
def read_timestamps(website_address: str):
    return helper.get_all_timestamps_for_website(app.state.weaviate_client, website_address)

@app.get("/get_urls/{query_id}")
async def get_urls(query_id: str):
...

@app.post("/vertexai_predict")
async def vertexai_predict(request: Request):
...

@app.get("/sitemap")
def sitemap(website: str = Query(...)):
...

@app.post("/scrape_sitemap")
async def scrape_sitemap(request: Request):
...
```
## FastAPI Routes (Endpoints)

- `"GET /"`: `get_index`: An endpoint that returns a welcome message. It can be accessed via the route path "/" and only responds to GET requests.

- `"GET /streaming"`: `streaming_endpoint`: This endpoint is a demonstration s for testing streaming responses in FastAPI. When accessed via a GET request at the "/streaming" path, it responds with an event stream. It uses an asynchronous function to generate events that consist of numbers from 0 to 9 in the format `"data: {i}"`, each separated by a 0.1-second delay. As these events are generated, they are sent out as part of the StreamingResponse. This can be useful for testing how the application or client handles streaming responses, because initially we didn't know to use the `-N` flag with cURL to prevent buffering of responses.

- `"POST /rag_query"`: `rag_query`: This endpoint accepts POST requests comprised of `website`, `timestamp` and `query` keys, and responds with a streaming response. It takes a JSON from the request's body and generates a `query_id`, then it uses a Weaviate client stored in the app state to query Weaviate. The function adds a background task and returns a streaming response, which is provided by a helper function.

- `"GET /websites"`: `read_websites`: A GET route, which uses a helper function to return all website addresses.

- `"GET /timestamps/{website_address}"`: `read_timestamps`: This GET route reads timestamps of a specific website, which is provided as a path parameter.

- `"GET /get_urls/{query_id}"`: `get_urls`: A GET route that takes a `query_id` as a path parameter. It retrieves stored URLs and a financial flag for this query_id, and is called immediately after `rag_query`.

- `"POST /vertexai_predict"`: `vertexai_predict`: This POST route accepts a request with a single text field in its body. It uses Vertex AI's Prediction API, using data from Google Cloud, to get the sentiment and probabilities for the text. 

- `"GET /sitemap"`: `sitemap`: A GET route that flexibly handles various forms of website or URL input. It aims to retrieve and process a website's sitemap, returning information about the number of pages, status of the retrieval, presence of nested sitemaps, and other relevant messages.

- `"POST /scrape_sitemap"`: `scrape_sitemap`: A POST route that initiates the scraping of a sitemap. It conducts a series of tasks including downloading pages, streaming updates, saving to Google Cloud storage, and storing data into a vector storage system. Updates on the scraping and saving progress, as well as any encountered errors, are streamed back to the client.

### api/helper.py

The `helper.py` module contains helper functions used in the other scripts for setting up and running the FastAPI application. Helper functions include those for interacting with Weaviate and Google Cloud's Vertex AI platform, managing background tasks, and processing streaming responses.