#!/usr/bin/python

import smtplib
from datetime import datetime

"""
    Sends an email message through GMail once the script is completed.
    Developed to be used with AWS so that instances can be terminated
    once a long job is done. Only works for those with GMail accounts.

    usr : the GMail username, as a string

    psw : the GMail password, as a string

    fromaddr : the email address the message will be from, as a string

    toaddr : a email address, or a list of addresses, to send the
    message to.
"""



class mailerClass:
    def __init__(self, usr, psw, fromaddr):
        self.usr = usr
        self.psw = psw
        self.fromaddr = fromaddr

    def send(self, toaddr, sub, body):
        # Initialize SMTP server
        server=smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(self.usr, self.psw)

        # Send email
        senddate=datetime.strftime(datetime.now(), '%I:%M %p, %b-%d-%Y')
        subject = "%s - %s" % (senddate, sub)
        #subject="Aquaponics pod stats (sent from our Arduino Yun!)"
        m="Date: %s\r\nFrom: %s\r\nTo: %s\r\nSubject: %s\r\nX-Mailer: My-Mail\r\n\r\n" % (senddate, self.fromaddr, toaddr, subject)
        server.sendmail(self.fromaddr, toaddr, m+body)
        server.quit()

