from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
# import asyncio
# from api.tracker import TrackerService
import pandas as pd
import os
from fastapi import File
# from tempfile import TemporaryDirectory
# from api import model
import weaviate
from datetime import datetime, timezone
from llama_index import Document
# # Suppress Pydantic warnings since it's based in llamaindex
import warnings
warnings.simplefilter(action='ignore', category=Warning)


from llama_index.node_parser import SimpleNodeParser
from llama_index.vector_stores import WeaviateVectorStore
from llama_index import VectorStoreIndex, StorageContext
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores.types import ExactMatchFilter, MetadataFilters

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

@app.post("/query-llamaindex")
async def query_llamaindex(website, query):
    # client setup
    client = weaviate.Client(url="http://" + WEAVIATE_IP_ADDRESS + ":8080")

    # construct vector store
    vector_store = WeaviateVectorStore(weaviate_client=client, index_name="Pages", text_key="text")

    # setting up the indexing strategy 
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # setup an index for the Vector Store
    index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

    # Create exact match filters for websiteAddress
    # value = website
    website_address_filter = ExactMatchFilter(key="websiteAddress", value=website)

    # Create a metadata filters instance with the above filters
    metadata_filters = MetadataFilters(filters=[website_address_filter]) 

    # Create a query engine with the filters
    query_engine = index.as_query_engine(filters=metadata_filters)

    # Execute the query
    response = query_engine.query(query)

    # Return the response 
    return {"response": response}


# @app.get("/experiments")
# def experiments_fetch():
#     # Fetch experiments
#     df = pd.read_csv("/persistent/experiments/experiments.csv")

#     df["id"] = df.index
#     df = df.fillna("")

#     return df.to_dict("records")


# @app.get("/best_model")
# async def get_best_model():
#     model.check_model_change()
#     if model.best_model is None:
#         return {"message": "No model available to serve"}
#     else:
#         return {
#             "message": "Current model being served:" + model.best_model["model_name"],
#             "model_details": model.best_model,
#         }


# @app.post("/predict")
# async def predict(file: bytes = File(...)):
#     print("predict file:", len(file), type(file))

#     self_host_model = True

#     # Save the image
#     with TemporaryDirectory() as image_dir:
#         image_path = os.path.join(image_dir, "test.png")
#         with open(image_path, "wb") as output:
#             output.write(file)

#         # Make prediction
#         prediction_results = {}
#         if self_host_model:
#             prediction_results = model.make_prediction(image_path)
#         else:
#             prediction_results = model.make_prediction_vertexai(image_path)

#     print(prediction_results)
#     return prediction_results