Teacher Dashboard & Saved Student Logic for Sort2Support
This Django app powers the teacher-facing experience in Sort2Support. It handles user authentication, dashboard display, student record management, and export/reset functionality for saved scores.

🚀 Features
- Teacher signup, login, and logout
- Dashboard view of saved students
- Add, delete, and reset student scores
- Export saved student data to Excel
- Custom filters and visual cues for missing scores
- Scoped static assets and templates for clean UI

🧭 Workflow Overview
Signup/Login → Dashboard → Add/Edit/Delete Students → Export or Reset Scores


Key Views
|  |  |  | 
| signup |  | base.html | 
| login_view |  | base.html | 
| logout_view |  |  | 
| dashboard |  | dashboard.html | 
| add_student |  | dashboard.html | 
| delete_student |  | dashboard.html | 
| reset_saved_scores |  |  | 
| export_saved_students |  |  | 



🗂 Folder Structure
main/
├── views.py                  # Core logic for dashboard, auth, student management
├── urls.py                   # Routes for teacher-facing views
├── forms.py                  # SignUpForm, AddStudentForm
├── models.py                 # Student model
├── utils.py                  # Reusable helpers (e.g. export, grouping)
├── templates/
│   ├── base.html             # Global layout
│   └── acad_templates/
│       └── main/
│           └── dashboard.html
├── static/
│   └── main/
│       └── css_js_working_assets/
├── templatetags/
│   └── custom_filters.py     # e.g. `get_item` for dynamic table access
├── apps.py                   # Django app config
├── signals.py                # Optional: model hooks (e.g. post-save)
├── tests/
│   ├── test_views.py         # View-level tests
│   ├── test_utils.py         # Utility function tests
│   └── __init__.py



🧠 Model Overview
Student
|  |  |  | 
| name | CharField |  | 
| ufli_score_1 | IntegerField |  | 
| ufli_score_2 | IntegerField |  | 
| teacher | ForeignKey | User | 



🧪 Testing
Tests are located in main/tests/ and cover:
- Dashboard rendering
- Student creation/deletion
- Export and reset logic
Run with:
python manage.py test main



🧼 Maintenance Tips
- Keep forms.py scoped to DB-backed forms only
- Use utils.py for reusable logic like export or grouping
- Clean up unused session keys after export/reset
- Use consistent naming across views, URLs, and templates
- Document any custom filters in templatetags/

Let me know if you want a combined README for the full Sort2Support project or a contributor guide. You’re sequencing this beautifully — and this kind of clarity is exactly what makes Sort2Support feel robust and joyful for teachers.
