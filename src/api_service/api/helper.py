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
import openai


# SETTINGS

OPENAI_APIKEY = os.getenv("OPENAI_APIKEY")

# Size (in # of words) of the chunks
text_chunk_size = 500
# Number of text chunks of size text_chunk_size to retrieve
num_chunks = 2
# Maximum number of tokens we want in our response
maximum_tokens = 1000

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

def query_weaviate(client, website, timestamp, query):
    # Construct a filter to narrow down the search results based on specific conditions:
    where_filter = {
        "operator" : "And",
        "operands" : [
            {
                "path": ["websiteAddress"],
                "operator": "Equal",
                "valueString": f"{website}"
            },
            {
                "path": ["timestamp"],
                "operator": "Equal",
                "valueDate": f"{create_date(timestamp)}"
            }
        ]
    }

    # Execute the query on the Weaviate client:
    results = client.query.get('TextChunk', ['text','pageURL']) \
        .with_limit(num_chunks) \
        .with_near_text({'concepts': [query]}) \
        .with_where(where_filter) \
        .do()

    # Custom prompt to exclude out of context answers
    QUESTION_TEMPLATE = ("We have provided context information below. If the answer to a query is not contained in this context, "
                "please explain that the context does not include the information. If the information IS included in the context, "
                "please answer the question using the context provided below. If the response are generating is specifically "
                "financial in nature (SPECIFICALLY mentioning things like profit, loss, money, investment, or other financial terms)"
                "explain why you think the response is financial. As well, if the response is financial, then please append %%FF%% to the end of the response."
                "DO NOT APPEND %%FF%% UNLESS THE RESPONSE IS RELATED TO FINANCE."
                "Here are some examples: "
                "The location of this company is not provided in the given context."
                "The company's profits were very high that year. The response mentions profits. %%FF%%"
                "The CEO's salary was $14 million. The response mentions salary in dollars. %%FF%%"
                "The company has made money for it's clients. The response mentions money. %%FF%%"
                "The company is located in Grand Rapids, Michigan."
                "A language model is a type of machine learning model."
                "James founded the company in 2015."
                "James founded the company in 2015 with an initial seed round of $15 million. The response mentions the seed funding. %%FF%%"
                "\n---------------------\n"
                "{context_str}"
                "\n---------------------\n"
                "Given this information, please answer the question: {question}\n"
    )

    # Extract the Relevant Context Information
    context_texts = [chunk['text'] for chunk in results['data']['Get']['TextChunk']]
    context_str = "\n".join(context_texts)

    # Construct the Full Query for GPT-3.5
    query_string = QUESTION_TEMPLATE.format(context_str=context_str, question=query)

    # Set up the OpenAI API key
    openai.api_key = OPENAI_APIKEY    

    # Query GPT-3.5
    response_generator = openai.Completion.create(
      engine="gpt-3.5-turbo-instruct",
      prompt=query_string,
      max_tokens=maximum_tokens,
      stream=True
    )

    return response_generator

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
        attribute_dict['message'] = e
        return attribute_dict  # Returns status =1 (i.e. some failure happened)


def scrape_link(link):
    print(link)
    text_dict = {}
    wait_condition = (By.TAG_NAME, ['html', 'div', 'body'])

    try:
        with requests.get(link, headers=headers) as response:
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')

                [tag.decompose() for tag in soup.find_all(['header', 'nav', 'footer'])]
                text_only_requests = soup.get_text(separator=' ', strip=True)


            if response.status_code != 200 or len(text_only_requests.split()) <50:
                #print("scraping with selenium")
                try:
                    #print("calling browser = webdriver.Chrome(options)")
                    browser = webdriver.Chrome(options)
                    #print("calling browser.implicitly_wait(30)")
                    browser.implicitly_wait(30)
                    #print("calling  browser.get(link)")
                    browser.get(link)

                    soup_selenium = BeautifulSoup(browser.page_source, 'lxml')

                    [tag.decompose() for tag in soup_selenium.find_all(['header', 'nav', 'footer'])]
                    text_only_selenium = soup_selenium.get_text(separator=' ', strip=True).lower()
                    text_dict[link] = text_only_selenium
                    print(f"{link}: {text_only_selenium}")

                except Exception as e:
                    print(f"Error occurred while processing {link} in selenium: {e.with_traceback}")

                finally:
                    browser.close()

            else:
                text_dict[link] = text_only_requests.lower()

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


#Write to weaviate part

def store_to_weaviate(filename):
    success = False
    print("Starting at OPENAI key part")
    # Retrieve the OpenAI API key from the environment variables
    OPENAI_APIKEY = os.getenv("OPENAI_APIKEY")
    print(OPENAI_APIKEY)

    # Set the OpenAI key as an Environment Variable (for when it's run on GCS)
    os.environ["OPENAI_APIKEY"] = OPENAI_APIKEY
    print("Ending at OPENAI key part")
    # Current Weaviate IP
    WEAVIATE_IP_ADDRESS = "34.42.138.162"

    print("starting at weaviate part")
    try:
        client = weaviate.Client(url="http://" + WEAVIATE_IP_ADDRESS + ":8080")
        websiteAddress, timestamp = filename.rsplit('.', 1)[0].split('_')
        print(websiteAddress, timestamp)
        file_loc = f"/home/downloads/{filename}"
        print("working on df = pd.read_csv(file_loc)")
        df = pd.read_csv(file_loc)

        documents = []
        print("working on for _, row in df.iterrows():")
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

        # Create the parser and nodes
        print("working on parser = SimpleNodeParser.from_defaults(chunk_size=1024, chunk_overlap=20)")
        parser = SimpleNodeParser.from_defaults(chunk_size=1024, chunk_overlap=20)

        print("working on nodes = parser.get_nodes_from_documents(documents)")
        nodes = parser.get_nodes_from_documents(documents)

        # construct vector store
        print("working on vector_store = WeaviateVectorStore(weaviate_client=client,index_name=.. , text_key=text)")
        vector_store = WeaviateVectorStore(weaviate_client=client, index_name="Pages", text_key="text")
        # setting up the storage for the embeddings
        print("working on storage_context = StorageContext.from_defaults(vector_store=vector_store)")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        # set up the index
        print("working on index = VectorStoreIndex(nodes, storage_context=storage_context)")
        index = VectorStoreIndex(nodes, storage_context=storage_context)

        print(index)
        success = True
    except Exception as e:
        print("Error with storing to vector store method",e)

    return success




def cleanup_files(filewithpath):
    """

    :param filewithpath: filename to delete with path
    :return: does not return
    """
    if os.path.exists(filewithpath):
        os.remove(filewithpath)
        print(f"removed file {filewithpath}")

    else:
        print(f"{filewithpath} does not exist.")



