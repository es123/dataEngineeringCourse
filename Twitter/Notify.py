import yagmail
from datetime import datetime


class Notify():
    """
    # Initialize smtp server
    """
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.port = 587  # For starttls

    def send_notification(self, sender, pwd, receiver, subj, msg, attachments=None):
        """
        # Send Email notification

        :param sender: sender email account
        :param pwd: sender email account password
        :param receiver: email recipients
        :param subj:email subject
        :param msg: email body message
        :param attachments: email attachments
        """

        self.sender = sender
        self.pwd = pwd
        self.receiver = receiver
        self.subj = subj + ' -' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.body = msg
        self.attachments = attachments

        try:
            # initializing the server connection
            yag = yagmail.SMTP(self.sender, self.pwd)
            yag.send(
                to=self.receiver,
                subject=self.subj,
                contents=self.body,
                attachments=self.attachments
            )
            print("Email sent successfully")
        except:
            print("Error, email was not sent")
