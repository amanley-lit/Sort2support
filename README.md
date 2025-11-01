# 🎯 Sort2Support

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-5.2-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Status](https://img.shields.io/badge/Status-In_Development-yellow)

Sort2Support is a joyful, teacher-facing dashboard for dynamic intervention groups. Built with Django and OpenPyXL, it empowers educators to upload rosters, select lessons, preview groups, and export polished Excel sheets — all with minimal friction and maximum clarity.

---

## 🧠 Purpose

Teachers deserve tools that feel intuitive, delightful, and empowering. Sort2Support helps educators:
- Upload student data via Excel
- Select UFLI lessons and group students by score
- Preview and export formatted intervention groups
- Reset class or scores with one click
- Download blank or sample templates for easy onboarding

---

## 🖼️ Screenshots

| Dashboard View | Upload Page |
|----------------|-------------|
| ![Dashboard](static/images/dashboard_preview.png) | ![Upload](static/images/upload_preview.png) |

---

## 🔗 Live Demo

Coming soon at [Sort2Support.com](https://sort2support.com)  
(Deployment in progress — SSL, domain, and hosting pipeline underway)

---

## 🏗️ Tech Stack

- **Backend:** Django 5.x
- **Frontend:** HTML, CSS, JavaScript
- **Excel Handling:** OpenPyXL
- **Authentication:** Django’s built-in login system
- **Deployment:** Ready for hosting with static files, SSL, and database setup

---

## 📁 Folder Structure
excel_site/
├── main/                     # Core app
│   ├── views.py              # Dashboard logic, upload/export/reset
│   ├── models.py             # Student model
│   ├── urls.py               # App-level routes
│   ├── templates/
│   │   └── main/             # HTML templates (dashboard, upload, etc.)
│   ├── static/
│   │   └── templates/        # Excel templates (blank/sample)
│   └── utils.py              # Helper functions (e.g. load_ufli_lessons)
├── excel_site/               # Project settings
│   ├── urls.py               # Root URLconf
│   ├── settings.py           # Static files, installed apps, etc.
├── static/                   # Global static files (CSS, logo, etc.)
├── media/                    # (Optional) for uploaded files
└── README.md                 # This file


---

## 📦 Setup Instructions

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/sort2support.git
   cd sort2support
2. **Install dependencies**
pip install -r requirements.txt

3. **Run migrations**
python manage.py migrate

4. **Create a superuser**
python manage.py createsuperuser

5. **Start the server**
python manage.py runserver



📄 Excel Templates
| file | purpose | 
| blank_template.xlsx | Empty sheet with headers for manual entry | 
| sample_template.xlsx | Example sheet with fake students | 

Located in: excel_site/static/templates/

🧪 Testing
- Upload a sample Excel file via /upload-excel/
- Preview student groups on /dashboard/
- Export formatted groups via “Export to Excel”
- Reset class or scores using dashboard buttons

🌐 Deployment Notes
- Static files are collected via collectstatic
- SSL and domain setup recommended for production
- Hosting options: Render, Railway, Fly.io, or traditional VPS

🧑‍💻 Contributing
Sort2Support is built with clarity, empathy, and public impact in mind. If you’d like to contribute:
- Fork the repo and submit a pull request
- Follow Django best practices
- Keep UI joyful and teacher-friendly

❤️ Credits
Built by Amy — a maximizer, architect, and engineer passionate about joyful workflows and public service. Sort2Support is designed to make technical tools intuitive and delightful for educators.

📜 License
This project is licensed under the MIT License.
