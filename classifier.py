import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

# 1. Expanded Training Data
data = [
    ("Need water and food packets", "Food/Water"),
    ("We are starving, need supplies", "Food/Water"),
    ("Looking for drinking water", "Food/Water"),
    ("Urgent medical help needed", "Medical"),
    ("Hospital needs blood donors", "Medical"),
    ("Medicine required for elderly", "Medical"),
    ("House destroyed, need shelter", "Shelter"),
    ("Looking for a place to sleep", "Shelter"),
    ("Emergency camp location?", "Shelter"),
    ("I want to help as a volunteer", "Volunteer"),
    ("Can provide truck for transport", "Volunteer"),
    ("Need oxygen cylinders urgently", "Medical"),
    ("Oxygen needed for patient", "Medical"),
    ("Cylinder O2 required immediately", "Medical"),
    ("Looking for oxygen supply", "Medical"),
    ("Medical kit and oxygen needed", "Medical"),
     ("khana chahiye", "Food/Water"),
    ("paani chahiye", "Food/Water"),
    ("madad chahiye", "Medical"),
    ("khoon ki zarurat hai", "Medical"),
    ("ambulance bulao", "Medical"),
    ("emergency hai", "Medical"),
    ("stuck in flood", "Shelter"),
    ("ghar gir gaya hai", "Shelter"),
    ("hi", "Noise"),
    ("hello", "Noise"),
    ("how are you", "Noise"),
    ("good morning", "Noise"),
    ("test message", "Noise"),
    ("hope you are safe", "Noise"),
    ("just checking in", "Noise"),
    ("hey there", "Noise"),
    ("is anyone active?", "Noise"),
    ("Praying for you", "Noise"),
    ("The weather is bad", "Noise"),
    ("Hello how are you", "Noise"),
    ("Stay safe everyone", "Noise"),
    ("This is a test message", "Noise")
]

df = pd.DataFrame(data, columns=['text', 'category'])

# 2. Improved Pipeline (using n-grams to catch phrases)
model = make_pipeline(
    TfidfVectorizer(ngram_range=(1, 2), stop_words='english'), 
    MultinomialNB(alpha=0.1)
)

model.fit(df['text'], df['category'])

def classify_message(text):
    # Simple Keyword Check (The "Safety Net")
    # If the ML model is unsure, these words force it to be a request
    keywords = ['need', 'urgent', 'help', 'hospital', 'water', 'food', 'medicine', 'shelter', 'blood']
    text_lower = text.lower()
    
    # ML Prediction
    prediction = model.predict([text])[0]
    
    # Logic: If ML says Noise, but the user typed "need" or "help", override it!
    if prediction == "Noise":
        if any(word in text_lower for word in keywords):
            return "General Request" # Force it to be processed
            
    return prediction