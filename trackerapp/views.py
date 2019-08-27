from django.shortcuts import render
import secrets, os
from . import models
from trackerapp.models import User,Projects,ProjectVersions,ProjectUsers
from rest_framework import viewsets, response, decorators, status
from . serializers import UserSerializer,UserResponseSerializer, ProjectsSerializer, ProjectVersionsResponseSerializer,ProjectVersionsSerializer,ProjectUsersSerializer,ProjectsResponseSerializer, TestSerializer,VersionsSerializer
from django.contrib.auth.hashers import make_password, check_password
from trackerapp import util
from trackerapp.util import send, auth, auth_cls,forgot,invite
from django.contrib import messages
from django.conf import settings
import django_filters.rest_framework
from rest_framework import filters
import requests,ast
from django.db.models import Q

@decorators.api_view(['GET'])
def usernames(request):
    data=request.data
    search=request.GET.get('search',None)
    if search !=None:
        names=User.objects.filter(name__icontains=search)
        print(names,'......')
        serializer = UserResponseSerializer(names, many=True)
        return response.Response({'result':serializer.data,'message':"list of Users"}, status=status.HTTP_200_OK )

@decorators.api_view(['GET'])
def searchprojects(request):
    data=request.data
    search=request.GET.get('search',None)
    if search !=None:
        projects=Projects.objects.filter(project_name__icontains=search)
        serializer = ProjectsSerializer(projects, many=True)
        return response.Response({'result':serializer.data,'message':"list of Projects"}, status=status.HTTP_200_OK )


@decorators.api_view(['GET'])
def search(request):
    data=request.data
    search=request.GET.get('search',None)
    if search !=None:
        names=Projects.objects.filter(project_name__icontains=search).values_list('project_name', flat=True)
        return response.Response({'result':names,'message':"list of Project Names"}, status=status.HTTP_200_OK )
    else:
        names=ProjectDetails.objects.values_list('project_name', flat=True)
        return response.Response({'result':names,'message':"list of Project Names"}, status=status.HTTP_200_OK )


@decorators.api_view(['GET'])
def searchemail(request):
    data=request.data
    search=request.GET.get('search',None)
    if search !=None:
        emails=User.objects.filter(email__icontains=search).values_list('email', flat=True)
        return response.Response({'result':emails,'message':"list of emails"}, status=status.HTTP_200_OK )
    else:
        emails=User.objects.values_list('email', flat=True)
        return response.Response({'result':emails,'message':"list of emails"}, status=status.HTTP_200_OK )
    


