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
    """
    Executes a query against the Weaviate vector store with specific filters and returns a streaming response.

    This function sets up a vector store and an index for querying, applies exact match filters for the
    website address and timestamp, and uses a custom prompt template for question-answering. The query is executed
    against the Weaviate vector store, and the response is streamed back.

    Args:
        client: A Weaviate client instance used to interact with the Weaviate vector store.
        website (str): The website address to be used as a filter for the query.
        timestamp (str): The timestamp to be used as a filter for the query.
        query (str): The query string for the question-answering.

    Returns:
        A streaming response object containing the results of the executed query.

    Note:
        The function measures the execution time of the query and prints it. The prompt template includes
        a specific format for handling financial information in the query response.
    """

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
    """
    Queries a Weaviate database to retrieve all unique website addresses stored in the Pages class.

    This function constructs and executes a GraphQL query to fetch the 'websiteAddress' field from
    all entries in the 'Pages' class of a Weaviate database. It ensures the uniqueness of the website
    addresses by storing them in a set before converting them back to a sorted list for the return value.

    Args:
        client: A Weaviate client instance used to execute the GraphQL query.

    Returns:
        list: A sorted list of unique website addresses retrieved from the Weaviate database.

    Raises:
        HTTPException: If any error occurs during the query execution or data processing,
                       an HTTPException with status code 500 is raised.
    """

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
    """
    Fetches all unique timestamps for a specified website address from a Weaviate database.

    This function constructs a GraphQL query to retrieve the 'timestamp' field from entries
    in the 'Pages' class that match a given website address. It ensures the uniqueness of
    timestamps by using a set, and returns them as a sorted list in reverse order (most recent first).

    Args:
        client: A Weaviate client instance for executing the GraphQL query.
        website_address (str): The website address for which timestamps are to be retrieved.

    Returns:
        list: A sorted list (in reverse order) of unique timestamps associated with the given website address.

    Raises:
        HTTPException: If any error occurs during the query execution or data processing,
                       an HTTPException with status code 500 is raised, including the error details.
    """

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
    """
   Extracts and collects document URLs from a given streaming response.

   This function iterates over the nodes within a streaming response, specifically looking for
   nodes that represent documents (identified by a node type of "4", corresponding to ObjectType.DOCUMENT).
   It collects the URLs (node IDs) of these document nodes and returns them in a list.

   Args:
       streaming_response: A streaming response object that contains source nodes with relationship information.

   Returns:
       list: A list of URLs (node IDs) extracted from the document nodes in the streaming response.
    """
    urls = []
    for node_with_score in streaming_response.source_nodes:
        relationships = node_with_score.node.relationships
        for related_node_info in relationships.values():
            if related_node_info.node_type == "4":  # Corresponds to ObjectType.DOCUMENT
                urls.append(related_node_info.node_id)
    return urls


#Scraper code
#defines a header, that is required for scraping with selenium.
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

#google cloud bucket name where csv's for company data are stored
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
    """
    Extracts attributes from a sitemap URL, including nested sitemaps.

    This function processes a given sitemap URL to extract URLs and identify if the sitemap is nested.
    It filters out image URLs and checks for nested sitemaps, making additional requests as necessary.
    The function returns a dictionary with the status of the operation, a pandas Series of URLs, a flag
    indicating if the sitemap is nested, and a message describing the outcome.

    Args:
        url (str): The URL of the sitemap to be processed.

    Returns:
        dict: A dictionary containing the status (0 for success, 1 for failure), a pandas Series of extracted URLs,
              a nested flag (1 for nested sitemap, 0 otherwise), and a message detailing the process or errors.

    Raises:
        requests.RequestException: If a request to fetch a URL fails, the error is caught and
                                   details are included in the returned dictionary.
    """

    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg']

    print("Inside get_sitemap_attributes")
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
            print(link)
            if is_image_url(link, image_extensions): # Ensure we're not scraping an image
                print(f"Skipping image URL: {link}")
                continue
            if link.endswith('xml'):
                nested_sitemap_flag = True
                try:
                    with requests.get(link, headers=headers) as response:
                        response.raise_for_status()  # Check if the request was successful
                        nested_soup = BeautifulSoup(response.text, 'lxml-xml')
                        nested_urls = [url.text.strip() for url in nested_soup.find_all('loc') if url]

                        for nested_link in nested_urls:
                            # yield f"Checking sitemap {nested_link}.\n"
                            if is_image_url(nested_link, image_extensions):
                                print(f"Skipping image URL in nested sitemap: {nested_link}")
                                continue
                            extended_urls.append(nested_link)
                except requests.RequestException as e:
                    print(f"Error occurred while processing {link}: {e}")
            else:
                extended_urls.append(link)

        if not extended_urls:
            attribute_dict['status'] =1 # return status =1 (i.e. some failure happened)
            attribute_dict['message'] = f"The sitemap URL {url} refers to a nested link of sitemaps. However, the scraper either did not find any links, or some unexpected error occured. "
            return attribute_dict

        attribute_dict['df'] = pd.Series(extended_urls).drop_duplicates().str.strip()
        if nested_sitemap_flag:
            attribute_dict['message'] = f"The sitemap URL {url} refers to a nested sitemap with {len(urls)} sitemap links."
            attribute_dict['nested_flag'] = 1
        else:
            attribute_dict['message'] = f"The sitemap URL {url} refers to a single sitemap."
        return attribute_dict

    except requests.RequestException as e:
        print(f"Error occurred: {e}")
        attribute_dict['status'] =1
        attribute_dict['message'] = extract_error_message_from_exception(e)
        return attribute_dict  # Returns status =1 (i.e. some failure happened)

