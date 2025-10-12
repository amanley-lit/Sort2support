import os
import json
import re
from datetime import date
import pandas as pd

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings

from .models import Student
from .forms import SignUpForm
from .utils import load_ufli_lessons, regroup_students, parse_excel

from openpyxl import Workbook

# --- Views ---

@login_required
def download_template(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Class Data"
    ws.append(["Name", "Score 1", "Score 2", "Notes (optional)"])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="class_template.xlsx"'
    wb.save(response)
    return response


@login_required
def upload_excel(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        xls = pd.ExcelFile(file)

        # Case 1: teacher already chose a sheet
        chosen_sheet = request.POST.get("sheet_name")
        if chosen_sheet:
            df = parse_excel(file, sheet_name=chosen_sheet)
        # Case 2: only one sheet
        elif len(xls.sheet_names) == 1:
            df = parse_excel(file, sheet_name=0)
        # Case 3: multiple sheets → let teacher choose
        else:
            return render(request, "main/select_sheet.html", {"sheets": xls.sheet_names})

        # ✅ Validate required headers
        required = {"Name", "Score 1", "Score 2"}
        if not required.issubset(df.columns):
            messages.error(request, f"Your file must include columns: {', '.join(required)}")
            return redirect("upload_excel")

        # ✅ Convert DataFrame → Student objects (not saved yet)
        students = []
        for _, row in df.iterrows():
            name = str(row.get("Name", "")).strip()
            if not name:
                continue
            score1 = row.get("Score 1")
            score2 = row.get("Score 2")
            students.append(Student(
                name=name,
                ufli_score_1=int(score1) if pd.notna(score1) else None,
                ufli_score_2=int(score2) if pd.notna(score2) else None,
                teacher=request.user
            ))

        # ✅ Preview before saving
        return render(request, "main/preview.html", {"students": students})

    # Case 4: no file uploaded yet
    return render(request, "main/upload.html")

@login_required
def export_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Groups"
    ws.append(["Name", "Score 1", "Score 2"])

    # Add your student data
    for student in Student.objects.filter(teacher=request.user):
        ws.append([student.name, student.ufli_score_1, student.ufli_score_2])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="groups.xlsx"'
    wb.save(response)
    return response

@login_required
def clear_names(request):
    # Delete all students for this teacher
    Student.objects.filter(teacher=request.user).delete()
    messages.success(request, "All student names have been cleared.")
    return redirect("dashboard")

@login_required
def save_uploaded_students(request):
    if request.method == "POST":
        # Clear old students
        Student.objects.filter(teacher=request.user).delete()

        # Rebuild from hidden form fields
        names = request.POST.getlist("name")
        scores1 = request.POST.getlist("score1")
        scores2 = request.POST.getlist("score2")

        for name, s1, s2 in zip(names, scores1, scores2):
            if not name.strip():
                continue
            Student.objects.create(
                teacher=request.user,
                name=name.strip(),
                ufli_score_1=int(s1) if s1 else None,
                ufli_score_2=int(s2) if s2 else None,
            )

        messages.success(request, "Students imported successfully!")
        return redirect("dashboard")


def add_group_color_highlighting(ws, start_row=2, last_col="E", group_col="B"):
    """
    Highlight entire rows based on whether the group label in group_col
    contains 'Red', 'Yellow', 'Green', or 'Blue'.
    The range automatically extends to ws.max_row.
    """

    end_row = ws.max_row  # dynamically detect last row with data

    colors = {
        "Red":    "F4CCCC",  # light red
        "Yellow": "FFF2CC",  # light yellow
        "Green":  "D9EAD3",  # light green
        "Blue":   "CFE2F3",  # light blue
    }

    for keyword, hex_color in colors.items():
        fill = PatternFill(start_color=hex_color, end_color=hex_color, fill_type="solid")
        # Formula: look for the keyword anywhere in the group label column
        formula = f'ISNUMBER(SEARCH("{keyword}",${group_col}{start_row}))'
        ws.conditional_formatting.add(
            f"A{start_row}:{last_col}{end_row}",
            FormulaRule(formula=[formula], fill=fill)
        )



def safe_sheet_name(name: str) -> str:
    """Make a string safe for Excel sheet names (<=31 chars, no forbidden chars)."""
    cleaned = re.sub(r'[:\\/*?\[\]]', '-', name).strip()
    return cleaned[:31]


def autofit_columns(ws):
    """Resize each column in a worksheet to fit its longest value."""
    for i, col in enumerate(ws.columns, 1):  # enumerate gives you the column index
        max_length = 0
        col_letter = get_column_letter(i)
        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = max_length + 2


def apply_banded_rows(ws, start_row: int = 2):
    """Apply alternating row shading starting from start_row."""
    fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
    for row in ws.iter_rows(min_row=start_row, max_row=ws.max_row):
        if row[0].row % 2 == 0:  # even-numbered rows
            for cell in row:
                cell.fill = fill

def style_header_row(ws, row_num: int = 1):
    """Style a header row with bold font, background color, and centered text."""
    header_font = Font(name="Comic Sans MS", bold=True, size=12, color="FFFFFF")
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")

    for cell in ws[row_num]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment

# ---------- Load UFLI lessons ----------
def load_ufli_lessons():
    path = os.path.join(settings.BASE_DIR, "main", "static", "main", "data", "ufli_lessons.json")
    with open(path, encoding="utf-8") as f:
        lessons = json.load(f)

    # Ensure every lesson has a total_points field
    for lesson in lessons:
        if "total_points" not in lesson:
            lesson["total_points"] = 5  # fallback

    return lessons

ufli_lessons = load_ufli_lessons()

# ---------- Auth Views ----------
def home(request):
    return render(request, "main/home.html")

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "main/signup.html", {"form": form})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Signup successful! Welcome to FluentPath.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'main/signup.html', {'form': form})

