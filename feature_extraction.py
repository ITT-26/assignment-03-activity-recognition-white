import numpy as np

# simple statistical features
# idea inspired by exercise notebook examples
# using mean/std instead of raw sensor stream
# reduces noise and gives fixed feature size

def extract_features(frame):
    features = []

    sensor_columns = [
        "acc_x",
        "acc_y",
        "acc_z",
        "gyro_x",
        "gyro_y",
        "gyro_z"
    ]

    for col in sensor_columns:
        values = frame[col].values

        features.append(np.mean(values))
        features.append(np.std(values))
        features.append(np.max(values))
        features.append(np.min(values))

    return features