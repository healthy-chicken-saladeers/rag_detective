from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
# import asyncio
# from api.tracker import TrackerService
# import pandas as pd
# import os
# from fastapi import File
# from tempfile import TemporaryDirectory
# from api import model

# # Initialize Tracker Service
# tracker_service = TrackerService()

# Setup FastAPI app
app = FastAPI(title="API Server", description="API Server", version="v1")

# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.on_event("startup")
# async def startup():
#     print("Startup tasks")
#     # Start the tracker service
#     # asyncio.create_task(tracker_service.track())


# Routes
@app.get("/")
async def get_index():
    return {"message": "Welcome to the RAG Detective App!"}


# @app.get("/experiments")
# def experiments_fetch():
#     # Fetch experiments
#     df = pd.read_csv("/persistent/experiments/experiments.csv")

#     df["id"] = df.index
#     df = df.fillna("")

#     return df.to_dict("records")


# @app.get("/best_model")
# async def get_best_model():
#     model.check_model_change()
#     if model.best_model is None:
#         return {"message": "No model available to serve"}
#     else:
#         return {
#             "message": "Current model being served:" + model.best_model["model_name"],
#             "model_details": model.best_model,
#         }


# @app.post("/predict")
# async def predict(file: bytes = File(...)):
#     print("predict file:", len(file), type(file))

#     self_host_model = True

#     # Save the image
#     with TemporaryDirectory() as image_dir:
#         image_path = os.path.join(image_dir, "test.png")
#         with open(image_path, "wb") as output:
#             output.write(file)

#         # Make prediction
#         prediction_results = {}
#         if self_host_model:
#             prediction_results = model.make_prediction(image_path)
#         else:
#             prediction_results = model.make_prediction_vertexai(image_path)

#     print(prediction_results)
#     return prediction_results