import os, json
import pandas as pd
from django.conf import settings
from django.template.loader import render_to_string

def load_ufli_lessons():
    path = os.path.join(settings.BASE_DIR, "main", "static", "main", "data", "ufli_lessons.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def regroup_students(students, lesson_1, lesson_2):
    concept1_name = lesson_1.get("concept") if lesson_1 else "Concept 1"
    concept2_name = lesson_2.get("concept") if lesson_2 else "Concept 2"

    try:
        max1 = int(lesson_1.get("total_points", 0)) if lesson_1 else 0
    except (ValueError, TypeError):
        max1 = 0
    try:
        max2 = int(lesson_2.get("total_points", 0)) if lesson_2 else 0
    except (ValueError, TypeError):
        max2 = 0

    # Define group buckets
    def bucket(pct):
        if pct <= 0.25:
            return "Red – Needs intensive support"
        elif pct <= 0.60:
            return "Yellow – Emerging understanding"
        elif pct < 1.0:
            return "Green – Approaching mastery"
        else:
            return "Blue – Ready to move on"

    # Two separate group dicts
    groups1 = { "Red – Needs intensive support": [],
                "Yellow – Emerging understanding": [],
                "Green – Approaching mastery": [],
                "Blue – Ready to move on": [] }
    groups2 = { k: [] for k in groups1 }

    for s in students:
        try:
            score1 = int(s.ufli_score_1 or 0)
        except (ValueError, TypeError):
            score1 = 0
        try:
            score2 = int(s.ufli_score_2 or 0)
        except (ValueError, TypeError):
            score2 = 0

        pct1 = (score1 / max1) if max1 else 0
        pct2 = (score2 / max2) if max2 else 0

        groups1[bucket(pct1)].append(s)
        groups2[bucket(pct2)].append(s)

    # Build grouped_data for Excel export
    grouped_data = [
        {
            "concept_name": concept1_name,
            "groups": [
                {
                    "group_name": g,
                    "students": [
                        {
                            "name": m.name,
                            "score": m.ufli_score_1,
                            "independent": getattr(m, "independent", False),
                        }
                        for m in members
                    ]
                }
                for g, members in groups1.items()
            ]
        },
        {
            "concept_name": concept2_name,
            "groups": [
                {
                    "group_name": g,
                    "students": [
                        {
                            "name": m.name,
                            "score": m.ufli_score_2,
                            "independent": getattr(m, "independent", False),
                        }
                        for m in members
                    ]
                }
                for g, members in groups2.items()
            ]
        }
    ]

    # Render two separate tables in your template
    grouped_html = render_to_string("main/_grouped_tables.html", {
        "concept1_name": concept1_name,
        "concept2_name": concept2_name,
        "groups1": groups1,
        "groups2": groups2,
        "lesson_1": lesson_1,
        "lesson_2": lesson_2,
    })

    return grouped_html, grouped_data

def parse_excel(file, sheet_name=0):
    """Parse a given Excel sheet into a DataFrame."""
    return pd.read_excel(file, sheet_name=sheet_name)
