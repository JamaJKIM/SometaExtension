"""
Chrome Extension API Routes
Handles requests from the Someta Math Helper Chrome extension
"""
import os
import logging
import json
import base64
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from services.openai_service import process_math_query, process_math_screenshot

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
extension_api = Blueprint('extension_api', __name__)

@extension_api.route('/chat', methods=['POST'])
def handle_chat():
    """
    Handle chat messages from the extension
    Can accept both text questions and screenshots
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get the message text
        message = data.get('message', '')
        
        # Check if there's a screenshot (base64 encoded image)
        screenshot = data.get('screenshot')
        has_screenshot = screenshot and isinstance(screenshot, str) and screenshot.startswith('data:image')
        
        # Log the request (not the full screenshot data)
        logger.info(f"Extension chat request: text={message}, has_screenshot={has_screenshot}")
        
        # Process based on whether there's a screenshot or just text
        if has_screenshot:
            # Extract the base64 encoded image
            image_data = screenshot.split(',')[1]
            
            # Get response from the OpenAI service
            response = process_math_screenshot(message, image_data)
        else:
            # Process as a text-only question
            response = process_math_query(message)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error processing extension chat: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@extension_api.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint for the extension
    """
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    }) 