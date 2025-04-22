"""
Service layer for processing different types of messages.
"""
from typing import Dict, Any, List
import json
from models.message_types import MessageType
from models.chat_targets import ChatTarget
from models.messages import UserMessage, AssistantMessage
from services.openai_service import OpenAIService
from services.logger import setup_logger

logger = setup_logger(__name__)

class MessageProcessingService:
    """Service for processing different types of messages."""
    
    @staticmethod
    async def process_problem_generation(
        content: str,
        messages: List[Dict[str, str]],
        student_id: str,
        target: ChatTarget
    ) -> Dict[str, Any]:
        """Process a problem generation request."""
        try:
            # Parse the content
            content_data = json.loads(content)
            interests = content_data.get('interests')
            standard = content_data.get('standard')
            standard_description = content_data.get('standardDescription')
            
            if not interests or not standard:
                raise ValueError("Missing interests or standard in problem generation request")
            
            # Get the system prompt from messages if available
            system_prompt = next(
                (msg["content"] for msg in messages if msg["role"] == "system"),
                ""
            )
            
            # Create the prompt for problem generation
            prompt = f"{system_prompt}\n\nGenerate a math problem based on:\nInterests: {interests}\nMath Standard: {standard}"
            
            # Add standard description if available
            if standard_description:
                prompt += f"\nStandard Description: {standard_description}"
            
            # Process with OpenAI
            response = await OpenAIService.process_message(
                messages=[{"role": "user", "content": prompt}],
                message_type=MessageType.GENERATED_PROBLEM
            )
            
            # Create the response message
            assistant_message = AssistantMessage(
                content=response,
                message_type=MessageType.GENERATED_PROBLEM,
                student_id=student_id
            )
            
            return {
                "status": "success",
                "message": response,
                "target": target.value,
                "message_type": MessageType.GENERATED_PROBLEM.value,
                "student_id": student_id
            }
            
        except Exception as e:
            logger.error(f"Error processing problem generation: {str(e)}")
            raise
    
    @staticmethod
    async def process_image_analysis(
        content: str,
        messages: List[Dict[str, str]],
        student_id: str,
        target: ChatTarget
    ) -> Dict[str, Any]:
        """Process an image analysis request."""
        try:
            # Get the system prompt from messages if available
            system_prompt = next(
                (msg["content"] for msg in messages if msg["role"] == "system"),
                ""
            )
            
            # Process the image with OpenAI
            response = await OpenAIService.analyze_image(
                image_url=content,
                prompt=system_prompt
            )
            
            # Create the analysis message
            analysis_message = AssistantMessage(
                content=response,
                message_type=MessageType.IMAGE_ANALYSIS,
                student_id=student_id
            )
            
            return {
                "status": "success",
                "message": response,
                "target": target.value,
                "message_type": MessageType.IMAGE_ANALYSIS.value,
                "student_id": student_id
            }
            
        except Exception as e:
            logger.error(f"Error processing image analysis: {str(e)}")
            raise
    
    @staticmethod
    async def process_text_message(
        content: str,
        messages: List[Dict[str, str]],
        message_type: MessageType,
        student_id: str,
        target: ChatTarget
    ) -> Dict[str, Any]:
        """Process a text-based message."""
        try:
            # Process the message with OpenAI
            response = await OpenAIService.process_message(
                messages=messages,
                message_type=message_type
            )
            
            # Create the response message
            assistant_message = AssistantMessage(
                content=response,
                message_type=message_type,
                student_id=student_id
            )
            
            return {
                "status": "success",
                "message": response,
                "target": target.value,
                "message_type": message_type.value,
                "student_id": student_id
            }
            
        except Exception as e:
            logger.error(f"Error processing text message: {str(e)}")
            raise
    
    @staticmethod
    def _convert_messages_to_dicts(messages: List[Any]) -> List[Dict[str, Any]]:
        """Convert a list of messages to a list of dictionaries."""
        return [msg.to_dict() if hasattr(msg, 'to_dict') else str(msg) for msg in messages]
    
    @staticmethod
    async def process_meta_analysis(
        content: str,
        all_histories: Dict[str, List[Dict[str, str]]],
        student_id: str,
        target: ChatTarget,
        messages: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Process a meta-analysis request across all chat histories."""
        try:
            # Get the system prompt from messages if available
            system_prompt = next(
                (msg["content"] for msg in messages if msg["role"] == "system"),
                ""
            ) if messages else ""
            
            # Convert histories to dictionaries for JSON serialization
            histories_dict = {
                'sofeea': MessageProcessingService._convert_messages_to_dicts(all_histories.get('sofeea', [])),
                'soproby': MessageProcessingService._convert_messages_to_dicts(all_histories.get('soproby', [])),
                'socrato': MessageProcessingService._convert_messages_to_dicts(all_histories.get('socrato', []))
            }
            
            # Prepare the meta-analysis prompt with all histories
            meta_prompt = f"""{system_prompt}

Student ID: {student_id}

SOFEEA History (Feedback):
{json.dumps(histories_dict['sofeea'], indent=2)}

SOPROBY History (Problem Generation):
{json.dumps(histories_dict['soproby'], indent=2)}

SOCRATO History (Help):
{json.dumps(histories_dict['socrato'], indent=2)}

Please analyze these interactions and provide insights following the format specified in the system prompt."""
            
            # Process with OpenAI using O1 model
            response = await OpenAIService.process_message(
                messages=[{"role": "user", "content": meta_prompt}],
                message_type=MessageType.META_ANALYSIS
            )
            
            return {
                "status": "success",
                "message": response,
                "target": target.value,
                "message_type": MessageType.META_ANALYSIS.value,
                "student_id": student_id,
                "analysis_type": "meta"
            }
            
        except Exception as e:
            logger.error(f"Error processing meta analysis: {str(e)}")
            raise 