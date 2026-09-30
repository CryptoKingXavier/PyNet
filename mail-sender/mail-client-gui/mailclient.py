# Import required libraries
from PyQt5 import uic
from faker import Faker
from dotenv import load_dotenv
from dataclasses import dataclass
from os import getenv, name, system
from typing import TypeVar, Literal
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.encoders import encode_base64
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP, SMTP_SSL, SMTPAuthenticationError
from PyQt5.QtWidgets import (
  QMainWindow,
  QApplication,
  QMessageBox,
  QPushButton,
  QFileDialog,
)


# Import session-based credentials
load_dotenv()


@dataclass
class EmailProxy:
  # Creating custom type annotations
  PROTOCOL = TypeVar("PROTOCOL", SMTP, SMTP_SSL)
  SERVER = TypeVar("SERVER", Literal["aiosmtpd"], Literal["ssl"], Literal["tls"])

  SERVERS = {
    "aiosmtpd": {"host": getenv("DEBUG_SERVER"), "port": 1025},
    "ssl": {"host": getenv("SMTP_SERVER"), "port": 465},
    "tls": {"host": getenv("SMTP_SERVER"), "port": 587},
    "custom": {
      "host": str(),
      "port": int(),
      "protocol": str(),
      "email": str(),
      "passwd": str(),
    },
  }

  def __post_init__(self) -> None:
    self.FAKE = Faker()  # Instantiating fake data object

  def customServerConfig(
    self,
    host: str = SERVERS.get("tls").get("host"),
    port: int = SERVERS.get("tls").get("port"),
    protocol: str = list(SERVERS.keys())[2],
    email: str = getenv("GMAIL_EMAIL_SENDER"),
    passwd: str = getenv("GMAIL_APP_PASSWD").replace(" ", ""),
  ) -> None:
    self.SERVERS["custom"]["host"] = host
    self.SERVERS["custom"]["port"] = port
    self.SERVERS["custom"]["protocol"] = protocol
    self.SERVERS["custom"]["email"] = email
    self.SERVERS["custom"]["passwd"] = passwd

  def startServer(self, server: SERVER) -> PROTOCOL:
    match server:
      case "aiosmtpd":
        return SMTP(
          self.SERVERS.get("aiosmtpd").get("host"),
          self.SERVERS.get("aiosmtpd").get("port"),
        )
      case "ssl":
        return SMTP_SSL(
          self.SERVERS.get("ssl").get("host"), self.SERVERS.get("ssl").get("port")
        )
      case "custom_ssl":
        return SMTP_SSL(
          self.SERVERS.get("custom").get("host"), self.SERVERS.get("custom").get("port")
        )
      case "tls":
        return SMTP(
          self.SERVERS.get("tls").get("host"), self.SERVERS.get("tls").get("port")
        )
      case "custom_tls":
        return SMTP(
          self.SERVERS.get("custom").get("host"), self.SERVERS.get("custom").get("port")
        )

  def secureLogin(self, smtp: PROTOCOL, server: SERVER) -> PROTOCOL:
    match server:
      case "tls" | "custom_tls":
        # Starting process and renegotiating the connection to use TLS encryption
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

    match server:
      case "custom_ssl" | "custom_tls":
        # Logging into custom account
        smtp.login(
          self.SERVERS.get("custom").get("email"), self.get("custom").get("passwd")
        )
      case "ssl" | "tls":
        # Logging into gmail account
        smtp.login(
          getenv("GMAIL_EMAIL_SENDER"), getenv("GMAIL_APP_PASSWD").replace(" ", "")
        )

    match server:
      case "aiosmtpd" | "custom_ssl" | "custom_tls" | "ssl" | "tls":
        # Return server instance
        return smtp


