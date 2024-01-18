from flask_mail import Message
from flask import current_app
# from flask_mail import Mail



def send_completion_reminder(email, progress_percentage, week, username,copy_recipients= None):
    from application import mail
    primary_recipient = [email]

    # Access email configuration settings
    default_sender = current_app.config['MAIL_DEFAULT_SENDER']
    

    cc_email = 'cynos1@morgan.edu'
    copy_recipients = copy_recipients or []
    copy_recipients.append(cc_email)

    subject = f'Friendly Reminder: Survey Completion Week {week}'
    
    body = f'''
        <p><b>Dear {username},</b></p>
        <p>We hope this email finds you well. Thank you once again for signing up to participate in this survey. Your insights are incredibly valuable to us. This is a friendly reminder to complete the survey. You have completed <b>{progress_percentage}%</b> of the survey for <b>WEEK {week}</b>.</p>
        <p>If you encounter any issues or have any questions, feel free to reach out to <a href="mailto:cynos1@morgan.edu">cynos1@morgan.edu</a>. Thank you once again for being a crucial part of this research! <br><a href = "https://www.morgan.edu/ceamls/research/labs/data-engineering-and-predictive-analytics-(depa)-lab">DEPA</a> Lab appreciates you!</p>
    '''
    
    

    message = Message(subject=subject, recipients=primary_recipient,cc=copy_recipients, html=body, sender=default_sender)
    
    with open('static/depa_banner1.jpg', 'rb') as logo_file:
        message.attach("depa_banner1.jpg", "image/jpg", logo_file.read())
    mail.send(message)




