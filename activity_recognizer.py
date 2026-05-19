# this program recognizes activities
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

from feature_extraction import extract_features
from dataset_loader import load_dataset

# main machine learning logic
# handles training and realtime activity prediction
class ActivityRecognizer:
    def __init__(self):
        self.model = None
        self.labels = None

    def train(self):
        # load all csv files from data folder
        data, labels = load_dataset("data")
        print(f"Loaded {len(data)} recordings")

        X = []
        for frame in data:
            X.append(extract_features(frame))

        self.labels = sorted(list(set(labels)))

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            labels,
            test_size=0.2,
            random_state=42,
            stratify=labels
        )

        # after comparing different kernels,
        # rbf gave the most stable results for our data
        self.model = make_pipeline(
            StandardScaler(),
            SVC(kernel="linear")
        )

        self.model.fit(X_train, y_train)

        prediction = self.model.predict(X_test)
        self.accuracy = accuracy_score(y_test, prediction)
        print(f"Classifier accuracy: {self.accuracy:.2f}")

    def predict_activity(self, frame):
        features = extract_features(frame)
        return self.model.predict([features])[0]