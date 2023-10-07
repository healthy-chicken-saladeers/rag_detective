## Original Schema Plan

#### This plan was abandoned after countless hours struggling with Weaviate to work with a 4 level hierarchy, and ultimately we adopted a flat structure.

For our app, we designed a schema that delineates the relationship between a website, its associated scrape sessions, and the segmented contents of each scraped page.

1. **TextChunk**: Represents the segmented or partitioned text content extracted from a webpage.
   - **Description**: A segmented portion of text from a scraped webpage.
   - **Properties**:
     - `key`: A unique index or identifier marking the text segment, making referencing efficient.
     - `text`: The authentic text extracted, which is confined in length (e.g., up to 500 words).

2. **Page**: Depicts the granular details of each webpage that underwent scraping in a session.
   - **Description**: Details of a specific webpage scraped during a session.
   - **Properties**:
     - `pageURL`: The distinct webpage URL that was scraped (e.g., `https://www.apple.com/iphone/`). This URL serves as an identifier for the scraped content.
     - `chunks`: A linkage to the `TextChunk` class, which encapsulates segmented content from the webpage.

3. **ScrapeSession**: Epitomizes individual scraping sessions that are timestamped.
   - **Description**: Represents a specific scrape event at a certain timestamp.
   - **Properties**:
     - `timestamp`: The exact moment when the scraping session was initiated, recorded in date format.
     - `pages`: A linkage to the `Page` class, storing detailed information about the web pages scraped during this specific session.

4. **Website**: Symbolizes the website that is being scraped.
   - **Description**: Represents a website which can have multiple scrape sessions.
   - **Properties**:
     - `websiteAddress`: The website's URL (e.g., `www.apple.com`). This address aids in identifying the website uniquely and establishes relationships with its scrape sessions.
     - `scrapeSessions`: A linkage to the `ScrapeSession` class, thereby defining the many scrape sessions associated with this website.

Provided this architecture, the `Website` class acts as the overarching parent entity. Nested within it, the `ScrapeSession` class records each timestamped scraping occurrence. The `Page` class maintains an inventory of details for every webpage scraped in that session. Finally, the `TextChunk` class signifies discrete segments of the content harvested from each page.

Below is the schema's representation in the JSON format:

```json
{
  "classes": [
    {
      "class": "TextChunk",
      "description": "A segmented portion of text from a scraped webpage.",
      "vectorizer": "text2vec-openai",
      "moduleConfig": {
        "generative-openai": {
          "model": "gpt-3.5-turbo"
        }
      },
      "properties": [
        {
          "name": "key",
          "dataType": ["string"],
          "description": "The identifier for the text chunk.",
          "indexInverted": true
        },
        {
          "name": "text",
          "dataType": ["string"],
          "description": "The content of the text chunk.",
          "indexInverted": true
        }
      ]
    },
    {
      "class": "Page",
      "description": "Details of a specific webpage scraped during a session.",
      "properties": [
        {
          "name": "pageURL",
          "dataType": ["string"],
          "description": "The specific URL of the scraped webpage.",
          "indexInverted": true
        },
        {
          "name": "chunks",
          "dataType": ["TextChunk"],
          "description": "Segmented content chunks from the scraped page."
        }
      ]
    },
    {
      "class": "ScrapeSession",
      "description": "Represents a specific scrape event at a certain timestamp.",
      "properties": [
        {
          "name": "timestamp",
          "dataType": ["date"],
          "description": "The date and time when the scrape session occurred.",
          "indexInverted": true
        },
        {
          "name": "pages",
          "dataType": ["Page"],
          "description": "Webpages scraped during the session."
        }
      ]
    },
    {
      "class": "Website",
      "description": "Represents a website which can have multiple scrape sessions.",
      "properties": [
        {
          "name": "websiteAddress",
          "dataType": ["string"],
          "description": "The address of the website.",
          "indexInverted": true
        },
        {
          "name": "scrapeSessions",
          "dataType": ["ScrapeSession"],
          "description": "The scrape sessions associated with the website."
        }
      ]
    }
  ]
}
```

Whenever we initiate a scraping process on a website, we introduce a new `ScrapeSession` object under the related `Website` entity. Every `ScrapeSession` then encompasses multiple `Page` objects, each signifying distinct web pages scraped during that event. Each of these `Page` objects further consists of several `TextChunk` objects, capturing the segmented content of that page.