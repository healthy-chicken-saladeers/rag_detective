# Optimizing BERT for Financial Sentiment Analysis

The model we chose for fine-tuning and optimization, BERT, especially the `bert-base-uncased` variant, is a commonly used foundation model for NLP tasks. When fine-tuned, it can be a powerful tool for financial sentiment analysis. To deploy BERT in real-world applications, especially on edge devices or under latency constraints, we want to optimize its size and speed. In our project, we tried three main optimization techniques: quantization, pruning, and distillation. It turned out we chose a challenging, complex model to conduct these techniques on.

Some initial research about using these methods on large language models led us to the following starting point:

**Most Likely to Succeed**: 

- **Distillation** has shown consistent results across various tasks and models. Given the domain specificity of financial sentiment analysis, distilling BERT into a smaller model tailored to this task seems promising.

**Riskiest**:

- **Pruning**, especially aggressive pruning, poses risks for transformer architectures. The inter-dependencies in self-attention mechanisms can be sensitive to drastic pruning. 

Let's go over our methodology.

## 1. Quantization

**Quantization** involves converting the model's weights (and sometimes activations) from 32-bit floating-point numbers to lower bit-width, such as 8-bit integers.

### Pros:
- **Size Reduction**: Quantized models occupy significantly less memory.
- **Speed**: On hardware that supports integer operations, quantized models can run faster.

### Cons:
- **Accuracy Trade-off**: Quantization can lead to a slight degradation in model accuracy.

### Applicability to BERT:
Given the size of `bert-base-uncased`, quantization can substantially reduce its memory footprint. TensorFlow Lite offers tools for post-training quantization. For BERT, weight quantization is safer than full integer quantization, as activations in transformers can have dynamic ranges.

### Our challenges in Quantizing our BERT Model

#### TensorFlow Lite and Dynamic range quantization

We discovered early on that most of the built-in quantization in TensorFlow is geared towards running models on edge devices, and use another framework called TensorFlow Lite. **Dynamic range quantization**, the first method we tried, required this conversion. The TensorFlow Lite converter has an option to quantize the model weights to 8-bit integers during this process, saving considerable amounts of memory and improve execution speed.

However, we hit a major problem in the conversion of BERT. When using the converted TFLite model's interpreter, the observed expected input shape was [1, 1], indicating that the model was expecting a single token as input. This was unusual for a BERT model, as BERT is designed to look at entire sequences of tokens, not just a single one. The expected input shape was noted from both the 'shape' and 'shape_signature' field of TFLite model's inputs. Ensuring the correctly expected shape for BERT-style inputs during conversion is vital, but we couldn't find any reason why our converted model stopped behaving like BERT. It could be just that the Hugging Face `Transformers` library is not compatible with TensorFlow Lite due to the size of some of the models.

#### Quantization-aware training (QAT) and Post-training quantization

- **Quantization-aware training (QAT)**: Quantization is considered during the training process itself. This can often result in better model accuracy compared to post-training quantization because the model is trained while being aware of the quantization errors. The model's weights are quantized during training, and the forward pass simulates the effects of quantization. By doing so, the model can adapt to the quantization process and can potentially provide more accurate results than simple post-training quantization.

- **Post-training quantization**: This is done after the model has been trained. There are multiple ways to perform post-training quantization:
   - **Weight Quantization**: Only the weights are quantized, but the activations remain in floating-point.
   - **Full Integer Quantization**: Both weights and activations are quantized to integers. This can significantly reduce model size and increase inference speed, especially on hardware that's optimized for integer operations.
   - **Float16 Quantization**: Convert all floating-point numbers (like weights and activations) to half-precision floating point (float16). This can help reduce model size while keeping a balance between accuracy and performance.

After a lot of experimentation and trying different methods, we found that both post-training quantization and quantization aware training in the TensorFlow Model Optimization Toolkit (TF-MOT) currently supports only Keras Sequential and Functional models. The BERT model loaded from Hugging Face transformers is a subclassed model, which is not currently supported.

Unfortunately, this meant that we could not use post-training quantization or QAT from TF-MOT to quantize the Hugging Face's BERT model directly. For this reason we moved on to pruning as an optimization technique.


## 2. Pruning

**Pruning** involves removing certain weights or neurons from the model, turning them to zero, based on certain criteria (like magnitude).

### Pros:
- **Size Reduction**: Sparse models can be compressed further.
- **Speed**: Some hardware can accelerate sparse operations.

### Cons:
- **Accuracy Trade-off**: Pruning can lead to accuracy drops if not done carefully.

### Applicability to BERT:
BERT has millions of parameters. By pruning, we can obtain a sparser model. However, aggressive pruning can degrade the performance of transformers. Gradual pruning during retraining is recommended.

### More issues with TF-MOT

The TensorFlow Model Optimization Toolkit also offers pruning capabilities. But similar to quantization, it is only compatible with Sequential or Functional Keras models rather than Subclassed models, which include models loaded from Hugging Face's Transformers.

To apply pruning using TF-MOT, the model needs to be wrapped similar to quantization, and the same compatibility issues arose as they did with quantization. Subclassed models like Hugging Face's `bert-base-uncased` don't expose their internal layer structure the way `Sequential` and `Functional` models do, which makes it more challenging for techniques like pruning and quantization.

We could have manually modified the `BERT` model to be a `Functional` model, but that would be quite complicated due to the interdependencies of the layers inside and effectively rebuilding `BERT` from scratch, which would really be taking us far from our original vision of this project.

## 3. Distillation

Distillation, often referred to as "knowledge distillation," is a technique in which a smaller model (the "student") is trained to mimic the behavior of a larger, more complex model (the "teacher"). The main idea is to transfer the "knowledge" from the teacher model to the student model, allowing the student to achieve better performance than if it were trained directly on the data.

