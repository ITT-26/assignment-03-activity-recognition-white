from collections import deque
import pandas as pd
import time

# stores realtime sensor data temporarily
# provides rolling sensor windows for prediction

class LiveDataBuffer:
    def __init__(self, max_samples=100):
        self.max_samples = max_samples

        self.rows = deque(maxlen=max_samples)

    def add_sensor_data(self, acc, gyro):
        self.rows.append({
            "timestamp": time.time(),
            "acc_x": acc.get("x", 0),
            "acc_y": acc.get("y", 0),
            "acc_z": acc.get("z", 0),
            "gyro_x": gyro.get("x", 0),
            "gyro_y": gyro.get("y", 0),
            "gyro_z": gyro.get("z", 0)
        })

    def is_ready(self):
        return len(self.rows) >= self.max_samples

    def to_dataframe(self):
        return pd.DataFrame(list(self.rows))