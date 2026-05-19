import os
import pandas as pd

# loads all csv recordings from the dataset folders
# prepares recordings for classifier training

def load_dataset(folder):
    data = []
    labels = []

    for root, dirs, files in os.walk(folder):

        for filename in files:

            if not filename.endswith(".csv"):
                continue

            path = os.path.join(root, filename)

            try:
                frame = pd.read_csv(path)
            except Exception:
                continue

            parts = filename.split("-")

            if len(parts) < 5:
                continue

            activity = parts[1]

            data.append(frame)
            labels.append(activity)

    return data, labels