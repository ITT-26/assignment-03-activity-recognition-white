import numpy as np

# simple statistical features
# idea inspired by exercise notebook examples
# using mean/std instead of raw sensor stream
# reduces noise and gives fixed feature size

def extract_features(frame, mode="all", sensors="both"):
    features = []

    if sensors == "acc_only":
        sensor_columns = ["acc_x", "acc_y", "acc_z"]
    elif sensors == "gyro_only":
        sensor_columns = ["gyro_x", "gyro_y", "gyro_z"]
    else:
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

        if mode == "mean_only":
            features.append(np.mean(values))
        elif mode == "mean_std":
            features.append(np.mean(values))
            features.append(np.std(values))
        elif mode == "raw": # ai generated feature - using raw values (padded/truncated to fixed length)
            fixed_length = 100
            if len(values) >= fixed_length:
                features.extend(values[:fixed_length])
            else:
                padded = np.zeros(fixed_length)
                padded[:len(values)] = values
                features.extend(padded)
        else: # "all"
            features.append(np.mean(values))
            features.append(np.std(values))
            features.append(np.max(values))
            features.append(np.min(values))

    return features