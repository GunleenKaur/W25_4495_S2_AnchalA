from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return build('gmail', 'v1', credentials=creds)

def fetch_emails_and_check_spam():
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', maxResults=5).execute()
    messages = results.get('messages', [])

    for msg in messages:
        message = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        snippet = message.get('snippet', '')

        # Call your API
        response = requests.post("http://localhost:5000/api/check_spam", json={"text": snippet})
        result = response.json()['is_spam']
        print(f"Message: {snippet[:50]}... => {'Spam' if result else 'Not Spam'}")

if __name__ == "__main__":
    fetch_emails_and_check_spam()
