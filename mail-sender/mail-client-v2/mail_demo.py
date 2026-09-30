# Import required libraries
from faker import Faker
from dotenv import load_dotenv
from smtplib import SMTP, SMTP_SSL
from os import getenv, name, system
from email.message import EmailMessage
from typing import Union, TypeVar, Literal
from PIL import Image, UnidentifiedImageError

# Import session-based credentials
load_dotenv()

# Recipients can be a comma separated string or a list of emails
CONTACTS: list[str] = [getenv("GMAIL_EMAIL_SENDER"), getenv("GMAIL_EMAIL_RECPT")]

# Instantiating fake data object
FAKE = Faker()

# Creating custom type annotations
PROTOCOL = TypeVar("PROTOCOL", SMTP, SMTP_SSL)
SERVER = TypeVar("SERVER", Literal["aiosmtpd"], Literal["ssl"], Literal["tls"])

CTX: dict[str, str] = {
  # Constructing plaintext email
  # "subject": "Grab dinner this weekend?",
  # "body": "How about dinner at 06:00PM this Saturday?",
  "subject": FAKE.date(),
  "body": FAKE.sentence(),
}

SERVERS: dict[str, dict[str, Union[str, int]]] = {
  "aiosmtpd": {"host": getenv("DEBUG_SERVER"), "port": 1025},
  "ssl": {"host": getenv("SMTP_SERVER"), "port": 465},
  "tls": {"host": getenv("SMTP_SERVER"), "port": 587},
}


# Custom imghdr.what() method implementation using Pillow
def what(image_path: str) -> Union[str, None]:
  """
  Identify the format of an image.
  Equivalent in purpose to the deprecated: imghdr.what(image_path)

  Keyword arguments:
  image_path -- path or relative path of image file

  Return: str | None: Image format such as "JPEG", "PNG",
  or None if the file cannot be identified as an image.
  """

  try:
    with Image.open(image_path) as image:
      return image.format.lower()
  except (OSError, UnidentifiedImageError):
    return None


def raw_message_sender(smtp: SMTP) -> None:
  """
  Crafting Email Message From Scratch:
    1. The subject needs to be added as a header.
    2. It should then be followed by blank lines (>=2).
    3. Finally, the body of the message is appended.
  """

  msg = f"Subject: {CTX.get('subject')}\n\n{CTX.get('body')}"

  # Sending mail via SMTP server
  smtp.sendmail(getenv("GMAIL_EMAIL_SENDER"), getenv("GMAIL_EMAIL_RECPT"), msg)


# Adding email html attachment
def attach_html(msg: EmailMessage, html_path: str) -> None:
  with open(html_path, "r") as html:
    html_data = html.read()
    msg.set_content(FAKE.sentence())
    msg.add_alternative(html_data, subtype="html")


# Adding email file attachment
def attach_file(msg: EmailMessage, file_path: str) -> None:
  with open(file_path, "rb") as file:
    file_data = file.read()
    file_name = file.name.split("/")[-1]

    # Octet-Stream is considered as a generic bag of bits type
    msg.add_attachment(
      file_data, maintype="application", subtype="octet-stream", filename=file_name
    )


# Adding email image attachment
def attach_image(msg: EmailMessage, image_path: str) -> None:
  with open(image_path, "rb") as image:
    image_data = image.read()
    image_type = what(image_path)
    image_name = image.name.split("/")[-1]

  msg.add_attachment(
    image_data, maintype="image", subtype=image_type, filename=image_name
  )


def email_message_sender(smtp: PROTOCOL) -> None:
  msg: EmailMessage = EmailMessage()

  # Crafting message
  msg["Subject"] = CTX.get("subject")
  msg["From"] = getenv("GMAIL_EMAIL_SENDER")
  # msg["To"] = CONTACTS   # Multiple recipients as a list
  # msg["To"] = ", ".join(CONTACTS)   # Multiple recipients as a csv list
  msg["To"] = getenv("GMAIL_EMAIL_RECPT")
  msg.set_content(CTX.get("body"))

  # Crafting different email attachments
  # attach_image(msg, "./attachments/passport.jpg")
  attach_file(msg, "./attachments/message.txt")
  # attach_html(msg, "./attachments/simple.html")

  # Sending mail via SMTP_SSL server
  smtp.send_message(msg)


def start_server(server: SERVER) -> PROTOCOL:
  match server:
    case "aiosmtpd":
      return SMTP(
        SERVERS.get("aiosmtpd").get("host"), SERVERS.get("aiosmtpd").get("port")
      )
    case "ssl":
      return SMTP_SSL(SERVERS.get("ssl").get("host"), SERVERS.get("ssl").get("port"))
    case "tls":
      return SMTP(SERVERS.get("tls").get("host"), SERVERS.get("tls").get("port"))


def secure_login(smtp: PROTOCOL, server: SERVER) -> PROTOCOL:
  match server:
    case "tls":
      # Starting process and renegotiating the connection to use TLS encryption
      smtp.ehlo()
      smtp.starttls()
      smtp.ehlo()

  match server:
    case "ssl" | "tls":
      # Logging into gmail account
      smtp.login(
        getenv("GMAIL_EMAIL_SENDER"), getenv("GMAIL_APP_PASSWD").replace(" ", "")
      )

  match server:
    case "aiosmtpd" | "ssl" | "tls":
      # Return server instance
      return smtp


def main() -> None:
  """
  Email PROTOCOLs:
    1. SMTP: Simple Mail Transfer PROTOCOL - Sending emails
    2. IMAP: Internet Message Access PROTOCOL - Accessing emails remotely
    3. POP3: Post Office PROTOCOL 3 - Receiving emails locally
  """

  # Creating SMTP server instance
  smtp: PROTOCOL = secure_login(start_server("aiosmtpd"), "aiosmtpd")

  # Sending email across network
  email_message_sender(smtp)

  # Confirmation message
  print("Mail Sent 📧!")


if __name__ == "__main__":
  system("cls" if name == "nt" else "clear")
  main()
