import cv2
import numpy as np
from scipy.signal import butter, filtfilt
from scipy.fft import fft

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# =========================
# 🎯 Stable signal extraction (NO tracker drift)
# =========================
def extract_signal(frames):
    signal = []
    bbox = None

    for i, frame in enumerate(frames):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 🔥 Detect every 8 frames (balance stability + speed)
        if i % 8 == 0 or bbox is None:
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) == 1:
                bbox = faces[0]
            else:
                continue

        x, y, w, h = bbox

        # Forehead ROI (most stable)
        roi = frame[y:y + h // 3, x:x + w]

        if roi.size == 0:
            continue

        green = roi[:, :, 1].astype(np.float32)

        # Normalize
        green = (green - np.mean(green)) / (np.std(green) + 1e-6)

        signal.append(np.mean(green))

    return np.array(signal)


# =========================
# 🔧 Bandpass
# =========================
def bandpass(signal, fps, low, high):
    if len(signal) < fps:
        return signal

    nyq = fps / 2
    b, a = butter(3, [low/nyq, high/nyq], btype='band')
    return filtfilt(b, a, signal)


# =========================
# ❤️ BPM
# =========================
def compute_bpm(signal, fps):
    signal = signal - np.mean(signal)

    # 🔥 tighter band → less noise
    signal = bandpass(signal, fps, 0.9, 2.2)

    if len(signal) == 0:
        return 0

    fft_vals = np.abs(fft(signal))
    freqs = np.fft.fftfreq(len(signal), d=1/fps)

    mask = (freqs > 0.9) & (freqs < 2.2)
    freqs = freqs[mask]
    fft_vals = fft_vals[mask]

    if len(freqs) == 0:
        return 0

    return int(freqs[np.argmax(fft_vals)] * 60)


# =========================
# 🫁 Respiration
# =========================
def compute_resp(signal, fps):
    signal = signal - np.mean(signal)
    signal = bandpass(signal, fps, 0.1, 0.4)

    if len(signal) == 0:
        return 0

    fft_vals = np.abs(fft(signal))
    freqs = np.fft.fftfreq(len(signal), d=1/fps)

    mask = (freqs > 0.1) & (freqs < 0.4)
    freqs = freqs[mask]
    fft_vals = fft_vals[mask]

    if len(freqs) == 0:
        return 0

    return int(freqs[np.argmax(fft_vals)] * 60)


def rppg_pipeline(chunk, fps):
    signal = extract_signal(chunk)

    if len(signal) < fps:
        return 0, 0

    return compute_bpm(signal, fps), compute_resp(signal, fps)