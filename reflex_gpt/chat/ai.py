from email.policy import default

from openai import OpenAI
from decouple import config

OPENAI_MODEL="gpt-4o"
OPENAI_KEY=config("OPENAI_KEY", cast=str, default=None)

def get_client():
    return OpenAI(api_key=OPENAI_KEY)

def get_llm_response(gtp_messages):
    client = get_client()
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=gtp_messages
    )
    return completion.choices[0].message.content


