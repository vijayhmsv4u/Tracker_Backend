
import smtplib 
from trackerapp.models import User,Projects,ProjectVersions,ProjectUsers
from rest_framework import response, status
import requests, urllib, datetime, os, webbrowser
from django.conf import settings



# creates SMTP session 
def send(mail,url):
    '''
        It sends an email for verification
    '''
    link=smtplib.SMTP('smtp.gmail.com',587)
    link.starttls()
    message = 'Subject: {}\n\n{}'.format("Welcome to NexiiTracker", str("Please Signup By Clicking Link - "+str(url)))
    link.login(settings.USEREMAIL,settings.PASSWORD)
    link.sendmail(settings.USEREMAIL,mail,message)
    link.quit()

def invite(mail,url):
    '''
        It sends an email for verification
    '''
    link=smtplib.SMTP('smtp.gmail.com',587)
    link.starttls()
    message = 'Subject: {}\n\n{}'.format("Welcome to NexiiTracker", str("You are Invited for a Project, Please Signup By Clicking Link to Join - "+str(url)))
    link.login(settings.USEREMAIL,settings.PASSWORD)
    link.sendmail(settings.USEREMAIL,mail,message)
    link.quit()

def forgot(mail,url):
    '''
        It sends an email for forgotpassword
    '''
    link=smtplib.SMTP('smtp.gmail.com',587)
    link.starttls()
    message = 'Subject: {}\n\n{}'.format("Forget password",str("Please Click Link To Change Password - "+str(url)))
    link.login(settings.USEREMAIL,settings.PASSWORD)
    link.sendmail(settings.USEREMAIL,mail,message)
    link.quit()


def auth(func):
    """
        Allows The User BY Authenticating 
    """
    def wrap(request, *args, **kwargs):
        if 'Authorization' in request.headers:      
            access_token= request.headers['Authorization'].split('Bearer')[1].strip()
            session= User.objects.filter(reset_code=access_token)
            if session.count():
                request.auth= session[0]
            else:
                return response.Response({'message':"Please Re-Login"}, status=status.HTTP_401_UNAUTHORIZED)
            return func(request, *args, **kwargs)

    wrap.__doc__= func.__doc__
    wrap.__name__= func.__name__
    return wrap

def auth_cls(func):
    """
        Allows The User BY Authenticating 
    """
    def wrap(cls, request, *args, **kwargs):
        if 'Authorization' in request.headers:      
            access_token= request.headers['Authorization'].split('Bearer')[1].strip()
            session= User.objects.filter(reset_code=access_token)
            if session.count():
                request.auth= session[0]
            else:
                return response.Response({'message':"Please Re-Login"}, status=status.HTTP_401_UNAUTHORIZED)
        return func(cls, request, *args, **kwargs)


    wrap.__doc__= func.__doc__
    wrap.__name__= func.__name__
    return wrap