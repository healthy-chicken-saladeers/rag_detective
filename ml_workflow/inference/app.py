from fastapi import FastAPI
from pydantic import BaseModel
from predictor import CustomPredictor
import json

class Item(BaseModel):
    instances: list

app = FastAPI()
predictor = CustomPredictor.from_path("/model")

@app.post("/predict")
def predict(item: Item):
    predictions = predictor.predict(item.instances)
    data = {"predictions": predictions, "success": True}
    return data
