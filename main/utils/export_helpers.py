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


def style_header_row(ws, row_num: int = 1):
    """Style a header row with bold font, background color, and centered text."""
    header_font = Font(name="Comic Sans MS", bold=True, size=12, color="FFFFFF")
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")

    for cell in ws[row_num]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
