from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np

model = WhisperModel("base", device="cuda", compute_type="float16")
buffer = np.zeros((0,))

def callback(indata, frames, time, status):
    global buffer
    buffer = np.concatenate([buffer, indata[:,0]])

sd.InputStream(channels=1, samplerate=16000, callback=callback).start()

while True:
    if len(buffer) >= 16000*3:
        segment = buffer[:16000*3]
        buffer = buffer[16000*1:]  # сдвиг
        segments, _ = model.transcribe(segment, batch_size=1)
        for seg in segments:
            print(seg.text, end="", flush=True)
