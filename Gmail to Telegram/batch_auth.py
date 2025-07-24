# batch_auth.py

from google_auth_oauthlib.flow import InstalledAppFlow
import pickle, os, time

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate(account_name):
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES
    )
    creds = flow.run_local_server(port=0)
    os.makedirs("tokens", exist_ok=True)
    with open(f"tokens/{account_name}_token.pickle", "wb") as token_file:
        pickle.dump(creds, token_file)
    print(f"✅ Token saved for {account_name}")

if __name__ == "__main__":
    # List of friendly account names — not the Gmail address itself
    account_names = [
        "email_004",
        "email_005",
        "email_006",
        # Add more here...
    ]

    for account in account_names:
        print(f"\n🔐 Authenticating: {account}")
        authenticate(account)
        time.sleep(2)  # Short pause between accounts (optional)
