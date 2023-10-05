For our app, we needed a schema that showcases the relationship between a website, the timestamped scrape session, and the scraped contents of each page.

1. `Website`: Represents the website being scraped.
   - Properties:
     - `websiteAddress`: URL of the website. E.g., `www.apple.com`.
     - `scrapedSessions`: A reference to the `ScrapedSession` class (to establish the relationship).

2. `ScrapedSession`: Represents each scraping session associated with a timestamp.
   - Properties:
     - `timestamp`: When the scraping occurred.
     - `scrapedPages`: A reference to the `ScrapedPage` class (to store scraped page details of that session).

3. `ScrapedPage`: Represents the scraped content of each page from a session.
   - Properties:
     - `pageURL`: The specific webpage that was scraped.
     - `textContent`: The text that was scraped from this page.

Given this structure, the `Website` class serves as the parent, with the `ScrapedSession` as a child representing each timestamped scraping event, and the `ScrapedPage` as the granular details of each scraping event.

Here's how the schema looks in JSON format:

```json
{
  "classes": [
    {
      "class": "Website",
      "properties": [
        {
          "name": "websiteAddress",
          "dataType": ["string"]
        },
        {
          "name": "scrapedSessions",
          "dataType": ["ScrapedSession"]
        }
      ]
    },
    {
      "class": "ScrapedSession",
      "properties": [
        {
          "name": "timestamp",
          "dataType": ["string"]  // or ["int"] or ["dateTime"] depending on how you store the timestamp
        },
        {
          "name": "scrapedPages",
          "dataType": ["ScrapedPage"]
        }
      ]
    },
    {
      "class": "ScrapedPage",
      "properties": [
        {
          "name": "pageURL",
          "dataType": ["string"]
        },
        {
          "name": "textContent",
          "dataType": ["string"]
        }
      ]
    }
  ]
}
```

When we scrape a website multiple times, we add multiple `ScrapedSession` objects under the same `Website` object, and each `ScrapedSession` would have multiple `ScrapedPage` objects, one for each page scraped during that session.
