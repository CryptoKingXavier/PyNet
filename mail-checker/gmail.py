# Import required libraries
from bs4 import BeautifulSoup
from imaplib import IMAP4_SSL
from dotenv import load_dotenv
from os import getenv, name, system
from email import message_from_bytes
from filter import GmailFolders, GmailFilters

# Import session-based credentials
load_dotenv()


# Get folders
def get_folders(imap: IMAP4_SSL) -> None:
  (status, folders) = imap.list()

  for (idx, folder) in enumerate(folders, start=1):
    print(f"{idx}. {folder.decode()}")


# Extract email body
def extract_email_body(msg: str) -> str:
  html_content = None
  text_content = None

  if msg.is_multipart():
    for part in msg.walk():
      content_type = part.get_content_type()

      if content_type == "text/html":
        html_content = part.get_payload(decode=True).decode(errors="replace")

      elif content_type == "text/plain":
        text_content = part.get_payload(decode=True).decode(errors="replace")

  else:
    content_type = msg.get_content_type()

    if content_type == "text/html":
      html_content = msg.get_payload(decode=True).decode(errors="replace")
    else:
      text_content = msg.get_payload(decode=True).decode(errors="replace")

  # Prefer HTML body if available
  if html_content:
    soup = BeautifulSoup(html_content, "lxml")

    # Remove unwanted elements
    for tag in soup(["script", "style", "head"]):
      tag.decompose()

    return soup.get_text(separator="\n", strip=True)

  return text_content


def main() -> None:
  """
  Email Protocols:
    1. SMTP: Simple Mail Transfer Protocol - Sending emails
    2. IMAP: Internet Message Access Protocol - Accessing emails remotely
    3. POP3: Post Office Protocol 3 - Receiving emails locally
  """

  # Connect to IMAP server
  imap = IMAP4_SSL(getenv("IMAP_SERVER"))
  imap.login(getenv("GMAIL_EMAIL"), getenv("GMAIL_APP_PASSWD").replace(" ", ""))

  # Select the Inbox
  imap.select(getenv("GMAIL_DEFAULT_FOLDER", GmailFolders.INBOX.value))

  # Search for all emails
  (status, messages) = imap.search(None, GmailFilters.ALL.value)

  # Get the ID of the most recent email
  mail_ids = messages[0].split()
  latest_id = mail_ids[-1]

  # Fetch the email
  (status, data) = imap.fetch(latest_id, getenv("GMAIL_BYTES_ENCODING"))

  # Parse the raw email
  raw_email = data[0][1]
  msg = message_from_bytes(raw_email)

  print(f"Message Number: {latest_id}")
  print(f"From: {msg.get('From')}")
  print(f"To: {msg.get('To')}")
  print(f"BCC: {msg.get('BCC')}")
  print(f"Date: {msg.get('Date')}")
  print(f"Subject: {msg.get('Subject')}")

  content = extract_email_body(msg)

  print(f"\nEmail Content:\n{content}")

  # Logout from server
  imap.logout()


if __name__ == "__main__":
  system("cls" if name == "nt" else "clear")
  main()
