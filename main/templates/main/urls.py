from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public home page (landing with signup/login/payment placeholder)
    path("", views.home, name="home"),

    # Authentication
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="main/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),

    # Dashboard (for logged-in teachers)
    path("dashboard/", views.dashboard, name="dashboard"),

    # Export to Excel
    path("export_excel/", views.export_students_excel, name="export_students_excel"),

    # Upload Excel file
    path("upload-excel/", views.upload_excel, name="upload_excel"),

    path("download-template/", views.download_template, name="download_template"),

    path("save-uploaded-students/", views.save_uploaded_students, name="save_uploaded_students"),

]
