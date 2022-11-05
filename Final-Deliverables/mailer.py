from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import os

load_dotenv()


def send_the_email(to_email,subject,html_content):
    message = Mail(from_email='sanjaysiva555@gmail.com',
    to_emails=to_email,subject=subject,
    html_content=html_content)

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return
    except Exception as e:
        print(e.message)
        return