def login_view(request):
    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def reset_class(request):
    Student.objects.filter(teacher=request.user).delete()
    messages.success(request, "🔄 Entire class reset successfully.")
    return redirect("dashboard")

# ---------- Grouping Logic ----------
def assign_group(student_data, lesson_1, lesson_2):
    # Helpers
    def get_color(score, max_points):
        if score is None or max_points == 0:
            return None
        percent = (score / max_points) * 100
        if percent <= 25: return "Red"
        elif 26 <= percent <= 60: return "Yellow"
        elif 61 <= percent <= 99: return "Green"
        elif percent == 100: return "Blue"
        return None

    def get_instruction_group(score, max_points):
        if score is None: return "Missing"
        if max_points == 3:
            return "Intensive Reteach" if score <= 1 else "Review" if score == 2 else "None"
        elif max_points == 4:
            return "Intensive Reteach" if score <= 1 else "Reteach" if score == 2 else "Review" if score == 3 else "None"
        elif max_points == 5:
            return "Intensive Reteach" if score <= 1 else "Reteach" if score in [2,3] else "Review" if score == 4 else "None"
        elif max_points == 6:
            return "Intensive Reteach" if score <= 1 else "Reteach" if score in [2,3] else "Review" if score in [4,5] else "None"
        return "Unclassified"

    def build_table(groups, concept_name, max_points, missing):
        html = f"<h4>{concept_name} (Max: {max_points})</h4>"
        html += "<table class='assessment-table'><tr><th>Group</th><th>Name</th><th>Score</th></tr>"
        for color in ["Red","Yellow","Green","Blue"]:
            css_class = color.lower() + "-group"
            for name, score in groups[color]:
                html += f"<tr class='{css_class}'><td>{color}</td><td>{name}</td><td>{score}</td></tr>"
        html += "</table>"
        if missing:
            html += f"<p class='note'><em>Not assessed / absent: {', '.join(missing)}</em></p>"
        return html

    def build_weekly_group_table(student_tags, score_key, concept_name, max_points):
        schedule_map = {
            "Intensive Reteach": ["M","Tu","W","Th","F"],
            "Reteach": ["M","W","F"],
            "Review": ["Tu","Th"],
            "None": [],
            "Missing": [],
            "Unclassified": []
        }
        day_order = ["M","Tu","W","Th","F"]
        day_labels = {"M":"M 📘","Tu":"Tu ✏️","W":"W 📚","Th":"Th 🎨","F":"F 🎉"}
        categories = {
            "Intensive Reteach": "🚨 Extra Boost Crew",
            "Reteach": "🔄 Reteach Squad",
            "Review": "🔍 Quick Checkers",
            "None": "🌟 Ready to Fly"
        }
        table_data = {cat:{day:[] for day in day_order} for cat in categories}

        for tag in student_tags:
            group = get_instruction_group(tag[score_key], max_points)
            if group in table_data:
                for day in schedule_map.get(group, []):
                    table_data[group][day].append(tag["name"])

        html = f"<h4>Weekly Group Plan – {concept_name} (Max: {max_points})</h4>"
        html += "<table class='weekly-group-table'>"
        html += "<tr><th>Focus Group</th>" + "".join(f"<th>{day_labels[d]}</th>" for d in day_order) + "</tr>"

        for cat, label in categories.items():
            html += f"<tr><td>{label}</td>"
            for day in day_order:
                names = ", ".join(table_data[cat][day]) or "— No group today —"
                html += f"<td>{names}</td>"
            html += "</tr>"

        html += "</table>"   
        return html

    def build_daily_group_table(student_tags, concept1_name, concept2_name):
        html = "<h4>Daily Grouping Summary</h4>"
        html += "<table class='daily-summary'><tr><th>Name</th>"
        html += f"<th>{concept1_name}</th><th>{concept2_name}</th></tr>"
        for tag in student_tags:
            html += f"<tr><td>{tag['name']}</td>"
            html += f"<td>{tag['concept_1_group']} ({tag['score1']})</td>"
            html += f"<td>{tag['concept_2_group']} ({tag['score2']})</td></tr>"
        html += "</table>"
        return html

    # ---------- Main logic ----------
    max1 = lesson_1["total_points"] if lesson_1 else 5
    max2 = lesson_2["total_points"] if lesson_2 else 5
    concept1_name = lesson_1["concept"] if lesson_1 else "Concept 1"
    concept2_name = lesson_2["concept"] if lesson_2 else "Concept 2"

    concept1_groups = {"Red":[],"Yellow":[],"Green":[],"Blue":[]}
    concept2_groups = {"Red":[],"Yellow":[],"Green":[],"Blue":[]}
    missing1, missing2, student_tags = [], [], []

    for student in student_data:
        name, score1, score2 = student["name"], student["score1"], student["score2"]
        
        student_tags.append({
            "name": name,
            "concept_1_group": group1,
            "concept_2_group": group2,
            "score1": score1,
            "score2": score2,
           
        })
        
        group1 = get_color(score1, max1) or "Missing"
        group2 = get_color(score2, max2) or "Missing"
        student_tags.append({
            "name": name,
            "concept_1_group": group1,
            "concept_2_group": group2,
            "score1": score1,
            "score2": score2,      
        })
        if group1: concept1_groups[group1].append((name,score1))
        else: missing1.append(name)
        if group2: concept2_groups[group2].append((name,score2))
        else: missing2.append(name)

    # ---------- Build HTML ----------
    html = "<div class='grouping-tables'>"
    html += build_table(concept1_groups, concept1_name, max1, missing1)
    html += build_table(concept2_groups, concept2_name, max2, missing2)
    html += build_daily_group_table(student_tags, concept1_name, concept2_name)
    html += "<hr><h3>Weekly Grouping Tables</h3>"
    html += build_weekly_group_table(student_tags, "score1", concept1_name, max1)
    html += build_weekly_group_table(student_tags, "score2", concept2_name, max2)
    html += "</div>"

    return html
