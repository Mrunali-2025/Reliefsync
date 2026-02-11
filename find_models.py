import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# This calls the "List Models" tool
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    data = response.json()
    if "models" in data:
        print("--- YOUR AVAILABLE MODELS ---")
        for m in data['models']:
            print(m['name'])
    else:
        print("Could not find any models. Error response:")
        print(data)
except Exception as e:
    print(f"Error: {e}")