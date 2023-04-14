import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import time

# access to a gmail account
def get_gmail_service():
    creds = None
    token_path = 'token.pickle'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/gmail.readonly'])
            creds = flow.run_local_server(port=0)

        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

# check emails
def check_emails(service, sender_email):
    results = service.users().messages().list(userId='me', q=f'from:{sender_email} is:unread').execute()
    messages = results.get('messages', [])
    return messages

# it is necessary to add python code here
def execute_python_code():
    print("A new email from the specified account has been found. Executing Python code.")

# this is the main part that runs continuously
def main():
    sender_email = "example@example.com"
    service = get_gmail_service()

    while True:
        new_emails = check_emails(service, sender_email)

        if new_emails:
            for email in new_emails:
                msg_id = email['id']
                msg = service.users().messages().get(userId='me', id=msg_id).execute()

                service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()

                print(f"Subject: {msg['snippet']}")

            execute_python_code()

        time.sleep(60)

if __name__ == '__main__':
    main()

