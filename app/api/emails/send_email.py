import os

import resend
from jinja2 import Environment, FileSystemLoader, select_autoescape

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

jinja_env = Environment(
    loader=FileSystemLoader(searchpath="app/api/emails/templates/"),
    autoescape=select_autoescape(),
)
template = jinja_env.get_template("welcome-email.html")


def create_email(receiver_fullname: str):
    ctx = {"full_name": receiver_fullname}
    output = template.render(ctx=ctx)
    return output


def send_email(receiver_fullname: str, receiver_email: str):
    html_content = create_email(receiver_fullname=receiver_fullname)
    resend.api_key = RESEND_API_KEY
    r = resend.Emails.send(
        {
            "from": "mynoiist@gmail.com",
            "to": receiver_email,
            "subject": "Welcome to Nemo",
            "html": html_content,
        }
    )


if __name__ == "__main__":
    send_email("", "")
