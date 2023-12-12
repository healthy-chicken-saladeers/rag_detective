# You need to have the OPENAI_APIKEY environment variable set for this.
# As well, ml-workflow.ml has to be placed in the /secrets folder of the repo
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, File, Query
from fastapi.responses import StreamingResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import datetime
import os
from typing import Dict, List
from api import helper, dummy
from typing import List
import asyncio 
from asyncio import Lock
import weaviate
import uuid
from google.cloud import aiplatform
from google.auth import exceptions
from google.oauth2 import service_account
# Suppress Pydantic warnings in LlamaIndex
import warnings
warnings.simplefilter(action='ignore', category=Warning)

class FinancialStatus:
    """
    A class to encapsulate and manage the financial status.

    Attributes:
        _is_financial (bool): A flag indicating whether the financial status is set.
    """

    def __init__(self):
        """Initializes the financial status to False by default."""
        self._is_financial = False

    def set_financial(self, status: bool):
        """
        Sets the financial status flag.
        
        Args:
            status (bool): The new status to be set, indicating whether the context is financial.
        """
        self._is_financial = status

    def is_financial(self) -> bool:
        """
        Checks if the current status is financial.

        Returns:
            bool: The current value of the financial status flag.
        """
        return self._is_financial

class QueryStorage:
    """
    A class for storing and retrieving queries in a thread-safe manner.

    Attributes:
        _storage (dict): A dictionary storing the queries with their IDs as keys.
        _lock (Lock): An asyncio lock to ensure thread-safe access to the storage.
    """

    def __init__(self):
        """Initializes an empty storage for queries and an asyncio lock for synchronization."""
        self._storage = {}
        self._lock = Lock()

    async def store_query(self, query_id: str, financial: bool, urls: List[str]):
        """
        Stores a query with its associated financial status and URLs in the storage.

        This method is thread-safe and uses an asyncio lock to protect the access to the storage.
        
        Args:
            query_id (str): The unique identifier for the query.
            financial (bool): The financial status associated with the query.
            urls (List[str]): A list of URLs associated with the query.
        """
        async with self._lock:
            self._storage[query_id] = (financial, urls)

    async def retrieve_query(self, query_id: str) -> tuple:
        """
        Retrieves and deletes a query from the storage.

        This method safely pops the query information based on the query ID, if it exists,
        and returns the financial status and associated URLs. Otherwise, returns (None, None).
        
        Args:
            query_id (str): The unique identifier for the query to be retrieved.
        
        Returns:
            tuple: A tuple containing the financial status and list of URLs for the query, or (None, None) if not found.
        """
        async with self._lock:
            return self._storage.pop(query_id, (None, None))


# Test using this line of curl:
# curl -N -H "Content-Type: application/json" -d "{\"website\": \"ai21.com\", \"query\": \"How was AI21 Studio a game changer\", \"timestamp\": \"2023-10-06T18-11-24\"}" http://localhost:9000/rag_query

# Set the OpenAI key as an Environment Variable (the different underscore notation is weaviate vs llamaindex)
os.environ["OPENAI_API_KEY"] = os.environ.get('OPENAI_APIKEY')

# Current Weaviate IP
WEAVIATE_IP_ADDRESS = "34.42.138.162"

# Setup FastAPI app
app = FastAPI(title="API Server", description="API Server", version="v1")

# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    Initializes application components and stores them in the application state at startup.

    This function is executed automatically when the FastAPI application starts. It establishes connections
    and configurations for the Weaviate client and also initializes the classes for managing financial status
    and URL storage.
    
    The Weaviate client is created using the IP address specified by the WEAVIATE_IP_ADDRESS environment variable
    and is stored in the application state for accessibility throughout the application lifecycle.
    
    Two instances of custom classes, QueryStorage and FinancialStatus, are also created and stored in the application's
    state. These instances handle financial flag status checks and URL storage management, respectively, enabling thread-safe
    encapsulation of functionality across API endpoints.

    Note:
    - The WEAVIATE_IP_ADDRESS environment variable must be set prior to starting the application.
    - QueryStorage encapsulates the storage and retrieval of query-related information.
    - FinancialStatus encapsulates the checking and setting of the financial status associated with query processing.

    Example usage:
    This function is not meant to be triggered manually; it is an event handler for application startup.
    """
    app.state.weaviate_client = weaviate.Client(url=f"http://{WEAVIATE_IP_ADDRESS}:8080")
    app.state.query_storage = QueryStorage()
    app.state.financial_status = FinancialStatus()


# Routes
@app.get("/")
async def get_index():
    """
    Responds with a welcome message at the root path of the application.

    This asynchronous endpoint is the default route for the application and is
    accessed via a GET request. When invoked, it returns a JSON object with a
    greeting message, indicating that the application is successfully running.

    Returns:
        dict: A JSON object containing a welcome message to the RAG Detective App.

    Example usage:
        curl http://localhost:9000/
        """
    return {"message": "Welcome to the RAG Detective App!"}

# Dummy function for testing streaming
@app.get("/streaming")
async def streaming_endpoint():
    """
    Streams data as a continuous response over time.

    This asynchronous endpoint streams a sequence of data points from a predefined
    dataset (DUMMY_DATA) in the 'dummy' module. Each data point is sent separately
    with a short delay (0.1 seconds) between them, simulating a real-time data stream.

    The function uses an asynchronous generator to yield each data point, which is
    then streamed back to the client as a continuous text response.

    Returns:
        StreamingResponse: An ongoing streaming response of data points, sent one by one.

    Example:
        curl http://localhost:9000/streaming

    """
    async def event_generator():
        for i in range(len(dummy.DUMMY_DATA)):
            yield f"{dummy.DUMMY_DATA[i]} "
            await asyncio.sleep(0.1)
    return StreamingResponse(event_generator(), media_type="text/plain")

async def process_streaming_response(local_streaming_response, financial_status: FinancialStatus):
    """
    Processes streaming response from a local source, checks for financial markers, 
    and yields processed text segments.

    This asynchronous function iterates over a generator of streaming responses,
    examining each text segment for a specific marker ("QQ"). "QQ" was chosen since for
    reasons only known to itself, GPT-3.5 seems to struggle with more complex flags.
    If such a marker is found, it indicates a financial context and the financial status 
    is set to True using the financial_status instance provided. The marker is then removed
    from the text.

    The function yields each processed text segment. It handles `asyncio.CancelledError` to
    gracefully manage the cancellation of the streaming.

    Args:
        local_streaming_response: An instance of a streaming response object with a 'response_gen'
                                  generator attribute, which is a generator yielding text segments.
        financial_status (FinancialStatus): An instance of FinancialStatus to manage the financial
                                            status throughout the processing.

    Yields:
        str: Processed text segments without the financial marker.
    
    Raises:
        asyncio.CancelledError: If the streaming process is cancelled. This is caught and handled 
                                to allow for a graceful shutdown of the generator.
    """
    try:
        for text in local_streaming_response.response_gen:
            # Check for the financial flag at the end of the text
            if "QQ" in text:
                financial_status.set_financial(True)
                text = text.replace("QQ", "")  # remove the "%%"
            if text:   # Check for null character or empty string
                print(f"Yielding: [{text}]")
                yield text  
        if financial_status.is_financial():
            print(" Financial flag set!", flush=True)
    except asyncio.CancelledError as e:
        print('Streaming cancelled', flush=True)

def check_required(data: Dict[str, str], keys: List[str]):
    """
    Checks if all required keys are present in the given data dictionary.

    This function iterates through a list of keys and verifies if each key is present in the
    provided data dictionary. If any key is missing, an HTTPException with status code 400 is raised,
    indicating a bad request due to a missing required field.

    Args:
        data (Dict[str, str]): The dictionary of data in which to look for keys. Each key maps to a string value.
        keys (List[str]): A list of keys that are required to be present in the data dictionary.

    Raises:
        HTTPException: If any of the required keys are missing in the data dictionary. The exception
                       contains the status code 400 and a detailed error message specifying the missing key.
    """
    for key in keys:
        if not data.get(key):
            raise HTTPException(status_code=400, detail=f"Missing required field: '{key}'")
    for key in keys:
        if not data.get(key):
            raise HTTPException(status_code=400, detail=f"Missing required field: '{key}'")

@app.post("/rag_query")
async def rag_query(request: Request, background_tasks: BackgroundTasks):
    """
    Processes a RAG query and returns a streaming response.

    This asynchronous endpoint accepts a JSON payload containing the parameters 'website', 'timestamp',
    and 'query'. It generates a unique ID for the query, performs a query using Weaviate, and initiates
    the URL processing in the background. The response is streamed back to the client, with updates on the
    processing progress.

    Args:
        request (Request): The incoming HTTP request containing the query parameters.
        background_tasks (BackgroundTasks): BackgroundTasks instance for scheduling background tasks.

    Returns:
        StreamingResponse: A streaming response that provides real-time updates of the query processing.

    Raises:
        HTTPException: If any required fields are missing in the request.

    Note:
        The endpoint interacts with the `financial_status` instance during URL processing to manage the financial flag.
        The response includes a custom 'X-Query-ID' header to track the query ID for reference retrieval.

    Example usage:
    curl -X POST http://localhost:9000/rag_query \
     -H "Content-Type: application/json" \
     -d {"website": "example.com", "timestamp": "2021-01-01T12:00:00", "query": "example query"}
    """
    data = await request.json()

    # Check if the required parameters are provided
    check_required(data, ["website", "timestamp", "query"])

    website = data.get('website')
    timestamp = data.get('timestamp')
    query = data.get('query')

    # Generate a unique ID for this specific query
    query_id = str(uuid.uuid4())
    print("Query ID:", query_id)

    # Query Weaviate
    streaming_response = helper.query_weaviate(app.state.weaviate_client, website, timestamp, query)

    financial_status_instance = request.app.state.financial_status

    # Add the URL processing function as a background task
    background_tasks.add_task(process_url_extraction, query_id, streaming_response, financial_status_instance, request.app.state.query_storage)

    # Generate the streaming response and return it
    headers = {
        'Cache-Control': 'no-cache',
        'Access-Control-Expose-Headers': 'X-Query-ID',  # Ensure the custom header is exposed
        'X-Query-ID': query_id  # set the header to track the query_id for the reference retrieval
    }

    return StreamingResponse(
        process_streaming_response(streaming_response, financial_status_instance),
        media_type="text/plain",
        headers=headers
    )

async def process_url_extraction(query_id: str, streaming_response, financial_status: FinancialStatus, query_storage: QueryStorage):
    """
    Processes the given streaming response to extract and store unique URLs.

    This asynchronous function takes a streaming response, extracts URLs from the
    documents in the stream, and uses the `query_storage` instance to store them. It ensures
    that the URLs are unique and maintains their order. The extracted URLs, along with the financial
    status, are associated with the provided `query_id`.

    Args:
        query_id (str): The unique identifier for the query.
        streaming_response: The streaming response object to process.
        financial_status (FinancialStatus): An instance representing the financial status checker.
        query_storage (QueryStorage): An instance for managing query-related URL storage.

    Note:
        URLs extraction and storage are managed by a `query_storage` instance which employs an asynchronous
        lock to ensure thread-safe operations. The storage format for each query is a tuple
        of the financial flag and the list of unique URLs.
    """
    extracted_urls = helper.extract_document_urls(streaming_response)
    unique_urls = []
    # Use a loop to maintain order and avoid duplicates
    for url in extracted_urls:
        if url not in unique_urls:
            unique_urls.append(url)
    
    # Use the provided instance to store the ordered, unique URLs
    await query_storage.store_query(query_id, financial_status.is_financial(), unique_urls)

@app.get("/websites", response_model=List[str])
def read_websites():
    """
    Retrieves a list of website addresses.

    This endpoint calls a helper function to fetch website addresses from a Weaviate client,
    which is stored in the application's state. It returns a list of strings, each representing
    a website address.

    Returns:
        List[str]: A list of website addresses as strings.

    Note:
        The actual fetching of website addresses is handled by the `helper.get_website_addresses`
        function, which interacts with the Weaviate client.

    Example usage:
        curl -X 'GET' 'http://localhost:9000/websites' -H 'accept: application/json'
    """
    return helper.get_website_addresses(app.state.weaviate_client)

@app.get("/timestamps/{website_address}", response_model=List[str])
def read_timestamps(website_address: str):
    """
    Retrieves a list of timestamps associated with the specified website address.

    This endpoint accepts a website address as a path parameter and returns a list of timestamps
    for that website. It uses a helper function that interacts with the Weaviate client (stored in the
    application's state) to fetch the timestamps.

    Args:
       website_address (str): The website address for which timestamps are requested.

    Returns:
       List[str]: A list of timestamp strings associated with the given website address.

    Note:
       The actual data retrieval is managed by the `helper.get_all_timestamps_for_website` function.

    Example usage:
       curl -X 'GET' 'http://localhost:9000/timestamps/ai21.com' -H 'accept: application/json'
    """

    return helper.get_all_timestamps_for_website(app.state.weaviate_client, website_address)

@app.get("/get_urls/{query_id}")
async def get_urls(request: Request, query_id: str):
    """
    Retrieves the URLs and financial flag associated with the provided query ID.

    This asynchronous endpoint takes a query ID as a path parameter, looks up the associated
    URLs and financial flag within the application's query storage, and returns them. If the URLs 
    are not available or the query ID is invalid, it responds with an error message and a 404 status code. 
    The URLs and flag are deleted from storage after retrieval to maintain simplicity.

    Args:
        request (Request): The incoming HTTP request object.
        query_id (str): The unique identifier for the query.

    Returns:
        JSONResponse: A response object containing the URLs and financial flag if available,
                      or an error message with a 404 status code if not.

    Raises:
        HTTPException: If the query ID is invalid or URLs are not available yet.

    Note:
        This function interacts with the query storage encapsulated by an instance of 
        'QueryStorage' class, part of the application's state, which is protected by 
        an asynchronous lock to ensure thread-safe operations.
    Example usage:
        curl http://localhost:9000/get_urls/{query_id}
    """
    financial_flag, urls = await request.app.state.query_storage.retrieve_query(query_id)
    if urls is None:
        # Correctly format the response with a custom status code
        return JSONResponse(content={"error": "URLs not available yet or invalid query ID"}, status_code=404)

    return {"urls": urls, "financial_flag": financial_flag}




@app.post("/vertexai_predict")
async def vertexai_predict(request: Request):
    """
    Performs sentiment analysis using Google Cloud's Vertex AI based on the provided text.

    This endpoint accepts a request containing text data and sends it to a pre-configured Vertex AI endpoint
    for sentiment analysis. It requires authentication with Google Cloud using a service account. The response
    from Vertex AI, including the sentiment and probabilities, is parsed and returned in a structured format.

    Args:
       request (Request): The incoming HTTP request containing the text data for prediction.

    Returns:
       dict: A dictionary containing the sentiment analysis results, including sentiment value and probabilities.

    Raises:
       HTTPException: If authentication with Google Cloud fails or other request-related issues occur.

    Note:
       The Vertex AI endpoint ID, project ID, and the location of the service account key are hard-coded in this
       function. Ensure these values are correctly set before deployment.

    Example usage:
       curl -N -H "Content-Type: application/json" -d "{\"text\": \"Turnover surged to EUR61 .8 m from EUR47 .6 m due to increasing service demand , especially in the third quarter , and the overall growth of its business .\"}" "http://localhost:9000/vertexai_predict"
       """
    ENDPOINT_ID = "7054451210648027136"
    PROJECT_ID = "rag-detective"
    SERVICE_ACCOUNT_FILE = './secrets/ml-workflow.json'

    # Load data received from your HTML file's JavaScript fetch function
    data = await request.json()
    text = data.get('text')

    # Before sending to the AI Platform Prediction, convert to needed format
    instances = [text]  # this is now a list with a single string

    # Location of your service account key json file

    # Authenticate and create the AI Platform (Unified) client
    try:
        # Load credentials from the service account file
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
        aiplatform.init(credentials=credentials)
    except exceptions.DefaultCredentialsError:
        return {"error": "Couldn't authenticate with Google Cloud."}

    endpoint = f'projects/{PROJECT_ID}/locations/us-central1/endpoints/{ENDPOINT_ID}'
    response = aiplatform.Endpoint(endpoint).predict(instances=instances)

    # Extract the sentiment and probabilities from the predictions
    sentiment, probabilities = response.predictions

    # Convert the sentiment to an integer
    sentiment_value = int(sentiment[0])
    probabilities_value = probabilities[0]

    # Construct the response structure
    response_structure = {
        "sentiment": sentiment_value,
        "probabilities": probabilities_value
    }

    return response_structure

# Scraper Endpoints

@app.get("/sitemap")
def sitemap(website:str = Query(...)):
    """
    The endpoint is designed to flexibly accommodate various formats of user input.
    It can process a simple website name, a fully qualified URL, a direct link to
    a sitemap (especially useful when the sitemap is not located in its default
    location), or a website URL ending with a slash. This adaptability ensures
    successful scraping across a range of possible URL variations provided by users.

    Args:
        website (str): The base URL of the website for which the sitemap is to be analyzed.

    Returns:
        dict: A dictionary containing the status of the sitemap retrieval, the count of pages,
              a nested flag, and a message with details or errors.

    Note:
        The endpoint assumes that the sitemap is located at '[website]/sitemap.xml'. If the provided
        URL does not follow this format, the endpoint attempts to correct it.

    Example usage:
    1. curl "http://localhost:9000/sitemap?website=ai21.com"
    2. curl "http://localhost:9000/sitemap?website=https://ai21.com"
    3. curl "http://localhost:9000/sitemap?website=https://ai21.com/sitemap.xml"
    4. curl "http://localhost:9000/sitemap?website=ai21.com/"
    """
    sitemap = website
    if "https://" not in sitemap:
        sitemap = f"https://{website}"

    if "sitemap.xml" not in sitemap:
        if sitemap[-1] != '/':
            sitemap = f"{sitemap}/sitemap.xml"
        else:
            sitemap = f"{sitemap}sitemap.xml"
    print(sitemap)
    attribute_dict = helper.get_sitemap_attributes(sitemap)
    response_dict = {}

    # If successful in retrieving urls in sitemap , returns status = 0 (success),
    # count: number of pages for the company website, nested_flag : indicates the sitemap had
    # nested sitemaps,(1 for True 0 for false), and message (includes message about the process)
    if attribute_dict['status'] ==0:
        response_dict['status'] =0
        response_dict['count'] = attribute_dict['df'].shape[0]
        response_dict['nested_flag'] = attribute_dict['nested_flag']
        response_dict['message'] = attribute_dict['message']

    #Failure return status, nested_flag, and message that may include errors, or what may have gone wrong
    else:
        response_dict['status'] = 1
        response_dict['message'] = attribute_dict['message']
        response_dict['nested_flag'] = attribute_dict['nested_flag']

    return response_dict

@app.post("/scrape_sitemap")
async def scrape_sitemap(request: Request):
    """
    Scrapes the sitemap of a given website and processes the scraped data.

    This asynchronous endpoint accepts a request containing a website URL, constructs the sitemap URL,
    and initiates a scraping process. The sitemap is scraped, and the data is saved to Google Cloud Platform (GCP).
    If successful, the data is also stored in a vector store (Weaviate). The function yields real-time updates of the
    scraping process through a streaming response.

    Args:
        request (Request): The incoming HTTP request containing the website URL.

    Returns:
        StreamingResponse: A streaming response that provides real-time updates of the scraping process.

    Raises:
        HTTPException: If the scraping process encounters issues or fails to complete.

    Note:
        The function assumes the sitemap is located at '[website]/sitemap.xml'. The scraping results are saved
        as a CSV file in a GCP bucket. Ensure GCP credentials and Weaviate settings are properly configured.

    Example usage:
        1. curl -X POST http://localhost:9000/scrape_sitemap -H "Content-Type: application/json" -d '{"text": "bland.ai"}'
        2. curl -X POST http://localhost:9000/scrape_sitemap -H "Content-Type: application/json" -d '{"text": "chooch.com"}'
        3. curl -X POST http://localhost:9000/scrape_sitemap -H "Content-Type: application/json" -d '{"text": "https://arvinas.com/"}'
    """
    data = await request.json()
    sitemap = data.get('text')

    if "https://" not in sitemap:
        sitemap = f"https://{sitemap}"

    if "sitemap.xml" not in sitemap:
        if sitemap[-1] != '/':
            sitemap = f"{sitemap}/sitemap.xml"
        else:
            sitemap = f"{sitemap}sitemap.xml"
    print(sitemap)
    attribute_dict = helper.get_sitemap_attributes(sitemap)
    link_split = sitemap.split('/')
    print(link_split)
    if link_split:
        website_name = link_split[2]

    async def scraping_process():
        if attribute_dict['df'].shape[0] ==0:
            yield f"Found 0 pages to scrape in {sitemap}\n"

        else:
            text_dict = {}
            i = 0
            for item in list(attribute_dict['df']):
                # Check if the item is a relative link and prepend the base URL
                if item.startswith('/'):
                    item = f"https://{website_name}{item}"
                i += 1
                yield f"{i} of {attribute_dict['df'].shape[0]}: {item}\n"
                try:
                    scraped_data = helper.scrape_link(item)
                    text_dict[item] = scraped_data[item]
                except Exception as e:
                    yield f"Failed to scrape {item}: {e}\n"
                    continue  # Skip this link and continue with the next one

            timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
            df = pd.DataFrame(list(text_dict.items()), columns=['key', 'text'])
            output_file = f"{website_name}_{timestamp}.csv"
            flag = helper.save_to_gcloud(df, output_file)
            if flag:
                yield f"Finished saving to GCP Bucket\n"
                success = helper.download_blob_from_gcloud(output_file)
                if success:
                    yield f"Chunking and preparing documents to insert into vector store.\n"

                    # Store to Weaviate and yield progress updates
                    for update in helper.store_to_weaviate(output_file):
                        yield update

                else:
                    print("Error occured while downloading file to gcloud bucket.\n")
            else:
                yield f"The scraping process did not complete as expected for {sitemap}\n"
        yield f"All steps completed successfully.\n" 
    return StreamingResponse(scraping_process(), media_type="text/plain")

@app.get("/status")
async def get_api_status():
    """
    Retrieves the current version of the API.

    This endpoint is a quick way to check the API version. It returns a JSON object containing
    the version number. This can be useful for debugging, logging, or ensuring compatibility
    with client applications.

    Returns:
       dict: A dictionary with the API version number.

    Example usage:
    curl http://localhost:9000/status
    """
    return {
        "version": "1.1"
    }
