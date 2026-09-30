# Import required libraries
from smtplib import SMTP
from dotenv import load_dotenv
from os import getenv, name, system
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from email.mime.multipart import MIMEMultipart

# Import session-based credentials
load_dotenv()


def main() -> None:
  """
  Email Protocols:
    1. SMTP: Simple Mail Transfer Protocol - Sending emails
    2. IMAP: Internet Message Access Protocol - Accessing emails remotely
    3. POP3: Post Office Protocol 3 - Receiving emails locally
  """

  server = SMTP(getenv("SMTP_SERVER"), 587)

  # Starting process and renegotiating the connection to use TLS encryption
  server.ehlo()
  server.starttls()
  server.ehlo()

  # Logging into gmail account
  server.login(
    getenv("GMAIL_EMAIL_SENDER"), getenv("GMAIL_APP_PASSWD").replace(" ", "")
  )

  # Crafting message
  msg = MIMEMultipart()

  # Defining message headers
  msg["From"] = "CryptoKingXavier"
  msg["To"] = getenv("GMAIL_EMAIL_RECPT")
  msg["Subject"] = "CKX SMTP-MAIL SENDING TESTING PHASE!!!"

  with open("./attachments/message.txt", "r") as f:
    message = f.read()

  # Adding text message content
  msg.attach(MIMEText(message, "plain"))

  # Adding email as attachment
  filename = "./attachments/passport.jpg"
  attachment = open(filename, "rb")

  # Creating a payload object
  payload = MIMEBase("application", "octet-stream")
  payload.set_payload(attachment.read())

  # Encoding payload data and adding headers
  encode_base64(payload)
  payload.add_header("Content-Disposition", f"attachment; filename={filename}")

  # Adding payload as attachment to the message
  msg.attach(payload)

  # Converting message to string
  parsed_mail = msg.as_string()

  # Sending mail via SMTP server
  server.sendmail(
    getenv("GMAIL_EMAIL_SENDER"), getenv("GMAIL_EMAIL_RECPT"), parsed_mail
  )

  print("Mail Sent 📧!")


if __name__ == "__main__":
  system("cls" if name == "nt" else "clear")
  main()
