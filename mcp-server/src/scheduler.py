from apscheduler.schedulers.background import BackgroundScheduler
import time
from email_utils import send_email

scheduler = BackgroundScheduler()
scheduler.start()

# Example function to send reminder
def remind_user(user_email, subject):
  try:
    print(f"Sending reminder to {user_email}")
    send_email(user_email, "Reminder from Trackl", f"This is a reminder email to {subject}.")
    print(f"Reminder sent to {user_email}")
  except Exception as e:
      # Print traceback for debugging
    import traceback
    print(f"Error sending email to {email}: {e}")
    traceback.print_exc()
