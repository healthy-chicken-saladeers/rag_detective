import weaviate
from datetime import datetime, timezone
from llama_index import Document
from llama_index.vector_stores import WeaviateVectorStore
from llama_index import VectorStoreIndex, StorageContext
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores.types import ExactMatchFilter, MetadataFilters
from llama_index.prompts import PromptTemplate
from llama_index.node_parser import SimpleNodeParser
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import ChromiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from pathlib import Path
from google.cloud import storage
import re
import fitz  # PyMuPDF


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
                "please explain that the context does not include the information. If the information IS included in the context, "
                "please answer the question using the context provided below. If the answer is "
                "financial in nature then please append QQ to the end of the response."
                "Here are some examples: "
                "The location of this company is not provided in the given context.\n"
                "The company's profits were very high that year. QQ \n"
                "The CEO's salary was $14 million. QQ \n"
                "The company has made money for it's clients. QQ \n"
                "The company is located in Grand Rapids, Michigan.\n"
                "A language model is a type of machine learning model.\n"
                "James founded the company in 2015.\n"
                "James founded the company in 2015 with an initial seed round of $15 million. QQ \n"
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
        return sorted(list(website_addresses_set))

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
        return sorted(list(timestamps_set), reverse=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        return []

def extract_document_urls(streaming_response):
    urls = []
    for node_with_score in streaming_response.source_nodes:
        relationships = node_with_score.node.relationships
        for related_node_info in relationships.values():
            if related_node_info.node_type == "4":  # Corresponds to ObjectType.DOCUMENT
                urls.append(related_node_info.node_id)
    return urls


#Scraper code
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

bucket_name = "ac215_scraper_bucket"

def set_chrome_options() -> ChromiumOptions:
    """Sets chrome options for Selenium.Chrome options for headless browser is enabled.
    Args: None

    returns:
        Chrome options that can work headless i.e. without actually launching the browser.
    """
    chrome_options = ChromiumOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options

options = set_chrome_options()

def extract_error_message_from_exception(exception):
    """
    Extracts the detailed error message found between ">:" and "([Errno" from an exception object.

    Args:
    - exception (Exception): The exception object containing the error message.

    Returns:
    - str: The extracted detailed error message, or the full exception message if not found.
    """
    # Converting the exception object to a string
    message = str(exception)

    # Regular expression to find the detailed error message segment
    match = re.search(r">: (.*?) \(\[Errno", message)
    return match.group(1) if match else message

def get_sitemap_attributes(url):

    print("inside get_sitemap_attributes")
    attribute_dict = {
        'status':0,
        'df': pd.Series(),
        'nested_flag': 0,
        'message': ""
    }
    error_message= ""
    nested_sitemap_flag = False
    try:
        with requests.get(url, headers=headers) as response:
            soup = BeautifulSoup(response.text, 'lxml-xml')
            urls = [link.text.strip() for link in soup.find_all('loc') if link]

        if not urls:
            attribute_dict['status'] =1
            attribute_dict['message'] = f'No urls found were found on {url}'
            return attribute_dict  # Return status =0

        extended_urls = []
        for link in urls:
            if link.endswith('xml'):
                nested_sitemap_flag = True
                try:
                    with requests.get(link, headers=headers) as response:
                        response.raise_for_status()  # Check if the request was successful
                        nested_soup = BeautifulSoup(response.text, 'lxml')
                        nested_urls = [url.text.strip() for url in nested_soup.find_all \
                            ('loc') if url]
                        extended_urls.extend(nested_urls)
                except requests.RequestException as e:
                    print(f"Error occurred while processing {link}: {e}")
            else:
                extended_urls.append(link)

        if not extended_urls:
            attribute_dict['status'] =1 # return status =1 (i.e. some failure happened)
            attribute_dict['message'] = f"The sitemap url {url} refers to a nested link of sitemaps. However, the scraper either did not find any links, or some unexpected error occured. "
            return attribute_dict

        attribute_dict['df'] = pd.Series(extended_urls).drop_duplicates().str.strip()
        if nested_sitemap_flag:
            attribute_dict['message'] = f"The sitemap url {url} refers to a nested sitemap with {len(urls)} sitemap links."
            attribute_dict['nested_flag'] = 1
        return attribute_dict

    except requests.RequestException as e:
        print(f"Error occurred: {e}")
        attribute_dict['status'] =1
        attribute_dict['message'] = extract_error_message_from_exception(e)
        return attribute_dict  # Returns status =1 (i.e. some failure happened)


def scrape_link(link):
    print(link)
    text_dict = {}
    wait_condition = (By.TAG_NAME, ['html', 'div', 'body'])
    browser = None  # Initialize browser to avoid crash

    try:
        with requests.get(link, headers=headers, stream=True) as response:
            content_type = response.headers.get('Content-Type', '')
            if 'application/pdf' in content_type:
                try:
                    # Handle PDF content
                    with fitz.open(stream=response.content, filetype="pdf") as doc:
                        text_from_pdf = ''.join([page.get_text() for page in doc])
                        text_dict[link] = text_from_pdf
                except Exception as e:
                    print(f"Error occurred while processing PDF at {link}: {e}")
                    text_dict[link] = ""
            else:
                if response.status_code == 200:
                    try:
                        soup = BeautifulSoup(response.text, 'lxml')
                        [tag.decompose() for tag in soup.find_all(['header', 'nav', 'footer'])]
                        text_only_requests = soup.get_text(separator=' ', strip=True)
                        text_dict[link] = text_only_requests
                    except Exception as e:
                        print(f"Error occurred while processing HTML at {link}: {e}")
                        text_dict[link] = ""
                if response.status_code != 200 or len(text_only_requests.split()) <50:
                    # print("scraping with selenium")
                    try:
                        # print("calling browser = webdriver.Chrome(options)")
                        browser = webdriver.Chrome(options)
                        # print("calling browser.implicitly_wait(30)")
                        browser.implicitly_wait(30)
                        # print("calling  browser.get(link)")
                        browser.get(link)

                        soup_selenium = BeautifulSoup(browser.page_source, 'lxml')

                        [tag.decompose() for tag in soup_selenium.find_all(['header', 'nav', 'footer'])]
                        text_only_selenium = soup_selenium.get_text(separator=' ', strip=True)
                        text_dict[link] = text_only_selenium
                        # print(f"{link}: {text_only_selenium}")

                    except Exception as e:
                        print(f"Error occurred while processing {link} in selenium: {e.with_traceback}")
                        text_dict[link] = ""
                    finally:
                        if browser: browser.close()
                else:
                    text_dict[link] = text_only_requests

    except requests.RequestException as e:
        print(f"Error occurred while processing {link}: {e}")

    return text_dict

def save_to_gcloud(df, filename):
    flag = False
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        if bucket:
            csv_data = df.to_csv(index=False)
            blob = bucket.blob(f'data/{filename}')
            blob.upload_from_string(csv_data, content_type='text/csv')
            flag = True
    except Exception as e:
        print(f"Could not write to gcp bucket. {e}")

    return flag

def download_blob_from_gcloud(filename):
    sourcefilename = f"data/{filename}"
    destinationfilename = f"/home/downloads/{filename}"

    success = False
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(sourcefilename)
        blob.download_to_filename(destinationfilename)
        success = True
        print(f"Downlod from gcloud succeeded")
    except Exception as e:
        print("Error while downloading blob from gcloud",e)

    return success


# Write to weaviate part
def store_to_weaviate(filename):
    success = False

    # Retrieve the OpenAI API key from the environment variables
    OPENAI_APIKEY = os.getenv("OPENAI_APIKEY")
    print(OPENAI_APIKEY)

    # Set the OpenAI key as an Environment Variable (for when it's run on GCS)
    os.environ["OPENAI_APIKEY"] = OPENAI_APIKEY
    print("Ending at OPENAI key part")
    # Current Weaviate IP
    WEAVIATE_IP_ADDRESS = "34.42.138.162"

    print("Starting to insert into Weaviate")
    try:
        client = weaviate.Client(url="http://" + WEAVIATE_IP_ADDRESS + ":8080")
        websiteAddress, timestamp = filename.rsplit('.', 1)[0].split('_')
        print(websiteAddress, timestamp)
        file_loc = f"/home/downloads/{filename}"
        df = pd.read_csv(file_loc)

        documents = []
        for _, row in df.iterrows():
            document = Document (
                text = row['text'],
                metadata={
                    'websiteAddress': websiteAddress,
                    'timestamp': timestamp
                }
            )
            document.doc_id = row['key']
            documents.append(document)

        index_count = 0
        total_documents = len(documents)

        # Update index with llamaindex
        vector_store = WeaviateVectorStore(
            weaviate_client=client,
            index_name="Pages",
            text_key="text"
        )
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            service_context=None
        )
        for document in documents:
            index.insert(document)
            index_count += 1
            # Yield progress update
            yield f"Inserted {index_count} of {total_documents} documents into vector store.\n"

        cleanup_files(file_loc)

    except Exception as e:
        print("Error with storing to vector store method",e)

    yield "All documents inserted successfully.\n"

def cleanup_files(filewithpath):
    if os.path.exists(filewithpath):
        try:
            os.remove(filewithpath)
            print(f"Removed file {filewithpath}")
        except Exception as e:
            print(f"Error occured while deleting {filewithpath}", e)
    else:
        print(f"{filewithpath} does not exist.")
