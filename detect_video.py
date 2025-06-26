import cv2
import numpy as np
import torch
import tempfile
import moviepy.editor as mp
from scream_detector import is_scream_from_file
from alert_utils import send_alert

model = torch.hub.load('ultralytics/yolov5', 'yolov5n', force_reload=False)
PERSON_CLASS_ID = 0

def process_uploaded_video(video_path):
    cap = cv2.VideoCapture(video_path)
    alert_sent = False
    people_alerted = False
    scream_alerted = False

    try:
        clip = mp.VideoFileClip(video_path)
        if clip.audio is not None:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
                clip.audio.write_audiofile(tmp_audio.name, logger=None)
                if is_scream_from_file(tmp_audio.name):
                    scream_alerted = True
        clip.close()
    except Exception as e:
        print(f"Audio extraction error: {e}")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model(frame_rgb)
        people = [x for x in results.xyxy[0] if int(x[-1]) == PERSON_CLASS_ID]
        if len(people) >= 3:
            people_alerted = True
            break

    cap.release()

    if (scream_alerted or people_alerted) and not alert_sent:
        send_alert("Alert: Crowd or Scream Detected in Uploaded Video")
        alert_sent = True

    return {
        "people_detected": people_alerted,
        "scream_detected": scream_alerted,
        "alert_sent": alert_sent
    }
