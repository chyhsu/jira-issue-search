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

SYSTEM_PROMPT = "You are an expert understanding both chinese and english. You should suggest user a concise and precise solution for his issue, according to the text. If you can't identify the issue or give a practical suggestion according to the text, you should just say 'No suggestion', or in traditional chinese '沒有建議'.Do NOT output your thinking process. Your response should not exceed 400 tokens. If the text contains Chinese, please answer in Traditional Chinese. Ensure no Simplified Chinese is used, and convert all Simplified Chinese to Traditional Chinese before automatic generation."

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
        "max_tokens": 400,
        "temperature": 0.4,
        "top_p": 0.9,
    })
    response = client.invoke_model(modelId=BEDROCK_SUGGEST_MODEL_ID, body=body)

    # Read the response body.
    model_response = json.loads(response["body"].read())
    
    # Extract choices.
    choices = model_response["choices"]
    return choices[0]['text']


def get_suggestion_bedrock_nova(text):
    model_id = "us.amazon.nova-lite-v1:0"
   
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=BEDROCK_REGION,
        aws_access_key_id=BEDROCK_ACCESS_KEY_ID,
        aws_secret_access_key=BEDROCK_SECRET_ACCESS_KEY,
    )

    request_body = {
        "messages": [{"role":"assistant","content":[{"text":SYSTEM_PROMPT}],"role": "user", "content": [{"text": text}]}]
    }
    
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=json.dumps(request_body),
        contentType="application/json",
    )
    response_body = json.loads(response.get("body").read())
    return response_body['output']['message']['content'][0]['text']