from django.http import HttpResponse
from openpyxl import Workbook
from django.contrib.auth.decorators import login_required

@login_required
def export_students_excel(request):
    grouped_data = request.session.get("grouped_data", [])

    concept1 = grouped_data[0] if len(grouped_data) > 0 else None
    concept2 = grouped_data[1] if len(grouped_data) > 1 else None

    wb = Workbook()
    ws_overview = wb.active
    ws_overview.title = "Overview"

    # --- Concept 1 table ---
    current_row = 1
    if concept1:
        ws_overview.append(["Concept 1", "Group", "Name", "Score"])
        style_header_row(ws_overview, row_num=current_row)
        current_row += 1

        for group in concept1["groups"]:
            for s in group["students"]:
                ws_overview.append([
                    "Concept 1",
                    group["group_name"],
                    s["name"],
                    s.get("score", "")
                ])
                current_row += 1
            ws_overview.append([])
            current_row += 1

        ws_overview.append([])
        current_row += 1

    # --- Concept 2 table ---
    if concept2:
        ws_overview.append(["Concept 2", "Group", "Name", "Score"])
        style_header_row(ws_overview, row_num=current_row)
        current_row += 1

        for group in concept2["groups"]:
            for s in group["students"]:
                ws_overview.append([
                    "Concept 2",
                    group["group_name"],
                    s["name"],
                    s.get("score", "")
                ])
                current_row += 1
            ws_overview.append([])
            current_row += 1

    # Autofit and highlighting
    autofit_columns(ws_overview)
    add_group_color_highlighting(
        ws_overview,
        start_row=2,   # safe if Concept 1 exists
        last_col="D",
        group_col="B"
    )

    # --- One sheet per concept ---
    for concept in grouped_data:
        sheet_name = safe_sheet_name(concept["concept_name"])
        ws = wb.create_sheet(title=sheet_name)

        ws.merge_cells("A1:C1")
        ws["A1"] = concept["concept_name"]

        ws.append(["Group", "Name", "Score"])
        style_header_row(ws, row_num=2)

        for group in concept["groups"]:
            for s in group["students"]:
                ws.append([
                    group["group_name"],
                    s["name"],
                    s.get("score", ""),
                ])
            ws.append([])

        autofit_columns(ws)
        add_group_color_highlighting(
            ws,
            start_row=3,
            last_col="C",
            group_col="A"
        )

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="groups.xlsx"'
    wb.save(response)
    return response

