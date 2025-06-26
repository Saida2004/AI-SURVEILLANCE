import cv2
import numpy as np
import torch
import sounddevice as sd
import queue
from scream_detector import is_scream
from alert_utils import send_alert

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5n')
PERSON_CLASS_ID = 0

# Global flag
monitoring = True
audio_buffer = queue.Queue(maxsize=5)

def audio_callback(indata, frames, time, status):
    if not audio_buffer.full():
        audio_buffer.put(indata.copy())

def run_live_monitoring():
    global monitoring
    monitoring = True
    cap = cv2.VideoCapture(0)
    stream = sd.InputStream(callback=audio_callback, samplerate=16000, channels=1)
    stream.start()

    alert_sent = False

    while monitoring and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        people = [x for x in results.xyxy[0] if int(x[-1]) == PERSON_CLASS_ID]
        people_count = len(people)

        scream_detected = False
        if not audio_buffer.empty():
            audio_chunk = audio_buffer.get()
            if is_scream(audio_chunk):
                scream_detected = True

        if (people_count >= 3 or scream_detected) and not alert_sent:
            send_alert("Alert: Crowd or Scream Detected (Live Monitoring)")
            alert_sent = True

        cv2.putText(frame, f"People: {people_count}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Live Monitoring", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    stream.stop()
    stream.close()
    cv2.destroyAllWindows()
    print("Monitoring stopped.")

def stop_monitoring():
    global monitoring
    monitoring = False
