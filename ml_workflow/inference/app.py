from fastapi import FastAPI
from pydantic import BaseModel
from predictor import CustomPredictor
import json

class Item(BaseModel):
    instances: list

app = FastAPI()
predictor = CustomPredictor.from_path("/model")

@app.get("/health")
def health():
    model_ready = predictor.is_ready()
    if model_ready:
        return {"status": "Ready"}
    else:
        return {"status": "Not Ready"}, 503


@app.post("/predict")
def predict(item: Item):
    predictions = predictor.predict(item.instances)
    data = {"predictions": predictions, "success": True}
    return data

# To test this API, use:
# curl -X POST "http://localhost:8000/predict" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"instances\":[\"Turnover surged to EUR61 .8 m from EUR47 .6 m due to increasing service demand , especially in the third quarter , and the overall growth of its business .\"]}"