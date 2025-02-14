import os
import json
import nearai
import openai
import requests
from smolagents import OpenAIServerModel

def get_client():
    hub_url = "https://api.near.ai/v1"

    # Login to NEAR AI Hub using nearai CLI.
    # Read the auth object from ~/.nearai/config.json
    auth = nearai.config.load_config_file()["auth"]
    signature = json.dumps(auth)

    client = openai.OpenAI(base_url=hub_url, api_key=signature)
    return client

def get_model(model_id):
    hub_url = "https://api.near.ai/v1"
    auth = nearai.config.load_config_file()["auth"]
    signature = json.dumps(auth)
    client = OpenAIServerModel(
        model_id=model_id,
        api_base=hub_url,
        api_key=signature,
    )
    return client

def test_client(model_id):
    client = get_client()
    completion = client.chat.completions.create(
    model="fireworks::accounts/fireworks/models/qwen2p5-72b-instruct",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
    )

    return completion.choices[0].message.content