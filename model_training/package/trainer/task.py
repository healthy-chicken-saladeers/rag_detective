
# Import necessary libraries
import os
import requests
import zipfile
import tarfile
import time
import argparse


# Used to suppress output for F1 validation calculation
import io
import contextlib

# For encoding detection
import chardet

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split

# Hugging Face Transformers for BERT
from transformers import BertTokenizer, TFBertForSequenceClassification

# Deep learning frameworks
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import backend as K
from tensorflow.keras.callbacks import EarlyStopping

# Ensure we have a GPU
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

# Verify current GPU
device_name = tf.test.gpu_device_name()
if device_name != '/device:GPU:0':
  raise SystemError('GPU device not found')
print('Found GPU at: {}'.format(device_name))

# Weights and Biases for tracking experiments
import wandb
from wandb.keras import WandbCallback
from sklearn.metrics import f1_score
from google.cloud import storage

#command line arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--epochs", dest="epochs", default=30, type=int, help="Number of epochs."
)
parser.add_argument(
    "--batch_size", dest="batch_size", default=8, type=int, help="Size of a batch."
)
parser.add_argument(
    "--wandb_key", dest="wandb_key", default="16", type=str, help="WandB API Key"
)
args = parser.parse_args()

#Helper method for downloading dataset
def download_file(packet_url, base_path="", extract=False, headers=None):
    if base_path != "":
        if not os.path.exists(base_path):
            os.mkdir(base_path)
    packet_file = os.path.basename(packet_url)
    with requests.get(packet_url, stream=True, headers=headers) as r:
        r.raise_for_status()
        with open(os.path.join(base_path, packet_file), "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    if extract:
        if packet_file.endswith(".zip"):
            with zipfile.ZipFile(os.path.join(base_path, packet_file)) as zfile:
                zfile.extractall(base_path)
        else:
            packet_name = packet_file.split(".")[0]
            with tarfile.open(os.path.join(base_path, packet_file)) as tfile:
                tfile.extractall(base_path)


start_time = time.time()
download_file(
    "https://github.com/sidhantx/datasets/archive/refs/tags/v1.0.zip",
    base_path="datasets",
    extract=True,
)
execution_time = (time.time() - start_time) / 60.0
print("Download execution time (mins)", execution_time)

base_path = os.path.join("datasets", "datasets-1.0")

# Easy place to track what we're training
# Use the 75% consensus dataset
WHICH_DATASET = f'{base_path}/Sentences_75Agree.txt'

# Save our model checkpoints to
bucket_name = "sentiment-trainer"
SAVE_PATH = os.getcwd()
seed_val = 42

goog_storage_client = storage.Client()
bucket = goog_storage_client.bucket(bucket_name)

# Load a dataset given its path
def load_data(data_path, seed):
    raw_data = open(data_path, 'rb').read()
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    print("Encoding for:", data_path, "is:", encoding)
    df = pd.read_csv(data_path, delimiter='@', header=None, names=['sentence', 'label'], encoding=encoding)
    return df.sample(frac=1, random_state=seed)

# Load data with correct encoding and delimiter
df_50agree = load_data(f'{base_path}/Sentences_50Agree.txt', seed_val)
train = load_data(WHICH_DATASET, seed_val)

# Save original count for unit testing purposes
original_50agree_count = train.shape[0]

# Take a random subset of sentences_50agree equal in size to the size of train dataset
subset_50agree = df_50agree.sample(n=len(train), random_state=seed_val)

# Randomly choose 31% of the data from this subset for validation/test
_, valid_test_subset = train_test_split(subset_50agree, test_size=0.31, random_state=seed_val, stratify=subset_50agree['label'])

# Remove items from train dataset that are in the validation/test set
train = train[~train['sentence'].isin(valid_test_subset['sentence'])]

# Split the validation/test set in half into validation and test set
valid, test = train_test_split(valid_test_subset, test_size=0.5, random_state=seed_val, stratify=valid_test_subset['label'])

# Load pre-trained BERT tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Convert texts to BERT input format
train_encodings = tokenizer(train.sentence.tolist(), truncation=True, padding=True)
val_encodings = tokenizer(valid.sentence.tolist(), truncation=True, padding=True)
test_encodings = tokenizer(test.sentence.tolist(), truncation=True, padding=True)

def make_tf_dataset(encodings, labels):
    """Function to convert encodings and labels into tensorflow dataset."""
    input_ids = np.array(encodings['input_ids'])
    attention_mask = np.array(encodings['attention_mask'])
    labels = np.array(labels)
    return tf.data.Dataset.from_tensor_slices((input_ids, attention_mask, labels)).map(
        lambda input_ids, attention_mask, labels : ({"input_ids": input_ids, "attention_mask": attention_mask}, labels))

# Defining the labels keys and their respective values as per the model
label2num = {'negative':0,'neutral':1,'positive':2}
train_labels = [label2num[x] for x in train.label.tolist()]
val_labels = [label2num[x] for x in valid.label.tolist()]
test_labels = [label2num[x] for x in test.label.tolist()]

# Convert encodings and labels into tensorflow dataset
train_dataset = make_tf_dataset(train_encodings, train_labels)
val_dataset = make_tf_dataset(val_encodings, val_labels)
test_dataset = make_tf_dataset(test_encodings, test_labels)

# Print the sizes and percentages
total_size = len(train) + len(valid) + len(test)

print("\nSize of Train set:", len(train),
      f"({(len(train)/total_size)*100:.2f}%)")
print("Size of Validation set:", len(valid),
      f"({(len(valid)/total_size)*100:.2f}%)")
print("Size of Test set:", len(test),
      f"({(len(test)/total_size)*100:.2f}%)")

# Distribution in the Training set
print("Training set:")
print(train['label'].value_counts())

# Distribution in the Validation set
print("\nValidation set:")
print(valid['label'].value_counts())

# Distribution in the Test set
print("\nTest set:")
print(test['label'].value_counts())


# Custom callback for F1 evaluation at the end of each epoch
class F1_Evaluation(tf.keras.callbacks.Callback):
    def __init__(self, validation_data=(), interval=1, save_path=SAVE_PATH):
        super(F1_Evaluation, self).__init__()
        self.best_f1_so_far = 0
        self.save_path = save_path
        self.interval = interval
        self.dataset = validation_data
        self.X_val, self.y_val = [], []

        # Iterating over the dataset to get batches
        for batch in self.dataset:
            # Batch consists of inputs and labels
            inputs, labels = batch
            self.X_val.append(inputs)  # inputs is a dict with keys ['input_ids', 'attention_mask']
            self.y_val.append(np.atleast_1d(np.squeeze(labels.numpy())))  # Converting labels tensor to numpy array

        self.f1_scores = []

    def on_epoch_end(self, epoch, logs={}):
        """Method called at the end of each epoch, calculating and logging F1 score."""
        print("\nCalculating validation F1 score...")
        # Process only for epochs with (epoch number modulo self.interval) equal to 0
        if epoch % self.interval == 0:
            y_pred = []

            # Iterate over inputs for each batch to generate predictions
            for X_val_batch in self.X_val:
                # Redirect stdout and stderr to avoid print statements inside keras.model.predict
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    y_pred_single = self.model.predict(X_val_batch).logits
                # Softmax on logits and take class with maximum probability
                y_pred_single = tf.nn.softmax(y_pred_single).numpy().argmax(axis=-1)
                # Ensure that y_pred_single is at least a 1D array even if it is a scalar
                y_pred.append(np.atleast_1d(y_pred_single))

            # Concatenate all predictions and labels
            y_pred = np.concatenate(y_pred)
            y_val = np.concatenate(self.y_val)

            # Calculate F1 score and append to F1 scores list
            _f1 = f1_score(y_val, y_pred, average='weighted')

            if _f1 > self.best_f1_so_far:
                self.best_f1_so_far = _f1
                print("Found new best F1 score:", _f1, "Saving the model.")

                self.model.save_pretrained(self.save_path)
                blob = bucket.blob('best_modelt.h5')
                stream = io.BytesIO(open(f"{self.save_path}/tf_model.h5", "rb").read())
                blob.upload_from_file(stream)

                blob = bucket.blob('config.json')
                stream = io.BytesIO(open(f"{self.save_path}/config.json", "rb").read())
                blob.upload_from_file(stream)

            self.f1_scores.append(_f1)

            print("Epoch: {} - validation_data f1_score: {:.4f}".format(epoch + 1, _f1))

            # Log the validation F1 score at the end of each epoch
            wandb.log({"val_f1_score": _f1})



# Log in to W&B account for experiment tracking
wandb.login(key=args.wandb_key)

# Load pre-trained BERT model with a classification layer on top
model = TFBertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=3)

