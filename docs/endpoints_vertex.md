# Vertex AI Text Classification Documentation

**Table of Contents:**

- [Overview](#overview)
- [API Endpoints](#api-endpoints)
  - [Vertex AI Prediction Endpoint](#vertex-ai-prediction-endpoint)
- [Authentication and Credentials](#authentication-and-credentials)
- [Testing and Usage](#testing-and-usage)
- [Response Structure](#response-structure)

## Overview

This FastAPI endpoint interacts with Google Vertex AI to classify text using a pre-trained BERT model. The API takes in a text instance, sends it for prediction, and provides a structured response with classification details.

## API Endpoints

### Vertex AI Prediction Endpoint

- #### Path: `/vertexai_predict`
- #### Method: `POST`
- #### Description:
  The Vertex AI Prediction endpoint receives text data in a POST request, forwards it to a specified Google Cloud Vertex AI Endpoint that hosts a fine-tuned BERT model, receives the prediction, and responds with the sentiment classification and associated probabilities.

- #### Request Body:
  JSON object containing:
  - `text`: Text to be classified (string).

- #### Response:
  JSON object containing:
  - `sentiment`: The sentiment classification value (integer).
  - `probabilities`: The probability scores for the classification (list or array).

## Authentication and Credentials

The endpoint uses a Google Cloud service account for authentication. It expects a service account JSON file to be located at a predefined path and uses this file to authenticate with Google Vertex AI services.

## Testing and Usage

The prediction endpoint can be tested using the `curl` command with the appropriate headers and request body.

```shell
curl -N -H "Content-Type: application/json" \
     -d "{\"text\": \"The company's revenue increased by 15% in the last quarter, driven by strong sales in the Asia-Pacific region and the successful launch of its new line of eco-friendly products.\"}" \
     "http://localhost:9000/vertexai_predict"
```

Replace `"The company's revenue increased by 15% in the last quarter, driven by strong sales in the Asia-Pacific region and the successful launch of its new line of eco-friendly products."` with the text you want to classify.

## Response Structure

The response from the Google Vertex AI prediction is parsed to extract the sentiment value and the probabilities. These values are then repackaged into a structured JSON object that is sent back to the requestor.

The `sentiment` key holds the predicted sentiment classification as an integer, and the `probabilities` key includes the probability scores that the model associates with each possible class.
