# test_setup.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

print("Testing environment setup...")
print(f"SECRET_KEY loaded: {'✅' if os.getenv('SECRET_KEY') else '❌'}")
print(f"GEMINI_API_KEY loaded: {'✅' if os.getenv('GEMINI_API_KEY') else '❌'}")

if os.getenv('GEMINI_API_KEY'):
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello!")
        print("✅ Gemini API working!")
    except Exception as e:
        print(f"❌ Gemini API error: {e}")