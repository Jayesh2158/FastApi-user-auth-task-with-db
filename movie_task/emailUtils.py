from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig


conf = ConnectionConfig(
    MAIL_USERNAME="lakman9520@gmail.com",
    MAIL_PASSWORD="gg44ggml",
    MAIL_FROM="lakman9520@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


async def send_mail(subjet: str, reciptent: List, message: str):
    message = MessageSchema(
        subject=subjet,
        recipients=reciptent,
        body=message,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)