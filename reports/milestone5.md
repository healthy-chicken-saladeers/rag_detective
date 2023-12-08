AC215 Milestone5
==============================

Project Organization
------------
    .
    └── ac215_healthychickensaladeers
        ├── LICENSE
        ├── README.md
        ├── docker-compose.yml
        ├── docs
        │   ├── api-service-documentation.md
        │   ├── deploy-custom-container-BERT-vertex.md
        │   ├── deployment.md
        │   ├── docker-gcsfuse.md
        │   ├── experiment-bert.md
        │   ├── frontend.md
        │   ├── gc-function-instructions.md
        │   ├── gcp-cli-instructions-macos.md
        │   ├── gcp-docker-commands.md
        │   ├── gcp-setup-instructions.md
        │   ├── gcs-bucket-instructions.md
        │   ├── notebooks_env_file_setup.md
        │   ├── optimization.md
        │   ├── vertex-ai-model-training.md
        │   └── vscode-remote-ssh-extension-gcp-vm.md
        ├── img
        │   ├── ...
        ├── ml_workflow
        │   ├── data_collector
        │   │   ├── Dockerfile
        │   │   ├── Pipfile
        │   │   ├── Pipfile.lock
        │   │   ├── Untitled.ipynb
        │   │   ├── cli.py
        │   │   ├── data
        │   │   │   └── v1.0.zip
        │   │   ├── docker-entrypoint.sh
        │   │   └── docker-shell.sh
        │   ├── inference
        │   │   ├── Dockerfile
        │   │   ├── app.py
        │   │   ├── docker-shell.sh
        │   │   └── predictor.py
        │   ├── model_training
        │   │   ├── Dockerfile
        │   │   ├── Pipfile
        │   │   ├── Pipfile.lock
        │   │   ├── cli.py
        │   │   ├── docker-entrypoint.sh
        │   │   ├── docker-shell.sh
        │   │   ├── package
        │   │   │   ├── setup.py
        │   │   │   └── trainer
        │   │   │       ├── __init__.py
        │   │   │       └── task.py
        │   │   ├── package-trainer.sh
        │   │   └── ragdetective-app-trainer.tar.gz
        │   └── workflow
        │       ├── Dockerfile
        │       ├── Pipfile
        │       ├── Pipfile.lock
        │       ├── cli.py
        │       ├── docker-entrypoint.sh
        │       ├── docker-shell.sh
        │       ├── model.py
        │       ├── model_training.yaml
        │       └── sample-pipeline1.yaml
        ├── model_training
        │   ├── Dockerfile
        │   ├── Pipfile
        │   ├── Pipfile.lock
        │   ├── cli.sh
        │   ├── docker-entrypoint.sh
        │   ├── docker-shell.sh
        │   ├── package
        │   │   ├── setup.py
        │   │   └── trainer
        │   │       ├── __init__.py
        │   │       └── task.py
        │   ├── package-trainer.sh
        │   └── secrets
        ├── notebooks
        │   ├── BERT_fine-tune_financials
        │   │   └── ...
        │   ├── BERT_fine-tune_financials_balanced
        │   │   ├── ...
        │   │   ├── intial_debiasing
        │   │   │   ├── ...
        │   │   └── longer_debiasing_20_epochs
        │   │       ├── ...
        │   ├── distillation
        │   │   ├── ...
        │   ├── financial_data
        │   │   ├── ...
        │   └── ...
        ├── reports
        │   ├── milestone2.md
        │   ├── milestone3.md
        │   └── milestone4.md
        └── src
            ├── api_service
            │   ├── Dockerfile
            │   ├── Pipfile
            │   ├── Pipfile.lock
            │   ├── README.txt
            │   ├── api
            │   │   ├── helper.py
            │   │   └── service.py
            │   ├── docker-entrypoint.sh
            │   ├── docker-shell.sh
            │   └── secrets
            ├── bert_financial
            │   ├── Dockerfile
            │   ├── Pipfile
            │   ├── Pipfile.lock
            │   ├── entrypoint.sh
            │   ├── finetune_bert.py
            │   └── gcsbucket
            ├── deployment
            │   ├── Dockerfile
            │   ├── README.md
            │   ├── deploy-create-instance.yml
            │   ├── deploy-docker-images.yml
            │   ├── deploy-provision-instance.yml
            │   ├── deploy-setup-containers.yml
            │   ├── deploy-setup-webserver.yml
            │   ├── docker-entrypoint.sh
            │   ├── docker-shell.sh
            │   ├── inventory.yml
            │   └── nginx-conf
            │       └── nginx
            │           └── nginx.conf
            ├── frontend
            │   ├── Dockerfile
            │   ├── Dockerfile.dev
            │   ├── README.txt
            │   ├── docker-shell.sh
            │   ├── img
            │   │   └── ...
            │   ├── index.html
            │   └── styles.css
            ├── llama_index
            │   ├── Dockerfile
            │   ├── Pipfile
            │   ├── Pipfile.lock
            │   ├── build_query.py
            │   ├── data
            │   │   └── ...
            │   ├── entrypoint.sh
            │   ├── gcf
            │   │   ├── add_to_weaviate
            │   │   │   ├── add_to_weaviate.py
            │   │   │   └── requirements.txt
            │   │   ├── create_weaviate_schema
            │   │   │   ├── gcf_create_weaviate_schema.py
            │   │   │   └── requirements.txt
            │   │   ├── index_llama_index
            │   │   │   ├── gcf_index_llamaindex.py
            │   │   │   └── requirements.txt
            │   │   └── query_llama_index
            │   │       ├── gcf_query_llamaindex.py
            │   │       └── requirements.txt
            │   └── gcsbucket
            ├── prompts
            │   └── prompts.py
            ├── scraper
            │   ├── Dockerfile
            │   ├── Pipfile
            │   ├── Pipfile.lock
            │   ├── chromedriver
            │   ├── log
            │   ├── scraper.py
            │   ├── scraperlib.py
            │   ├── scraping_notebook.ipynb
            │   └── sitemap.csv
            └── vector_store
                ├── schema.json
                ├── schema_old.json
                ├── weaviate.schema.md
                └── weaviate.schema.old.md

