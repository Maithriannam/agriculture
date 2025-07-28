import os
from twilio.rest import Client

def send_sms_alert(message):
    # ✅ Load environment variables from Render (not dotenv)
    account_sid = os.environ.get("TWILIO_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("FROM_PHONE")
    to_number = os.environ.get("TO_PHONE")

    # ✅ Check if any variable is missing
    if not all([account_sid, auth_token, from_number, to_number]):
        print("❌ Missing one or more environment variables. SMS not sent.")
        return

    try:
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        print("✅ SMS sent successfully. SID:", msg.sid)
    except Exception as e:
        print("❌ Failed to send SMS:", str(e))

