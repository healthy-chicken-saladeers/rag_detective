# FastAPI Web Scraper with Cloud and Vector Store Integration Documentation

**Table of Contents:**

- [Overview](#overview)
- [API Endpoints](#api-endpoints)
  - [Sitemap Endpoint](#sitemap-endpoint)
  - [Scrape Sitemap Endpoint](#scrape-sitemap-endpoint)
- [Error Handling](#error-handling)
- [Testing and Usage](#testing-and-usage)
- [Helpers](#helpers)
  - [Set Chrome Options](#set-chrome-options)
  - [Scrape Link](#scrape-link)
  - [Save to GCloud](#save-to-gcloud)
  - [Download Blob from GCloud](#download-blob-from-gcloud)
  - [Store to Weaviate](#store-to-weaviate)
  - [Extract Error Message](#extract-error-message)
  - [Get Sitemap Attributes](#get-sitemap-attributes)
- [Test Calls/Usage Examples](#test-callsusage-examples)

## Overview

The scraper API comprises two FastAPI endpoints: `/sitemap` and `/scrape_sitemap`. Both endpoints are integral parts of the larger system designed to scrape sitemaps from websites, albeit with different functionalities and workflows.

The `/sitemap` endpoint is specialized for retrieving sitemaps of websites and outputting the data into CSV files, with asynchronous updates delivered through the process. It is adept at handling various forms of website URLs, whether it involves adding the HTTPS protocol, appending 'sitemap.xml', or conforming to different URL formatting styles.

The `/scrape_sitemap` endpoint extends this functionality by not only scraping sitemaps but also by streaming the scraping process, saving the scraped results to Google Cloud Storage, and finally storing the data in a vector store. This endpoint is the data collection step of an end-to-end solution that encompasses fetching web data, processing it through various stages of storage and handling, and finally indexing it for optimized retrieval.

In certain cases, simply fetching web data through standard HTTP requests may not be sufficient due to dynamic content generation by JavaScript in modern websites. The `/scrape_sitemap` endpoint overcomes these barriers by utilizing the Selenium WebDriver, which enables the scraper to interact with web pages in a manner akin to a real user browsing a website with a full-fledged browser.

When the scraper encounters a web page that cannot be effectively processed through direct HTTP requests, or if initial scraping efforts fail to gather a minimum threshold of data, the Selenium WebDriver is invoked. Selenium uses a headless Chrome browser, which operates without the GUI of a traditional browser window, to access the web page and execute any necessary JavaScript, allowing for the retrieval of content that is dynamically loaded.

This approach makes the scraper more versatile, capable of handling a wide variety of web pages that would otherwise be inaccessible or yield incomplete data. The combination of `BeautifulSoup` for parsing initial HTML/CSS content and Selenium for dynamic interaction ensures that even the most complex web pages can be scraped accurately.

Furthermore, the scraper is configured to avoid unnecessary overhead during the Selenium scrape, such as by not loading images. After the Selenium browser retrieves the page content, it passes the data back to BeautifulSoup to isolate and extract the textual information. This extracted data is subsequently processed, saved to Google Cloud Storage, and eventually pushed to a vector store.

The integration of Selenium into the scraping process, therefore, represents an important enhancement to the system's scraping capabilities, allowing it to tackle both static and dynamically-generated web content and ensuring a more comprehensive data collection effort.

## API Endpoints

### Sitemap Endpoint

- #### Path: `/sitemap`
- #### Method: `GET`
- #### Description:
  The sitemap endpoint processes the given website URL, constructs the appropriate sitemap URL, fetches the sitemap contents, and extracts the URLs it contains. It handles both flat and nested sitemaps, differentiates between image URLs and sitemap URLs, and aggregates all the non-image URLs for the consumer.

- #### Parameters:
  - `website`: The website base URL or full sitemap URL (string).

- #### Response:
  JSON object containing:
  - `status`: 0 for success, 1 for failure.
  - `count`: Number of URLs retrieved (only on success).
  - `nested_flag`: 1 if the sitemap is nested, 0 otherwise.
  - `message`: Process information or error description.

### Scrape Sitemap Endpoint

- #### Path: `/scrape_sitemap`
- #### Method: `POST`
- #### Description:
  This endpoint allows performing multiple steps from scraping web pages referenced in a sitemap, to streaming the output, saving the scraped data to Google Cloud Storage, and finally inserting the data into a vector store (Weaviate). It accepts a website domain or sitemap URL in JSON format and handles the URL processing internally.

- #### Input JSON:
  - `text`: Domain name or direct link to the sitemap (string).

- #### Response:
  A streaming text response that updates with the progress of scraping, saving, and storing the data.

## Error Handling

Error handling in the system reports at all stages of the scraping process, from HTTP requests to PDF processing, webpage scraping, cloud operations, and storing data in the vector store. Exception handling is implemented within helper functions, ensuring that any errors encountered are not only caught but also relayed back for debugging through informative messages.

When an error occurs during the HTTP request process, webpage scraping or cloud operations, the error details are printed immediately on the console. For errors that occur within the scraping endpoints, the system is designed to provide a detailed error message within the response JSON object to inform the user of what went wrong. This includes using an internal utility that attempts to extract a more detailed error message from an exception when available. If a specific pattern of error message isn't found, the system defaults to returning the full exception message, thereby ensuring that users are well-informed about the operational status of their scraping requests.

## Testing and Usage

To interact with the service endpoints, send `curl` commands with JSON payloads for POST requests, or simply use GET requests as appropriate. The JSON payload should contain the website domain or a direct sitemap URL. For POST requests to the `/scrape_sitemap` endpoint, the domain or URL should be specified within the `text` key in the JSON payload. With GET requests to the `/sitemap` endpoint, you can use the URL parameters to provide the base website URL, a full URL starting with 'https://', or a direct link to a sitemap XML. The endpoints are designed to be flexible and accommodate various forms of input to suit different user requirements.

## Helpers

### Set Chrome Options

Configures the headless Chrome browser options for scraping with Selenium, useful when standard HTTP requests do not retrieve complete data.

### Scrape Link

Processes links obtained from a sitemap using HTTP requests and possibly Selenium with headless Chrome. It differentiates between PDF content and HTML, extracts text, and returns it in a dictionary keyed by the URL.

### Save to GCloud

Saves a Pandas DataFrame, representing the scraped data, as a CSV file to a specified Google Cloud Storage bucket.

### Download Blob from GCloud

Retrieves the CSV file from Google Cloud Storage and saves it locally for further processing.

### Store to Weaviate

Handles the insertion of scraped data into a Weaviate vector store. It monitors the progress and reports updates as documents are added to the vector store.

### Extract Error Message

A utility function within `helper.py` that takes exception objects and extracts detailed error messages for clearer debugging insights.

### Get Sitemap Attributes

This function analyzes the sitemap URL, filters out image URLs, detects nested sitemaps, extracts and deduplicates URLs, and prepares them for CSV export. It captures the operational status, message, and information regarding whether the sitemap is nested.

## Test Calls/Usage Examples

To test the API endpoints, use the following `curl` commands from the command line for both `POST` and `GET` requests:

For the `/scrape_sitemap` POST endpoint, which carries out the full workflow of scraping, saving, and storing data:
```shell
curl -X POST http://localhost:9000/scrape_sitemap -H "Content-Type: application/json" -d '{"text": "bland.ai"}'
curl -X POST http://localhost:9000/scrape_sitemap -H "Content-Type: application/json" -d '{"text": "chooch.com"}'
curl -X POST http://localhost:9000/scrape_sitemap -H "Content-Type: application/json" -d '{"text": "https://arvinas.com/"}'
```

For the `/sitemap` GET endpoint, which accepts a variety of URL inputs to conveniently process different website specifications:
```shell
curl "http://localhost:9000/sitemap?website=ai21.com"
curl "http://localhost:9000/sitemap?website=https://ai21.com"
curl "http://localhost:9000/sitemap?website=https://ai21.com/sitemap.xml"
curl "http://localhost:9000/sitemap?website=ai21.com/"
```

These `curl` commands are designed to trigger the web scraping processes for the respective endpoints. The `/sitemap` endpoint is particularly flexible, capable of handling user inputs ranging from a simple domain name to a complete URL, including those that directly point to a sitemap XML or end with a forward slash. This ensures that users can successfully initiate the scraping process with various forms of website URLs.

