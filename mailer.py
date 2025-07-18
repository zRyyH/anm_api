from email.message import EmailMessage
from models import EmailMessageData
from config import EMAIL_CONFIG
from email import encoders
import mimetypes
import smtplib
import os


class EmailSender:
    def __init__(self, config: dict = EMAIL_CONFIG):
        self.config = config

    def send(self, email_data: EmailMessageData, buffer_attachments: list = None):
        msg = EmailMessage()
        msg["Subject"] = email_data.subject
        msg["From"] = email_data.from_addr
        msg["To"] = ", ".join(email_data.to_addrs)
        if email_data.cc_addrs:
            msg["Cc"] = ", ".join(email_data.cc_addrs)

        msg.set_content(email_data.body, subtype="html" if email_data.html else "plain")

        # Anexos de arquivo
        for path in email_data.attachments:
            if os.path.isfile(path):
                mime_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
                maintype, subtype = mime_type.split("/", 1)
                with open(path, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype=maintype,
                        subtype=subtype,
                        filename=os.path.basename(path),
                    )

        # Anexos de buffer
        if buffer_attachments:
            for item in buffer_attachments:
                item["buffer"].seek(0)
                msg.add_attachment(
                    item["buffer"].read(),
                    maintype="application",
                    subtype="octet-stream",
                    filename=item["filename"],
                )

        all_recipients = (
            email_data.to_addrs + email_data.cc_addrs + email_data.bcc_addrs
        )

        with smtplib.SMTP(
            self.config["smtp_server"], self.config["smtp_port"]
        ) as server:
            if self.config["use_tls"]:
                server.starttls()
            server.login(self.config["username"], self.config["password"])
            server.send_message(
                msg, from_addr=email_data.from_addr, to_addrs=all_recipients
            )
