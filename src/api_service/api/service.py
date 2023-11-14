from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
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

# # Initialize Tracker Service
# tracker_service = TrackerService()

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


# @app.on_event("startup")
# async def startup():
#     print("Startup tasks")
#     # Start the tracker service
#     # asyncio.create_task(tracker_service.track())


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

@app.post("/query-llamaindex")
async def rag_query(website, query):

    # Query Weaviate
    response = helper.query_weaviate(WEAVIATE_IP_ADDRESS, website, query)

    # Return the response 
    print(response)
    return StreamingResponse(astreamer(response.response_gen), media_type="text/event-stream")