--------
# AC215 - Milestone5 - RAG Detective

**Team Members**
Ian Kelk, Mandy Wong, Alyssa Lutservitz, Nitesh Kumar

**Group Name**
Healthy Chicken Saladeers

**Project**
To develop an application that uses Retrieval Augmented Generation (RAG) with an LLM to create a chatbot that can answer specific questions about a company through the complete knowledge of all the information available publicly on their website in a manner that’s more specific and insightful than using a search engine.

# Application Design

We've put together a detailed design document outlining the application’s architecture, comprised of a Solution Architecture and Technical Architecture graphic to ensure all our components work together.

![](img/solution_architecture_1.png)

![](img/solution_architecture_2.png)

## Technical Architecture:

![](img/technical_architecture.png)

## Quick look: The new documentation files for this milestone
#### The full summaries of these documents are discussed below
- [API Service Documentation](./docs/api-service-documentation.md)
- [Frontend Documentation](./docs/frontend.md)
- [Deploying Custom Container with BERT onto Vertex AI](./docs/deploy-custom-container-BERT-vertex.md)
- [Deployment with Ansible](./docs/deployment.md)
- [VS Code Remote SSH Extension Guide](./docs/vscode-remote-ssh-extension-gcp-vm.md)

# FastAPI Service Summary

This section hosts a Dockerized FastAPI service designed for deployment on Google Cloud. It features a range of files facilitating Docker containerization and FastAPI application management.

## Key Components

### Docker Setup
- `Dockerfile`: Creates a Docker image for the FastAPI app, based on Debian with Python 3.9.
- `docker-shell.sh`: Script to build and run the Docker container, mapping local directories and setting environment variables.
- `docker-entrypoint.sh`: Script that initiates the Uvicorn server to serve the FastAPI app.

