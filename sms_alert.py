import os
from twilio.rest import Client

def send_sms_alert(message):
    account_sid = os.environ.get("TWILIO_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("FROM_PHONE")
    to_number = os.environ.get("TO_PHONE")

    if not all([account_sid, auth_token, from_number, to_number]):
        print("❌ Missing environment variables.")
        return

    try:
        client = Client(account_sid, auth_token)
        msg = client.messages.create(body=message, from_=from_number, to=to_number)
        print("✅ SMS sent:", msg.sid)
    except Exception as e:
        print("❌ SMS failed:", str(e))
