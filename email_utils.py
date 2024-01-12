from email.mime import application
from flask_mail import Message
from flask import current_app
from flask_mail import Mail

# maindeal
def send_completion_reminder(email, progress_percentage, week, copy_recipients= None):
    from application import mail
    primary_recipient = [email]

    # Access email configuration settings
    default_sender = current_app.config['MAIL_DEFAULT_SENDER']
    mail_server = current_app.config['MAIL_SERVER']
    mail_port = current_app.config['MAIL_PORT']

    copy_recipients = copy_recipients or []
    subject = f'Survey Completion Reminder - Week {week}'
    body = f'Dear participant,\n\nThis is a reminder to complete the survey. You have completed {progress_percentage}% of the survey for Week {week}.\n\nThank you for your participation!'
    
    message = Message(subject=subject, recipients=primary_recipient,cc=copy_recipients, body=body, sender=default_sender)
    mail.send(message)