class UserAuthViewSet(viewsets.GenericViewSet):
    queryset = User.objects.filter() 
    serializer_class = UserSerializer
    
    @auth_cls
    def list(self, request, *args, **kwargs):
        """
            GET /userauth/
            Response Type - JSON
            List Of All Roles with/Without filter 

        """
        request.data['actor'] = request.auth
        user=User.objects.filter(id=request.auth.id)
        if user.count() and user[0].user_type=='ADMIN':
            queryset = self.get_queryset()
            serializer = UserResponseSerializer(queryset, many=True)
            return response.Response({'result':serializer.data,'message':"List Of All Users"}, status=status.HTTP_200_OK )
        else:
            return response.Response({'message':"You Are Not Admin To Access"}, status=status.HTTP_400_BAD_REQUEST )

    def create(self, request, *args, **kwargs):
        """
            POST /userauth/
            Response Type - JSON
            Create/Add New User 
        """
        data= request.data
        token = secrets.token_urlsafe(20)
        serializer= self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if 'HTTP_ORIGIN' in request.META:
            hit_url=request.META["HTTP_ORIGIN"]
            url= str(hit_url)+'/tracker/v1.0/user_confirmation/?token='+str(token)+'&user='+data['email']
            send(data['email'],url)
            return response.Response({'result':serializer.data, 'message':"Verification Email Has Sent Successfully"}, status=status.HTTP_200_OK)
        else:
            url= settings.IP_ADDRESS+'/tracker/v1.0/user_confirmation/?token='+str(token)+'&user='+data['email']
            send(data['email'],url)
            return response.Response({'result':serializer.data, 'message':"Verification Email Has Sent Successfully"}, status=status.HTTP_200_OK)
    

    @auth_cls
    def update(self, request, *args, **kwargs):
        """
            PUT /userauth/{id}
            Response Type - JSON
            Updates User's Details By ID
        """
        user=User.objects.filter(id=request.auth.id)
        print(user,'-----user')
        if user.count() and user[0].user_type =='ADMIN':
            queryset=self.get_object()
            if 'is_blocked' in request.data and request.data['is_blocked']:
                queryset.is_blocked = request.data['is_blocked']
                queryset.is_active = False
                queryset.save()
            else:
                queryset.is_blocked=request.data['is_blocked']
                queryset.is_active=True
                queryset.save()
        elif user.count() and user[0].user_type =='USER':
            queryset = self.get_object()
            if 'name' in request.data:
                queryset.name = request.data['name']
                queryset.save()
            if 'phone_number' in request.data:
                queryset.phone_number = request.data['phone_number']
                queryset.save()
            if 'designation' in request.data:
                queryset.designation = request.data['designation']
                queryset.save()
            if 'joined_on' in request.data:
                queryset.joined_on = request.data['joined_on']
                queryset.save()
        serializer = self.get_serializer(queryset)
        return response.Response({'result':serializer.data,'message':"Successfully Updated"}, status=status.HTTP_200_OK )

    @auth_cls
    def retrieve(self, request, *args, **kwargs):
        """
            GET /userauth/{id}
            Response Type - JSON
            Retrive user_type By ID
        """
        request.data['actor'] = request.auth
        user=User.objects.filter(id=request.auth.id)
        if user.count() and user[0].user_type=='ADMIN':
            queryset = self.get_object()
            self.serializer_class = UserResponseSerializer
            serializer = self.get_serializer(queryset)
            return response.Response({'result':serializer.data,'message':"User Successfully Retrived"},status=status.HTTP_200_OK )
        else:
            queryset = self.get_object()
            self.serializer_class = UserSerializer
            serializer = self.get_serializer(queryset)
            return response.Response({'result':serializer.data,'message':"User Successfully Retrived"},status=status.HTTP_200_OK )
        
    @auth_cls
    def delete(self, request, *args, **kwargs):
        """
            DELETE /userauth/{id}
            Response Type - JSON
            DELETE  UserBy ID

        """
        request.data['actor'] = request.auth
        user= User.objects.filter(id=request.auth.id)
        if user.count():
            user=user[0]
            if user.user_type == 'ADMIN':
                queryset = self.get_object()
                queryset.delete()
                serializer = self.get_serializer(queryset) 
                return response.Response({'result':serializer.data,'message':"Deleted Successfully"}, status=status.HTTP_200_OK )
            else:
                return response.Response({'message':"You Are Not Admin To Access"}, status=status.HTTP_400_BAD_REQUEST )
        
