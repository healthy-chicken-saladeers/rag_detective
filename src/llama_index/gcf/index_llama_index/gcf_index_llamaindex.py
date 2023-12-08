import functions_framework
import weaviate
import pandas as pd
import os
from datetime import datetime, timezone
from llama_index import Document
# Suppress Pydantic warnings since it's based in llamaindex
import warnings
warnings.simplefilter(action='ignore', category=Warning)


from llama_index.node_parser import SimpleNodeParser
from llama_index.vector_stores import WeaviateVectorStore
from llama_index import VectorStoreIndex, StorageContext
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores.types import ExactMatchFilter, MetadataFilters
from google.cloud import storage

os.environ.get("OPENAI_API_KEY")
WEAVIATE_IP_ADDRESS = "34.133.13.119"

@functions_framework.http
def index_llamaindex(request):

    request_json = request.get_json(silent=True)
    request_args = request.args

    bucket_name = "ac215_scraper_bucket"
    csv_file = 'data/verily.com_2023-10-06T19-26-47.csv'

    if request_args and 'bucket_name' in request_args:
        bucket_name = request_args['bucket_name']
    if request_args and 'csv_file' in request_args:
        csv_file = request_args['csv_file']

    def create_date(date_string):
      """ 
      Convert a date string to RFC 3339 formatted string with timezone.

      Parameters:
      - date_string (str): Input date string in the format "%Y-%m-%dT%H-%M-%S".

      Returns:
      - str: RFC 3339 formatted date-time string.
      """
      dt_object = datetime.strptime(date_string, "%Y-%m-%dT%H-%M-%S")
      # convert datetime object to RFC 3339 string (with timezone)
      rfc3339_string = dt_object.replace(tzinfo=timezone.utc).isoformat()
      return rfc3339_string

    client = weaviate.Client(url="http://" + WEAVIATE_IP_ADDRESS + ":8080")

    # Get the existing schema from Weaviate
    schema = client.schema.get()

    # Get the website address and timestamp from the filename
    websiteAddress, timestamp = csv_file.rsplit('.', 1)[0].split('_')

    # Initialize the GCS client
    gs_client = storage.Client()

    # Get the GCS bucket
    bucket = gs_client.get_bucket(bucket_name)

    # Define the path to the CSV file in the GCS bucket
    blob = bucket.blob(csv_file)

    # Download the CSV file to a local temporary file
    local_temp_file = "/tmp/temp_file.csv"  # You can change this path as needed
    blob.download_to_filename(local_temp_file)

    # Read the CSV file into a DataFrame
    df = pd.read_csv(local_temp_file)

    # Manually assemble the documents
    documents = []
    for _, row in df.iterrows():
        document = Document(
            text=row['text'],
            metadata={
                'websiteAddress': websiteAddress,
                'timestamp': timestamp
            }
        )
        document.doc_id = row['key']
        documents.append(document)

    # Create the parser and nodes
    parser = SimpleNodeParser.from_defaults(chunk_size=1024, chunk_overlap=20)
    nodes = parser.get_nodes_from_documents(documents)

    # construct vector store
    vector_store = WeaviateVectorStore(weaviate_client = client, index_name="Pages", text_key="text")
    # setting up the storage for the embeddings
    storage_context = StorageContext.from_defaults(vector_store = vector_store)
    # set up the index
    index = VectorStoreIndex(nodes, storage_context=storage_context)

    return(f"Successfully added {csv_file} to Weaviate.")