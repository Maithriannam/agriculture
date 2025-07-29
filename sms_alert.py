from twilio.rest import Client
from dotenv import load_dotenv
import os

# ✅ Load environment variables
load_dotenv()

def send_sms_alert(message):
    account_sid = os.getenv("TWILIO_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("FROM_PHONE")
    to_number = os.getenv("TO_PHONE")

    # Check if all env vars are present
    if not all([account_sid, auth_token, from_number, to_number]):
        return "❌ Missing Twilio environment variables."

    try:
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        return "✅ SMS sent successfully"
    
    except Exception as e:
        error_msg = str(e)
        if "limit" in error_msg.lower() or "63038" in error_msg:
            return "❌ SMS limit reached"
        return f"❌ Failed to send SMS: {error_msg}"
