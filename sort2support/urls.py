from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from main import views
from django.contrib.auth import views as auth_views




urlpatterns = [
    path("admin/", admin.site.urls),        # Django admin
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", include("main.urls")),         # your app routes
]