@login_required
def dashboard(request):

    # Get all students for the logged-in teacher
    students = Student.objects.filter(teacher=request.user)

    # Load UFLI lessons (from your JSON file via utils.py)
    ufli_lessons = load_ufli_lessons()
    lesson_1, lesson_2 = None, None
    grouped_html, grouped_data = (None, None)

    # Pass everything into the template
    context = {
        "students": students,
        "ufli_lessons": ufli_lessons,
    }

    if request.method == "POST":
        # --- Handle concept selection ---
        lesson_1_id = request.POST.get("lesson_1")
        lesson_2_id = request.POST.get("lesson_2")
        if lesson_1_id:
            lesson_1 = next((l for l in ufli_lessons if str(l.number) == lesson_1_id), None)
        if lesson_2_id:
            lesson_2 = next((l for l in ufli_lessons if str(l.number) == lesson_2_id), None)

        # --- Reset actions ---
        if request.POST.get("clear_names") == "true":
            Student.objects.filter(teacher=request.user).delete()
            messages.success(request, "🔄 Entire class reset successfully.")
            return redirect("dashboard")

        elif request.POST.get("reset_scores") == "true":
            for s in students:
                s.ufli_score_1 = None
                s.ufli_score_2 = None
                s.save()
            messages.success(request, "🧹 Scores cleared, names preserved.")
            return redirect("dashboard")

        # --- Save & Sort ---
        elif request.POST.get("save_and_sort") == "true":
            new_students = []
            i = 1
            while f"student_name_{i}" in request.POST:
                name = request.POST.get(f"student_name_{i}", "").strip()
                score1 = request.POST.get(f"ufli_score_1_{i}") or None
                score2 = request.POST.get(f"ufli_score_2_{i}") or None
                if name:
                    new_students.append(Student(
                        name=name,
                        teacher=request.user,
                        ufli_score_1=score1,
                        ufli_score_2=score2
                    ))
                i += 1

            if not new_students:
                messages.warning(request, "⚠️ No students were entered. Your class list was not updated.")
            else:
                Student.objects.filter(teacher=request.user).delete()
                for s in new_students:
                    s.save()
                students = new_students
                messages.success(request, "✅ Class saved successfully! Your students will be remembered next time you log in.")

        # --- Handle class size entry ---
        elif request.POST.get("enter_by_class_size") == "true" and request.POST.get("class_size"):
            try:
                size = int(request.POST.get("class_size"))
            except (TypeError, ValueError):
                size = 0
            students = [Student(name="", teacher=request.user) for _ in range(size)]
            grouped_html, grouped_data = (None, None)

        # --- Regroup unless skipped ---
        if not (request.POST.get("reset_scores") or request.POST.get("clear_names") or request.POST.get("enter_by_class_size")):
            grouped_html, grouped_data = regroup_students(students, lesson_1, lesson_2)
            request.session["grouped_data"] = grouped_data
    
    # --- Build context for template ---

    context = {
        "students": students,
        "lesson_1": lesson_1,
        "lesson_2": lesson_2,
        "ufli_lessons": ufli_lessons,
        "grouped_html": grouped_html,
        "groups": grouped_data,
    }
    return render(request, "main/dashboard.html", context)


@login_required
def reset_class(request):
    Student.objects.filter(teacher=request.user).delete()
    messages.success(request, "🔄 Entire class reset successfully.")
    return redirect("dashboard")