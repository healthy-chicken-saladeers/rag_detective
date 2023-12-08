AC215-Template (Milestone2)
==============================

AC215 - Milestone2

Project Organization
------------
      └── rag-detective
          ├── LICENSE
          ├── README.md
          ├── docker-compose.yml
          ├── docs
          │   ├── gcp-scraper-commands.md
          │   └── gcp-setup-instructions.md
          ├── img
          │   ├── docker-compose-up.jpg
          │   ├── firewall-rule.jpg
          │   ├── indexing.png
          │   ├── querying.png
          │   ├── weaviate-console1.jpg
          │   └── weaviate-console2.jpg
          ├── notebooks
          │   ├── scraped_data_1.csv
          │   ├── scraping_notebook.ipynb
          │   └── sitemap.csv
          └── src
              ├── llama_index
              │   ├── Dockerfile
              │   ├── Pipfile
              │   ├── Pipfile.lock
              │   ├── build_query.py
              │   └── data
              │       └── paul_graham_essay.txt
              └── scraper
                  ├── Dockerfile
                  ├── Pipfile
                  ├── Pipfile.lock
                  ├── scraper.py
                  ├── scraping_notebook.ipynb
                  └── sitemap.csv


--------
# AC215 - Milestone2 - RAG Detective

**Team Members**
Ian Kelk, Mandy Wong, Alyssa Lutservitz, Nitesh Kumar, Bailey Bailey

**Group Name**
Healthy Chicken Saladeers

**Project**
To develop an application that uses Retrieval Augmented Generation (RAG) with an LLM to create a chatbot that can answer specific questions about a company through the complete knowledge of all the information available publicly on their website in a manner that’s more specific and insightful than using a search engine.

### More docs

To run the installation from scratch on a new Google Cloud instance, full instructions are located in:
* [docs/gcp-setup-instructions.md](./docs/gcp-setup-instructions.md)

Granular instructions on how to run the `scraper` container alone are located in:
* [docs/gcp-scraper-commands.md](./docs/gcp-scraper-commands.md)

### Milestone2 ###

# Scraper Docker Container

We scrape all textual data off of websites based on the site's `sitemap.xml` file, which is a mapping created by websites specifically to instruct search engine crawlers to scrape their data.

## Requirements
- Python
- pandas
- BeautifulSoup
- requests

## Functions

#### `scrape_sitemap(url: str) -> pd.Series`
Extracts all links from the provided company's sitemap.xml URL.
- **Args:**
  - `url` (str): The URL for a company sitemap.xml.
- **Returns:**
  - A pandas Series containing all the extracted links, or None if no links are found.

#### `scrape_website(all_links: pd.Series) -> pd.DataFrame`
Extracts all textual content from the webpages of the provided links.
- **Args:**
  - `all_links` (pd.Series): A pandas Series containing all the links in the company's website.
- **Returns:**
  - A pandas DataFrame containing the scraped data including webpage link, text content, and timestamp of when the data was scraped.

#### `main()`
Runs the scraping engine, reads the input sitemap URLs from "sitemap.csv", extracts data from the specified sitemaps, and saves the extracted data to CSV files.

## Output

The script currently generates CSV files containing the scraped data from the first 10 webpages of each sitemap, named as 'scraped_data_<index>.csv' However, this will be changed to store the data in the Weaviate vector store.

# Weaviate Vector Store Container

Weaviate is an open-source knowledge graph program that utilizes GraphQL and RESTful APIs. It’s designed to organize large amounts of data in a manner that makes the data interconnected and contextual, allowing users to perform semantic searches and analyses. It can automatically classify and interpret data through machine learning models, facilitating more intelligent and informed data retrievals and insights. It is scalable and can be used for a variety of applications, such as data analysis and information storage and retrieval.

Weaviate can be queried through either a semantic (vector) search, a lexical (scalar) search, or a combination of both. A vector search enables the execution of searches based on similarity, while scalar searches facilitate filtering through exact matches. This is important, as it will allow us to query for specific website scrapes and dates, as well as match the embeddings to find relevant data.

In our current cloud instance with everything installed, the command to start everything up is just:

* `docker-compose up -d` to start up the containers
* `docker-compose down` to stop them.

# LlamaIndex

Retrieval Augmented Generation (RAG) serves as a framework to enhance Language and Learning Models (LLM) using tailored data. This approach typically involves two primary phases:

1. **Indexing Phase**: This is the initial stage where a knowledge base is developed and organized for future references.

2. **Querying Phase**: In this phase, pertinent information is extracted from the prepared knowledge base to aid the LLM in formulating responses to inquiries.

### Indexing Stage

In the initial indexing stage, text data must be first collected as documents and metadata. In this implementation, this is performed by the scraping of website. This data must be then split into "nodes", which is a represents a "chunk" or part of the data containing a certain portion of information. Nodes must are then indexed via an embedding model, where we plan on using OpenAI's `Ada v2` embedding model. The embeddings and metadata together create a rich representation to aid in retrieval.

