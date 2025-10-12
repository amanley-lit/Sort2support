import pandas as pd
import json

# 1. Load your CSV file (export your lesson table as CSV first)
# Make sure the CSV has headers: Lesson, Concept, Irregular Words, New Concept Points
df = pd.read_csv("lessons.csv")

records = []

# 2. Convert each row into a dictionary
for _, row in df.iterrows():
    records.append({
        "number": str(row["Lesson"]).strip(),  # keep lesson numbers as strings (handles 35a, 35b, etc.)
        "concept": str(row["Concept"]).strip() if pd.notna(row["Concept"]) else "",
        "irregular_words": str(row["Irregular Words"]).strip() if pd.notna(row["Irregular Words"]) else "",
        "total_points": int(row["New Concept Points"]) if pd.notna(row["New Concept Points"]) else None
    })

# 3. Save to JSON
with open("ufli_lessons.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print("✅ JSON file created: ufli_lessons.json")