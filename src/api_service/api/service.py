from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
import pandas as pd
import os
from fastapi import File
from api import helper

# # Suppress Pydantic warnings since it's based in llamaindex
import warnings
warnings.simplefilter(action='ignore', category=Warning)

# Set the OpenAI key as an Environment Variable (for when it's run on GCS)
os.environ["OPENAI_API_KEY"] = "sk-OPENAI_API_KEY"

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


# https://stackoverflow.com/questions/76288582/is-there-a-way-to-stream-output-in-fastapi-from-the-response-i-get-from-llama-in
async def astreamer(generator):
    try:
        for i in generator:
            yield (i)
            await asyncio.sleep(.1)
    except asyncio.CancelledError as e:
        print('cancelled')


@app.post("/rag_query")
async def rag_query(website, query):
    # Query Weaviate
    response = helper.query_weaviate(WEAVIATE_IP_ADDRESS, website, query)

    # Return the response (convert to string)
    response = str(response) 
    # print(response)

    # streaming_response = StreamingResponse(astreamer(response.response_gen), media_type="text/event-stream")
    # print(streaming_response)

    return response