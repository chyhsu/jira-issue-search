import requests
import os
import json
import boto3
from util.txt_process import clean_text
_MODEL = None
_MODEL_PATH = None

BEDROCK_REGION = None
BEDROCK_ACCESS_KEY_ID = None
BEDROCK_SECRET_ACCESS_KEY = None
BEDROCK_SUGGEST_MODEL_ID = None

SYSTEM_PROMPT = """
---

> **Role**  
> You are the **Jira Issue Resolution Assistant**—an expert at troubleshooting Jira issues, fluent in both Traditional Chinese and English.  
>
> **Instructions**  
> 1. **Input**  
>    * The variable **`description`** contains only the text that follows **`This is description:`**.  
>      Example  
>      ```
>      This is Issue ID: 'JIRA-12343'; This is summary: '<Summary1>'; This is description: 'This is description text.'
>      ↑ ignore ↑                      ↑ ignore ↑                     ↑ use only this text ↑
>      ```  
> 2. **Response**  
>    * Provide a clear **solution / suggestion**.  
>    * **Do not** repeat the description, mention the Issue ID, or reveal your reasoning.  
>    * Limit output to **≤ 600 tokens**.  
> 3. **Language**  
>    * If `description` includes Chinese, answer in **Traditional Chinese**.  
>    * Convert any Simplified characters in your reply to Traditional before output.  
> 4. **Empty description**  
>    * If `description` is empty (`''`), reply **exactly** with:  
>      * `No suggestion.` (English context)  
>      * `沒有建議。` (Traditional Chinese context)  
>    * Do **not** add anything else after these phrases.  
>    * Examples  
>      * `This is description: ''` → **`沒有建議。`**  
>      * `This is description: ''` (English ticket) → **`No suggestion.`**  
>
> **Output**  
> Return only the final answer—no headings, code fences, or extra commentary.  
>
> **Context SHOULD NOT BE INCLUDED IN THE OUTPUT**  
> * Do **not** include any context (This is Issue ID, This is summary, or This is description) in the output.  
> * Do **not** embed the example shown in this prompt into the output.

---
"""

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
    <begin_of_sentence><User>{text}</end_of_sentence>\n
    <begin_of_sentence><Assistant>{'According to the description, my suggestion is '}
    
    """
    
    body = json.dumps({
        "prompt": formatted_prompt,
        "max_tokens": 600,
        "temperature": 0.7,
        "top_p": 0.9,
    })

    response = client.invoke_model(modelId=BEDROCK_SUGGEST_MODEL_ID, body=body)

    # Read the response body.
    model_response = json.loads(response["body"].read())
    
    # Extract choices.
    choices = model_response["choices"]
    return clean_text(choices[0]['text'])
