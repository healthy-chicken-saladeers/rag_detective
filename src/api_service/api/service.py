from fastapi import FastAPI, Request, BackgroundTasks 
from fastapi.responses import StreamingResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
import os
from fastapi import File
from api import helper
from typing import List
import asyncio 
from asyncio import Lock
import weaviate
import uuid

query_url_storage = {}
storage_lock = Lock()

# Test using this line of curl:
# curl -N -H "Content-Type: application/json" -d "{\"website\": \"ai21.com\", \"query\": \"How was AI21 Studio a game changer\"}" http://localhost:9000/rag_query

# Suppress Pydantic warnings since it's based in llamaindex
import warnings
warnings.simplefilter(action='ignore', category=Warning)

# Set the OpenAI key as an Environment Variable (for when it's run on GCS)
os.environ["OPENAI_API_KEY"] = "sk-KEY"

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

# Dummy function for testing streaming
@app.get("/streaming")
async def streaming_endpoint():
    async def event_generator():
        for i in range(10):
            yield f"data: {i} "
            await asyncio.sleep(0.1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")


# Routes
@app.get("/")
async def get_index():
    return {"message": "Welcome to the RAG Detective App!"}

async def process_streaming_response(local_streaming_response):
    financial = False
    try:
        # If local_streaming_response.response_gen is an asynchronous generator, you should use an async for.
        for i, text in enumerate(local_streaming_response.response_gen):
            print(f"Yielding: [{text}]")
            if i > 0:  # Skip the initial character and check for financial flag.
                if i == 1:
                    financial = text == "1" # Check for the financial flag
                    continue
                if text == "": # Check for null character
                    continue
                yield text.strip() if i == 2 else text # Handle the first word (strip leading space) 
    except asyncio.CancelledError as e:
        print('Streaming cancelled', flush=True)
    if financial:
        print(" Financial flag set!", flush=True)

@app.post("/rag_query")
async def rag_query(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    website = data.get('website')
    timestamp = data.get('timestamp')
    query = data.get('query')

    # Generate a unique ID for this specific query
    query_id = str(uuid.uuid4())
    print("Query ID:", query_id)

    # Query Weaviate
    streaming_response = helper.query_weaviate(app.state.weaviate_client, website, timestamp, query)

    # Add the URL processing function as a background task
    background_tasks.add_task(process_url_extraction, query_id, streaming_response)

    # Generate the streaming response and return it
    headers = {
        'Cache-Control': 'no-cache',
        'Access-Control-Expose-Headers': 'X-Query-ID',  # Ensure the custom header is exposed
        'X-Query-ID': query_id  # set the header
    }
    return StreamingResponse(
        process_streaming_response(streaming_response),
        media_type="text/plain",
        headers=headers
    )

async def process_url_extraction(query_id: str, streaming_response):
    extracted_urls = helper.extract_document_urls(streaming_response)
    unique_urls = []
    # Use a loop to maintain order and avoid duplicates
    for url in extracted_urls:
        if url not in unique_urls:
            unique_urls.append(url)
    # Store the ordered, unique URLs in the storage
    async with storage_lock:
        query_url_storage[query_id] = unique_urls

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
        urls = query_url_storage.get(query_id)
        if urls is None:
            # Correctly format the response with a custom status code
            return JSONResponse(content={"error": "URLs not available yet or invalid query ID"}, status_code=404)
        # Once retrieved, you may want to delete the entry if it's no longer needed
        del query_url_storage[query_id]
        print(urls)
    return {"urls": urls}