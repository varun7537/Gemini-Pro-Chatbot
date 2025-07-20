# app.py
from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
import os
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure from environment or use defaults
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("⚠️  WARNING: GEMINI_API_KEY not found in environment variables!")
    print("Please create a .env file with your API key")
    GEMINI_API_KEY = 'YOUR_GEMINI_API_KEY_HERE'  # Fallback

# Available Gemini models (as of 2025)
AVAILABLE_MODELS = [
    'gemini-2.5-flash',      # Fast and efficient 
    'gemini-2.5-pro',        # Most advanced reasoning
    'gemini-1.5-flash',      # Fallback (may not work for new projects)
    'gemini-1.5-pro'         # Fallback (may not work for new projects)
]

def initialize_gemini():
    """Initialize Gemini with the best available model"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY_HERE':
        print("❌ Invalid API key")
        return None, None
    
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Try models in order of preference
    for model_name in AVAILABLE_MODELS:
        try:
            print(f"🔄 Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            # Test the model with a simple query
            test_response = model.generate_content("Hello")
            print(f"✅ Successfully initialized {model_name}")
            return model, model_name
        except Exception as e:
            print(f"❌ Failed to initialize {model_name}: {e}")
            continue
    
    print("❌ No working Gemini models found")
    return None, None

# Initialize the model
model, current_model_name = initialize_gemini()



def initialize_session():
    """Initialize session variables for chat history"""
    if 'chat_history' not in session:
        session['chat_history'] = []
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

@app.route('/')
def home():
    """Render the main chatbot interface"""
    initialize_session()
    return render_template('index.html', model_name=current_model_name)

@app.route('/status')
def status():
    """Get current model status"""
    return jsonify({
        'model_available': model is not None,
        'current_model': current_model_name,
        'api_key_configured': GEMINI_API_KEY != 'YOUR_GEMINI_API_KEY_HERE'
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages and get Gemini response"""
    try:
        initialize_session()
        
        # Check if model is available
        if model is None:
            return jsonify({'error': 'Gemini API not configured. Please check your API key.'}), 500
        
        user_message = request.json.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Generate response using Gemini
        response = model.generate_content(user_message)
        bot_response = response.text
        
        # Create chat entry
        chat_entry = {
            'id': str(uuid.uuid4()),
            'user_message': user_message,
            'bot_response': bot_response,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add to session history
        session['chat_history'].append(chat_entry)
        
        # Keep only last 50 messages to prevent session bloat
        if len(session['chat_history']) > 50:
            session['chat_history'] = session['chat_history'][-50:]
        
        session.modified = True
        
        return jsonify({
            'response': bot_response,
            'timestamp': chat_entry['timestamp'],
            'id': chat_entry['id']
        })
        
    except Exception as e:
        print(f"Error in chat route: {e}")
        return jsonify({'error': f'Error generating response: {str(e)}'}), 500

@app.route('/history')
def get_history():
    """Get chat history for the current session"""
    initialize_session()
    return jsonify({'history': session.get('chat_history', [])})

@app.route('/clear-history', methods=['POST'])
def clear_history():
    """Clear chat history for the current session"""
    session['chat_history'] = []
    session.modified = True
    return jsonify({'message': 'History cleared successfully'})

if __name__ == '__main__':
    print("🚀 Starting Flask Gemini Chatbot...")
    print("📋 Checking configuration...")
    
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not found!")
        print("Please create a .env file with:")
        print("SECRET_KEY=your-secret-key")
        print("GEMINI_API_KEY=your-gemini-api-key")
    else:
        print("✅ Environment variables loaded")
    
    print("🌐 Server starting on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)