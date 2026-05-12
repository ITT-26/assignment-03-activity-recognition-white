import os
import sys
import signal
import csv
import time
import pyglet
from pyglet import window, text
from pyglet import clock
from datetime import datetime
from DIPPID import SensorUDP

# Constants
PORT = 5700
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
RECORD_TIME_SEC = 10.0
STUDENT_NAME = "Daniel"
ACTIVITIES = ['running', 'rowing', 'lifting', 'jumpingjacks']
RATES_HZ = [20, 100]
PLACEMENTS = ['hand', 'pocket']
UI_UPDATE_RATE_HZ = 30

sensor = SensorUDP(PORT)
win = window.Window(WINDOW_WIDTH, WINDOW_HEIGHT, caption="Data Gatherer")

# UI State variables 
# 1) Activity
cur_activity_idx = 0

# 2) Sample Rate
cur_rate_idx = 0

# 3) Placement
cur_placement_idx = 0

# 4) State
recording_requested = False
is_recording = False
is_auto_record = False
is_aborted = False
record_start_time = 0
data_rows = []

is_waiting = False
wait_start_time = 0
wait_duration = 0
auto_record_count = 0

# Selected config parameter to modify
# 0 = Activity, 1 = Sample Rate, 2 = Placement, 3 = Auto Record
tgt_config = 0

# Pyglet texts
lbl_status = text.Label('Status: IDLE', font_size=20, x=50, y=500, color=(255,255,255,255))
lbl_config = text.Label('', font_size=16, x=50, y=450, color=(200,200,255,255))
lbl_hint = text.Label('[Btn 1: Next Opt] [Btn 2: Change Val] [Btn 3: Start] [Btn 4: Stop]', x=50, y=100)
lbl_acc = text.Label('Acc: -', x=50, y=300)
lbl_gyro = text.Label('Gyro: -', x=50, y=250)

last_btn1 = 0
def btn1_press(data):
    """Cycle which setting we are changing.(ai generated feature)"""
    global last_btn1, tgt_config
    val = int(data)
    if val == 1 and last_btn1 == 0 and not is_recording:
        tgt_config = (tgt_config + 1) % 4
    last_btn1 = val

last_btn2 = 0
def btn2_press(data):
    """Change the currently selected setting's value.(ai generated feature)"""
    global last_btn2, cur_activity_idx, cur_rate_idx, cur_placement_idx, is_auto_record
    val = int(data)
    if val == 1 and last_btn2 == 0 and not is_recording:
        if tgt_config == 0:
            cur_activity_idx = (cur_activity_idx + 1) % len(ACTIVITIES)
        elif tgt_config == 1:
            cur_rate_idx = (cur_rate_idx + 1) % len(RATES_HZ)
        elif tgt_config == 2:
            cur_placement_idx = (cur_placement_idx + 1) % len(PLACEMENTS)
        elif tgt_config == 3:
            is_auto_record = not is_auto_record
    last_btn2 = val

def start_recording(dt=None):
    global is_recording, record_start_time, data_rows, is_aborted
    is_recording = True
    is_aborted = False
    record_start_time = time.time()
    data_rows = []
    
    # Schedule data sampling at the desired rate
    freq = RATES_HZ[cur_rate_idx]
    clock.schedule_interval(sample_sensor, 1.0 / freq)
    
def stop_recording():
    global is_recording, is_auto_record, is_waiting, wait_start_time, wait_duration, auto_record_count
    if not is_recording: return
    is_recording = False
    
    # stop sampling
    clock.unschedule(sample_sensor)
    
    if is_aborted:
        return
        
    # Save to CSV
    activity = ACTIVITIES[cur_activity_idx]
    rate = RATES_HZ[cur_rate_idx]
    placement = PLACEMENTS[cur_placement_idx]
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.join(script_dir, "data")
    os.makedirs(dir_path, exist_ok=True)
    
    # Dynamically find the next available ID for this configuration (ai generated feature)
    idx = 1
    while True:
        filename = f"{STUDENT_NAME}-{activity}-{rate}Hz-{placement}-{idx}.csv"
        path = os.path.join(dir_path, filename)
        if not os.path.exists(path):
            break
        idx += 1
        
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        # Format: id,timestamp,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z
        writer.writerow(["id", "timestamp", "acc_x", "acc_y", "acc_z", "gyro_x", "gyro_y", "gyro_z"])
        writer.writerows(data_rows)

    if is_auto_record:
        auto_record_count += 1
        
        if auto_record_count >= 10:
            # Stop auto-recording after 10 loops
            is_auto_record = False
            auto_record_count = 0
            is_waiting = False
        else:
            is_waiting = True
            wait_start_time = time.time()
            wait_duration = 5.0


