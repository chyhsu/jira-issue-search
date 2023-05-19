import os
import pandas as pd
import openai

openai.api_key = os.getenv('OPENAI_API_KEY')


def document(summary, description):
    text = f"the issue's summary is {summary} and description is {description}"
    return text


def get_embedding(text):
    result = openai.Embedding.create(
       model='text-embedding-ada-002',
       input=text 
    )
    return result['data'][0]['embedding']


if __name__ == '__main__':
    df = pd.read_csv('jira.csv')
    df['document'] = df.apply(
        lambda df: document(
            df['summary'],
            df['description']
        ), axis=1)
    df['embedding'] = df['document'].apply(get_embedding)
    df.to_csv('jira_with_vector.csv', index=False, header=True)
