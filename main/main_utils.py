import os, json
import pandas as pd
from django.conf import settings

# ---------- Load UFLI lessons ----------
def load_ufli_lessons():
    path = os.path.join(settings.BASE_DIR, "main", "static", "main", "data", "ufli_lessons.json")
    with open(path, encoding="utf-8") as f:
        lessons = json.load(f)

    # Optional: validate total_points
    for lesson in lessons:
        if not isinstance(lesson, dict):
            print(f"⚠️ Skipping invalid lesson entry: {lesson}")
            continue
        if "total_points" not in lesson or not isinstance(lesson["total_points"], int):
            print(f"⚠️ Lesson {lesson.get('number')} missing valid total_points")

    return lessons



# ---------- Grouping Helpers ----------
def get_color(score, max_points):
    percent = (score / max_points) * 100
    if percent <= 25: return "Red"
    elif 26 <= percent <= 60: return "Yellow"
    elif 61 <= percent <= 99: return "Green"
    elif percent == 100: return "Blue"
    return None

def get_color_class(score, max_points):
    try:
        score = int(score)
        max_points = int(max_points)
    except (TypeError, ValueError):
        return ""
    if max_points == 0:
        return ""
    percent = (score / max_points) * 100
    if percent <= 25:
        return "red"
    elif percent <= 60:
        return "yellow"
    elif percent <= 99:
        return "green"
    elif percent == 100:
        return "blue"
    return ""



def get_instruction_group(score, max_points):
    if max_points == 3:
        return "Intensive Reteach" if score <= 1 else "Review" if score == 2 else "None"
    elif max_points == 4:
        return "Intensive Reteach" if score <= 1 else "Reteach" if score == 2 else "Review" if score == 3 else "None"
    elif max_points == 5:
        return "Intensive Reteach" if score <= 1 else "Reteach" if score in [2,3] else "Review" if score == 4 else "None"
    elif max_points == 6:
        return "Intensive Reteach" if score <= 1 else "Reteach" if score in [2,3] else "Review" if score in [4,5] else "None"
    return "Unclassified"

def build_table(groups, concept_name, max_points):
    html = f"<h4>{concept_name} (Max: {max_points})</h4>"
    html += "<table class='assessment-table'><tr><th>Group</th><th>Name</th><th>Score</th></tr>"
    for color in ["Red","Yellow","Green","Blue"]:
        css_class = color.lower() + "-group"
        for name, score in groups[color]:
            html += f"<tr class='{css_class}'><td>{color}</td><td>{name}</td><td>{score}</td></tr>"
    html += "</table>"
    return html

def build_weekly_group_table(students, score_key, concept_name, max_points):
    schedule_map = {
        "Intensive Reteach": ["M","Tu","W","Th","F"],
        "Reteach": ["M","W","F"],
        "Review": ["Tu","Th"],
        "None": [],
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

    for student in students:
        score = student[score_key]
        name = student["name"]
        group = get_instruction_group(score, max_points)
        if group in table_data:
            for day in schedule_map.get(group, []):
                table_data[group][day].append(name)
    print("🧪 students[0]:", students[0])
    print("🧪 type:", type(students[0]))


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

def build_daily_group_table(daily_group_data, concept1_name, concept2_name):
    html = "<h4>Student Grouping Categories</h4>"
    html += "<table class='daily-summary'>"
    html += f"<tr><th>Name</th><th>{concept1_name}</th><th>{concept2_name}</th></tr>"

    for student in daily_group_data:
        html += f"<tr><td>{student['name']}</td>"
        html += f"<td>{student['group_1']}</td>"
        html += f"<td>{student['group_2']}</td></tr>"

    html += "</table>"
    return html


# ---------- Main grouping orchestrator ----------
def assign_group(preview_data, lesson_1, lesson_2, student_tags):
    max1 = lesson_1["total_points"] if lesson_1 else 5
    max2 = lesson_2["total_points"] if lesson_2 else 5
    concept1_name = lesson_1["concept"] if lesson_1 else "Concept 1"
    concept2_name = lesson_2["concept"] if lesson_2 else "Concept 2"

    concept1_groups = {"Red": [], "Yellow": [], "Green": [], "Blue": []}
    concept2_groups = {"Red": [], "Yellow": [], "Green": [], "Blue": []}
    daily_group_data = []

    for student in preview_data:
        name = student["name"]
        score1 = student.get("score1", 0)
        score2 = student.get("score2", 0)

        group1 = get_color(score1, max1)
        group2 = get_color(score2, max2)

        if group1 in concept1_groups:
            concept1_groups[group1].append((name, score1))
        if group2 in concept2_groups:
            concept2_groups[group2].append((name, score2))

        daily_group_data.append({
            "name": name,
            "group_1": group1,
            "concept_1": concept1_name,
            "group_2": group2,
            "concept_2": concept2_name,
        })

    # --- Build HTML blocks ---
    html = "<div class='grouping-tables'>"

    # 🎯 Concept 1 block
    html += f"""
    <div class='concept-block'>
    <button class='collapsible'>📘 {concept1_name}</button>
    <div class='collapsible-content'>
        {build_table(concept1_groups, concept1_name, max1)}
    </div>
    </div>
    """

    # 🎯 Concept 2 block
    html += f"""
    <div class='concept-block'>
    <button class='collapsible'>📗 {concept2_name}</button>
    <div class='collapsible-content'>
        {build_table(concept2_groups, concept2_name, max2)}
    </div>
    </div>
    """

    # 🗓️ Daily grouping
    html += f"""
    <div class='concept-block'>
    <h3>📅 Daily Grouping Table</h3>
    {build_daily_group_table(daily_group_data, concept1_name, concept2_name)}
    </div>
    """

    # 📊 Weekly grouping
    weekly_html_1 = build_weekly_group_table(preview_data, "score1", concept1_name, max1)
    weekly_html_2 = build_weekly_group_table(preview_data, "score2", concept2_name, max2)

    html += "<hr><h3>📈 Weekly Grouping Tables</h3>"
    html += f"""
    <div class='concept-block'>
    <h4>🟢 {concept1_name} Weekly</h4>
    {weekly_html_1}
    </div>
    <div class='concept-block'>
    <h4>🔵 {concept2_name} Weekly</h4>
    {weekly_html_2}
    </div>
    """

    html += "</div>"

    return html, {
        "daily": daily_group_data,
        "weekly_1": weekly_html_1,
        "weekly_2": weekly_html_2,
        "concept1": concept1_groups,
        "concept2": concept2_groups,
        "tags": student_tags,
    }