@decorators.api_view(['POST'])
def user_login(request):
    """
        POST/login/
        For User Signin
        User will provide Email and Password for their account.
        On Success, User will get success message.

    """
    data = request.data
    user = User.objects.filter(email= data['email'])
    if not user.count():
        return response.Response({'message':"Email Doesnot Exist"}, status=status.HTTP_400_BAD_REQUEST)
    user=user[0] 
    if check_password(data['password'], user.password):
        if 'email' in request.data and 'password' in request.data:
            if user.is_active:
                if not user.is_blocked:
                    reset_code = secrets.token_urlsafe(20)
                    user.reset_code= reset_code
                    user.save()
                else:
                    return request.Response({'message':"Your Account is Deactivated"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return request.Response({'message':"Please Activate Your Account"}, status=status.HTTP_401_UNAUTHORIZED)
            serializer= UserSerializer(user)
            return response.Response({'result':serializer.data, 'message': "You Are Successfully SignedIn"}, status=status.HTTP_200_OK)
        return response.Response({'message':"Email/Password are required Fields"}, status=status.HTTP_401_UNAUTHORIZED)
    return response.Response({'message':"Invalid Password"}, status=status.HTTP_401_UNAUTHORIZED)


@decorators.api_view(['POST'])
def user_confirmation(request):

    """
        POST /cvbank/v1/user_confirmation/token/email
        Response Type - JSON
        User Activation By Email&Token
    """ 
    data= request.data
    token = request.GET.get('token')
    email = request.GET.get('user')
    user = User.objects.filter(token = token)
    if not user.count():
        return response.Response({'message':"Please Provide Proper Email"}, status=status.HTTP_401_UNAUTHORIZED)
    if user[0].is_active:
        return response.Response('User is Already Activated')
    if user.count():
        user = user[0]
        user.password = make_password(data['password'])
        user.is_active = True
        user.is_blocked = False
        user.save()
        return response.Response('Successfully Created')
    return response.Response({'message':'Please provide Proper Details'},status=status.HTTP_401_UNAUTHORIZED)

@decorators.api_view(['GET'])
@auth
def user_logout(request):
    """
        GET /user_logout/{id}
        Response Type - JSON
        Logout User By ID
    """
    access_token= request.headers['Authorization'].split('Bearer')[1].strip()
    user=User.objects.filter(reset_code=access_token)[0]
    user.reset_code=None
    user.save()
    return response.Response({'message':'Logged Out Successfully'}, status=status.HTTP_200_OK)


@decorators.api_view(['POST'])   
@auth                                                          
def change_password(request):
    """
        POST /changepassword/
        Response Type - JSON
        Login User Can Change User Password
    """
    data= request.data
    if 'password' not in data:
        return response.Response({'message':"Please Provide Password"}, status=status.HTTP_400_BAD_REQUEST)
    if 'newpassword' not in data:
        return response.Response({'message':"Please Provide NewPassword"}, status=status.HTTP_400_BAD_REQUEST)
    if 're-newpassword' not in data:
        return response.Response({'message':"Please Provide Re-NewPassword"}, status=status.HTTP_400_BAD_REQUEST)
        
    userdetails= request.auth.reset_code
    user= User.objects.filter(reset_code= userdetails)
    if user.count():
        user= user[0]
    else:
        return response.Response({'message':"User Not Found"}, status=status.HTTP_400_BAD_REQUEST)
    if check_password(data['password'], user.password):
        if 'password' in request.data:
            if user.is_active:            
                if request.data['newpassword'] != request.data['re-newpassword']:
                    return response.Response({'message':"NewPassword not matched with Re-NewPassword"}, status=status.HTTP_400_BAD_REQUEST)
                else:                
                    user.password = make_password(data['newpassword'])  
                    user.save()
                    serializer= UserSerializer(user)
            return response.Response({ 'result':serializer.data,'message': "Your Password Changed Successfully"}, status=status.HTTP_200_OK)
        else:
            return response.Response({'message':"Your Account is InActive"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return response.Response({'message':"Please Provide Previous Password"}, status=status.HTTP_400_BAD_REQUEST)


@decorators.api_view(['POST'])
def password(request):
    data = request.data    
    email = data['email']   
    user = User.objects.filter(email = email)
    if not user.count():
        return response.Response('Email Doesnot Exist')
    token = secrets.token_urlsafe(20)
    if user.count():
        user=user[0]
        user.token=token
        user.save()
    if 'HTTP_ORIGIN' in request.META:
        hit_url=request.META["HTTP_ORIGIN"]        
        url= str(hit_url)+'/forgot/password/?token='+str(token)+'&user='+data['email']
        forgot(data['email'],url)
        return response.Response("Forgot Password Link has been Sent to your Email")
    else:
        url= settings.IP_ADDRESS+'/forgot/password/?token='+str(token)+'&user='+data['email']
        forgot(data['email'],url)
        return response.Response("Forgot Password Link has been Sent to your Email")


@decorators.api_view(['POST'])
def forgot_password(request):
    data= request.data
    token = request.GET.get('token')
    email = request.GET.get('user')

    user = User.objects.filter(email = email)
    if not user.count():
        return response.Response('Email Doesnot Exist')
    if user.count():
        user = user[0]
        user.password = make_password(data['newpassword'])
        user.save()
        return response.Response('Password Changed Succcessfully')
    return response.Response('Please provide Proper Details')


class ProjectsViewSet(viewsets.GenericViewSet):
    queryset = Projects.objects.all() 
    serializer_class = ProjectsSerializer
    
    @auth_cls
    def list(self, request, *args, **kwargs):
        """
            GET /ProjectDetails/
            Response Type - JSON
            List Of All ProjectDetails
        """       
        user=User.objects.filter(id=request.auth.id)
        if user.count() and user[0].user_type =='ADMIN':
            queryset = Projects.objects.all()
            serializer = ProjectsSerializer(queryset, many=True)
            return response.Response({'result':serializer.data,'message':"List Of All Users Project Details"}, status=status.HTTP_200_OK )           
        if user.count():
            queryset= ProjectUsers.objects.filter(user=request.auth.id)
            serializer = TestSerializer(queryset, many=True)
            return response.Response({'result':serializer.data,'message':"List Of  User Projects"}, status=status.HTTP_200_OK )


    @auth_cls
    def retrieve(self, request, *args, **kwargs):
        """
            GET /ProjectDetails/{id}
            Response Type - JSON
            List Of Particular ProjectDetails By ID
        """
        data=request.data
        user=User.objects.filter(id=request.auth.id)
        if user.count() and user[0].user_type=='ADMIN':
            queryset = self.get_object()
            serializer = ProjectsResponseSerializer(queryset)
            return response.Response({'result':serializer.data,'message':"List Of  Project Details"}, status=status.HTTP_200_OK )
        else:
            queryset = self.get_object()
            serializer = ProjectsResponseSerializer(queryset)
            return response.Response({'result':serializer.data,'message':"List Of Project Details"}, status=status.HTTP_200_OK)

    @auth_cls
    def create(self, request, *args, **kwargs):
        """
            POST /ProjectDetails/
            Response Type - JSON
            Create's User ProjectDetails
        """
        data=request.data
        project = Projects.objects.filter(project_name=data['project_name'])
        if project.count():
            project= project[0]
            if "is_hosted" in request.data and request.data["is_hosted"]:
                pro_ver = ProjectVersions.objects.filter(project=project)
                if pro_ver.count() and pro_ver[0].version==data['version']:
                    return response.Response({'message':'Project Details Already Exist'},status=status.HTTP_400_BAD_REQUEST)
                else:
                    project_versions=ProjectVersions.objects.create(
                        project=project,
                        created_by=request.auth,
                        updated_by=request.auth,
                        repo_url = data['repo_url'],
                        is_hosted=data['is_hosted'],
                        hosted_username=data['hosted_username'],
                        hosted_password=data['hosted_password'],
                        hosted_ip_address=data['hosted_ip_address'],
                        version=data['version'],
                        postman_link=data['postman_link'],
                        status=data['status']
                    )
            else:
                project_version=ProjectVersions.objects.create(
                    project=project,
                    created_by=request.auth,
                    updated_by=request.auth,
                    repo_url = data['repo_url'],
                    postman_link=data['postman_link'],
                    status=data['status'],
                    is_hosted=data['is_hosted'],
                    version=data['version']
                )        
        else:
            project=Projects.objects.create(
                project_name=data['project_name'],
                created_by=request.auth,
                updated_by=request.auth,            
                )
            if "is_hosted" in request.data and request.data["is_hosted"]:                
                project_versions=ProjectVersions.objects.create(
                    project=project,
                    created_by=request.auth,
                    updated_by=request.auth,
                    repo_url = data['repo_url'],
                    is_hosted=data['is_hosted'],
                    hosted_username=data['hosted_username'],
                    hosted_password=data['hosted_password'],
                    hosted_ip_address=data['hosted_ip_address'],
                    version=data['version'],
                    postman_link=data['postman_link'],
                    status=data['status']
                )
            else:
                project_version=ProjectVersions.objects.create(
                    project=project,
                    created_by=request.auth,
                    updated_by=request.auth,
                    repo_url = data['repo_url'],
                    postman_link=data['postman_link'],
                    status=data['status'],
                    is_hosted=data['is_hosted'],
                    version=data['version']
                )
            user=User.objects.filter(id=request.auth.id)
            if user.count() and user[0].user_type=='ADMIN':
                if 'developers' in request.data:
                    for each in data['developers']:
                        user=User.objects.filter(email=each['email'])
                        if not user.count():
                            token = secrets.token_urlsafe(20)
                            user=User.objects.create(email=each['email'])
                            if 'HTTP_ORIGIN' in request.META:
                                hit_url=request.META["HTTP_ORIGIN"]
                                url= str(hit_url)+'/tracker/v1.0/user_confirmation/?token='+str(token)+'&user='+each['email']
                                invite(each['email'],url)                                
                            else:
                                url= settings.IP_ADDRESS+'/tracker/v1.0/user_confirmation/?token='+str(token)+'&user='+each['email']
                                invite(each['email'],url)                            
                            project_user=ProjectUsers.objects.create(project=project,user=user,role=each['role'])
                        else:
                            project_user=ProjectUsers.objects.create(project=project,user=user[0],role=each['role'])
            else:              
                project_user=ProjectUsers.objects.create(project=project,user=user[0],role=data['role'])
        serializer=ProjectsSerializer(project)
        return response.Response({'result':serializer.data, 'message':"ProjectDetails Created Successfully"}, status=status.HTTP_200_OK)
    # @auth_cls
    # def update(self, request, *args, **kwargs):
    #     """
    #         PUT /ProjectDetails/{id}
    #         Response Type - JSON
    #         Update User ProjectDetails By ID
    #     """
    #     queryset = self.get_object()
    #     data=request.data
    #     need_to_save = False
    #     if 'project_name' in request.data:
    #         queryset.project_name = request.data['project_name']
    #         need_to_save=True
    #     if need_to_save:
    #         queryset.updated_by= request.auth
    #         queryset.save()

    #     projects=ProjectVersions.objects.filter(project=queryset.id)
    #     projects=projects[0]
    #     need_to_save = False    
    #     if 'repo_url' in request.data:
    #         projects.repo_url = request.data['repo_url']
    #         need_to_save= True
    #     if 'status' in request.data:
    #         projects.status = request.data['status']
    #         need_to_save= True
    #     if 'postman_link' in request.data:
    #         projects.postman_link = request.data['postman_link']
    #         need_to_save= True
    #     if 'is_hosted' in request.data:
    #         projects.is_hosted = request.data['is_hosted']
    #         need_to_save= True
    #     if 'hosted_username' in request.data:
    #         projects.hosted_username = request.data['hosted_username']
    #         need_to_save= True
    #     if 'hosted_password' in request.data:
    #         projects.hosted_password = request.data['hosted_password']
    #         need_to_save= True
    #     if 'hosted_ip_address' in request.data:
    #         projects.hosted_ip_address = request.data['hosted_ip_address']
    #         need_to_save= True
    #     if need_to_save:
    #         projects.updated_by=request.auth
    #         projects.save()
    #     serializer = self.get_serializer(queryset)
    #     return response.Response({'result':serializer.data,'message':"Successfully Updated"}, status=status.HTTP_200_OK )        
    @auth_cls
    def delete(self, request, *args, **kwargs):
        """
            DELETE /projectdetails/{id}
            Response Type - JSON
            Deleting A Projects
        """

        request.data['actor'] = request.auth


        user= User.objects.filter(id=request.auth.id)
        if user.count() and user[0].user_type=='ADMIN':
            queryset = self.get_object()
            queryset.delete()
            serializer = self.get_serializer(queryset) 
            return response.Response({'result':serializer.data,'message':"Deleted Successfully"}, status=status.HTTP_200_OK )
        else:
            return response.Response({'message':"You Are Not Admin To Access"}, status=status.HTTP_400_BAD_REQUEST )
    
class ProjectVersionsViewSet(viewsets.GenericViewSet):
    
    queryset = ProjectVersions.objects.filter() 
    serializer_class = ProjectVersionsSerializer

    @auth_cls
    def update(self, request, *args, **kwargs):
        """
            PUT /ProjectVersions/{id}
            Response Type - JSON
            Update User ProjectVersios By ID
        """
        queryset = self.get_object()
        request.data['actor'] = request.auth.id       
        data=request.data
        need_to_save = False           
        if 'repo_url' in request.data:
            queryset.repo_url = request.data['repo_url']
            need_to_save=True
        if 'status' in request.data:
            queryset.status = request.data['status']
            need_to_save=True
        if 'postman_link' in request.data:
            queryset.postman_link = request.data['postman_link']
            need_to_save=True
        if 'is_hosted' in request.data:
            queryset.is_hosted = request.data['is_hosted']
            need_to_save=True
        if 'hosted_username' in request.data:
            queryset.hosted_username = request.data['hosted_username']
            need_to_save=True
        if 'hosted_password' in request.data:
            queryset.hosted_password = request.data['hosted_password']
            need_to_save=True
        if 'hosted_ip_address' in request.data:
            queryset.hosted_ip_address = request.data['hosted_ip_address']
            need_to_save=True
        if need_to_save:
            queryset.updated_by=request.auth
            queryset.save()
        project=Projects.objects.filter(id=queryset.project_id)
        if project.count():
            project=project[0]
            if 'project_name' in request.data:
                project.project_name=request.data['project_name']
                need_to_save=True
            if need_to_save:
                project.updated_by=request.auth
                project.save()
        serializer = ProjectVersionsResponseSerializer(queryset)
        return response.Response({'result':serializer.data,'message':"Successfully Updated"}, status=status.HTTP_200_OK )   

@decorators.api_view(['POST'])
@auth                                                          
def user_add(request):
    data=request.data
    project_name=data['project_name']
    project_role=data['role']
    user=User.objects.filter(id=request.auth.id)
    if user.count():
        user=user[0]
        email=user.id
        project=Projects.objects.filter(project_name=project_name)
        pro_users=ProjectUsers.objects.filter(project=project[0])
        if pro_users.count() and pro_users[0].user==request.auth:
            return response.Response({"message":"You Are Already Exist In Project "},status=status.HTTP_400_BAD_REQUEST)        
        project_user=ProjectUsers.objects.create(role=project_role,user=request.auth,project=project[0])
        serializer=ProjectUsersSerializer(project_user)
        return response.Response({'result':serializer.data,"message":"you are Successfully Added to the Project"},status=status.HTTP_200_OK)
    else:
        return response.Response({'message':"Create a New Project"}, status=status.HTTP_400_BAD_REQUEST )


@decorators.api_view(['GET'])
@auth                                                          
def project_versions(request):
    data=request.data
    project=request.GET.get('project_id')
    user=ProjectVersions.objects.filter(project=project)
    serializer=VersionsSerializer(user,many=True)
    return response.Response({'result':serializer.data,"message":"List Of Project versions"},status=status.HTTP_200_OK)

@decorators.api_view(['GET'])
@auth                                                          
def project_details(request):
    data = request.data
    version = request.GET.get('version_id')
    details = ProjectVersions.objects.filter(id=version)
    details=details[0]
    serializer=ProjectVersionsResponseSerializer(details)
    return response.Response({'result':serializer.data,"message":"List Of Project Details"},status=status.HTTP_200_OK)

@decorators.api_view(['GET'])
@auth                                                          
def user_projects(request):
    data=request.data
    user=request.GET.get('user_id')
    projects=ProjectUsers.objects.filter(user=user)
    serializer=ProjectUsersSerializer(projects,many=True)
    return response.Response({'result':serializer.data,"message":"List Of Projects"},status=status.HTTP_200_OK)
