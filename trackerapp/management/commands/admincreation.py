from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password, check_password
import secrets,requests
from trackerapp import util
from trackerapp.util import send, auth, auth_cls,forgot
from trackerapp.models import User,Projects,ProjectVersions,ProjectUsers


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('designation', type=str)
        parser.add_argument('phone_number', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('joined_on', type=str)
    def handle(self, *args, **options):
        user= User.objects.filter()
        name = options['name']
        while not len(name):
            name = input("\n    Enter Your Name Here - (REQUIRED) ")
        email = options['email']
        while not len(email):
            print ("\n    EMAIL NOTE - Valid and active email address.\n")
            email = input("    Enter Email Here - (REQUIRED) ")
            check_user = User.objects.filter(email=str(email))
            if check_user.count():
                print ("\n    **Email "+str(email)+" is already registered. You can directly login Or if forgot password\n    then click forget password link.\n")
                email= ''
        designation = options['designation']
        while not len(designation):
            designation = input("\n    Enter Your Designation Here - (REQUIRED) ")        
        phone_number = options['phone_number']
        if not len(phone_number):
            phone_number = input("\n    Enter Your Phone Number Here - (REQUIRED) ")
        password = options['password']
        if not len(password):
            password = input("\n    Enter Your Password Here - (REQUIRED) ")        
        joined_on = options['joined_on']
        if not len(joined_on):
            joined_on = input("\n    Enter Your Joining Date Here - (REQUIRED) ")        
        print ("\n    Hi "+str(name).title()+", Your Account Created Successfully,Please Login to Continue.\n")
        user = User.objects.create(
            name = name, 
            email=email,
            phone_number=phone_number,
            user_type="ADMIN",
            designation=designation,
            password=make_password(password),
            joined_on=joined_on,
            is_active=True,
            is_blocked=False,
        )
        
                
