import os
import pickle
import requests
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

BOT_TOKEN = "7920891849:AAH8_________" #Telegram Bot Token
CHAT_ID = "80558@@@@@" #Telegram Bot Chat ID

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram Error: {e}")

def get_service(token_file):
    with open(token_file, 'rb') as f:
        creds = pickle.load(f)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('gmail', 'v1', credentials=creds)

def is_recent(internal_date_ms, minutes=5):
    try:
        email_time = datetime.fromtimestamp(int(internal_date_ms) / 1000, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        return now - email_time <= timedelta(minutes=minutes)
    except Exception as e:
        print(f"Time parse error: {e}")
        return False

def check_emails():
    for token_file in os.listdir('tokens'):
        token_path = os.path.join('tokens', token_file)
        try:
            service = get_service(token_path)
            user_id = 'me'

            # ?? Get Gmail address for this token
            profile = service.users().getProfile(userId='me').execute()
            account_email = profile.get('emailAddress', 'Unknown')

            results = service.users().messages().list(
                userId=user_id, labelIds=['INBOX'], q='is:unread'
            ).execute()
            messages = results.get('messages', [])

            for msg in messages:
                msg_data = service.users().messages().get(userId=user_id, id=msg['id']).execute()
                internal_date = msg_data.get('internalDate')
                if not is_recent(internal_date):
                    continue

                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
                receiver = next((h['value'] for h in headers if h['name'].lower() == 'to'), 'Unknown')
                snippet = msg_data.get('snippet', '')

                alert = (
                    f"*New Email*\n"
                    f"Account: `{account_email}`\n"
                    f"From: {sender}\n"
                    f"To: {receiver}\n"
                    f"Subject: {subject}\n"
                    f"Snippet: {snippet[:100]}"
                )
                send_telegram(alert)

        except Exception as e:
            print(f"Error processing {token_file}: {e}")

if __name__ == "__main__":
    check_emails()
