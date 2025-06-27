from vosk import Model, KaldiRecognizer
import pyaudio
import requests
import json
import threading

url = "http://localhost:11434/api/generate"

headers = {
    "Content-Type": "application/json"
}

AI_SETTINGS = '''
You are a kind friend for a user. Answer only in Russian.
Now you need to answer to user.
Here's what user said:
'''

model = Model("vosk-model-small-ru-0.22")
rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()
print("Available input devices:\n")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info["maxInputChannels"] > 0:
        print(f"Index {i}: {info['name']} (Channels: {info['maxInputChannels']})")
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=2048, input_device_index=4)
stream.start_stream()

def ask_ai(text: str):
    responses = requests.post(url, headers=headers, data=json.dumps({"model": "llama3", "prompt": text, "stream": True}))
    responses = responses.text.splitlines()
    response = ""
    for line in responses:
        response = response + json.loads(line)['response']
    return response

def respond_async(text):
    def worker():
        print("Answer:", ask_ai(AI_SETTINGS + text))
    threading.Thread(target=worker).start()

while True:
    data = stream.read(4000)
    if rec.AcceptWaveform(data):
        res = json.loads(rec.Result())['text']
        if not res:
            continue
        print("You said:", res)
        respond_async(res)