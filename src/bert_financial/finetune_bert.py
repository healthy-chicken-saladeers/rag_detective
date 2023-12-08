# Import necessary libraries
import os

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

# Custom callback for F1 evaluation at the end of each epoch
class F1_Evaluation(tf.keras.callbacks.Callback):
    def __init__(self, validation_data=(), interval=1):
        super(F1_Evaluation, self).__init__()
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
            self.f1_scores.append(_f1)

            print("Epoch: {} - validation_data f1_score: {:.4f}".format(epoch+1, _f1))

# Log in to W&B account for experiment tracking
wandb.login()

# Define the path to dataset
data_path = './data/Sentences_50Agree.txt'

# Load raw data as binary
raw_data = open(data_path, 'rb').read()
# Detect encoding of the data (needed by pandas to import successfully with many text datasets)
result = chardet.detect(raw_data)
encoding = result['encoding']
print("Encoding is: " + encoding)

# Load data into a pandas dataframe with correct encoding and delimiter
df = pd.read_csv(data_path, delimiter='@', header=None, names=['sentence', 'label'], encoding=encoding)

# Split data into train, validation, and test sets with stratification
train,test = train_test_split(df,test_size=0.3,random_state=42,stratify=df['label'])
valid,test = train_test_split(test,test_size=0.5,random_state=42,stratify=test['label'])

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
wandb.init(project="bert-sentiment", name="bert-finetune-run-50agree-10")

# Prepare for F1 score evaluation
val_dataset_temp = val_dataset.batch(8)
f1_evaluation = F1_Evaluation(validation_data=val_dataset_temp, interval=1)

# Add early stopping (disabled for now)
early_stopping = EarlyStopping(monitor='val_loss', patience=2, restore_best_weights=True)

# Train the model
history = model.fit(
    train_dataset.batch(8),
    validation_data=val_dataset_temp,
    epochs=10,
    callbacks=[WandbCallback(save_model=False), f1_evaluation] #, early_stopping]
)

# Evaluate the model with test dataset and show the classification report
y_test = test.label.map(label2num).values
y_pred = tf.nn.softmax(model.predict(test_dataset.batch(8)).logits).numpy().argmax(axis=-1)

print(classification_report(y_test, y_pred, target_names=['negative', 'neutral', 'positive']))
print("F1 Score:", f1_score(y_test, y_pred, average='weighted'))

# Log the F1 score to wandb
wandb.log({'f1_score': f1_score(y_test, y_pred, average='weighted')})

# Create a figure and a 1x3 subplot
fig, axs = plt.subplots(1, 3, figsize=(18, 4))

# Plotting loss
axs[0].plot(history.history["loss"])
axs[0].plot(history.history["val_loss"])
axs[0].set_title("Model loss")
axs[0].set_ylabel("Loss")
axs[0].set_xlabel("Epoch")
axs[0].legend(["Train", "Validation"], loc="upper left")

# Plotting accuracy
axs[1].plot(history.history["accuracy"])
if "val_accuracy" in history.history:
    axs[1].plot(history.history["val_accuracy"])
axs[1].set_title("Model accuracy")
axs[1].set_ylabel("Accuracy")
axs[1].set_xlabel("Epoch")
axs[1].legend(["Train", "Validation"], loc="upper left")

# Plotting Validation F1 Scores
axs[2].plot(f1_evaluation.f1_scores)
axs[2].set_title("Validation F1 Score")
axs[2].set_ylabel("F1 Score")
axs[2].set_xlabel("Epoch")
axs[2].legend(["Validation"], loc="upper left")

# Adjusts subplot params so they fit into the figure area
plt.tight_layout()
plt.savefig('metrics_plot.png')