def is_image_url(url, image_extensions):
    """
   Determines whether a given URL is an image URL based on its file extension.

   This function checks if the URL ends with any of the provided image file extensions.
   It's useful for filtering out image URLs when processing a list of mixed URLs.

   Args:
       url (str): The URL to be checked.
       image_extensions (list): A list of image file extensions (e.g., ['.jpg', '.png']) to check against.

   Returns:
       bool: True if the URL ends with any of the specified image file extensions, False otherwise.
    """
    return any(url.lower().endswith(ext) for ext in image_extensions)

def scrape_link(link):
    """
    Scrapes text content from a given URL, handling both HTML and PDF formats.

    This function attempts to scrape text from the provided URL. For PDF content, it extracts text using PyMuPDF.
    For HTML content, it uses BeautifulSoup for initial scraping. If the content is too short, it then attempts
    scraping with Selenium to render JavaScript-based pages. The function returns a dictionary mapping the URL to
    the scraped text.

    Args:
       link (str): The URL of the webpage or PDF to be scraped.

    Returns:
       dict: A dictionary with the URL as the key and the scraped text as the value. If an error occurs,
             the value will be an empty string.

    Raises:
       requests.RequestException: If there's an issue with the HTTP request to the URL.

    Note:
    Selenium is used as a fallback for pages that require JavaScript rendering or if the initial scrape does
    not return sufficient content. The function handles headers, footers, and navigational elements by removing
    them from the scraped text.
    """
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
    """
    Saves a pandas DataFrame to Google Cloud Storage as a CSV file.

    This function attempts to save the provided DataFrame to a specified bucket in Google Cloud Storage.
    It converts the DataFrame into CSV format and uploads it using the given filename. The function
    returns a boolean flag indicating the success or failure of the operation.

    Args:
       df (pandas.DataFrame): The DataFrame to be saved.
       filename (str): The name of the file to be used when saving the DataFrame in the storage bucket.

    Returns:
       bool: True if the DataFrame is successfully saved to Google Cloud Storage, False otherwise.

    Raises:
       Exception: If any error occurs during the saving process, it is caught and printed. No exception
                  is raised to the caller.

    Note:
       The function requires access to a Google Cloud Storage bucket and appropriate permissions to write data.
       Ensure that the storage client and bucket are correctly configured and accessible.
    """
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
    """
    Downloads a file from Google Cloud Storage to a local directory.

    This function fetches a file specified by the filename from Google Cloud Storage
    and saves it to a local directory. It returns a boolean flag indicating whether
    the download was successful.

    Args:
       filename (str): The name of the file to be downloaded from Google Cloud Storage.
                       Assumes the file is located in a 'data' subdirectory within the storage bucket.

    Returns:
       bool: True if the file is successfully downloaded, False otherwise.

    Raises:
       Exception: Catches any exceptions that occur during the download process and prints an error message.
    Note:
       The function expects the storage client and bucket to be correctly configured and accessible.
       The destination path for the downloaded file is set to '/home/downloads/'.
    """
    sourcefilename = f"data/{filename}"
    destinationfilename = f"/home/downloads/{filename}"

    success = False
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(sourcefilename)
        blob.download_to_filename(destinationfilename)
        success = True
        print(f"Download from gcloud succeeded")
    except Exception as e:
        print("Error while downloading blob from gcloud",e)

    return success


# Write to weaviate part
def store_to_weaviate(filename):
    """
    Stores documents into a Weaviate vector store and yields progress updates.

    This function reads a CSV file specified by the filename, extracts documents, and stores them
    into a Weaviate vector store. It uses the filename to extract metadata (websiteAddress and timestamp)
    for each document. The function yields updates on the number of documents inserted into the vector store.

    Args:
       filename (str): The name of the CSV file containing documents to be stored.

    Yields:
       str: Progress updates on the number of documents inserted into the vector store.

    Raises:
       Exception: Catches any exceptions that occur during the process and prints an error message.

    Note:
       The function expects the Weaviate instance to be accessible at the given IP address and the
       OpenAI API key to be set as an environment variable.
    """
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
    """
    Deletes a file from the given file path.

    This function checks if the specified file exists at the given path. If it does, the function
    attempts to delete it. It prints a confirmation message upon successful deletion or an error
    message if the deletion fails. If the file does not exist, it prints a message indicating so.

    Args:
        filewithpath (str): The complete path of the file to be deleted, including the filename.

    Note:
        This function uses the os module to interact with the file system. It handles any exceptions
        raised during file deletion and prints relevant messages.

    Example:
        cleanup_files("/path/to/file.txt")
        # This will attempt to delete 'file.txt' from '/path/to/' and print a message regarding the outcome.
        """
    if os.path.exists(filewithpath):
        try:
            os.remove(filewithpath)
            print(f"Removed file {filewithpath}")
        except Exception as e:
            print(f"Error occured while deleting {filewithpath}", e)
    else:
        print(f"{filewithpath} does not exist.")
