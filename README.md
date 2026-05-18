# Assignment 03 - Activity Recognition

## Overview

This project implements a real-time activity recognition system using sensor data from the DIPPID application and a machine learning classifier based on scikit-learn.

The application predicts activities continuously and visualizes the prediction with pyglet.

## Important Files

### `gather_data.py`

Records accelerometer and gyroscope data from DIPPID and stores recordings as CSV files.

### `activity_recognizer.py`

Handles:

* loading datasets
* feature extraction
* train/test split
* training the SVM classifier
* activity prediction

### `feature_extraction.py`

Extracts statistical features from sensor data.

The following features are used:

* mean
* standard deviation
* minimum
* maximum

Using statistical features produced more stable predictions than using raw sensor values directly.

### `dataset_loader.py`

Loads all CSV recordings recursively from the data directory.

### `fitness_trainer.py`

Main application.

This file:

* trains the classifier at startup
* receives real-time DIPPID sensor data
* continuously predicts activities
* updates the pyglet UI

### `evaluation.py`

Used to compare different kernel functions and evaluate classifier performance.

## Classifier Evaluation

Different SVM kernels were tested:

```text id="6d40v6"
linear 0.76
poly   0.63
rbf    0.73
```

The linear kernel achieved the best overall accuracy and was selected for the final application.

The polynomial kernel appeared to overfit the training data and produced the lowest accuracy.

## Pre-processing

Raw sensor values resulted in unstable predictions because of noisy motion data.

Extracting statistical features improved:

* prediction stability
* overall accuracy
* realtime prediction consistency

## Realtime Prediction

The application continuously receives accelerometer and gyroscope data from the DIPPID device.

Sensor values are temporarily stored inside a rolling buffer before prediction.

This prevents predictions from changing too rapidly and improves classifier stability.
