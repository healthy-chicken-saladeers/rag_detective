import weaviate
from datetime import datetime, timezone
from llama_index import Document
from llama_index.vector_stores import WeaviateVectorStore
from llama_index import VectorStoreIndex, StorageContext
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores.types import ExactMatchFilter, MetadataFilters
from llama_index.prompts import PromptTemplate


def query_weaviate(WEAVIATE_IP_ADDRESS, website, query):
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

    # Execute the query
    streaming_response = query_engine.query(query)

    return streaming_response