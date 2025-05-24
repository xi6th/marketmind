# config_setup.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ServerConfig:
    def __init__(self):
        self.host = os.getenv('HOST', 'localhost')
        self.port = int(os.getenv('PORT', 8000))
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        self.api_key = os.getenv('API_KEY')
        self.base_url = os.getenv('BASE_URL', 'https://www.alphavantage.co/query')
        self.valid_intervals = os.getenv('VALID_INTERVALS', '1min,5min,15min,30min,60min').split(',')
        
    def cors(self):
        # Get allowed origins from environment or use defaults
        allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
        if not allowed_origins or allowed_origins == ['']:
            allowed_origins = ["*"]
            
        return {
            "allow_origins": allowed_origins,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
    
    def allowed_origins(self):
        origins = os.getenv('ALLOWED_ORIGINS')
        if origins:
            return origins.split(',')
        return [
            "http://localhost:4000",
            "http://localhost:3500",
            "https://marketmind-ezjx.onrender.com",
            "https://getmarketmind.com"
        ]