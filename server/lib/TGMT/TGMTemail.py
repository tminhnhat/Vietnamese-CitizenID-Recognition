import time
from django.core.mail import send_mail
from django.conf import settings
import threading
from django.utils.html import strip_tags
from api.apps import *
from api.views.log import WriteLog

####################################################################################################

def SendEmailAsync(subject, html_content, recipient_list):
    if(subject == None or html_content == None or recipient_list == None):
        return False

    EmailThread(subject, html_content, recipient_list).start()        


####################################################################################################

class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        if(type(recipient_list) == type([])):
            self.recipient_list = recipient_list
        else:
            self.recipient_list = [recipient_list]
        self.html_content = html_content
        threading.Thread.__init__(self)

    def run (self):
        try:
            result = send_mail(self.subject,
                self.html_content,
                settings.EMAIL_SENDER,
                self.recipient_list,
                html_message = self.html_content,
                fail_silently=False)
            if(result > 0):
                printt("Send email to " + str(self.recipient_list) + " success")
            else:
                printt("Send email to " + str(self.recipient_list) + " failed")
        except Exception as e:    
            err = str(e)
            printt(err)
            WriteLog("Send email failed", err)
            if("_ssl.c:2805" in err):
                time.sleep(5)
                self.run()