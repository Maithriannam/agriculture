from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

def send_sms_alert(message):
    account_sid = os.getenv("TWILIO_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("FROM_PHONE")
    to_number = os.getenv("TO_PHONE")

    client = Client(account_sid, auth_token)
    msg = client.messages.create(
        body=message,
        from_=from_number,
        to=to_number
    )
    print("✅ SMS sent:", msg.sid)
