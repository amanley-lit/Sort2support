from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.contrib import admin 

from django.urls import path, re_path
from .views import under_construction

urlpatterns = [
    path('', under_construction),
    re_path(r'^.*$', under_construction),
]

#urlpatterns = [
    # Home page (landing for signup/login)
#    path("home/", views.home, name="home"),
#    path("", views.home, name="home"),   # root URL shows home page

#    # Authentication
#    path("signup/", views.signup, name="signup"),
#    path("login/", auth_views.LoginView.as_view(template_name="main/login.html"), name="login"),
#    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),

    # Dashboard (only for logged-in users)
#    path("dashboard/", views.dashboard, name="dashboard"),
    
#    path("upload-excel/", views.upload_excel, name="upload_excel"),

#    path("download-template/", views.download_template, name="download_template"),
#    path("save-uploaded-students/", views.save_uploaded_students, name="save_uploaded_students"),

    # export to excel
#    path("export-excel/", views.export_excel, name="export_excel"),

    # Clear student names
#    path("clear-names/", views.clear_names, name="clear_names"),

#    path("reset-class/", views.reset_class, name="reset_class"),

#]