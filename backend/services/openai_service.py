"""
OpenAI service for handling all OpenAI API interactions.
"""
from typing import List, Dict, Any
import os
from openai import OpenAI
from dotenv import load_dotenv
from models.message_types import MessageType

# Load environment variables
load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ Missing OpenAI API key! Check your .env file.")

client = OpenAI(api_key=OPENAI_API_KEY)

class OpenAIService:
    """Service for handling OpenAI API interactions."""
    
    @staticmethod
    def get_model_for_type(message_type: MessageType) -> str:
        """Get the appropriate model for the message type."""
        if message_type == MessageType.META_ANALYSIS:
            return "gpt-4-1106-preview"  # O1 model for meta analysis
        else:
            return "gpt-4o"
     
    
    @classmethod
    async def process_message(
        cls,
        messages: List[Dict[str, str]],
        message_type: MessageType,
        stream: bool = False
    ) -> str:
        """Process a text message with OpenAI."""
        try:
            response = client.chat.completions.create(
                model=cls.get_model_for_type(message_type),
                messages=messages,
                stream=stream
            )
            
            if stream:
                return response
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error processing message with OpenAI: {str(e)}")
    
    @classmethod
    async def analyze_image(cls, image_url: str, prompt: str) -> str:
        """Analyze an image with OpenAI's vision model."""
        try:
            # Check if it's a base64 image
            if not image_url.startswith('http'):
                image_url = f"data:image/jpeg;base64,{image_url}"
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error analyzing image with OpenAI: {str(e)}") 