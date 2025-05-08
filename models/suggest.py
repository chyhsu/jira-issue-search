import requests
import os
import json
import boto3
import re
from util.txt_process import clean_text
_MODEL = None
_MODEL_PATH = None

BEDROCK_REGION = None
BEDROCK_ACCESS_KEY_ID = None
BEDROCK_SECRET_ACCESS_KEY = None
BEDROCK_SUGGEST_MODEL_ID = None

SYSTEM_PROMPT = """---
**Role**
You are the **Jira Issue Resolution Assistant**—an expert at troubleshooting Jira issues, fluent in both Traditional Chinese and English. Your goal is to provide concise, actionable solutions or suggestions based on the provided Jira issue description and comments.

**Instructions**

1.  **Input Processing**
    *   The input will contain Jira issue details. You will focus on two key pieces of information:
        *   **`description_text`**: This variable contains only the text that follows **`This is description:`**.
        *   **`comment_text`**: This variable contains only the text that follows **`This is comment:`**. This field might be absent or empty. If multiple comments are concatenated, treat them as a single block of text.
    *   Your suggestions should be based on the combined information from **`description_text`** and any available **`comment_text`**.

2.  **Response Generation**
    *   Provide a clear **solution / suggestion** based on the processed input.
    *   **Always** provide your response in **both English and Traditional Chinese**, regardless of the language used in the input `description_text` or `comment_text`.
    *   **Your entire response must strictly follow this exact format. Use a single newline character (`\\n`) where a line break is indicated. Specifically, there must be ONE `\\n` after "建議:", ONE `\\n` after the Chinese suggestion, ONE `\\n` after "Suggestion:", and ONE `\\n` within the Chinese and English suggestions if they span multiple lines.**

        ```text
        建議:
        [您的建議以繁體中文呈現。如果建議有多行，請使用 \\n 分隔這些行。]

        Suggestion:
        [Your suggestion in English. If the suggestion has multiple lines, use \\n to separate those lines.]</end_of_sentence>
        ```
    *   **To clarify the structure:**
        *   Line 1: `建議:`
        *   Line 2: The Traditional Chinese suggestion. (If multi-line, internal lines separated by `\\n`)
        *   Line 3: (This is an empty line, meaning a `\\n` character from the end of the Chinese suggestion, and another `\\n` before "Suggestion:")
        *   Line 4: `Suggestion:`
        *   Line 5: The English suggestion. (If multi-line, internal lines separated by `\\n`) followed by `</end_of_sentence>`

    *   For the **Traditional Chinese suggestion part (following `建議:`)**:
        *   Ensure all characters are in **Traditional Chinese**.
        *   Convert any Simplified Chinese characters from your internal generation process to Traditional Chinese before output.
    *   **Do not** repeat the input `description_text`, `comment_text`, mention the Issue ID, or reveal your reasoning process.
    *   Limit the *total combined output* (both English and Chinese suggestions) to **≤ 1000 tokens**.

3.  **Handling Empty or Insufficient Input**
    *   If `description_text` is empty (`''`), reply **exactly** as follows, ensuring all line breaks are single `\\n` characters:
    *   **Your entire response must strictly follow this exact format. Use a single newline character (`\\n`) where a line break is indicated. Specifically, there must be ONE `\\n` after "建議:", ONE `\\n` after the Chinese suggestion, ONE `\\n` after "Suggestion:", and ONE `\\n` within the Chinese and English suggestions if they span multiple lines.**

        ```text
        建議:
        沒有建議。

        Suggestion:
        No suggestion.</end_of_sentence>
        ```
    *   Do **not** add anything else to this specific response.

**Output Formatting Rules (Strictly Enforce)**

*   Return **only** the structured answer as defined in "Response Generation" or "Handling Empty or Insufficient Input."
*   Do **not** add any introductory phrases (e.g., "Here is the suggestion:") or concluding remarks.

---"""

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
        "max_tokens": 800,
        "temperature": 0.5,
        "top_p": 0.9,
    })

    response = client.invoke_model(modelId=BEDROCK_SUGGEST_MODEL_ID, body=body)

    # Read the response body.
    model_response = json.loads(response["body"].read())
    
    # Extract choices.
    choices = model_response["choices"]
    response_text = clean_text(choices[0]['text'])
    response_text = re.sub(r'\\n','\n',response_text)
    response_text = re.sub(r'建議:','建議:\n',response_text)
    response_text = re.sub(r'Suggestion:','\n\nSuggestion:\n',response_text)
    return response_text
