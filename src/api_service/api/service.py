# You need to have the OPENAI_APIKEY environment variable set for this.
# As well, ml-workflow.ml has to be placed in the /secrets folder of the repo
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, File
from fastapi.responses import StreamingResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
import os
from typing import Dict, List
from api import helper
from typing import List
import asyncio 
from asyncio import Lock
import weaviate
import uuid
from google.cloud import aiplatform
from google.auth import exceptions
from google.oauth2 import service_account
query_url_storage = {}
storage_lock = Lock()
financial = False

# Test using this line of curl:
# curl -N -H "Content-Type: application/json" -d "{\"website\": \"ai21.com\", \"query\": \"How was AI21 Studio a game changer\", \"timestamp\": \"2023-10-06T18-11-24\"}" http://localhost:9000/rag_query

# Suppress Pydantic warnings since it's based in llamaindex
import warnings
warnings.simplefilter(action='ignore', category=Warning)

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
    # Create a Weaviate client when the app starts and store it in the app state
    app.state.weaviate_client = weaviate.Client(url=f"http://{WEAVIATE_IP_ADDRESS}:8080")

# Routes
@app.get("/")
async def get_index():
    return {"message": "Welcome to the RAG Detective App!"}

# Dummy function for testing streaming
@app.get("/streaming")
async def streaming_endpoint():
    async def event_generator():
        for i in range(10):
            yield f"data: {i} "
            await asyncio.sleep(0.1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

async def process_streaming_response(local_streaming_response):
    global financial
    try:
        for text in local_streaming_response.response_gen:
            # Check for the financial flag at the end of the text
            if "%%FF%%" in text:
                financial = True
                text = text.replace("%%FF%%", "")  # remove the "%%FF%%"
            if text.strip():   # Check for null character or empty string
                print(f"Yielding: [{text}]")
                yield text  
        if financial:
            print(" Financial flag set!", flush=True)
    except asyncio.CancelledError as e:
        print('Streaming cancelled', flush=True)

def check_required(data: Dict[str, str], keys: List[str]):
    for key in keys:
        if not data.get(key):
            raise HTTPException(status_code=400, detail=f"Missing required field: '{key}'")

@app.post("/rag_query")
async def rag_query(request: Request, background_tasks: BackgroundTasks):
    global financial
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

    # Add the URL processing function as a background task
    background_tasks.add_task(process_url_extraction, query_id, streaming_response, financial)

    # Generate the streaming response and return it
    headers = {
        'Cache-Control': 'no-cache',
        'Access-Control-Expose-Headers': 'X-Query-ID',  # Ensure the custom header is exposed
        'X-Query-ID': query_id  # set the header to track the query_id for the reference retrieval
    }
    return StreamingResponse(
        process_streaming_response(streaming_response),
        media_type="text/plain",
        headers=headers
    )

async def process_url_extraction(query_id: str, streaming_response, financial: bool):
    extracted_urls = helper.extract_document_urls(streaming_response)
    unique_urls = []
    # Use a loop to maintain order and avoid duplicates
    for url in extracted_urls:
        if url not in unique_urls:
            unique_urls.append(url)
    # Store the ordered, unique URLs in the storage
    async with storage_lock:
        query_url_storage[query_id] = financial, unique_urls

# Test using: curl -X 'GET' 'http://localhost:9000/websites' -H 'accept: application/json'
@app.get("/websites", response_model=List[str])
def read_websites():
    return helper.get_website_addresses(app.state.weaviate_client)


# Test using: curl -X 'GET' 'http://localhost:9000/timestamps/ai21.com' -H 'accept: application/json'
@app.get("/timestamps/{website_address}", response_model=List[str])
def read_timestamps(website_address: str):
    return helper.get_all_timestamps_for_website(app.state.weaviate_client, website_address)

@app.get("/get_urls/{query_id}")
async def get_urls(query_id: str):
    async with storage_lock:
        # Use the query_id to retrieve the stored URLs
        financial_flag, urls = query_url_storage.get(query_id)
        if urls is None:
            # Correctly format the response with a custom status code
            return JSONResponse(content={"error": "URLs not available yet or invalid query ID"}, status_code=404)
        # Once retrieved, delete the entry to keep things simple
        del query_url_storage[query_id]
        print(urls)
    return {"urls": urls, "financial_flag": financial_flag}


# Test using: curl -N -H "Content-Type: application/json" -d "{\"text\": \"Turnover surged to EUR61 .8 m from EUR47 .6 m due to increasing service demand , especially in the third quarter , and the overall growth of its business .\"}" "http://localhost:9000/vertexai_predict"
@app.post("/vertexai_predict")
async def vertexai_predict(request: Request):
    ENDPOINT_ID = "7054451210648027136"
    PROJECT_ID = "rag-detective"
    SERVICE_ACCOUNT_FILE = './secrets/ml-workflow.json'
    print("hello", os.getcwd())

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

#scraper functionalities

#Test call
# curl -X POST http://localhost:9000/sitemap_attributes/ -H "Content-Type: application/json" -d '{"text":"https://bland.ai/sitemap.xml"}'
@app.post("/sitemap_attributes/")
async def sitemap_attributes(request: Request):
    """
        Analyze sitemap attributes from the provided text in the request body.

        This endpoint processes a sitemap, provided as JSON in the request body, and returns various attributes of the sitemap. The analysis is conducted by the 'helper.get_sitemap_attributes' function.

        Args:
            request (Request): The request object that includes the JSON body. The JSON body should contain a key 'text' with the sitemap as its value.

        Returns:
            dict: A dictionary containing the analysis results. The dictionary includes:
                - 'status' (int): The status of the analysis (1 for success, 0 for failure).
                - 'count' (int): The number of items processed in the sitemap, only included if 'status' is 1.
                - 'nested_flag' (int): A flag indicating if nested structures are present, included in both success and failure cases.
                - 'message' (str): A message providing details about the analysis or the error encountered.
                - Optional 'sitemap_urls' (list): A list of URLs found in the sitemap. This is commented out by default and can be included based on requirements.

        Raises:
            HTTPException: If the request body does not contain valid JSON or the 'text' key is missing.

        Note:
            The function prints the sitemap for logging/debugging purposes.
            The actual analysis logic is abstracted in 'helper.get_sitemap_attributes'.
        """
    data = await request.json()
    sitemap = data.get('text')
    response_dict = {}
    print(sitemap)
    attribute_dict = helper.get_sitemap_attributes(sitemap)

    if attribute_dict['status'] ==1:
        response_dict['status'] =1
        response_dict['count'] = attribute_dict['df'].shape[0]
        response_dict['nested_flag'] = attribute_dict['nested_flag']
        response_dict['message'] = attribute_dict['message']
        # Note : List of urls in the sitemap can also be returned.
        # example usage:
        # response_dict['sitemap_urls'] = list(attribute_dict['df'])

    else:
        response_dict['status'] = 0
        response_dict['count'] = 0
        response_dict['message'] = attribute_dict['message']
        response_dict['nested_flag'] = 0

    return response_dict

