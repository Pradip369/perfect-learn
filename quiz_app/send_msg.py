from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives
from django.conf import settings
import threading
import requests
import json

class EmailThread(threading.Thread):
    def __init__(self,template,subject,receiver_email,**kwargs):
        self.template = template
        self.subject = subject
        self.receiver_email = receiver_email
        self.kwargs = kwargs
        threading.Thread.__init__(self)
    
    def run(self):
        try:
            email_template = render_to_string(self.template,self.kwargs)    
            email_content = EmailMultiAlternatives(
                            self.subject, 
                            None,
                            settings.EMAIL_HOST_USER, 
                            [self.receiver_email],
                        )
            email_content.attach_alternative(email_template, 'text/html')
            email_content.send()
        except Exception:
            return None

def send_email(template,subject,receiver_email,**kwargs):
    return EmailThread(template, subject, receiver_email,**kwargs).start()


class SMSThread(threading.Thread):
    def __init__(self,mobile_no,domain,username):
        self.mobile_no = mobile_no
        self.domain = domain
        self.username = username
        threading.Thread.__init__(self)

    def run(self):
        try:
            url = "https://www.fast2sms.com/dev/bulkV2"
            headers = {
                "authorization":settings.SMS_SECRET_KEY,
                "Content-Type":"application/json",
                }
            msg = f"Welcome {self.username}, Your account successfully activated at ITSE. Now you can access all the features of this site."
            payload = {
                    "route" : "v3",
                    "sender_id" : settings.SENDER_ID,
                    "message" : msg,
                    "language" : "english",
                    "flash" : 0,
                    "numbers" : self.mobile_no,
                    }

            requests.post(url, data =json.dumps(payload),headers = headers)
            
            # returned_msg = json.loads(response.text)
            # print(returned_msg['message'])
            # print(response.text)

        except Exception as e:
            return None

def send_sms(mobile_no,domain,username):
    return SMSThread(mobile_no,domain,username).start()