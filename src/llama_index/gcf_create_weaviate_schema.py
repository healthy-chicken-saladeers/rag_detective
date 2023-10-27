import functions_framework
import weaviate
import os

os.environ.get("OPENAI_API_KEY")
WEAVIATE_IP_ADDRESS = "34.133.13.119"

@functions_framework.http
def create_weaviate_schema():

    schema = {
    "classes": [
        {
            "class": "Document",
            "description": "A full document of text from a scraped webpage with full details.",
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
                    "name": "text",
                    "dataType": ["string"],
                    "description": "The content of the document.",
                    "indexInverted": True
                },
                {
                    "name": "websiteAddress",
                    "dataType": ["string"],
                    "description": "The address of the website this document comes from.",
                    "indexInverted": True
                },
                {
                    "name": "timestamp",
                    "dataType": ["date"],
                    "description": "The date and time when the document was scraped.",
                    "indexInverted": True
                }
              ]
            }
        ]
      }
    
    # Create Weaviate client
    client = weaviate.Client(url="http://" + WEAVIATE_IP_ADDRESS + ":8080")
    
    # Delete existing schema (caution: this deletes the current structure)
    client.schema.delete_all()

    # Here we use the schema created in the previous cell.
    client.schema.create(schema)
    return("Schema was created.")