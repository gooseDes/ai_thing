from vosk import Model, KaldiRecognizer
import pyaudio

model = Model("vosk-model-ru-0.42")
rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()
print("Available input devices:\n")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info["maxInputChannels"] > 0:
        print(f"Index {i}: {info['name']} (Channels: {info['maxInputChannels']})")
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000, input_device_index=4)
stream.start_stream()

while True:
    data = stream.read(800)
    if rec.AcceptWaveform(data):
        print("You said:", rec.Result())