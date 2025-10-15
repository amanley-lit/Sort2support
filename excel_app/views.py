from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import StudentFormSet
from openpyxl import load_workbook
from datetime import datetime
import os
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from main.models import Student
from .utils import parse_excel

def upload_excel(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        html_table = parse_excel(file)
        return render(request, "excel_app/preview.html", {"table": html_table})
    return render(request, "excel_app/upload.html")

# excel_app/views.py

@login_required
def upload_file(request):
    data = request.session.get('new_entries', [])

    if request.method == 'POST':
        formset = StudentFormSet(request.POST)
        if formset.is_valid():
            new_data = []
            for i, form in enumerate(formset):
                name = data[i][0] if i < len(data) else form.cleaned_data.get('name')
                score_c1 = form.cleaned_data.get('score_c1')
                score_c2 = form.cleaned_data.get('score_c2')
                if name:
                    new_data.append([name, score_c1, score_c2])
            request.session['new_entries'] = new_data
            data = new_data
    else:
        formset = StudentFormSet(initial=[
            {'name': entry[0], 'score_c1': entry[1], 'score_c2': entry[2]}
            for entry in data
        ])

    for i, form in enumerate(formset):
        if i < len(data) and data[i][0]:
            form.fields['name'].widget.attrs['readonly'] = True

    return render(request, 'excel_app/upload.html', {'formset': formset, 'data': data})
@login_required
def clear_scores(request):
    data = request.session.get('new_entries', [])
    cleared_data = [[entry[0], None, None] for entry in data if entry]
    request.session['new_entries'] = cleared_data
    return redirect('upload')

@login_required
def clear_names(request):
    Student.objects.update(name='')
    messages.success(request, "All student names have been cleared.")
    return redirect('dashboard')

@login_required
def clear_names(request):
    request.session['new_entries'] = []
    return redirect('upload')
@login_required
def export_excel(request):
    export_data = request.session.get('new_entries', [])
    template_path = os.path.join('excel_app', 'static', 'template.xlsx')
    wb = load_workbook(template_path, data_only=False)
    ws = wb['Data']

    for i, row in enumerate(export_data):
        ws.cell(row=5 + i, column=2).value = row[0]
        ws.cell(row=5 + i, column=3).value = row[1]
        ws.cell(row=5 + i, column=4).value = row[2]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"student_template_{timestamp}.xlsx"

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response
