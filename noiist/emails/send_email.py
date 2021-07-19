import os
import smtplib
import ssl
from smtplib import SMTPAuthenticationError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader(searchpath="noiist/emails/templates/"),
    autoescape=select_autoescape()
)

template = env.get_template("welcome-email.html")

app_email = os.getenv("GMAIL_EMAIL")
app_password = os.getenv("GMAIL_EMAIL_PASSWORD")
email_port = os.getenv("GMAIL_EMAIL_PORT")

email_message = MIMEMultipart("alternative")
email_message["Subject"] = "Welcome to Noisli"
email_message["From"] = app_email


def create_email(receiver_fullname: str):
    ctx = {"full_name": receiver_fullname}
    output = template.render(ctx=ctx)
    return output


def send_email(receiver_fullname: str, receiver_email: str):
    html_content = create_email(receiver_fullname=receiver_fullname)
    email_message["To"] = receiver_email
    email_message.attach(MIMEText(html_content, "html"))

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", email_port, context=context) as server:
            server.login(app_email, app_password)
            server.sendmail(
                app_email, receiver_email, email_message.as_string()
            )
    except SMTPAuthenticationError:
        print("The server didn’t accept the username/password combination.")
