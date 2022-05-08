import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader, select_autoescape

jinja_env = Environment(
    loader=FileSystemLoader(searchpath="app/api/emails/templates/"),
    autoescape=select_autoescape(),
)
template = jinja_env.get_template("welcome-email.html")

app_email: str = os.getenv("GMAIL_EMAIL", "")
app_password: str = os.getenv("GMAIL_EMAIL_PASSWORD", "")
email_port: int = int(os.getenv("GMAIL_EMAIL_PORT", 465))

email_message = MIMEMultipart("alternative")
email_message["Subject"] = "Welcome to Nemo"
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
    with smtplib.SMTP_SSL("smtp.gmail.com", email_port, context=context) as server:
        server.login(app_email, app_password)
        server.sendmail(app_email, receiver_email, email_message.as_string())


if __name__ == "__main__":
    send_email("Rupayan", "rupayan98@gmail.com")
