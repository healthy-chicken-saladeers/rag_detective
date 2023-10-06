## Weaviate Schema

#### Although not ideal as it flattens the relationships between websites, timestamps, pages, and chunks, this was the only way we could get Weaviate to cooperate.

We flattened the previous hierarchical model into a singular class: `TextChunk`. Now, each `TextChunk` has properties that once belonged to separate classes like `Page`, `ScrapeSession`, and `Website`.

---

## New Schema for Scraping Application

In order to meet the requirements of Weaviate and optimize search, we've adopted a flattened schema structure. Our new schema focuses on a singular class, `TextChunk`, which encapsulates all necessary properties to describe a scraped content chunk along with its associated webpage, website, and the timestamp of the scraping session.

### **TextChunk**
- **Description**: A segmented portion of text from a scraped webpage containing comprehensive details about its origin and scraping context.
- **InvertedIndexConfig**: To perform queries which are filtered by timestamps, the target class must first be configured to maintain an inverted index for each object by their internal timestamps.
- **Vectorizer**: OpenAI’s text embeddings measure the relatedness of text strings. Embeddings are used for semantic search (where results are ranked by relevance to a query string).

- **Properties**:
  - `key`: 
    - **Description**: A unique identifier for the text chunk. 
    - **Data Type**: string
    - **Indexed**: Yes

  - `text`: 
    - **Description**: The actual content of the text chunk.
    - **Data Type**: string
    - **Indexed**: Yes
  
  - `pageURL`: 
    - **Description**: The specific URL of the webpage this chunk was extracted from.
    - **Data Type**: string
    - **Indexed**: Yes
  
  - `websiteAddress`: 
    - **Description**: The root address of the website from which this chunk was sourced.
    - **Data Type**: string
    - **Indexed**: Yes
  
  - `timestamp`: 
    - **Description**: The exact date and time when the scraping session was conducted, which produced this chunk.
    - **Data Type**: date
    - **Indexed**: Yes

- **Vectorizer**: `text2vec-openai`
  
- **Module Configuration**: 
  - **Model**: `gpt-3.5-turbo`

This new approach streamlines our data model by nesting all the required properties under a single entity. By doing so, we eliminate the complexities of managing deep hierarchical relationships and benefit from faster search capabilities.

Here is how the schema is structured in JSON:

```json
{
    "classes": [
        {
            "class": "TextChunk",
            "description": "A segmented portion of text from a scraped webpage with full details.",
            "invertedIndexConfig": {
                "indexTimestamps": True
            },
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
                    "indexInverted": True
                },
                {
                    "name": "text",
                    "dataType": ["string"],
                    "description": "The content of the text chunk.",
                    "indexInverted": True
                },
                {
                    "name": "pageURL",
                    "dataType": ["string"],
                    "description": "The specific URL of the scraped webpage this chunk belongs to.",
                    "indexInverted": True
                },
                {
                    "name": "websiteAddress",
                    "dataType": ["string"],
                    "description": "The address of the website this chunk comes from.",
                    "indexInverted": True
                },
                {
                    "name": "timestamp",
                    "dataType": ["date"],
                    "description": "The date and time when the chunk was scraped.",
                    "indexInverted": True
                }
            ]
        }
    ]
}
```
