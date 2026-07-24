---
layout: post
slug: federated-learning-explained-simply-with-tensorflow-code
title: "Federated Learning Explained Simply (With TensorFlow Code)"
subtitle: "Train together without sharing raw data—like a group study where everyone keeps their own notes"
author: "Arijit Nandi"
date: "2026-05-09"
read_time: "10 min read"
category: "Federated Learning"
tags: ["Federated Learning", "TensorFlow", "Privacy", "Machine Learning", "Distributed ML"]
image: "assets/images/fl.png"
excerpt: "A friendly introduction to federated learning—what it is, why it matters for privacy, and how to simulate it with plain TensorFlow and Keras."
---

# Federated Learning Explained Simply (With TensorFlow Code)

Imagine ten hospitals each have patient data. They all want a smarter model to help doctors, but **they cannot (and should not) ship patient records to one central server**.  

**Federated learning** is the idea: **each place keeps its own data**, trains a little on that data, and **only shares small updates** (like improved knob-settings for the model). A central coordinator **combines those updates** into one better global model. Nobody had to hand over the raw files.

That is the whole story in one paragraph. The rest is detail.

## Normal training vs federated training

**Classic machine learning (centralized)**  

1. Collect all data in one place.  
2. Train one model on all of it.  

**Federated learning**  

1. Start with one shared model (same architecture everywhere).  
2. Each client (phone, hospital, bank branch…) trains **only on local data** for a short time.  
3. Each client sends **updates** (for example, new weights or gradients)—**not** the raw training rows.  
4. The server **averages** those updates (or uses a similar rule) and sends back an improved global model.  
5. Repeat.

So: **data stays local; knowledge still travels**.

## Why people care

- **Privacy & compliance**: Sensitive data does not need to leave the device or organization.  
- **Less network load**: You move small model updates, not huge databases.  
- **Personalization-friendly**: You can mix a global model with local fine-tuning on each device.

## Federated Averaging (FedAvg) in plain words

The most common starter algorithm is **Federated Averaging**:

1. The server sends the **current global weights** to each client.  
2. Each client trains a few steps on **its own data**.  
3. Each client sends **its new weights** back.  
4. The server computes a **weighted average** of those weights (often weighted by how many examples each client used) and sets that as the new global model.

No magic—mostly **train locally, then average models**.

## Implementing a tiny FedAvg simulation in TensorFlow

Below is a **simulation** on one machine: we **split MNIST** into three fake “clients” and run FedAvg with **TensorFlow and Keras** only. This matches how many tutorials introduce the idea before adding production frameworks.

**What you need**

```bash
pip install tensorflow
```

**Code**

```python
import numpy as np
import tensorflow as tf

# ---- 1. Global model (same architecture every client uses) ----
def create_model():
    return tf.keras.Sequential([
        tf.keras.layers.Input(shape=(784,)),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dense(10, activation="softmax"),
    ])


def dataset_from_images_labels(images, labels, batch_size=32, shuffle=True):
    ds = tf.data.Dataset.from_tensor_slices((images, labels))
    if shuffle:
        ds = ds.shuffle(min(len(images), 1000))
    return ds.batch(batch_size)


# ---- 2. Load data and split into 3 "clients" (non-IID split is optional; here we use simple chunks) ----
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train = x_train.reshape(-1, 784).astype("float32") / 255.0
x_test = x_test.reshape(-1, 784).astype("float32") / 255.0

n_clients = 3
n_samples = len(x_train)
chunk = n_samples // n_clients
client_sets = []
for i in range(n_clients):
    start = i * chunk
    end = (i + 1) * chunk if i < n_clients - 1 else n_samples
    client_sets.append((x_train[start:end], y_train[start:end]))

# ---- 3. Federated averaging loop ----
global_model = create_model()
global_model.compile(
    optimizer=tf.keras.optimizers.SGD(learning_rate=0.1),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

fed_rounds = 5
local_epochs = 1

for r in range(fed_rounds):
    client_weight_lists = []
    client_sample_counts = []

    global_weights = global_model.get_weights()

    for images, labels in client_sets:
        # Local copy starts from global weights
        local_model = create_model()
        local_model.set_weights(global_weights)
        local_model.compile(
            optimizer=tf.keras.optimizers.SGD(learning_rate=0.1),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        local_model.fit(
            dataset_from_images_labels(images, labels),
            epochs=local_epochs,
            verbose=0,
        )
        client_weight_lists.append(local_model.get_weights())
        client_sample_counts.append(len(images))

    # Weighted average by number of samples per client
    total = float(sum(client_sample_counts))
    new_weights = []
    for idx in range(len(client_weight_lists[0])):
        stacked = np.stack([w[idx] for w in client_weight_lists], axis=0)
        weights_for_avg = np.array(client_sample_counts).reshape(-1, *([1] * (stacked.ndim - 1))) / total
        new_weights.append(np.sum(stacked * weights_for_avg, axis=0))

    global_model.set_weights(new_weights)

    loss, acc = global_model.evaluate(
        dataset_from_images_labels(x_test, y_test, shuffle=False),
        verbose=0,
    )
    print(f"Round {r + 1}/{fed_rounds} — global test accuracy: {acc:.4f}")

print("Done.")
```

**What to notice**

- Each “client” only sees **its slice** of MNIST.  
- After each round, **`global_model`** is the **weighted average** of all client models.  
- You can change `n_clients`, `fed_rounds`, and `local_epochs` to see how learning behaves.

This is **not** secure aggregation or real cross-device networking—it is the **core optimization pattern** (local fit + average) that powers many federated systems.

## What about TensorFlow Federated (TFF)?

Google’s **[TensorFlow Federated](https://www.tensorflow.org/federated)** adds proper **federated computations**, simulation datasets, and patterns closer to research and production. For a first project, the snippet above builds intuition; when you outgrow it, `pip install tensorflow-federated` and the official **FedAvg with EMNIST** tutorial are the natural next step.

## Limitations (honest and short)

- **Communication cost**: Many rounds × many clients can mean lots of updates.  
- **Non-IID data**: If each client’s data looks very different, training can get harder; researchers use many tricks.  
- **Privacy**: Averaging weights is **not** the same as formal privacy; for strong guarantees people add noise (**differential privacy**) and other mechanisms.

## Conclusion

**Federated learning** means: **learn from many sources without centralizing their raw data**. The simplest algorithm is **train locally, average models on the server**. The TensorFlow example above shows exactly that loop so you can run it, change it, and connect the code to the story.

If you want to go deeper next: differential privacy in federated settings, personalization (FedPer / fine-tuning), and TensorFlow Federated for scalable simulations.