class UI(QMainWindow):
  def __init__(self) -> None:
    super(UI, self).__init__()
    uic.loadUi("./mailclient.ui", self)
    self.show()

    # Initializing EmailProxy server
    self.emailProxy = EmailProxy()

    # Customizing button event handlers
    self.pushButton.clicked.connect(self.login)
    self.pushButton_2.clicked.connect(self.attach_sth)
    self.pushButton_3.clicked.connect(self.send_mail)

  def login(self) -> None:
    try:
      # Configuring custom server credentials
      self.emailProxy.customServerConfig(
        host=self.lineEdit_3.text(),
        port=self.lineEdit_4.text(),
        email=self.lineEdit.text(),
        passwd=self.lineEdit_2.text(),
      )

      # Creating server instance
      self.server = self.emailProxy.secureLogin(
        self.emailProxy.startServer("custom_tls"), "custom_tls"
      )

      # Toggling visibility & readonly modes for GUI fields
      # 1. Toggle mode: off
      self.lineEdit.setEnabled(False)
      self.lineEdit_2.setEnabled(False)
      self.lineEdit_3.setEnabled(False)
      self.lineEdit_4.setEnabled(False)
      self.pushButton.setEnabled(False)
      # 2. Toggle mode: on
      self.lineEdit_5.setEnabled(True)
      self.lineEdit_6.setEnabled(True)
      self.textEdit.setEnabled(True)
      self.pushButton_2.setEnabled(True)
      self.pushButton_3.setEnabled(True)

      # Crafting message
      self.msg = MIMEMultipart()
    except SMTPAuthenticationError:
      message_box = QMessageBox()
      message_box.setText("Invalid Credentials!")
      message_box.exec()
    except Exception:
      message_box = QMessageBox()
      message_box.setText("Login Failed!")
      message_box.exec()

  def attach_sth(self) -> None:
    options = QFileDialog.Options()
    filenames, _ = QFileDialog.getOpenFileNames(
      self, "Open File", "", "All Files (*.*)", options=options
    )

    if filenames:
      for filename in filenames:
        # Adding email attachment
        attachment = open(filename, "rb")

        # Slicing and truncating filepath to filename
        filename = filename[filename.rfind("/") + 1 :]

        # Creating a payload object
        payload = MIMEBase("application", "octet-stream")
        payload.set_payload(attachment.read())

        # Encoding payload data and adding headers
        encode_base64(payload)
        payload.add_header("Content-Disposition", f"attachment; filename={filename}")

        # Adding payload as attachment to the message
        self.msg.attach(payload)

        # Converting message to string
        if not self.label_8.text().endswith(":"):
          self.label_8.setText(f"{self.label_8.text()},")

        # Adding filename to attachment label
        self.label_8.setText(f"{self.label_8.text()} {filename}")

  def send_mail(self) -> None:
    dialog = QMessageBox()
    dialog.setText("Do you want to send this mail?")
    dialog.addButton(QPushButton("Yes"), QMessageBox.YesRole)  # 0
    dialog.addButton(QPushButton("No"), QMessageBox.NoRole)  # 1

    if dialog.exec_() == 0:
      try:
        # Defining message headers
        self.msg["From"] = "CryptoKingXavier"
        self.msg["To"] = self.lineEdit_5.text()
        self.msg["Subject"] = self.lineEdit_6.text()

        # Adding text message content
        self.msg.attach(MIMEText(self.textEdit.toPlainText(), "plain"))

        # Converting message to string
        parsed_mail = self.msg.as_string()

        # Sending mail via SMTP server
        self.server.sendmail(self.lineEdit.text(), self.lineEdit_5.text(), parsed_mail)

        # Crafting mail confirmation
        message_box = QMessageBox()
        message_box.setText("Mail Sent 📧!")
        message_box.exec()
      except Exception:
        message_box = QMessageBox()
        message_box.setText("Failed Sending Mail 📧!")
        message_box.exec()


def main() -> None:
  """
  Email PROTOCOLs:
    1. SMTP: Simple Mail Transfer PROTOCOL - Sending emails
    2. IMAP: Internet Message Access PROTOCOL - Accessing emails remotely
    3. POP3: Post Office PROTOCOL 3 - Receiving emails locally
  """
  # Creating UI instance
  app = QApplication([])
  window = UI()
  app.exec_()


if __name__ == "__main__":
  system("cls" if name == "nt" else "clear")
  main()
