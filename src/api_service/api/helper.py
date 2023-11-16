import weaviate
from datetime import datetime, timezone
from llama_index import Document
from llama_index.vector_stores import WeaviateVectorStore
from llama_index import VectorStoreIndex, StorageContext
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores.types import ExactMatchFilter, MetadataFilters
from llama_index.prompts import PromptTemplate

import time

def query_weaviate(client, website, timestamp, query):
    # construct vector store
    vector_store = WeaviateVectorStore(weaviate_client=client, index_name="Pages", text_key="text")

    # setting up the indexing strategy 
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # setup an index for the Vector Store
    index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

    # Create exact match filters for websiteAddress
    # value = website
    website_address_filter = ExactMatchFilter(key="websiteAddress", value=website)
    timestamp_filter = ExactMatchFilter(key="timestamp", value=timestamp)

    # Create a metadata filters instance with the above filters
    metadata_filters = MetadataFilters(filters=[website_address_filter, timestamp_filter])

    # Custom prompt to exclude out of context answers
    template = ("We have provided context information below. If the answer to a query is not contained in this context, "
                "please only reply with the first two characters of '0 ', and then explain that the context does not include "
                "the information. If the information IS included in the context, and your response will be financial "
                "in nature, make the two characters of the completion '1 ', and if it is not financial, make the first "
                "character '0 '. After this initial number, 0 or 1, please continue your response as instructed previously. "
                "Here are some examples: "
                "0 The location of this company is not provided in the given context. "
                "1 The company's profits were very high that year. "
                "0 The company is located in Grand Rapids, Michigan. "
                "\n---------------------\n"
                "{context_str}"
                "\n---------------------\n"
                "Given this information, please answer the question: {query_str}\n"
    )

    qa_template = PromptTemplate(template)

    # Create a query engine with the filters
    query_engine = index.as_query_engine(text_qa_template=qa_template,
                                         streaming=True,
                                         filters=metadata_filters)


    # Start timer
    start_time = time.time()
    # Execute the query
    streaming_response = query_engine.query(query)
    # End timer
    end_time = time.time()

    # Calculate the duration
    duration = end_time - start_time

    print(f"Query execution time: {duration} seconds")

    return streaming_response

def get_website_addresses(client):
    # Construct the GraphQL query to fetch all websiteAddress values from the Pages class
    graphql_query = '''
    {
        Get {
            Pages {
                websiteAddress
            }
        }
    }
    '''

    # Initialize a set to collect unique website addresses
    website_addresses_set = set()

    try:
        # Perform the query
        result = client.query.raw(graphql_query)

        # Extract website addresses from the 'Pages' class results
        pages = result.get('data', {}).get('Get', {}).get('Pages', [])
        for page in pages:
            if 'websiteAddress' in page and page['websiteAddress']:
                # Add to set to ensure uniqueness
                website_addresses_set.add(page['websiteAddress'])

        # Convert the set back to a list to return
        return list(website_addresses_set)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        return []

def get_all_timestamps_for_website(client, website_address: str):
    # GraphQL query that fetches timestamps for a particular websiteAddress
    graphql_query = f'''
    {{
        Get {{
            Pages(
                where: {{
                    operator: Equal
                    path: ["websiteAddress"]
                    valueString: "{website_address}"
                }}
            ) {{
                timestamp
            }}
        }}
    }}
    '''
    
    # Initialize a set to collect unique timestamps
    timestamps_set = set()

    try:
        # Perform the query
        result = client.query.raw(graphql_query)

        # Extract timestamps from the 'Pages' class results
        pages = result.get('data', {}).get('Get', {}).get('Pages', [])
        for page in pages:
            if 'timestamp' in page and page['timestamp']:
                # Add to set to ensure uniqueness
                timestamps_set.add(page['timestamp'])

        # Convert the set back to a list to return
        return list(timestamps_set)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        return []
