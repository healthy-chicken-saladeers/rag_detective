# Starting up the API Service

### Build Docker Image and Run Container

In the cloned git repo cd into the `api_service` directory:

```
cd src/api_service
```

Execute the following command in your terminal to build the Docker image and run the container:

```
sh docker-shell.sh
```

### Test Start-up of FastAPI
To test the start-up of FastAPI, run the following command:

```
uvicorn api.service:app --host 0.0.0.0 --port 9000 --log-level debug --reload --reload-dir api/ "$@"
```

This command launches FastAPI, making it accessible at http://0.0.0.0:9000/.

### Access in Browser
Open your browser and navigate to http://0.0.0.0:9000/ to access the API service.

### Explore API Documentation
Explore the API documentation by visiting http://0.0.0.0:9000/docs. This page provides comprehensive information about the API, including available endpoints, request and response examples, and interactive testing capabilities.