from google.appengine.api import mail
from google.appengine.ext import webapp

class SendMail(webapp.RequestHandler):
 
   def post(self):
        to_addr = "foipenalti@foipenalti.com"
 
        message = mail.EmailMessage()
        message.sender = self.request.get("email")
        message.to = to_addr
        message.body = "de:%s<BR>%s" % (self.request.get("nome"), self.request.get("body"))
        message.send()
