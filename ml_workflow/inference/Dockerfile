FROM tensorflow/tensorflow:latest
COPY . /app
WORKDIR /app
COPY ./best_model /model
RUN pip install fastapi uvicorn transformers
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
