"""
Someta Math Helper Backend API
Main application entry point
"""
import os
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from routes import app

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable CORS with specific configuration
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "chrome-extension://*",
            "https://someta-api.onrender.com"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Configure Flask app
app.config.update(
    # Security
    SECRET_KEY=os.getenv('SECRET_KEY', os.urandom(24)),
    
    # Request handling
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB for screenshots
    JSON_AS_ASCII=False,  # Support non-ASCII characters
    
    # Performance
    JSONIFY_PRETTYPRINT_REGULAR=True,
    JSON_SORT_KEYS=False
)

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    logger.warning(f"Bad request: {error}")
    return jsonify({
        "success": False,
        "error": "Bad request",
        "message": str(error)
    }), 400

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"Not found: {error}")
    return jsonify({
        "success": False,
        "error": "Not found",
        "message": str(error)
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 8080))
    
    # Log startup information
    logger.info(f"Starting Someta Math Helper API on port {port}")
    logger.info(f"Debug mode: {app.debug}")
    
    # Run the application
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
