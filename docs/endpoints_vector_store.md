# FastAPI Vector Store Query API Documentation

**Table of Contents:**

**Combined Table of Contents:**

- [Overview](#overview)
- [API Endpoints](#api-endpoints)
  - [Websites Endpoint](#websites-endpoint)
  - [Timestamps Endpoint](#timestamps-endpoint)
  - [RAG Query Endpoint](#rag-query-endpoint)
- [Background Tasks and Async Helpers](#background-tasks-and-async-helpers)
  - [Process Streaming Response](#process-streaming-response)
  - [Check Required Fields](#check-required-fields)
  - [Process URL Extraction](#process-url-extraction)
- [Helper Implementations](#helper-implementations)
  - [Get Website Addresses](#get-website-addresses)
  - [Get All Timestamps for Website](#get-all-timestamps-for-website)
  - [Query Weaviate](#query-weaviate)
  - [Extract Document URLs](#extract-document-urls)
- [Testing and Usage](#testing-and-usage)

## Combined Overview

This API is designed for querying a vector store through the FastAPI framework. The service not only allows users to retrieve lists of website addresses and related timestamps stored in the vector store, but it also facilitates the retrieval of question-answering results using Retreival Augmented Generatil (RAG) methodology applied to vectorized data. Once the relevant information is retrieved from the Weaviate vector store, it is prepended to the prompt using the `LlamaIndex` library. Built to handle both GraphQL and prompt-driven queries, the API manages asynchronous requests, background tasks for post-processing, streaming responses to the client, and provides a versatile interface for extracting and processing structured data from vectorized sources.

## API Endpoints

### Websites Endpoint

- #### Path: `/websites`
- #### Method: `GET`
- #### Description:
  Retrieves a list of all website addresses from the 'Pages' class within the vector store.

- #### Response Model: `List[str]`
  An array of string values, each representing a distinct website address.

### Timestamps Endpoint

- #### Path: `/timestamps/{website_address}`
- #### Method: `GET`
- #### Description:
  Fetches all timestamps related to a specific website address from the 'Pages' class.

- #### Parameters:
  - `website_address`: The address of the website for which to retrieve timestamps (string).

- #### Response Model: `List[str]`
  An array of string values, each representing a timestamp, sorted in reverse chronological order.

### RAG Query Endpoint

- #### Path: `/rag_query`
- #### Method: `POST`
- #### Description:
  Accepts a JSON payload with a `website`, `timestamp`, and `query`. It generates a unique `query_id` and triggers a query against the vector store. The querying process is streamed back to the client, with additional background tasks initiated to process URLs from the response.

- #### Parameters:
  - `request`: The FastAPI `Request` object containing the JSON payload.
  - `background_tasks`: The FastAPI `BackgroundTasks` object for deferring tasks that shouldn't hold up the request such as URL extraction.

- #### Response:
  A `StreamingResponse` is returned with the querying results as they are generated.

## Background Tasks and Async Helpers

### Process Streaming Response

An asynchronous function iterates over the chunks of text yielded by the streaming query. It identifies and handles any text indicating financial information by setting a global `financial` flag.

### Check Required Fields

Validates the presence of required fields (`website`, `timestamp`, and `query`) in the payload and raises `HTTPException` if any are missing.

### Process URL Extraction

Executes as a background task to extract and store unique document URLs from the streaming response. It utilizes a global `query_url_storage` with an `async` lock to maintain concurrency safety.

## Helper Implementations

### Get Website Addresses

A function that executes a GraphQL query to the vector store to obtain all unique website addresses in the 'Pages' class, ensures the uniqueness of website addresses, and sorts them before returning.

### Get All Timestamps for Website

This function performs a GraphQL query specifically designed to retrieve timestamps for the pages associated with a given website address within the 'Pages' class, returning a sorted and deduplicated list of timestamp strings.

### Query Weaviate

Constructs and executes a RAG-style query within the vector store, utilizing filters for `websiteAddress` and `timestamp`. A prompt template aids in managing context and identifying financial information. Returns a streaming response from GPT-3.5 answering the prompt using the relevant context, including query results and time taken.

### Extract Document URLs

Parses a streaming response to extract URLs that point to documents from the vector store's relationship nodes.

## Testing and Usage

Use the following `curl` commands to test the various endpoints of the API:

To test the endpoint that lists all website addresses:
```shell
curl -X 'GET' 'http://localhost:9000/websites' -H 'accept: application/json'
```

To test fetching timestamps for a specific website address:
```shell
curl -X 'GET' 'http://localhost:9000/timestamps/ai21.com' -H 'accept: application/json'
```
Replace `ai21.com` with the desired website address to retrieve its associated timestamps.

To test the RAG Query endpoint for question-answering results:
```shell
curl -X 'POST' 'http://localhost:9000/rag_query' \
     -H 'accept: application/json' \
     -H 'Content-Type: application/json' \
     -d '{ "website": "example.com", "timestamp": "2021-06-01T12:00:00Z", "query": "What is the purpose of the company?" }'
```
Replace `example.com`, `2021-06-01T12:00:00Z`, and the query text with actual values. The `POST` request must include a JSON body with keys `website`, `timestamp`, and `query`.

The API is constructed to handle the queries asynchronously, stream the responses back to the client, and manage any background tasks such as URL extraction. In the event of exceptions, an `HTTPException` with a status code of 500 and a detailed error message will be raised to inform the client of any issues encountered during the processing of the requests.

