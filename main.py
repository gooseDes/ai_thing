from vosk import Model, KaldiRecognizer
import pyaudio
import requests
import json
import threading
import subprocess

url = "http://localhost:11434/api/generate"

headers = {
    "Content-Type": "application/json"
}

VOICE_MODE = False

AI_SETTINGS = '''
You are a kind voice assistant for a user. Answer only in Russian.
Now you need to answer/make what user said. If you think that you need to execute some linux bash command(for example open some app), you can do it by writing "CMD: <command>" in the end of your message. You can execute only linux bash commands.
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
        res = ask_ai(AI_SETTINGS + text)
        print("Answer:", res)
        if 'cmd:' in res.lower():
            cmd = res.split("CMD:")[1].strip()
            print(f"Executing command: {cmd + ' & disown'}")
            process = subprocess.run(cmd, shell=True)
    thread = threading.Thread(target=worker)
    thread.start()
    return thread

while True:
    if not VOICE_MODE:
        text = input("You: ")
        if text.lower() == "exit":
            break
        respond_async(text).join()
        continue
    data = stream.read(2048)
    if rec.AcceptWaveform(data):
        res = json.loads(rec.Result())['text']
        if not res:
            continue
        print("You said:", res)
        respond_async(res)