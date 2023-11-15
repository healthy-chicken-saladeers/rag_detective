from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
import os
from fastapi import File
from api import helper
import asyncio 

# Test using this line of curl:
# curl -N -H "Content-Type: application/json" -d "{\"website\": \"ai21.com\", \"query\": \"How was AI21 Studio a game changer\"}" http://localhost:9000/rag_query

# Suppress Pydantic warnings since it's based in llamaindex
import warnings
warnings.simplefilter(action='ignore', category=Warning)

# Set the OpenAI key as an Environment Variable (for when it's run on GCS)
os.environ["OPENAI_API_KEY"] = "sk-OpenAI-KEY"

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
    streaming_response = helper.query_weaviate(WEAVIATE_IP_ADDRESS, website, query)

    # Generate the streaming response and return it
    headers = {'Cache-Control': 'no-cache'}
    return StreamingResponse(process_streaming_response(streaming_response), media_type="text/plain", headers=headers)
