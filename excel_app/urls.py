from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload'),  # Table view
    path('export/', views.export_excel, name='export'),
    path('clear-scores/', views.clear_scores, name='clear_scores'),
    path('clear-names/', views.clear_names, name='clear_names'),
]
