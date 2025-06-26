import numpy as np
import joblib
import librosa
import soundfile as sf

# Load pre-trained models
model = joblib.load('scream_detection_model.pkl')
scaler = joblib.load('scaler.pkl')

def extract_features(audio, sr):
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=41)
    return np.mean(mfcc.T, axis=0).reshape(1, -1)

def is_scream(audio_chunk, sr=16000):
    audio_np = audio_chunk.flatten()
    if len(audio_np) == 0:
        return False
    features = extract_features(audio_np, sr)
    features = scaler.transform(features)
    prediction = model.predict(features)
    return prediction[0] == 1

def is_scream_from_file(filepath):
    audio, sr = sf.read(filepath)
    return is_scream(audio, sr)
