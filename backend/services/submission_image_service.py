"""
Service for processing submitted assignment images.
This service provides specialized functionality for analyzing and grading 
student assignment submissions with multiple pages.
"""

import json
from services.openai_client import client
from services.session_management import initialize_session
from services.submission_history import add_submission_record, get_submission_history
from services.logger import setup_logger
from services.config import ImageSubmission

# Set up logger
logger = setup_logger(__name__)

# System prompt for assignment grading
ASSIGNMENT_GRADING_PROMPT = ImageSubmission["prompt"]

def process_submission(images_data, session_obj=None, session_id=None, student_id="Unknown"):
    """
    Process submitted assignment images and provide grading results.
    
    This function:
    1. Combines multiple images (up to 3 pages) into a single analysis
    2. Generates a comprehensive grade and feedback
    3. Stores the submission in the submission history
    
    Args:
        images_data: List of base64 encoded images (max 3)
        session_obj: Flask session object
        session_id: Session ID for history
        student_id: ID of the student
        
    Returns:
        tuple: (analysis_results, session_id)
    """
    try:
        num_pages = len(images_data) if images_data else 0
        logger.info(f"Processing submission with {num_pages} pages for student {student_id}")
        
        if not images_data:
            logger.warning("No image data provided for submission")
            return None, session_id
            
        # Initialize session if needed
        if session_obj:
            session_id = initialize_session(session_obj, student_id, session_id)
            logger.info(f"Session initialized with ID: {session_id}")
        
        # Process the assignment submission as a whole
        analysis_results = []
        
        # First, generate individual page analyses
        page_analyses = []
        for i, encoded_image in enumerate(images_data):
            if not encoded_image or not isinstance(encoded_image, str):
                continue
                
            # Analyze each page individually
            page_analysis = analyze_single_page(encoded_image, i+1)
            if page_analysis:
                page_analyses.append(page_analysis)
        
        if not page_analyses:
            error_message = "⚠️ No valid page analyses were generated."
            logger.error(error_message)
            return [error_message], session_id
        
        # Now, generate a combined analysis considering all pages
        combined_result = generate_combined_analysis(page_analyses, len(images_data))
        if combined_result:
            analysis_results.append(combined_result)
            
            # Extract grade from the combined result
            grade = extract_grade(combined_result)
            
            # Store in submission history if session is available
            if session_obj and session_id:
                add_submission_record(
                    session_obj,
                    session_id,
                    student_id,
                    grade,
                    combined_result,
                    pages_submitted=len(images_data),
                    submission_type="assignment"
                )
        
        if not analysis_results:
            error_message = "⚠️ No valid analysis results were generated."
            logger.error(error_message)
            return [error_message], session_id
        
        # Return analysis results and session ID
        return analysis_results, session_id

    except Exception as e:
        logger.error(f"Error processing submission: {str(e)}", exc_info=True)
        error_message = f"⚠️ Error processing submission: {str(e)}"
        return [error_message], session_id

def analyze_single_page(encoded_image, page_number):
    """
    Analyze a single page of a submission.
    
    Args:
        encoded_image: Base64 encoded image
        page_number: The page number
        
    Returns:
        str: The analysis text
    """
    try:
        # Add the image to analyze
        image_content = [{
            "type": "image_url", 
            "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
        }]
        
        # Prepare messages for OpenAI with a detailed prompt
        messages = [
            {"role": "system", "content": ASSIGNMENT_GRADING_PROMPT}
        ]
        
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": f"This is page {page_number} of a student assignment. Analyze the content:"}] + image_content
        })
        
        # Call OpenAI API
        logger.info(f"Calling OpenAI API for analysis of page {page_number}")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        
        # Extract AI response
        if response and hasattr(response, "choices") and len(response.choices) > 0:
            return response.choices[0].message.content
        
        return None
    except Exception as e:
        logger.error(f"Error analyzing page {page_number}: {str(e)}", exc_info=True)
        return None

def generate_combined_analysis(page_analyses, total_pages):
    """
    Generate a combined analysis from individual page analyses.
    
    Args:
        page_analyses: List of individual page analyses
        total_pages: Total number of pages in the submission
        
    Returns:
        str: The combined analysis text
    """
    try:
        # Create a prompt for the combined analysis
        combined_prompt = f"""
        Based on the analyses of {total_pages} pages of a student assignment, provide a comprehensive 
        grading assessment. Include:
        
        1. Overall grade (A, B, C, D, or F)
        2. Summary of student understanding
        3. Key strengths
        4. Specific feedback for improvement
        
        Format with clear headings for each section.
        
        Here are the individual page analyses:
        
        {chr(10).join([f"--- PAGE {i+1} ---{chr(10)}{analysis}{chr(10)}" for i, analysis in enumerate(page_analyses)])}
        """
        
        # Call OpenAI API for combined analysis
        logger.info(f"Generating combined analysis for {total_pages} pages")
        messages = [
            {"role": "system", "content": ASSIGNMENT_GRADING_PROMPT},
            {"role": "user", "content": combined_prompt}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        
        # Extract AI response
        if response and hasattr(response, "choices") and len(response.choices) > 0:
            combined_analysis = response.choices[0].message.content
            return combined_analysis
        
        return None
    except Exception as e:
        logger.error(f"Error generating combined analysis: {str(e)}", exc_info=True)
        return None

def extract_grade(analysis_text):
    """
    Extract the grade from the analysis text.
    
    Args:
        analysis_text: The analysis text
        
    Returns:
        str: The extracted grade or "Not Graded"
    """
    try:
        # Look for grade patterns like "Grade: A" or "Overall Grade: B+"
        import re
        grade_match = re.search(r'(?:Grade|GRADE|grade):\s*([A-F][+-]?|[0-9]+\/[0-9]+|[0-9]+%)', analysis_text)
        if grade_match:
            return grade_match.group(1)
        
        # Try another pattern for "Overall: B"
        grade_match = re.search(r'(?:Overall|OVERALL):\s*([A-F][+-]?|[0-9]+\/[0-9]+|[0-9]+%)', analysis_text)
        if grade_match:
            return grade_match.group(1)
        
        return "Not Graded"
    except Exception as e:
        logger.error(f"Error extracting grade: {str(e)}", exc_info=True)
        return "Not Graded" 