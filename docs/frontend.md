# Frontend

## Files

The repository `/src/frontend` folder includes the following files:

- `Dockerfile`: This file creates a Docker image that serves the frontend application.
- `docker-shell.sh`: A shell script which is used to run Docker commands to build the image from the Dockerfile and then start a container from it.
- `README.txt`: A documentation file that provides the necessary instructions on how to build the Docker image and run a Docker Container for simple frontend and React frontend.
- `index.html`: This is the main file for the frontend application, providing the interface that users interact with. It includes structure, content, and scripts for the web page.
- `styles.css`: The CSS document defining the visual design of the application. It includes all the stylings for the various HTML elements in the frontend webpage.

## Dockerfile, docker-shell.sh, and README.txt

**Dockerfile**: Defines each stage of the Docker image building process and how to run the application inside a Docker container.

- It uses a lightweight web server (nginx) as the base image, sets the working directory inside the container, and copies the HTML files, CSS files, and the image folder into the container.

- The Docker file then exposes port 80 and sets the command to run the application.

**docker-shell.sh**: A shell script for building the Docker image and running the Docker container.

- It first defines the environment variables, including the name of the image and the base directory. Then, the docker build command is used to build the Docker image based on the Dockerfile.

- After the Docker image is built, the Docker run command is used to create a new container from the image. The --rm option is used to remove the container when it exits. It also maps the container's port 8080 to the host's port 8080.

**README.txt**: A text file that contains instructions on how to build the Docker image and run the Docker container for the simple frontend (and React frontend which we aren't currently using).

## Instructions

### Build docker image and run container

In the cloned git repo cd into the `api_service` directory:

```
cd src/frontend
```

Execute the following command in your terminal to build the Docker image and run the container:

```
sh docker-shell.sh
```

### Run development web server (simple frontend)

```
http-server
```
Access at http://localhost:8080/

## index.html

### RAG functionality

The index.html file is the main HTML document of the web app. It defines the structure and content of the web page.

The `index.html` file sets up the layout for an interactive web application called "Rag Detective". When you load the webpage, you can select a scraped website and a specific timestamp, and then input a query for the application to analyze.

- When the document finishes loading, the `fetchWebsites` function is called, which sends a `GET` request to an API endpoint (`/websites`) to populate the websites dropdown menu with websites data.

- `websiteDropdown` and `scrapeSessionDropdown` are dropdown menus. When the website is chosen via `websiteDropdown`, the `updateScrapeSession` function populates the `scrapeSessionDropdown` with timestamps corresponding to the selected website, by sending a `GET` request to the `/timestamps/{website}` endpoint.

- Upon inputting and submitting the query, the `generate_response` function is invoked. This function retrieves the selected values from the dropdown lists and the prompt input. After that, it sends a `POST` request to `/rag_query` endpoint with the payload being the selected website, timestamp, and input query. The server responds with a stream of text that is continuously appended to the `output` textarea.

- While the query data is being fetched and the response is being displayed, a loading overlay is displayed. After the loading is finished, the loading overlay is hidden.

- The `fetchURLs` function is then invoked with the given query ID. This function fetches URLs through a `GET` request to the `/get_urls/{query_id}` endpoint. If the returned data includes URLs, it then delgates the display logic to the function `displayURLs`.

- The `displayURLs` function iterates over the returned URLs and appends them as list items under the "urlsContainer" HTML div. If the `financial_flag` field of the returned data is true, the function sends a `POST` request to the `/vertexai_predict` endpoint to analyze the sentiment of the response. It then appends the sentiment result to the "urlsContainer" and generates a bar chart representing the prediction probabilities for negative, neutral, and positive sentiments.

Additionally, an image of a chatbot named BERT is displayed that changes depending on the sentiment detected:
  - Negative sentiment: A grumpy BERT image is displayed.
  - Neutral sentiment: A shrugging BERT image is displayed.
  - Positive sentiment: A BERT image giving a thumbs up is displayed.

![](../img/rag-detective-app.jpg)

### Scraping functionality

The `tuneButton` is an interactive element that responds to click events. It's represented by a button with a "tune" icon. When a user clicks on this button, the `slideInPanel`—which is a side panel containing an input field and a "scrape site" button—toggles its display state. That means if the panel is not visible, it becomes visible by sliding in, and if it is visible, it slides out to become hidden.

Once the panel is visible, the user can enter a website URL into the `website-to-scrape` input field. This field is styled with Material Design components and outlined text field presentation, giving it an aesthetically pleasing look and feel.

After entering a valid URL, the user can click the "scrape site" button. Upon clicking this button, several actions occur in sequence:

1. **Validation:** The `validateURL` function checks the inputted URL against a regular expression (regex) pattern to ensure it is properly formatted. If invalid, an error message is displayed in the `scrapeResults` textarea indicating "Invalid URL".

2. **Loading Indicator:** A loading indicator (`loadingIndicator`) is displayed to provide feedback to the user that the application is processing their request.

3. **Fetching Sitemap:** The application sends a GET request to an API endpoint (`/sitemap`) with the website URL as a parameter. This is designed to check how many pages are available to scrape from the website's sitemap.

4. **Handling Response:**
   - If the API returns a status indicating an error, the loading indicator is hidden, and the error message is appended to the `scrapeResults` textarea.
   - If the status indicates success, the application retrieves the number of pages available for scraping from the returned data and displays a confirmation message. The confirmation modal (`confirmationModal`) is displayed, asking the user if they would like to proceed with scraping the pages of the website.

5. **Scraping Initiation:** If the user clicks "Yes" on the confirmation modal, the `startScrapingStream` function is invoked. This function initiates the scraping process by sending a POST request to the `/scrape_sitemap` endpoint. This request includes the website URL as JSON content in the body.

6. **Stream Handling:** The response from the POST request is a stream, which `startScrapingStream` reads and processes by chunks. As data is received incrementally from the server, it is appended to the `scrapeResults` textarea, allowing the user to see the real-time progress of the scraping activity.

7. **Completion and Cleanup:** When the stream is complete, the loading indicator is hidden, and the final status, including the duration taken for scraping, is added to the `scrapeResults` textarea.

In summary, the side panel acts as a user interface for submitting a scraping request to an API. This scraping request involves validating the website URL, indicating progress through a visual indicator, providing real-time feedback within the panel's textarea, and offering the user a choice to confirm or cancel the scraping operation.

![](../img/rag-detective-app4.jpg)

## styles.css

The styles.css file defines the look and feel of the web app. Currently:

- The body has light-grey as its background color and uses the Roboto font from Google.

- Different components like the top app bar, content, input section, output section, etc., have their own stylings defined in the CSS file.

- The outputs, loading overlay, spinner, URLs, etc., have their own designated CSS styles to ensure a smooth and appealing user experience.

- Various CSS animations are defined such as `fadeIn` and `popIn` to experiment with the appearing BERT people.

- Sentiment image widths and heights are defined to ensure proper display. Each sentiment color is also represented in the CSS file (e.g., negative sentiment is represented by red).