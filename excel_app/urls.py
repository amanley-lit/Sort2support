from django.urls import path, include
from . import views

app_name = "excel_app"

urlpatterns = [
    # 🧹 Session Management
    path('reset/', views.reset_session, name='reset_session'),
    path('clear_preview_scores/', views.clear_preview_scores, name='clear_preview_scores'),

    # 👩‍🏫 Student Management
    path('add-student/', views.add_student, name='add_student'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('edit_uploaded_score/', views.edit_uploaded_score, name='edit_uploaded_score'),
    path('save-student_scores/', views.save_student_scores, name='save_student_scores'),
    


    # 📥 Upload & Preview
    path('parse_excel_upload/', views.parse_excel_upload, name='parse_excel_upload'), # Handles Excel file upload and parsing (backend logic)
    path('preview_uploaded_students/', views.preview_uploaded_students, name='preview_uploaded_students'), # Returns parsed student data for preview (AJAX)
    path("excel-preview/", views.parse_excel_upload, name="excel_preview"), # Optional: alternate route for frontend preview
    path("save/", views.save_students, name="save_students"),


    # 📚 Lesson & Group Assignment
    path('load_ufli_lessons/', views.load_ufli_lessons, name='load_ufli_lessons'),

    # 📤 Export & Download
    path("download-template/", views.download_template, name="download_template"),

]