last_btn3 = 0
def btn3_press(data):
    """Start recording."""
    global last_btn3, recording_requested, is_waiting, wait_start_time, wait_duration, auto_record_count
    val = int(data)
    if val == 1 and last_btn3 == 0 and not is_recording and not is_waiting:
        is_waiting = True
        wait_start_time = time.time()
        wait_duration = 20.0
        auto_record_count = 0
    last_btn3 = val

last_btn4 = 0
def btn4_press(data):
    """Stop recording manually."""
    global last_btn4, recording_requested, is_aborted, is_waiting
    val = int(data)
    if val == 1 and last_btn4 == 0:
        if is_recording:
            is_aborted = True
            recording_requested = False
        elif is_waiting:
            is_waiting = False
    last_btn4 = val

sensor.register_callback('button_1', btn1_press)
sensor.register_callback('button_2', btn2_press)
sensor.register_callback('button_3', btn3_press)
sensor.register_callback('button_4', btn4_press)

def sample_sensor(dt):
    """Source: Polling sensor adapted from sample-code/demo_device/demo_polling.py"""
    global is_recording, recording_requested, record_start_time
    if not is_recording:
        return
        
    elapsed = time.time() - record_start_time
    if elapsed >= RECORD_TIME_SEC:
        recording_requested = False
        return
        
    acc = sensor.get_value('accelerometer') or {'x':0, 'y':0, 'z':0}
    gyro = sensor.get_value('gyroscope') or {'x':0, 'y':0, 'z':0}
    
    # id,timestamp,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z
    row_id = len(data_rows) + 1
    tstamp = time.time()
    data_rows.append([
        row_id, tstamp, 
        acc.get('x',0), acc.get('y',0), acc.get('z',0),
        gyro.get('x',0), gyro.get('y',0), gyro.get('z',0)
    ])

def update_ui(dt): #(ai generated feature)
    global is_recording, recording_requested, is_waiting
    
    if is_waiting:
        elapsed_wait = time.time() - wait_start_time
        if elapsed_wait >= wait_duration:
            is_waiting = False
            recording_requested = True

    # Check if a state change was requested by the background thread
    if recording_requested and not is_recording:
        start_recording()
    elif not recording_requested and is_recording:
        stop_recording()
        
    if is_waiting:
        rem = max(0, wait_duration - (time.time() - wait_start_time))
        lbl_status.text = f"Status: WAITING ({rem:.1f} s)"
    else:
        lbl_status.text = f"Status: {'RECORDING' if is_recording else 'IDLE'}"
        if is_recording:
            elapsed = time.time() - record_start_time
            lbl_status.text += f" ({elapsed:.1f}/{RECORD_TIME_SEC} s)"
    
    c_act = ACTIVITIES[cur_activity_idx]
    c_rate = RATES_HZ[cur_rate_idx]
    c_pos = PLACEMENTS[cur_placement_idx]
    
    sel = [" ", " ", " ", " "]
    sel[tgt_config] = ">"
    
    lbl_config.text = f"{sel[0]} Activity: {c_act} | {sel[1]} Rate: {c_rate}Hz | {sel[2]} Position: {c_pos} | {sel[3]} Auto: {is_auto_record}"

    # show realtime sensor values
    acc = sensor.get_value('accelerometer')
    if acc: lbl_acc.text = f"Acc: {acc.get('x',0):.2f}, {acc.get('y',0):.2f}, {acc.get('z',0):.2f}"
    
    gyro = sensor.get_value('gyroscope')
    if gyro: lbl_gyro.text = f"Gyro: {gyro.get('x',0):.2f}, {gyro.get('y',0):.2f}, {gyro.get('z',0):.2f}"

clock.schedule_interval(update_ui, 1.0 / UI_UPDATE_RATE_HZ)

@win.event
def on_draw():
    win.clear()
    lbl_status.draw()
    lbl_config.draw()
    lbl_hint.draw()
    lbl_acc.draw()
    lbl_gyro.draw()

@win.event
def on_close():
    on_shutdown()

has_shutdown = False
def on_shutdown(*args): #(ai generated feature)
    global has_shutdown
    if has_shutdown:
        return
    has_shutdown = True
    
    print(" Shutting down...")
    try:
        sensor.disconnect()
    except ValueError:
        # Sensor might already be disconnected
        pass
        
    pyglet.app.exit()
    sys.exit(0)

# Catch Ctrl+C
signal.signal(signal.SIGINT, on_shutdown)

# Source: standard pyglet run loop
if __name__ == '__main__':
    try:
        pyglet.app.run()
    finally:
        on_shutdown()

