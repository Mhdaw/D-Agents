import os
import json
import openai
import requests
from smolagents import OpenAIServerModel

base_url = "https://chatapi.akash.network/api/v1"
api_key = "sk-s2Hpm8x0MkhzV743Ecqzqw"
def get_client():

    client = openai.OpenAI(base_url=base_url, api_key=api_key)
    return client

def get_model(model_id: str="nvidia-Llama-3-1-Nemotron-70B-Instruct-HF"):

    client = OpenAIServerModel(
        model_id=model_id,
        api_base=base_url,
        api_key=api_key,
    )
    return client

def test_client(model_id: str="nvidia-Llama-3-1-Nemotron-70B-Instruct-HF"):
    client = get_client()
    completion = client.chat.completions.create(
    model=model_id,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
    )

    return completion.choices[0].message.content