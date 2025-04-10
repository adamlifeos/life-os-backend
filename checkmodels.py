import os
from dotenv import load_dotenv
from openai import OpenAI

# Load the .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

models = client.models.list()

for model in models.data:
    print(model.id)