Here's a deeper dive into how distillation works, particularly focusing on the loss functions:

## Loss Functions in Distillation:

### 1. Hard Target Loss:

This is the traditional loss used when training neural networks. It computes the difference between the predictions of the student model and the ground truth labels in the dataset.

If $y$ is the ground truth and $\hat{y}_{student}$ is the prediction from the student:

Hard Target Loss = $L(y, \hat{y}_{student})$


For classification tasks, this is usually the cross-entropy loss.

### 2. Soft Target Loss:

This loss computes the difference between the soft predictions (logits or probabilities) of the teacher model and those of the student model. The "soft" predictions are often obtained by raising the temperature of the softmax function used in the final layer of the model.

Given the logits from the teacher $z_{teacher}$ and the logits from the student $z_{student}$, the soft target loss can be expressed as:

Soft Target Loss = $L($ Softmax $(z_{teacher}/T),$ Softmax $(z_{student}/T))$

where
- $T$ is the "temperature" hyperparameter. A value greater than 1 makes the softmax outputs softer (i.e., closer to a uniform distribution), which emphasizes the relationships between classes.

## Combining the Losses:

To train the student model, a weighted combination of the hard target loss and soft target loss is used:

Total Loss = $\alpha \times$ Hard Target Loss $+ (1-\alpha) \times$ Soft Target Loss

where
- $\alpha$ is a hyperparameter that controls the weighting of the respective losses. $\alpha$ values closer to 1 put a greater emphasis on the hard labels, and $\alpha$ closer to zero emphasize the teacher model's logits.

The soft targets capture the relationships between different classes. In our 3-class classification for financial sentiment (negative, positive, or neutral), if a particular input results in the teacher model assigning high probabilities to class 3 and slightly lower probabilities to classes 1 and 2, this provides more information than simply knowing the ground truth is class 3. The student model learns from this additional information, which helps in its generalization.

### Pros:

- **Compact Model**: Obtains a smaller model with comparable performance.
- **Maintained Accuracy**: When done correctly, the distilled model retains most of the accuracy.

### Cons:

- **Training Complexity**: Requires a two-step process: training the teacher and then the student.

### Applicability to BERT:

Distillation can be an effective approach for BERT. Given its depth, a shallower model can be trained to mimic BERT's performance, especially if we're focused on a specific domain like financial sentiment analysis.

## Our distillation methodology

Our initial experimentation with the 4 datasets of different levels of annotation consensus can be found [here.](experiment-bert.md) We continued on from this however to dig deeper by running the fine-tuning for more epochs and seeing which models had the best validation F1 scores, which we added to be calculated for every epoch.

Our results were surprising and changed our view yet again, as the `75Agree` dataset, which indicated 75% consensus, now appeared to give the best results by far in terms of both accuracy and f1.

![](../img/experiment-results-20.jpg)

## First, we fine-tuned BERT with Model Checkpointing and F1 Evaluation using a different dataset and for 30 epochs

The main changes we implemented here involved calculating the F1 score at the end of each training epoch, and saving the model that achieves the best F1 score on the validation data. This well-performing model is subsequently exploited to evaluate its performance on unseen test data.

## Methodology

**Step 1:** Login into the Weights & Biases platform to track the experiment metrics.

**Step 2:** Load the pre-trained BERT sequence classification model which is designed to classify inputs into one of the three labels.

**Step 3:** Defined the loss function as `Sparse Categorical Crossentropy` loss in this case. Also, configure the optimizer `Adam` with a learning rate schedule.

**Step 4:** Initialize the Weights & Biases project to monitor experiment metrics. Set up the custom `F1_Evaluation` Callback which saves the model whenever there is an improvement in the F1 Score.

**Step 5:** Invoke the model training over 30 epochs, incorporating the callbacks to log metrics to Weights & Biases, and perform custom F1 evaluation and model checkpointing. This is an increase to the 10 we had originally done and even the 20 we did later. Through model checkpointing this was a convenient way to find our most performant model that wasn't overfitting.

**Step 6:** Post training, utilize the plot function defined to visualize the trend of loss, accuracy, and F1 score on the training and the validation data.

**Step 7:** Load into memory the trained model saved during the F1 Evaluation. Disable further training of this model to evaluate its performance as is on the test dataset.

**Step 8:** Predict labels for the test data with this model. Obtain a comprehensive classification report with precision, recall, f1-score, and support.

**Step 9:** Log the F1 score achieved on the test dataset into the Weights & Biases dashboard. 

## Hyperparameters

- **Learning Rate Schedule:** An initial learning rate of `3e-5`, which gradually decays as per an exponential decay schedule with decay steps set to `10000` and decay rate set to `0.9`.
- **Batch Size:** Set to `8` for both validation and training datasets.
- **Epochs:** The model is trained over `30` epochs.
- **Interval for F1 Evaluation:** F1 score is calculated at the end of each epoch, thus, the interval is set to `1`.

In this particular run, we reached an F1 of 0.87 and an accuracy of 0.8655 at epoch 24 (the `val_f1_score` was saved in reference to `step` but this can be seen from the `val_accuracy` and `val_loss plots`. This is a pretty good result and better than our previous best of about .84 using the `66Agree` dataset.

Since the model was checkpointed upon reaching its best f1 score at epoch 24, it didn't affect it to continue the training for visualization purposes.

The full training can be seen in the [75Agree_balanced_30_checkpointed.ipynb](../notebooks/BERT_fine-tune_financials_balanced/75Agree_balanced_30_checkpointed.ipynb) notebook.

![](../img/experiment-results-30.jpg)