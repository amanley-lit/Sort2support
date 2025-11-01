Excel Upload & Preview Module for Sort2Support
This Django app handles the full lifecycle of uploading, parsing, previewing, editing, and saving student score data from Excel files. It’s designed to support teacher workflows with clarity, flexibility, and robust error handling.

🚀 Features
- Upload .xlsx files with student scores
- Normalize headers and deduplicate entries
- Preview parsed data before saving
- Edit scores via formset before committing
- Save scores to database
- Export preview or saved data to Excel
- Reset scores or session state
- Custom filters and visual cues for missing data

🧭 Workflow Overview
Excel Upload → Parse & Normalize → Preview Table → Edit Scores (optional) → Save to DB → Export


Key Views
|  |  |  | 
| parse_excel_upload |  | preview.html | 
| edit_uploaded_scores |  | upload.html | 
| preview_uploaded_students |  | preview.html | 
| save_student_scores |  |  | 
| clear_preview_scores |  |  | 
| export_preview_excel |  |  | 
| reset_saved_scores |  |  | 
| export_saved_students |  |  | 



🗂 Folder Structure
excel_app/
├── views.py                  # Core view logic
├── urls.py                   # Routes (namespaced as studentdataentry)
├── forms.py                  # Formsets for score editing
├── utils/
│   ├── parse_excel.py        # Excel parsing and normalization
│   ├── grouping.py           # Instructional grouping logic
│   └── export_excel.py       # Workbook generation
├── templates/
│   └── excel_app/
│       ├── preview.html      # Preview table
│       └── upload.html       # Formset editing
├── static/
│   └── excel_app/
│       └── style.css         # Scoped styling
├── templatetags/
│   └── custom_filters.py     # e.g. `get_item` for dynamic table access
├── tests/
│   ├── test_views.py         # View-level tests
│   ├── test_utils.py         # Utility function tests
│   └── __init__.py
└── apps.py                   # Django app config



🧠 Session Keys Used
|  |  | 
| uploaded_students |  | 
| new_entries |  | 
| score_columns |  | 
| score_keys |  | 
| file_uploaded |  | 



🧪 Testing
Tests are located in excel_app/tests/ and cover:
- Excel parsing logic
- View behavior and session handling
- Grouping and export helpers
Run with:
python manage.py test excel_app



🧼 Maintenance Tips
- Keep utils/ modular and reusable
- Use forms.py only for DB-backed or formset logic
- Keep templatetags/ minimal and documented
- Clean up unused session keys after save
- Use consistent naming across views, URLs, and templates
