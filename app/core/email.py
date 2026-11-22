import base64
from email.message import EmailMessage
from html import escape
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parents[2]
TOKEN_FILE = BASE_DIR / "credentials" / "token.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def get_gmail_service():
    credentials = Credentials.from_authorized_user_file(
        TOKEN_FILE,
        SCOPES,
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

    return build("gmail", "v1", credentials=credentials)

def create_email_html(
    title: str,
    greeting: str,
    message: str,
    button_text: str,
    button_url: str,
    expiration: str,
    notice: str,
) -> str:
    safe_title = escape(title)
    safe_greeting = escape(greeting)
    safe_message = escape(message)
    safe_button_text = escape(button_text)
    safe_button_url = escape(button_url, quote=True)
    safe_expiration = escape(expiration)
    safe_notice = escape(notice)

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{safe_title}</title>
    </head>
    <body style="
        margin: 0;
        padding: 0;
        background-color: #f3f4f6;
        font-family: Arial, Helvetica, sans-serif;
        color: #1f2937;
    ">
        <table role="presentation" width="100%" cellspacing="0"
               cellpadding="0" style="background-color: #f3f4f6; padding: 32px 12px;">
            <tr>
                <td align="center">
                    <table role="presentation" width="100%" cellspacing="0"
                           cellpadding="0" style="
                        max-width: 560px;
                        background-color: #ffffff;
                        border-radius: 12px;
                        overflow: hidden;
                    ">
                        <tr>
                            <td style="
                                background-color: #1e3a8a;
                                padding: 28px 32px;
                                text-align: center;
                            ">
                                <h1 style="
                                    margin: 0;
                                    color: #ffffff;
                                    font-size: 21px;
                                    font-weight: 700;
                                ">
                                    Simulador de Entrevistas Técnicas
                                </h1>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 36px 32px;">
                                <h2 style="
                                    margin: 0 0 20px;
                                    font-size: 22px;
                                    color: #111827;
                                ">
                                    {safe_title}
                                </h2>

                                <p style="font-size: 15px; line-height: 1.6;">
                                    Hola, <strong>{safe_greeting}</strong>:
                                </p>

                                <p style="
                                    margin: 18px 0;
                                    font-size: 15px;
                                    line-height: 1.7;
                                    color: #4b5563;
                                ">
                                    {safe_message}
                                </p>

                                <table role="presentation" cellspacing="0"
                                       cellpadding="0" style="margin: 28px auto;">
                                    <tr>
                                        <td align="center" style="
                                            background-color: #2563eb;
                                            border-radius: 8px;
                                        ">
                                            <a href="{safe_button_url}" style="
                                                display: inline-block;
                                                padding: 14px 28px;
                                                color: #ffffff;
                                                font-size: 15px;
                                                font-weight: 700;
                                                text-decoration: none;
                                            ">
                                                {safe_button_text}
                                            </a>
                                        </td>
                                    </tr>
                                </table>

                                <p style="
                                    font-size: 13px;
                                    line-height: 1.6;
                                    color: #6b7280;
                                ">
                                    Si el botón no funciona, copia y pega
                                    el siguiente enlace en tu navegador:
                                </p>

                                <p style="
                                    overflow-wrap: anywhere;
                                    font-size: 13px;
                                    line-height: 1.6;
                                ">
                                    <a href="{safe_button_url}" style="color: #2563eb;">
                                        {safe_button_url}
                                    </a>
                                </p>

                                <p style="
                                    margin-top: 24px;
                                    font-size: 13px;
                                    line-height: 1.6;
                                    color: #6b7280;
                                ">
                                    {safe_expiration}
                                </p>

                                <p style="
                                    margin-top: 16px;
                                    font-size: 13px;
                                    line-height: 1.6;
                                    color: #6b7280;
                                ">
                                    {safe_notice}
                                </p>
                            </td>
                        </tr>
                        <tr>
                            <td style="
                                padding: 20px 32px;
                                background-color: #f9fafb;
                                text-align: center;
                                border-top: 1px solid #e5e7eb;
                            ">
                                <p style="
                                    margin: 0;
                                    font-size: 12px;
                                    color: #9ca3af;
                                ">
                                    Este es un mensaje automático.
                                    Por favor, no respondas a este correo.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: str | None = None,
) -> None:
    message = EmailMessage()
    message["To"] = to_email
    message["From"] = (
        f"{settings.GMAIL_SENDER_NAME} <{settings.GMAIL_SENDER}>"
    )
    message["Subject"] = subject
    message.set_content(body)

    if html_body:
        message.add_alternative(html_body, subtype="html")

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    service = get_gmail_service()

    service.users().messages().send(
        userId="me",
        body={"raw": encoded_message},
    ).execute()
