import pandas as pd

def parse_excel(file):
    df = pd.read_excel(file)

    # Normalize column names
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # Expected columns: name, score1, score2
    required = {"name", "score1", "score2"}
    if not required.issubset(df.columns):
        raise ValueError("Excel file must include columns: Name, Score1, Score2")

    # Convert to list of dicts
    student_data = df.to_dict(orient="records")
    return student_data
