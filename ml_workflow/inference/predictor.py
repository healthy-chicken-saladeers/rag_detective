from transformers import BertTokenizer
import tensorflow as tf
import numpy as np

class CustomPredictor(object):
  def __init__(self, model):
    self._model = model

  def is_ready(self):
    return self._model is not None and self._model.model is not None and self._model.tokenizer is not None

  def predict(self, instances, **kwargs):
    """
    Perform inference on a list of input instances.
    """
    
    # Preprocess the input
    preprocessed_data = self._model.preprocess(instances)

    # Run model prediction
    predictions = self._model.predict(preprocessed_data)

    # Postprocess the prediction results
    postprocessed_outputs = self._model.postprocess(predictions)

    return postprocessed_outputs
  
  @classmethod
  def from_path(cls, model_dir):
    """
    Function to load the model. BERT specific code here.
    """

    model = CustomModelPredictor(model_dir)
    return cls(model)

class CustomModelPredictor(object):
  def __init__(self, model_path):
    self.model = tf.keras.models.load_model(model_path)
    self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

  def predict(self, instances): 
    return self.model.predict(instances)


  def preprocess(self, instances):
    tokenized_inputs = self.tokenizer(instances, truncation=True, padding=True, return_tensors="tf")
    return tokenized_inputs.data

  def postprocess(self, predictions):
    logits = predictions.get('logits', predictions)
    probabilities = tf.nn.softmax(logits, axis=-1)
    predicted_class = tf.argmax(probabilities, axis=-1)
    return {'class': predicted_class.numpy().tolist(), 'probabilities': probabilities.numpy().tolist()}

