from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
import os
from fastapi import File
from api import helper
from typing import List
import asyncio 
import weaviate

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
async def rag_query(request: Request):
    data = await request.json()
    website = data.get('website')
    query = data.get('query')

    # Query Weaviate
    streaming_response = helper.query_weaviate(app.state.weaviate_client, website, query)

    # Generate the streaming response and return it
    headers = {'Cache-Control': 'no-cache'}
    return StreamingResponse(process_streaming_response(streaming_response),
                             media_type="text/plain", headers=headers)

# Test using: curl -X 'GET' 'http://localhost:9000/websites' -H 'accept: application/json'
@app.get("/websites", response_model=List[str])
def read_websites():
    return helper.get_website_addresses(app.state.weaviate_client)


# Test using: curl -X 'GET' 'http://localhost:9000/timestamps/ai21.com' -H 'accept: application/json'
@app.get("/timestamps/{website_address}", response_model=List[str])
def read_timestamps(website_address: str):
    return helper.get_all_timestamps_for_website(app.state.weaviate_client, website_address)