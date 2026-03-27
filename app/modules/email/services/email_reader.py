import asyncio
import email
from imapclient import IMAPClient

from app.core.config import get_settings
from app.core.db import AsyncSessionLocal
from app.modules.email.models.message import EmailMessage


def extract_body(msg) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                break
    else:
        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
    return body


async def save_to_db(from_email: str, subject: str, body: str):
    settings = get_settings()
    async with AsyncSessionLocal() as session:
        email_message = EmailMessage(
            sender_email=from_email,
            receiver_email=settings.SMTP_USER,
            subject=subject or "(mavzu yo'q)",
            body=body or "",
        )
        session.add(email_message)
        await session.commit()
        print(f"✅ DB ga saqlandi: {subject}")


def _blocking_imap_listen(callback):
    settings = get_settings()

    with IMAPClient("imap.gmail.com") as client:
        client.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        client.select_folder("INBOX")

        print(f"✅ Gmail ga ulandi: {settings.SMTP_USER}")
        print("⏳ Yangi emaillar kutilmoqda...")

        while True:
            client.idle()
            responses = client.idle_check(timeout=300)
            client.idle_done()

            for response in responses:
                if response[1] == b"EXISTS":
                    messages = client.search(["UNSEEN"])
                    for uid in messages:
                        raw = client.fetch([uid], ["RFC822"])[uid][b"RFC822"]
                        msg = email.message_from_bytes(raw)

                        subject = msg["Subject"] or "(mavzu yo'q)"
                        from_email = msg["From"] or "unknown"
                        body = extract_body(msg)

                        print("=" * 40)
                        print(f"📩 Yangi email!")
                        print(f"   From   : {from_email}")
                        print(f"   Subject: {subject}")
                        print(f"   Body   : {body[:200]}")
                        print("=" * 40)

                        callback(from_email, subject, body)


async def listen_for_emails_async():
    loop = asyncio.get_event_loop()

    saved_items = []

    def sync_callback(from_email, subject, body):
        asyncio.run_in_executor(
            None,
            lambda: asyncio.run(save_to_db(from_email, subject, body))
        )

    try:
        await loop.run_in_executor(
            None,
            lambda: _blocking_imap_listen(sync_callback)
        )
    except asyncio.CancelledError:
        print("🛑 IMAP listener to'xtatildi")