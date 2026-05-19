import pyglet
from pyglet.window import Window
from pyglet import clock
from DIPPID import SensorUDP
from live_data_buffer import LiveDataBuffer

import activity_recognizer as activity
from ui_elements import TrainerUI

# main realtime fitness trainer application
# receives DIPPID data and visualizes predictions

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
PORT = 5700
sensor = SensorUDP(PORT)

window = Window(
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    caption="Fitness Trainer"
)

pyglet.gl.glClearColor(0.92, 0.92, 0.92, 1) # light gray background


recognizer = activity.ActivityRecognizer()
recognizer.train()
buffer = LiveDataBuffer(max_samples=100)

ui = TrainerUI()
ui.accuracy.text = f"Model accuracy: {recognizer.accuracy:.2f}"

def update(dt):

    acc = sensor.get_value("accelerometer")
    gyro = sensor.get_value("gyroscope")

    if not acc or not gyro:
        return

    buffer.add_sensor_data(acc, gyro)

    if not buffer.is_ready():
        return

    frame = buffer.to_dataframe()

    try:
        prediction = recognizer.predict_activity(frame)
        ui.set_activity(prediction)

    except Exception as e:
        print(e)

@window.event
def on_draw():
    window.clear()
    ui.draw()

clock.schedule_interval(update, 1 / 20.0)
if __name__ == "__main__":
    try:
        pyglet.app.run()
    except Exception:
        pass
    finally:
        try:
            sensor.disconnect()
        except ValueError:
            pass
        window.close()
        print(" ...Fitness Trainer exited.")