from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('movie_task/.env')

load_dotenv(dotenv_path=dotenv_path)

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_FROM=os.getenv('MAIL_FROM'),
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