from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import validators
import os
import string
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Load environment variables
load_dotenv()

# Initialize Flask app with CORS
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))

# MongoDB setup
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(mongo_uri, connectTimeoutMS=30000, serverSelectionTimeoutMS=30000)
db = client.url_shortener
urls_collection = db.urls

# Create indexes
urls_collection.create_index('short_code', unique=True)
urls_collection.create_index('original_url')
urls_collection.create_index('expires_at')

# Custom Logging Middleware
class LoggingMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Log request details
        request_method = environ.get('REQUEST_METHOD')
        path_info = environ.get('PATH_INFO')
        query_string = environ.get('QUERY_STRING')
        
        print(f"[{datetime.utcnow().isoformat()}] {request_method} {path_info}?{query_string}")
        
        # Call the actual app
        return self.app(environ, start_response)

# Apply logging middleware
app.wsgi_app = LoggingMiddleware(app.wsgi_app)

def generate_short_code(length=6):
    """Generate a random short code"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def is_valid_custom_code(code):
    """Validate custom short code"""
    if not code:
        return False
    if len(code) > 20:
        return False
    # Only allow letters, numbers, and hyphens/underscores
    return all(c.isalnum() or c in ('-', '_') for c in code)

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
        
    data = request.get_json()
    original_url = data.get('url', '').strip()
    custom_code = data.get('custom_code', '').strip()
    validity = int(data.get('validity', 30))  # Default to 30 minutes
    
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400
    
    if not validators.url(original_url):
        return jsonify({'error': 'Invalid URL format'}), 400
    
    # Calculate expiration time
    expires_at = datetime.utcnow() + timedelta(minutes=validity)
    
    # Handle custom code if provided
    if custom_code:
        if not is_valid_custom_code(custom_code):
            return jsonify({
                'error': 'Custom code can only contain letters, numbers, hyphens and underscores (max 20 chars)'
            }), 400
        
        # Check if custom code already exists
        existing = urls_collection.find_one({'short_code': custom_code})
        if existing:
            return jsonify({
                'error': 'This custom URL is already taken'
            }), 400
        
        short_code = custom_code
    else:
        # Generate random code if no custom code provided
        short_code = generate_short_code()
        while urls_collection.find_one({'short_code': short_code}):
            short_code = generate_short_code()
    
    # Insert new record
    urls_collection.insert_one({
        'original_url': original_url,
        'short_code': short_code,
        'visits': 0,
        'created_at': datetime.utcnow(),
        'last_accessed': None,
        'expires_at': expires_at,
        'is_custom': bool(custom_code),
        'validity_minutes': validity
    })
    
    return jsonify({
        'original_url': original_url,
        'short_url': f"{request.host_url}{short_code}",
        'short_code': short_code,
        'expires_at': expires_at.isoformat(),
        'status': 'created',
        'is_custom': bool(custom_code)
    })

@app.route('/<short_code>')
def redirect_to_original(short_code):
    """Redirect short URL to original URL"""
    url = urls_collection.find_one_and_update(
        {'short_code': short_code},
        {'$inc': {'visits': 1}, '$set': {'last_accessed': datetime.utcnow()}},
        return_document=True
    )
    
    if not url:
        return jsonify({'error': 'URL not found'}), 404
    
    if url.get('expires_at') and url['expires_at'] < datetime.utcnow():
        return jsonify({'error': 'URL has expired'}), 410
    
    return redirect(url['original_url'], code=302)

@app.route('/api/url/<short_code>', methods=['GET'])
def get_original_url(short_code):
    url = urls_collection.find_one({'short_code': short_code})
    
    if not url:
        return jsonify({'error': 'URL not found'}), 404
    
    if url.get('expires_at') and url['expires_at'] < datetime.utcnow():
        return jsonify({'error': 'URL has expired'}), 410
    
    return jsonify({
        'original_url': url['original_url'],
        'short_code': url['short_code'],
        'expires_at': url['expires_at'].isoformat() if url.get('expires_at') else None,
        'visits': url['visits']
    })

@app.route('/api/stats/<short_code>', methods=['GET'])
def get_url_stats(short_code):
    url = urls_collection.find_one({'short_code': short_code})
    
    if not url:
        return jsonify({'error': 'URL not found'}), 404
    
    return jsonify({
        'original_url': url['original_url'],
        'short_code': url['short_code'],
        'visits': url['visits'],
        'created_at': url['created_at'].isoformat(),
        'last_accessed': url.get('last_accessed', '').isoformat() if url.get('last_accessed') else None,
        'expires_at': url.get('expires_at', '').isoformat() if url.get('expires_at') else None,
        'is_custom': url.get('is_custom', False),
        'validity_minutes': url.get('validity_minutes', 30)
    })

@app.route('/api/recent', methods=['GET'])
def recent_urls():
    recent = urls_collection.find({
        'expires_at': {'$gt': datetime.utcnow()}  # Only show non-expired URLs
    }).sort('created_at', -1).limit(5)
    
    return jsonify([{
        'original_url': u['original_url'],
        'short_url': f"{request.host_url}{u['short_code']}",
        'short_code': u['short_code'],
        'visits': u['visits'],
        'created_at': u['created_at'].isoformat(),
        'last_accessed': u.get('last_accessed', '').isoformat() if u.get('last_accessed') else None,
        'expires_at': u.get('expires_at', '').isoformat() if u.get('expires_at') else None,
        'is_custom': u.get('is_custom', False)
    } for u in recent])

@app.route('/api/check-code/<short_code>', methods=['GET'])
def check_code_availability(short_code):
    if not is_valid_custom_code(short_code):
        return jsonify({
            'available': False,
            'message': 'Invalid code format. Only letters, numbers, hyphens and underscores are allowed (max 20 chars)'
        })
    
    existing = urls_collection.find_one({
        'short_code': short_code,
        'expires_at': {'$gt': datetime.utcnow()}  # Only check non-expired URLs
    })
    
    return jsonify({
        'available': not existing,
        'message': 'Code already in use' if existing else 'Code available'
    })

# Background cleanup task for expired URLs
def cleanup_expired_urls():
    result = urls_collection.delete_many({'expires_at': {'$lt': datetime.utcnow()}})
    print(f"Cleaned up {result.deleted_count} expired URLs")

scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_expired_urls, 'interval', minutes=30)
scheduler.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)