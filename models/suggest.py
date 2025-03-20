import requests
import os
import json
import boto3
_MODEL = None
_MODEL_PATH = None

BEDROCK_REGION = None
BEDROCK_ACCESS_KEY_ID = None
BEDROCK_SECRET_ACCESS_KEY = None
BEDROCK_SUGGEST_MODEL_ID = None

SYSTEM_PROMPT = "You are an expert proficient in both Traditional Chinese and English. Provide the user with a concise and precise solution based on the text, disregarding any 'Issue ID' mentioned. If the text does not allow identification of an issue or a practical suggestion cannot be offered, respond solely with 'No suggestion' in English or '沒有建議' in Traditional Chinese. Do not include your reasoning or thought process. Limit responses to 600 tokens. If the text includes Chinese, reply in Traditional Chinese, converting any Simplified Chinese to Traditional Chinese before generating the response. Do not append any formatting tags, such as '</end-of-sentence>', to the output."

def init():
    global _MODEL
    global _MODEL_PATH
    _MODEL_PATH = os.getenv('SUGGEST_MODEL_PATH')
    _MODEL = os.getenv('SUGGEST_MODEL')
    global BEDROCK_REGION
    global BEDROCK_ACCESS_KEY_ID
    global BEDROCK_SECRET_ACCESS_KEY
    global BEDROCK_SUGGEST_MODEL_ID
    BEDROCK_REGION = os.getenv('BEDROCK_REGION')
    BEDROCK_ACCESS_KEY_ID = os.getenv('BEDROCK_ACCESS_KEY_ID')
    BEDROCK_SECRET_ACCESS_KEY = os.getenv('BEDROCK_SECRET_ACCESS_KEY')
    BEDROCK_SUGGEST_MODEL_ID = os.getenv('BEDROCK_SUGGEST_MODEL_ID')



def get_suggestion(text):
    payload = {
        "model": _MODEL,
        "messages":[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
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


def get_suggestion_bedrock(text):
    client = boto3.client(
    service_name="bedrock-runtime",
    region_name=BEDROCK_REGION,
    aws_access_key_id=BEDROCK_ACCESS_KEY_ID,
    aws_secret_access_key=BEDROCK_SECRET_ACCESS_KEY,)
    formatted_prompt = f"""
    <begin_of_sentence><System>{SYSTEM_PROMPT}</end_of_sentence>\n
    <begin_of_sentence><User>{text}<Assistant>\n
    
    """

    body = json.dumps({
        "prompt": formatted_prompt,
        "max_tokens": 600,
        "temperature": 0.4,
        "top_p": 0.9,
    })
    response = client.invoke_model(modelId=BEDROCK_SUGGEST_MODEL_ID, body=body)

    # Read the response body.
    model_response = json.loads(response["body"].read())
    
    # Extract choices.
    choices = model_response["choices"]
    return choices[0]['text']
