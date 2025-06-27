import requests
import json

url = "http://localhost:11434/api/generate"

headers = {
    "Content-Type": "application/json"
}

data = {
    "model": "llama3",
    "prompt": "",
    "stream": True,
}

responses = requests.post(
    url,
    data=json.dumps(data)
)

responses = responses.text.splitlines()
response = ""
for line in responses:
    response = response + json.loads(line)['response']
print(response)