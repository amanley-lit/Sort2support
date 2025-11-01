from django.contrib.auth.decorators import login_required
import os, json  # ✅ if you're reading lesson data


# Grouping logic

def assign_group(student_data, lesson_1, lesson_2):
    def get_color(score, max_points):
        if score is None or max_points == 0:
            return None  # no group if missing
        percent = (score / max_points) * 100
        if percent <= 25:
            return "Red"
        elif percent <= 50:
            return "Yellow"
        elif percent <= 75:
            return "Green"
        else:
            return "Blue"

    max1 = lesson_1["total_points"] if lesson_1 else 5
    max2 = lesson_2["total_points"] if lesson_2 else 5

    concept1_groups = {"Red": [], "Yellow": [], "Green": [], "Blue": []}
    concept2_groups = {"Red": [], "Yellow": [], "Green": [], "Blue": []}
    missing1, missing2 = [], []

    for student in student_data:
        score1 = student['score1']
        score2 = student['score2']

        group1 = get_color(score1, max1)
        group2 = get_color(score2, max2)

        if group1:
            concept1_groups[group1].append((student['name'], score1))
        else:
            missing1.append(student['name'])

        if group2:
            concept2_groups[group2].append((student['name'], score2))
        else:
            missing2.append(student['name'])

    def build_table(groups, concept_name, max_points, missing):
        html = f"<h4>{concept_name} (Max: {max_points})</h4>"
        html += "<table class='assessment-table'><tr><th>Group</th><th>Name</th><th>Score</th></tr>"
        for color in ["Red", "Yellow", "Green", "Blue"]:
            css_class = color.lower() + "-group"
            for name, score in groups[color]:
                html += f"<tr class='{css_class}'><td>{color}</td><td>{name}</td><td>{score}</td></tr>"
        html += "</table>"
        if missing:
            html += f"<p class='note'><em>Not assessed / absent: {', '.join(missing)}</em></p>"
        return html

    concept1_name = lesson_1["concept"] if lesson_1 else "Concept 1"
    concept2_name = lesson_2["concept"] if lesson_2 else "Concept 2"

    html = "<div class='grouping-tables'>"
    html += build_table(concept1_groups, concept1_name, max1, missing1)
    html += build_table(concept2_groups, concept2_name, max2, missing2)
    html += "</div>"

    return html, {
    "concept1": concept1_groups,
    "concept2": concept2_groups,
    "missing1": missing1,
    "missing2": missing2,
    }
    