### FastAPI Application
- `api/service.py`: The core application file defining API endpoints and their functionalities.
- `api/helper.py`: Provides support functions for the FastAPI routes.

### Documentation and Instructions
- `README.txt`: Basic instructions for Docker image and container operations, and FastAPI interaction.

## API Endpoints Overview
- `GET /`: Returns a welcome message.
- `GET /streaming`: Demonstrates streaming responses.
- `POST /rag_query`: Handles queries with streaming response.
- `GET /websites`: Lists website addresses.
- `GET /timestamps/{website_address}`: Retrieves timestamps for a specific website.
- `GET /get_urls/{query_id}`: Fetches URLs and financial flags for a query.
- `POST /vertexai_predict`: Uses Vertex AI's Prediction API for sentiment analysis.

![](img/api_server_docs.jpg)

The repository offers comprehensive guidance on setting up and running the Dockerized FastAPI service, alongside detailed documentation accessible through the FastAPI's interactive documentation feature.

For more information and detailed instructions, see [api-service-documentation.md.](./docs/api-service-documentation.md)

# Frontend Service Summary

This section contains a Dockerized frontend application, suitable for deployment with a web server. It includes essential files for building and running the application in a Docker container.

## Key Components

### Docker Setup
- `Dockerfile`: Creates a Docker image using nginx, copies HTML and CSS files into the container, and exposes port 80.
- `docker-shell.sh`: A script for building the Docker image and running a container, mapping the container's port 8080 to the host's port 8080.
- `README.txt`: Documentation on building and running the Docker container for both simple and React frontends.

### Frontend Application
- `index.html`: The main HTML file for the app, setting up the layout and interactive elements for the "Rag Detective" web application.
- `styles.css`: Defines the visual design of the application, including animations, color schemes, and responsive elements for a user-friendly interface.

![](img/rag-detective-app.jpg)
![](img/rag-detective-app2.jpg)

## Detailed Overview

### Dockerfile and Scripts
- **Dockerfile**: Outlines steps for building the Docker image with a lightweight web server and deploying the frontend application.
- **docker-shell.sh**: Automates the Docker image building and container running processes.
- **README.txt**: Provides detailed instructions for Docker operations and frontend deployment.

### index.html
- Features interactive elements for selecting websites and timestamps, inputting queries, and displaying responses.
- Implements API interactions for fetching website data, submitting queries, and retrieving URLs and sentiment analysis.
- Displays dynamic content based on user interactions and server responses, including sentiment-driven images of a chatbot character, BERT.

### styles.css
- Applies modern styling to the web application, utilizing Google's Roboto font and various CSS animations.
- Ensures a cohesive and appealing visual experience, with designated styles for different UI components.

For a comprehensive guide on setting up and interacting with the frontend application, see [frontend.md.](./docs/frontend.md)

# Financial Sentiment BERT Custom Model Container

This section provides the setup for deploying a BERT model, fine-tuned for financial sentiment, using FastAPI, Docker, and Google Vertex AI.

## Key Components

### Files and Scripts
- `predictor.py`: Handles pre-processing, model prediction, and post-processing.
- `app.py`: A FastAPI wrapper for serving the model.
- `Dockerfile`: Defines Docker commands for setting up the API's image.
- `shell_script.sh`: Builds and runs the Docker image.

### Detailed Descriptions

#### Predictor.py
- `CustomPredictor` class: Manages predictions, loading the model, and providing API readiness status.
- `CustomModelPredictor` class: Handles model loading, prediction, and pre/post-processing tasks.

#### App.py
- Implements FastAPI endpoints for health checks (`/health`) and predictions (`/predict`).

#### Dockerfile
- Configures the TensorFlow image base, copies code, installs dependencies, and starts the API on port 8080.

#### Shell Script
- Automates Docker image building and container launching, binding the container's port 8000 to the host's port 8000.

## Usage Instructions
- Download the pre-trained model from Google Cloud Storage.
- Build and run the Docker container using `docker-shell.sh`.
- Test the API using `curl` commands.

# Deployment to Google Cloud Vertex AI

