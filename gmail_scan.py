from googleapiclient.discovery import build
from datetime import datetime, timedelta
import base64
import email

# ✅ Gmail Service
def get_gmail_service(credentials):
    return build('gmail', 'v1', credentials=credentials)

# ✅ Gmail Scanner
def scan_old_emails(service, days_old=365, max_results=100):
    old_emails = []
    cutoff = (datetime.utcnow() - timedelta(days=days_old)).strftime('%Y/%m/%d')

    try:
        results = service.users().messages().list(
            userId='me',
            q=f"before:{cutoff}",
            maxResults=max_results
        ).execute()
        messages = results.get('messages', [])

        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = msg_data.get('payload', {}).get('headers', [])
            subject = sender = date = "N/A"

            for h in headers:
                if h['name'] == 'Subject':
                    subject = h['value']
                elif h['name'] == 'From':
                    sender = h['value']
                elif h['name'] == 'Date':
                    date = h['value']

            old_emails.append({
                'Subject': subject,
                'From': sender,
                'Date': date,
                'ID': msg['id']
            })

    except Exception as e:
        print("Error fetching emails:", e)

    return old_emails
