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
          ├── requirements.txt
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

### Milestone2 ###

# Scraper Docker Container

We scrape all textual data off of websites based on the site's `sitemap.xml` file, which is a mapping created by websites specifically to instruct search engine crawlers to scrape their data.

## Requirements
- Python
- pandas
- BeautifulSoup
- requests

## Functions

### `scrape_sitemap(url: str) -> pd.Series`
Extracts all links from the provided company's sitemap.xml URL.
- **Args:**
  - `url` (str): The URL for a company sitemap.xml.
- **Returns:**
  - A pandas Series containing all the extracted links, or None if no links are found.

### `scrape_website(all_links: pd.Series) -> pd.DataFrame`
Extracts all textual content from the webpages of the provided links.
- **Args:**
  - `all_links` (pd.Series): A pandas Series containing all the links in the company's website.
- **Returns:**
  - A pandas DataFrame containing the scraped data including webpage link, text content, and timestamp of when the data was scraped.

### `main()`
Runs the scraping engine, reads the input sitemap URLs from "sitemap.csv", extracts data from the specified sitemaps, and saves the extracted data to CSV files.

## Output

The script currently generates CSV files containing the scraped data from the first 10 webpages of each sitemap, named as 'scraped_data_<index>.csv' However, this will be changed to store the data in the Weaviate vector store.

# Weaviate Vector Store Container

Retrieval Augmented Generation (RAG) serves as a framework to enhance Language and Learning Models (LLM) using tailored data. This approach typically involves two primary phases:

1. **Indexing Phase**: This is the initial stage where a knowledge base is developed and organized for future references.

2. **Querying Phase**: In this phase, pertinent information is extracted from the prepared knowledge base to aid the LLM in formulating responses to inquiries.

### Indexing Stage

In the initial indexing stage, text data must be first collected as documents and metadata. In this implementation, this is performed by the scraping of website. This data must be then split into "nodes", which is a represents a "chunk" or part of the data containing a certain portion of information. Nodes must are then indexed via an embedding model, where we plan on using OpenAI's `Ada v2` embedding model. The embeddings and metadata together create a rich representation to aid in retrieval.

![](../img/indexing.png)

### Querying Stage
In this stage, the RAG pipeline extracts the most pertinent context based on a user’s query and forwards it, along with the query, to the LLM to generate a response. This procedure equips the LLM with current knowledge that wasn’t included in its original training data. This also reduces the likelihood of hallucinations, a problem for LLMs when they invent answers for data they were insufficiently trained with. The pivotal challenges in this phase revolve around the retrieval, coordination, and analysis across one or several knowledge bases.

![](../img/querying.png)

In our current cloud instance with everything installed, the command to start everything up is just `docker-compose up -d` to start up the containers and `docker-compose down` to stop them.

To run the installation from scratch on a new Google Cloud instance, full instructions are located in [docs/gcp-setup-instructions.md](./docs/gcp-setup-instructions.md)

Granular instructions on how to run the `scraper` container alone are located in [docs/gcp-scraper-commands.md](./docs/gcp-scraper-commands.md)

## Notebooks

This folder contains the code and output of our scraper, currently hardcoded to only read the first 10 pages of [apple.com](https://apple.com)