### Step-by-Step Guide
1. **Build and Push Docker Image:** Set environment variables, build the Docker image, and push it to the Google Container Registry.
2. **Upload Model to Vertex AI:** Use `gcloud` commands to upload the model to Vertex AI, specifying custom health and prediction routes.
3. **Create Endpoint:** Generate an endpoint for model serving.
4. **Deploy Model to Endpoint:** Deploy the model using `gcloud` commands and test via the cloud console or `curl`.

![](img/instances.jpg)

## Cloud Testing
- Test the deployed model and endpoint on Google Cloud's console or using `curl` commands.

This repository offers comprehensive guidance on setting up, testing, and deploying the BERT model for financial sentiment analysis using Docker and Google Vertex AI.

For more information and detailed instructions, see [deploy-custom-container-BERT-vertex.md.](./docs/deploy-custom-container-BERT-vertex.md)

# Deployment

This section outlines the deployment procedures for the RAG Detective App using Ansible and Google Cloud Platform (GCP) services.

## Key Components

### Setup and Deployment
- **Enable GCP APIs**: Compute Engine, Service Usage, Cloud Resource Manager, and Google Container Registry APIs.
- **GCP Service Accounts**: Steps to create and configure service accounts like `deployment` and `gcp-service` with specific roles for deployment activities.

### Docker Container Setup
- Using Docker to build a container for connecting to GCP and creating VMs.
- Detailed instructions for building and running the Docker container, including the expected output.

### SSH Configuration
- Enabling OS login and creating SSH keys for the service account.
- Adding public SSH keys to instances for secure access.

### Deployment Setup
- **Build and Push Docker Containers to GCR**: Utilizing Ansible to automate the process.
- **Create Compute Instance (VM) Server in GCP**: Steps to create a VM and update the inventory file with its external IP address.
- **Provision Compute Instance in GCP**: Instructions for installing and setting up required deployment elements.
- **Setup Docker Containers in the Compute Instance**: Configuring and launching necessary Docker containers.

### Web Server Configuration
- Creating and setting up an Nginx configuration file for the web server.
- Deploying and restarting the Nginx container to reflect changes.

## Testing and Verification
- Commands to SSH into the server, check container statuses, and access logs.
- Verification of the web server's functionality by accessing the deployed app via its external IP address.

This repository provides a comprehensive guide for deploying the RAG Detective App using Ansible and GCP, ensuring a streamlined and secure deployment process.

For more information and detailed instructions, see [deployment.md.](./docs/deployment.md)

## Using VS Code Remote - SSH Extension to Connect to GCP VM

We also provide documentation on this functionality [here.](./docs/vscode-remote-ssh-extension-gcp-vm.md)

## We've archived the rest of the readme content from previous milestones

This concludes what was shown in the [Milestone5](https://github.com/ac2152023/ac2152023_template/tree/milestone5) template, so to make this more organized we've moved all the previous content to [reports/milestone4.md.](reports/milestone4.md)

### Appendix: More docs from previous milestones

- [W&B Report on BERT fine-tuning](https://api.wandb.ai/links/iankelk/mmrp03k6)
- [Static version of Report on BERT fine-tuning](./docs/experiment-bert.md)
- [W&B Report on BERT into LSTM and 6-layer BERT](https://api.wandb.ai/links/iankelk/jpvsoack)
- [Static version of Report on BERT into LSTM and 6-layer BERT](./docs/optimization.md)
- [Setting Up a Google Cloud Function](./docs/gc-function-instructions.md)
- [Serverless Model training with Vertex AI](./docs/vertex-ai-model-training.md)
- [How to install the Google Cloud CLI ](./docs/gcp-cli-instructions-macos.md)
- [How to set up a Google Cloud Storage bucket](./docs/gcs-bucket-instructions.md)
- [Google Cloud Platform Setup](./docs/gcp-setup-instructions.md)
- [How we launch `gcsfuse` upon container launch](./docs/docker-gcsfuse.md)
- [Granular instructions on how to run the `scraper` container alone](./docs/gcp-docker-commands.md)