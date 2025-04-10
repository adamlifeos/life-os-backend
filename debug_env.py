import os
from dotenv import load_dotenv

print("🐍 Script started")

# Load the .env file
dotenv_loaded = load_dotenv()
print("📄 .env loaded:", dotenv_loaded)

# Show current working directory
print("📁 Current directory:", os.getcwd())

# Confirm if .env file exists
env_path = os.path.join(os.getcwd(), ".env")
print("🔎 .env file exists:", os.path.exists(env_path))

# Print raw OPENAI_API_KEY
api_key = os.getenv("OPENAI_API_KEY")
print("🔑 OPENAI_API_KEY:", api_key if api_key else "❌ NOT FOUND")