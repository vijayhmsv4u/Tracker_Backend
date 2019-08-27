from django.conf.urls import url, include
from trackerapp import views
from rest_framework import routers
from django.contrib import admin
from django.conf import settings
# from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register('tracker/v1.0/userauth', views.UserAuthViewSet) # User CRUD
router.register('tracker/v1.0/projects', views.ProjectsViewSet) # User ProjectDetails CRUD
router.register('tracker/v1.0/versions',views.ProjectVersionsViewSet)
 
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'tracker/v1.0/login', views.user_login), #  User Login 
    url(r'tracker/v1.0/user_confirmation/',views.user_confirmation), # User Confirmation with email-linlk
    url(r'tracker/v1.0/logout', views.user_logout), # User Logout
    url(r'tracker/v1.0/changepassword', views.change_password), # Login User Change Password
    url(r'tracker/v1.0/forgotpasswordemail/',views.password),#forgot password with email link
    url(r'tracker/v1.0/forgot/password/',views.forgot_password),#user Forgot password
    url(r'tracker/v1.0/projectnames',views.search),#user Forgot password
    url(r'tracker/v1.0/emails',views.searchemail),#user Forgot password
    url(r'tracker/v1.0/useradd',views.user_add),
    url(r'tracker/v1.0/names',views.usernames),
    url(r'tracker/v1.0/pronames',views.searchprojects),
    url(r'tracker/v1.0/projectversion',views.project_versions),
    url(r'tracker/v1.0/details',views.project_details),
    url(r'tracker/v1.0/userprojects',views.user_projects),
    ]

# ]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

