# Optimizing BERT for Financial Sentiment Analysis

The mdoel we chose for fine-tuning and optimization, BERT, especially the `bert-base-uncased` variant, is a commonly used foundation model for NLP tasks. When fine-tuned, it can be a powerful tool for financial sentiment analysis. To deploy BERT in real-world applications, especially on edge devices or under latency constraints, we want to optimize its size and speed. In our project, we tried three main optimization techniques: quantization, pruning, and distillation. It turned out we chose a challenging, complex model to conduct these techniques on.

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

The TensorFlow Model Optimization Toolkit also offers pruning capabilities. But similar to quantization, it is only compatible with Sequential or Functional Keras models rather than Subclassed models, which includes models loaded from Hugging Face's Transformers.

To apply pruning using TF-MOT, the model needs to be wrapped similar to quantization, and the same compatibility issues arose as they did with quantization. Subclassed models like Hugging Face's `bert-base-uncased` don't expose their internal layer structure the way `Sequential` and `Functional` models do, which makes it more challenging for techniques like pruning and quantization.

We could have manually modified the `BERT` model to be a `Functional` model, but that would be quite complicated due to the interdependencies of the layers inside and effectively rebuilding `BERT` from scratch, which would really be taking us far from our original vision of this project.

## 3. Distillation

Distillation, often referred to as "knowledge distillation," is a technique in which a smaller model (the "student") is trained to mimic the behavior of a larger, more complex model (the "teacher"). The main idea is to transfer the "knowledge" from the teacher model to the student model, allowing the student to achieve better performance than if it were trained directly on the data.

Here's a deeper dive into how distillation works, particularly focusing on the loss functions:

## Loss Functions in Distillation:

### 1. Hard Target Loss:

This is the traditional loss used when training neural networks. It computes the difference between the predictions of the student model and the ground truth labels in the dataset.

If $y$ is the ground truth and $\hat{y}_{student}$ is the prediction from the student:

```math
Hard Target Loss = L(y, \hat{y}_{student})
```

For classification tasks, this is usually the cross-entropy loss.

### 2. Soft Target Loss:

This loss computes the difference between the soft predictions (logits or probabilities) of the teacher model and those of the student model. The "soft" predictions are often obtained by raising the temperature of the softmax function used in the final layer of the model.

Given the logits from the teacher $z_{teacher}$ and the logits from the student $z_{student}$, the soft target loss can be expressed as:

```math
Soft Target Loss = L(Softmax(z_{teacher}/T), Softmax(z_{student}/T))
```

Where:
- $T$ is the "temperature" hyperparameter. A value greater than 1 makes the softmax outputs softer (i.e., closer to a uniform distribution), which emphasizes the relationships between classes.

## Combining the Losses:

To train the student model, a weighted combination of the hard target loss and soft target loss is used:

```math
Total Loss = \alpha \times Hard Target Loss + (1-\alpha) \times Soft Target Loss
```

Where:
- \( \alpha \) is a hyperparameter that controls the weighting of the respective losses. $\alpha$ values closer to 1 put a greater emphasis on the hard labels, and $\alpha$ closer to zero emphasize the teacher model's logits.

The soft targets capture the relationships between different classes. In our 3-class classification for financial sentiment (negative, positive, or neutral), if a particular input results in the teacher model assigning high probabilities to class 3 and slightly lower probabilities to classes 1 and 2, this provides more information than simply knowing the ground truth is class 3. The student model learns from this additional information, which helps in its generalization.

### Pros:

- **Compact Model**: Obtains a smaller model with comparable performance.
- **Maintained Accuracy**: When done correctly, the distilled model retains most of the accuracy.

### Cons:

- **Training Complexity**: Requires a two-step process: training the teacher and then the student.

### Applicability to BERT:

Distillation can be an effective approach for BERT. Given its depth, a shallower model can be trained to mimic BERT's performance, especially if we're focused on a specific domain like financial sentiment analysis.

