import requests
import os
import json
_MODEL = None
_MODEL_PATH = None

def init():
    global _MODEL
    global _MODEL_PATH
    _MODEL_PATH = os.getenv('SUGGEST_MODEL_PATH')
    _MODEL = os.getenv('SUGGEST_MODEL')


def get_suggestion(text):
    payload = {
        "model": _MODEL,
        "messages":[
            {
                "role": "system",
                "content": "You are an expert understanding both chinese and english and suggest user concise and precise solution for his issue. Give suggestion for issue according to the text. If you can'tidentify the issue according to the text, you should just say 'No suggestion'. Your response should not exceed 600 tokens. If the text contains Chinese, please answer in Traditional Chinese. Ensure no Simplified Chinese is used, and convert all Simplified Chinese to Traditional Chinese before automatic generation." 
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "stream": False
    }

    # Send POST request to Ollama API
    response = requests.post(_MODEL_PATH, json=payload)
    response.raise_for_status()  # Raise an error for bad status codes
    response_json = json.loads(response.text)
    return response_json['message']['content'] 


