import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


# .env (create this file and add your actual API key)
SECRET_KEY=your-super-secret-key-here
GEMINI_API_KEY=your-gemini-api-key-here


# static/css/style.css (additional styles if needed)
/* Additional custom styles can be added here */
.typing-animation {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 2px solid #4285f4;
    border-radius: 50%;
    border-top-color: transparent;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.message-bubble pre {
    background: rgba(0,0,0,0.05);
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
    overflow-x: auto;
}

.message-bubble code {
    background: rgba(0,0,0,0.1);
    padding: 2px 5px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
}