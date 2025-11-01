import pandas as pd

def parse_excel(file):
    # Example: read Excel into DataFrame and render as HTML
    df = pd.read_excel(file)
    return df.to_html(classes="table table-striped", index=False)