# Define loss function, optimizer, and metrics
loss_fn = keras.losses.SparseCategoricalCrossentropy(from_logits=True)

lr_schedule = keras.optimizers.schedules.ExponentialDecay(
    initial_learning_rate=3e-5,
    decay_steps=10000,
    decay_rate=0.9)
optimizer = keras.optimizers.Adam(learning_rate=lr_schedule)

# optimizer = keras.optimizers.Adam(learning_rate=3e-5)
model.compile(optimizer=optimizer, loss=loss_fn, metrics=['accuracy'])

# Initializing wandb run
wandb.init(project="temp-project")

# Prepare for F1 score evaluation
val_dataset_temp = val_dataset.batch(args.batch_size)
f1_evaluation = F1_Evaluation(validation_data=val_dataset_temp, interval=1, save_path=SAVE_PATH)


# Add early stopping (disabled for now)
early_stopping = EarlyStopping(monitor='val_loss', patience=2, restore_best_weights=True)

# Train the model
history = model.fit(
    train_dataset.batch(args.batch_size),
    validation_data=val_dataset_temp,
    epochs=args.epochs,
    callbacks=[WandbCallback(save_model=False), f1_evaluation] #, early_stopping]
)

# Load the checkpointed model
finetuned_model = TFBertForSequenceClassification.from_pretrained(SAVE_PATH)
finetuned_model.trainable = False

# Evaluate the model with test dataset and show the classification report
y_test = test.label.map(label2num).values
y_pred = tf.nn.softmax(finetuned_model.predict(test_dataset.batch(8)).logits).numpy().argmax(axis=-1)

print(classification_report(y_test, y_pred, target_names=['negative', 'neutral', 'positive']))
test_f1_score = f1_score(y_test, y_pred, average='weighted')
print("Test F1 Score:", test_f1_score)

# Log the test F1 score to wandb (single data point)
wandb.log({'test_f1_score': test_f1_score})

