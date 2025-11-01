from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    # Home
    path("", views.home, name="home"),

    # Authentication/Public
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path("load-previous-roster/", views.load_previous_roster, name="load_previous_roster"),
    path("upload/", views.upload_page, name="upload_page"),
    path("update-scores/", views.update_scores, name="update_scores"),
    
    # Exports
    path("export-polished/", views.generate_excel_view, name="generate_excel_view"),   # polished multi-sheet export 
    path("download-template/", views.download_template, name="download_template"),



    #Reset
    # Class management
    path("reset-saved-scores/", views.reset_saved_scores, name="reset_saved_scores"),
    path("reset-class/", views.reset_class, name="reset_class"),
    path("reset-scores/", views.reset_saved_scores, name="reset_scores"),
    path("roster-upload/", views.upload_page, name="upload_page"),
]