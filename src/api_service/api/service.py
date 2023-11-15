from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
import os
from fastapi import File
from api import helper
import asyncio 

# # Suppress Pydantic warnings since it's based in llamaindex
import warnings
warnings.simplefilter(action='ignore', category=Warning)

# Set the OpenAI key as an Environment Variable (for when it's run on GCS)
os.environ["OPENAI_API_KEY"] = "sk-OpenAIKEY"

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


# Routes
@app.get("/")
async def get_index():
    return {"message": "Welcome to the RAG Detective App!"}


async def process_streaming_response(streaming_response):
    financial = False
    try:
        for i, text in enumerate(streaming_response.response_gen):
            if i == 0:  # Skip the initial null character
                continue
            elif i == 1:  # Check for the financial flag
                financial = text == "1"
            elif i == 2:  # Handle the first word (strip leading space)
                yield(text.lstrip())
            else:         # For subsequent words, print as is
                yield(text)

            await asyncio.sleep(0.1)  # Add a slight delay to enable streaming behavior
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
    return StreamingResponse(process_streaming_response(streaming_response), media_type="text/plain")