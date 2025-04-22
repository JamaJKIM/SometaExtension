import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import pytz
import base64
import os
import json
from models.message_types import MessageType
from models.chat_targets import ChatTarget

# ✅ Decode Google Credentials from Environment Variable
json_str = base64.b64decode(os.getenv("GOOGLE_CREDENTIALS")).decode()
creds_dict = json.loads(json_str)

# ✅ Google Sheets Setup (Use Restricted Access)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client_gsheets = gspread.authorize(creds)
sheet_link = "https://docs.google.com/spreadsheets/d/1k7Xg6UjwP9BaA1vjnX55K0X3gaExF2YSCkNaeRZQ-OQ"

# ✅ Function to Log Conversation with Purpose
def log_to_sheets(student_id, user_input, ai_response, messageType: MessageType, chatTarget: ChatTarget):
    try:
        sheet = client_gsheets.open_by_url(sheet_link).sheet1  # Open sheet by URL
        pacific_tz = pytz.timezone("America/Los_Angeles")
        timestamp = datetime.datetime.now(pacific_tz).strftime("%Y-%m-%d %I:%M:%S %p") 

        # Truncate very long responses to avoid sheet issues
        if len(ai_response) > 50000:  # Google Sheets has cell character limits
            ai_response = ai_response[:50000] + "... (truncated)"

        # Add row with messageType and chatTarget (using enum values)
        sheet.append_row([timestamp, student_id, user_input, ai_response, messageType.value, chatTarget.value])
        print(f"✅ Logged to Google Sheets: {messageType.value}, {chatTarget.value}, {timestamp}, {student_id}, {user_input} → {ai_response}")
    except Exception as e:
        print(f"❌ Error logging to Google Sheets: {e}")
