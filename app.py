from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
import os
from datetime import datetime
import uuid
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in environment variables!")
    print("Please create a .env file with your API key")
    GEMINI_API_KEY = 'YOUR_GEMINI_API_KEY_HERE'

AVAILABLE_MODELS = [
    'gemini-2.5-flash',
    'gemini-2.5-pro',
    'gemini-1.5-flash',
    'gemini-1.5-pro'
]

def initialize_gemini():
    """Initialize Gemini with the best available model"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY_HERE':
        print("Invalid API key")
        return None, None
    
    genai.configure(api_key=GEMINI_API_KEY)
    
    for model_name in AVAILABLE_MODELS:
        try:
            print(f"Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            test_response = model.generate_content("Hello")
            print(f"Successfully initialized {model_name}")
            return model, model_name
        except Exception as e:
            print(f"Failed to initialize {model_name}: {e}")
            continue
    
    print("No working Gemini models found")
    return None, None

model, current_model_name = initialize_gemini()

def initialize_session():
    """Initialize session variables for chat history and reactions"""
    if 'chat_history' not in session:
        session['chat_history'] = []
    if 'reactions' not in session:
        session['reactions'] = []
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
        
        if model is None:
            return jsonify({'error': 'Gemini API not configured. Please check your API key.'}), 500
        
        user_message = request.json.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        response = model.generate_content(user_message)
        bot_response = response.text
        
        chat_entry = {
            'id': str(uuid.uuid4()),
            'user_message': user_message,
            'bot_response': bot_response,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        session['chat_history'].append(chat_entry)
        
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

@app.route('/upload', methods=['POST'])
def upload():
    """Handle file uploads"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return jsonify({'message': 'File uploaded', 'filename': filename})

@app.route('/reaction', methods=['POST'])
def reaction():
    """Handle message reactions"""
    try:
        data = request.get_json()
        if not data or 'message' not in data or 'reaction' not in data:
            return jsonify({'error': 'Invalid reaction data'}), 400
        
        reaction = {
            'message': data['message'],
            'reaction': data['reaction'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        session['reactions'].append(reaction)
        session.modified = True
        return jsonify({'message': 'Reaction stored'})
    except Exception as e:
        print(f"Error in reaction route: {e}")
        return jsonify({'error': f'Error storing reaction: {str(e)}'}), 500

@app.route('/export')
def export():
    history = session.get('history', [])
    export_data = json.dumps(history, indent=2)
    with open('export.json', 'w') as f:
        f.write(export_data)
    return send_file('export.json', as_attachment=True)

@app.route('/add-tag', methods=['POST'])
def add_tag():
    data = request.get_json()
    tag = data.get('tag')
    if not tag:
        return jsonify({'error': 'No tag'}), 400
    session.setdefault('tags', []).append(tag)
    session.modified = True
    return jsonify({'message': f'Tag {tag} added'})

@app.route('/analytics')
def analytics():
    stats = {
        'total_messages': len(session.get('chat_history', [])),
        'regenerations': session.get('regen_count', 0),
        'uploads': session.get('upload_count', 0),
        'reactions': len(session.get('reactions', []))
    }
    return render_template('analytics.html', stats=stats)


if __name__ == '__main__':
    print("Starting Flask Gemini Chatbot...")
    print("Checking configuration...")
    
    if not os.getenv('GEMINI_API_KEY'):
        print("GEMINI_API_KEY not found!")
        print("Please create a .env file with:")
        print("SECRET_KEY=your-secret-key")
        print("GEMINI_API_KEY=your-gemini-api-key")
    else:
        print("Environment variables loaded")
    
    print("Server starting on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)