![](img/indexing.png)

### Querying Stage
In this stage, the RAG pipeline extracts the most pertinent context based on a user’s query and forwards it, along with the query, to the LLM to generate a response. This procedure equips the LLM with current knowledge that wasn’t included in its original training data. This also reduces the likelihood of hallucinations, a problem for LLMs when they invent answers for data they were insufficiently trained with. The pivotal challenges in this phase revolve around the retrieval, coordination, and analysis across one or several knowledge bases.

![](img/querying.png)

LlamaIndex is a data framework to ingest, structure, and access private or domain-specific data. We plan on using it to chunk our text data and combine it with the metadata to create nodes to insert into the Weaviate vector store. We plan on using its functions as follows:

* **Data connector** to ingest the nodes into Weaviate
* **Data index** using Weaviate to store the embeddings and 
* **Query engine** to retreive the knowledge-augmented output
* **Application integrations** to work with Docker and likely Flask.

At present, LlamaIndex is set up to run a short "build and index" query using Paul Graham’s essay, [“What I Worked On”](http://paulgraham.com/worked.html). As we build the application, this will be changed to query the Weaviate store and output to the OpenAI API.

# Note

* Currently, both LlamaIndex and our scraper perform short demonstration tasks. As such, once these tasks complete in a few seconds, the containers shut down automatically.

* Since the `scraper` and `llama_index` services need to be continuously running to receive requests, they should ideally be long-running services, such as web servers or APIs that are designed to run indefinitely and handle incoming requests. We will likely achieve this by running a web framework like Flask or FastAPI in our containers to receive and handle HTTP requests.

* Additionally, we do not have any `requirements.txt` present since the dependencies are handled by the Dockerfiles.

* Currently, both Weaviate and LlamaIndex have access to the OpenAI API. There are two models that need to be used; the `Ada v2` embedding model and `GPT-3.5`, so depending on how the work is distributed for the data ingestion and the retrieval, one or both of Weaviate or LlamaIndex may use the API.

# Additional Files

### `docker-compose.yml`

We use Docker Compose to define and run multi-container Docker applications. Below is a summary of the services defined in our `docker-compose.yml` file.

#### 1. Weaviate Service
   - **Image:** `semitechnologies/weaviate:1.21.3`
   - **Purpose:** Vector store for use with RAG
   - **Command:** Runs Weaviate with specified host, port, and scheme.
   - **Ports:** Exposes port `8080` for external access.
   - **Environment Variables:**
     - Uses OpenAI API Key from host environment variable `$OPENAI_APIKEY`.
     - Configures various Weaviate parameters like `QUERY_DEFAULTS_LIMIT`, `PERSISTENCE_DATA_PATH`, and `ENABLE_MODULES`.
   - **Volume:** Persists data at `/var/lib/weaviate` using a named volume `weaviate_data`.
   - **Restart Policy:** Restarts the container on failure.

#### 2. Scraper Service
   - **Build Context:** `./src/scraper`
   - **Purpose:** Scrapes a given website using its `sitemap.xml`
   - **Command:** Executes `scraper.py` with Python.
   - **User:** Runs as user `appuser`.
   - **Volume:** Mounts `./src/scraper/scraper_data` to `/app/data` in the container.

#### 3. Llama_index Service
   - **Build Context:** `./src/llama_index`
   - **Purpose:** Provides the RAG framework.
   - **Command:** Currently executes `build_query.py` with Python as a test example.
   - **User:** Runs as user `appuser`.
   - **Environment Variables:**
     - Uses the same OpenAI API Key as Weaviate from host environment variable `$OPENAI_APIKEY`.
   - **Volume:** Mounts `./src/llama_index` to `/app/llama_index` in the container.

### Volumes
- **weaviate_data:** Used by the Weaviate service to persist data.
- **scraper_data:** Intermediate scraping data which may or may not be needed such as CSV and XML files.

As mentioned previously, to run the defined services, navigate to the root project directory containing the `docker-compose.yml` file and run the following command in the terminal:

```sh
docker-compose up
```

### `gcp-scraper-commands.md` and `gcp-setup-instructions.md`

* Additional documentation files in markdown format on starting up the project from a brand new GCP instance and to control the Docker containers individually if so desired

### `img` folder

* Image assets for display in this and the above markdown files.

### `notebooks`

* This folder contains the code and output of our scraper in `scraping_notebook.ipynb`. The `sitemap.csv` is a list of sitemaps to scrape, currently set to only [apple.com](https://apple.com). It also contains the results of the scraping, `scraped_data1.csv`.

### `src`

* Contains all the Python code and Dockerfiles to build the project. It also contains the data `paul_graham_essay.txt` which is used as test data for LlamaIndex.




