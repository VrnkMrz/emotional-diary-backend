import os
from mailersend import emails
from django.conf import settings

class MailerSendService:
    def __init__(self):
        api_key = settings.MAILERSEND_API_TOKEN
        self.client = emails.NewEmail(api_key)

    def send_otp(self, to_email: str, otp_code: str):
        mail = {
            "from": {
                "email": settings.MAILERSEND_SENDER,
                "name":  "Emotional Diary Service",
            },
            "to": [
                {
                    "email": to_email,
                    "name":  "",
                }
            ],
            "subject": "Ваш OTP-код",
            "text":    f"Доброго дня!\nВаш тимчасовий OTP-код: {otp_code}\nТермін дії — 5 хвилин.",
            "html":    f"<p>Ваш тимчасовий <strong>OTP-код</strong>: <code>{otp_code}</code></p>"
        }

        response = self.client.send(mail)
        print(f"Mail server response: {response}")
        return response 
