import aiosmtplib
from email.message import EmailMessage
import mimetypes

from app.core.config import get_settings


async def send_email(
    to_email: str,
    subject: str,
    body: str,
    file_paths: list = None,
):
    settings = get_settings()

    message = EmailMessage()
    message["From"] = settings.SMTP_USER
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    if file_paths:
        for file_path in file_paths:
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or "application/octet-stream"

            maintype, subtype = mime_type.split("/", 1)

            with open(file_path, "rb") as f:
                message.add_attachment(
                    f.read(),
                    maintype=maintype,
                    subtype=subtype,
                    filename=file_path.split("/")[-1],
                )

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        use_tls=True,
    )