import email, smtplib, ssl
import urllib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path

import config

def register_email(firstname, lastname, resiver, verify_code):
    email_file = open("/home/mahyar/W/LMS/LMS/templates/email/register.html")

    # /home/mahyar/W/LMS/LMS/templates/email/index.html
    port = 465  # For SSL
    sender_email = config.EMAIL_USER
    password = config.EMAIL_PASS
    receiver_email = resiver
    message = MIMEMultipart("alternative")
    message["Subject"] = "multipart test"
    message["From"] = sender_email
    message["To"] = receiver_email
    email_url = urllib.parse.quote(resiver)
    html = email_file.read()
    # print(html)
    html = html.format(firstname=firstname,lastname=lastname,verify_code=verify_code,email_url=email_url)
# Turn these into plain/html MIMEText objects

    part = MIMEText(html, "html")


    message.attach(part)


    # Create a secure SSL context
    context = ssl.create_default_context()
    print('stat sending')
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    print('send email')



def welcome_email(firstname, lastname, resiver, verify_code):
    email_file = open("/home/mahyar/W/LMS/LMS/templates/email/index.html")

    # /home/mahyar/W/LMS/LMS/templates/email/index.html
    port = 465  # For SSL
    sender_email = config.EMAIL_USER
    password = config.EMAIL_PASS
    receiver_email = resiver
    message = MIMEMultipart("alternative")
    message["Subject"] = "multipart test"
    message["From"] = sender_email
    message["To"] = receiver_email
    email_url = urllib.parse.quote(resiver)
    html = email_file.read()
    # print(html)
    html = html.format(firstname=firstname,lastname=lastname,verify_code=verify_code,email_url=email_url)
# Turn these into plain/html MIMEText objects

    part = MIMEText(html, "html")


    message.attach(part)


    # Create a secure SSL context
    context = ssl.create_default_context()
    print('stat sending')
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    print('send email')


# emailSender('mahyar', 'kakvand', 'mahyarkakvand85@gmail.com','653967')
