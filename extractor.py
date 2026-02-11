import os, json, re, requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def extract_info(user_message):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"""
     You are a professional crisis translator. 
    Analyze this message: "{user_message}"
    This message might be in Hinglish (Hindi written in English script) or another local language.
    Extract ONLY the following as JSON:
    1. Identify the language (e.g., Hindi, Spanish, French, German, Arabic).
    2. Translate it COMPLETELY into English.
    3. Extract: item, location, contact, urgency (1-10)
    
    Return ONLY a JSON object:
    {{
    -"language": "Language Name",
    - "translation": "English Translation",
    - item: (The specific resource needed)
    - location: (ONLY the place name. Do not include 'call me' or phone numbers here)
    - contact: (The phone number digits only)
    - urgency: (1-10)
    - translation: (English version)
    }}
 
    """
    
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
        result = response.json()
        
        if 'candidates' in result:
            raw_text = result['candidates'][0]['content']['parts'][0]['text']
            clean_json = re.sub(r'```json|```', '', raw_text).strip()
            return json.loads(clean_json)
        else:
            raise Exception("Quota Full")

    except Exception:
        # --- IMPROVED FALLBACK SCANNER ---
        # 1. Broadened Phone Scanner (detects 7 to 15 digits)
        phone_match = re.search(r'\d{7,15}', user_message)
        contact = phone_match.group() if phone_match else "None Found"
        
        # 2. Clean Location Scanner
        # Looks for words after 'in' or 'at' and stops before 'call', 'my', 'ph'
        loc_match = re.search(r'(?:at|in|near)\s+([^.]+)', user_message, re.IGNORECASE)
        location = "Unknown"
        if loc_match:
            location = loc_match.group(1)
            # Remove "call me" or phone numbers if they leaked into the location
            location = re.split(r'call|ph|my|contact|tel|at', location, flags=re.IGNORECASE)[0].strip()

        return {
            "language": "Detected",
            "translation": user_message,
            "item": "Emergency Resource",
            "location": location,
            "contact": contact,
            "urgency": 5,
            
        }