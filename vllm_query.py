import sys

import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


url = sys.argv[1]
model_name = sys.argv[2]


# Your vLLM endpoint and model name
url = f"http://{url}/v1/chat/completions"

headers = {
    "Content-Type": "application/json"
}

payload = {
    "model": model_name,
    "messages": [
        {
            "role": "user",
            "content": "Oracle oci es un..."
        }
    ],
    "stream": True,
    "max_tokens": 1000,
    "temperature": 0.7,
    "top_p": 1.0,
    "n": 1
}

def stream_completion_response():
    # assuming payload looks something like:
    # payload = {
    #   "model": "text-davinci-003",
    #   "prompt": "Explain the benefits of Kubernetes in bullet points:",
    #   "max_tokens": 150,
    #   "temperature": 0.5,
    #   "stream": True
    # }
    with requests.post(url, headers=headers, json=payload, stream=True, verify=False) as response:
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            # OpenAI prepends each chunk with "data: "
            if line.startswith("data: "):
                line = line[len("data: "):]

            # the API sends a final data: [DONE] line when complete
            if line.strip() == "[DONE]":
                break

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            # extract the text for this chunk
            chunk_text = data["choices"][0].get("text")
            if chunk_text:
                print(chunk_text, end="", flush=True)

def stream_chat_response():
    with requests.post(url, headers=headers, data=json.dumps(payload), stream=True, verify=False) as response:
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                try:
                    data = json.loads(line[len("data: "):])
                    delta = data["choices"][0]["delta"]
                    content = delta.get("content")
                    if content:
                        print(content, end='', flush=True)
                except json.JSONDecodeError:
                    continue  # Skip bad chunks
        print()  # Newline after completion

if __name__ == "__main__":
    #stream_completion_response()
    stream_chat_response()