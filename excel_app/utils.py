import pandas as pd

def parse_excel(file):
    df = pd.read_excel(file)
    return df.to_html(classes='assessment-table', index=False)