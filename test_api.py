import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# We use the 'v1' stable endpoint, not 'v1beta'
url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"

headers = {'Content-Type': 'application/json'}
data = {
    "contents": [{"parts": [{"text": "Is the API working? Reply with 'YES'"}]}]
}

try:
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    
    if response.status_code == 200:
        print("--- API TEST RESULT ---")
        print(result['candidates'][0]['content']['parts'][0]['text'])
        print("-----------------------")
    else:
        print(f"API TEST FAILED: {result}")
except Exception as e:
    print(f"CONNECTION ERROR: {e}")