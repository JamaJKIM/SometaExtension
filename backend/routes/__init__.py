from flask import Flask, Blueprint
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://127.0.0.1:8080", "http://localhost:8080"],
        "methods": ["POST", "GET", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"],
        "supports_credentials": True
    }
})

app.secret_key = os.urandom(24)

# Import and register the static routes blueprint
from .static_routes import static_bp
app.register_blueprint(static_bp)

# Import and register the test routes blueprint
from .test_routes import test_bp
app.register_blueprint(test_bp, url_prefix='/api')

# Import and register the message routes blueprint
from .message_routes import message_bp
app.register_blueprint(message_bp)

# Print registered routes for debugging
print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.endpoint} -> {rule.rule} [{', '.join(rule.methods)}]")