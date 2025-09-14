import smtplib
from email.mime.text import MIMEText

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "cybercoder.nishant@gmail.com"
    msg["To"] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.set_debuglevel(1)  # <--- this prints detailed SMTP session
        server.starttls()
        server.login("cybercoder.nishant@gmail.com", "")
        server.send_message(msg)
