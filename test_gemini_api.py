import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_setup():
    """Test Gemini API setup and find available models"""
    print("🔍 Testing Gemini API Setup...")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        print("Please create a .env file with:")
        print("GEMINI_API_KEY=your-actual-api-key-here")
        return
    
    print(f"✅ API Key loaded (length: {len(api_key)})")
    
    # Configure API
    genai.configure(api_key=api_key)
    
    # Test different models
    models_to_test = [
        'gemini-2.5-flash',
        'gemini-2.5-pro', 
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro'  # Old model name
    ]
    
    working_models = []
    
    for model_name in models_to_test:
        print(f"\n🔄 Testing model: {model_name}")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello!")
            print(f"✅ {model_name} - WORKING")
            print(f"   Response: {response.text[:50]}...")
            working_models.append(model_name)
        except Exception as e:
            print(f"❌ {model_name} - FAILED: {str(e)[:100]}...")
    
    print("\n" + "=" * 50)
    print("📊 RESULTS:")
    if working_models:
        print(f"✅ Working models: {', '.join(working_models)}")
        print(f"🎯 Recommended: {working_models[0]}")
    else:
        print("❌ No working models found!")
        print("🔧 Troubleshooting steps:")
        print("1. Check your API key at https://makersuite.google.com/app/apikey")
        print("2. Ensure your API key has Gemini API access")
        print("3. Try creating a new API key")
    
    print("\n🔗 Useful links:")
    print("• Get API key: https://makersuite.google.com/app/apikey")
    print("• Gemini API docs: https://ai.google.dev/gemini-api/docs")

def list_available_models():
    """List all available models from Google AI"""
    try:
        print("\n🔍 Querying available models...")
        models = genai.list_models()
        
        print("📋 Available models:")
        for model in models:
            print(f"  • {model.name}")
            if hasattr(model, 'supported_generation_methods'):
                methods = ', '.join(model.supported_generation_methods)
                print(f"    Methods: {methods}")
    except Exception as e:
        print(f"❌ Failed to list models: {e}")

if __name__ == "__main__":
    test_gemini_setup()
    list_available_models()
    
    print("\n🚀 If you see working models above, your Flask app should work!")
    print("Run: python app.py")