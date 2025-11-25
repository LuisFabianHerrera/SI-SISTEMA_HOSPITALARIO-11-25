from django.shortcuts import render, redirect, get_object_or_404
from .models import Paciente, Anamnesis
from .forms import PacienteForm, AnamnesisForm
from django.contrib import messages
from .models import Diagnostico
from .forms import DiagnosticoForm
from .models import Cita
from .forms  import CitaForm
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from .models import Paciente


# ----------------- PACIENTES -----------------

# Listar pacientes
def lista_pacientes(request):
    pacientes = Paciente.objects.all().order_by('apellido_paterno')
    return render(request, 'gestion_pacientes/lista_pacientes.html', {'pacientes': pacientes})

# Agregar paciente
def agregar_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente agregado correctamente.')
            return redirect('lista_pacientes')
    else:
        form = PacienteForm()
    return render(request, 'gestion_pacientes/formulario_paciente.html', {'form': form, 'titulo': 'Agregar Paciente'})

# Editar paciente
def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente actualizado correctamente.')
            return redirect('lista_pacientes')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'gestion_pacientes/formulario_paciente.html', {'form': form, 'titulo': 'Editar Paciente'})

# Eliminar paciente
def eliminar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    paciente.delete()
    messages.success(request, 'Paciente eliminado correctamente.')
    return redirect('lista_pacientes')


# ----------------- ANAMNESIS -----------------

# Lista de pacientes para registrar anamnesis
def lista_pacientes_anamnesis(request):
    pacientes = Paciente.objects.all().order_by('apellido_paterno')
    return render(request, 'gestion_pacientes/lista_pacientes_anamnesis.html', {'pacientes': pacientes})

# Lista todas las anamnesis de un paciente
def lista_anamnesis(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    anamnesis_list = paciente.anamnesis.all().order_by('-fecha_registro')  # Todas las anamnesis de ese paciente
    return render(request, 'gestion_pacientes/lista_anamnesis.html', {
        'paciente': paciente,
        'anamnesis_list': anamnesis_list
    })

# Agregar Anamnesis para un paciente específico
def agregar_anamnesis(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    if request.method == 'POST':
        form = AnamnesisForm(request.POST, paciente_genero=paciente.genero)
        if form.is_valid():
            anamnesis = form.save(commit=False)
            anamnesis.paciente = paciente
            anamnesis.save()
            messages.success(request, f'Anamnesis registrada para {paciente.nombre} {paciente.apellido_paterno}.')
            return redirect('lista_pacientes_anamnesis')
    else:
        form = AnamnesisForm(paciente_genero=paciente.genero)
    
    return render(request, 'gestion_pacientes/formulario_anamnesis.html', {
        'form': form,
        'paciente': paciente
    })
    
    # Editar anamnesis
def editar_anamnesis(request, anamnesis_id):
    anamnesis = get_object_or_404(Anamnesis, id=anamnesis_id)
    paciente = anamnesis.paciente
    if request.method == 'POST':
        form = AnamnesisForm(request.POST, instance=anamnesis, paciente_genero=paciente.genero)
        if form.is_valid():
            form.save()
            messages.success(request, 'Anamnesis actualizada correctamente.')
            return redirect('lista_anamnesis', paciente_id=paciente.id)
    else:
        form = AnamnesisForm(instance=anamnesis, paciente_genero=paciente.genero)
    return render(request, 'gestion_pacientes/formulario_anamnesis.html', {'form': form, 'paciente': paciente})


# Eliminar anamnesis
def eliminar_anamnesis(request, anamnesis_id):
    anamnesis = get_object_or_404(Anamnesis, id=anamnesis_id)
    paciente_id = anamnesis.paciente.id
    anamnesis.delete()
    messages.success(request, 'Anamnesis eliminada correctamente.')
    return redirect('lista_anamnesis', paciente_id=paciente_id)


# Listar anamnesis de un paciente
def lista_anamnesis(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    anamnesis_list = paciente.anamnesis.all().order_by('-fecha_registro')  # <- aquí
    return render(request, 'gestion_pacientes/lista_anamnesis.html', {
        'paciente': paciente,
        'anamnesis_list': anamnesis_list
    })
    
    
# Listar diagnósticos de un paciente
def lista_diagnosticos(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    diagnosticos = paciente.diagnosticos.all().order_by('-fecha_inicio')
    return render(request, 'gestion_pacientes/lista_diagnosticos.html', {
        'paciente': paciente,
        'diagnosticos': diagnosticos
    })

# Agregar diagnóstico
def agregar_diagnostico(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        form = DiagnosticoForm(request.POST)
        if form.is_valid():
            diagnostico = form.save(commit=False)
            diagnostico.paciente = paciente
            diagnostico.save()
            messages.success(request, f'Diagnóstico registrado para {paciente.nombre} {paciente.apellido_paterno}.')
            return redirect('lista_diagnosticos', paciente_id=paciente.id)
    else:
        form = DiagnosticoForm()
    return render(request, 'gestion_pacientes/formulario_diagnostico.html', {'form': form, 'paciente': paciente})

# Editar diagnóstico
def editar_diagnostico(request, diagnostico_id):
    diagnostico = get_object_or_404(Diagnostico, id=diagnostico_id)
    paciente = diagnostico.paciente
    if request.method == 'POST':
        form = DiagnosticoForm(request.POST, instance=diagnostico)
        if form.is_valid():
            form.save()
            messages.success(request, 'Diagnóstico actualizado correctamente.')
            return redirect('lista_diagnosticos', paciente_id=paciente.id)
    else:
        form = DiagnosticoForm(instance=diagnostico)
    return render(request, 'gestion_pacientes/formulario_diagnostico.html', {'form': form, 'paciente': paciente})

# Eliminar diagnóstico
def eliminar_diagnostico(request, diagnostico_id):
    diagnostico = get_object_or_404(Diagnostico, id=diagnostico_id)
    paciente_id = diagnostico.paciente.id
    diagnostico.delete()
    messages.success(request, 'Diagnóstico eliminado correctamente.')
    return redirect('lista_diagnosticos', paciente_id=paciente_id)

# ----------------- CITAS -----------------

# Listar citas de un paciente
def lista_citas(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    citas = paciente.citas.all().order_by('-fecha_cita')
    return render(request, 'gestion_pacientes/lista_citas.html', {
        'paciente': paciente,
        'citas': citas
    })

# Agregar cita
def agregar_cita(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.paciente = paciente
            cita.save()
            messages.success(request, f'Cita registrada para {paciente.nombre} {paciente.apellido_paterno}.')
            return redirect('lista_citas', paciente_id=paciente.id)
    else:
        form = CitaForm()
    return render(request, 'gestion_pacientes/formulario_cita.html', {'form': form, 'paciente': paciente})

# Editar cita
def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    paciente = cita.paciente
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cita actualizada correctamente.')
            return redirect('lista_citas', paciente_id=paciente.id)
    else:
        form = CitaForm(instance=cita)
    return render(request, 'gestion_pacientes/formulario_cita.html', {'form': form, 'paciente': paciente})

# Eliminar cita
def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    paciente_id = cita.paciente.id
    cita.delete()
    messages.success(request, 'Cita eliminada correctamente.')
    return redirect('lista_citas', paciente_id=paciente_id)


# =============================
#     REPORTE INDIVIDUAL
# ============================= 
  
# =============================
#     REPORTE INDIVIDUAL
# =============================
def reporte_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    anamnesis_list = paciente.anamnesis.all().order_by('-fecha_registro')
    diagnosticos = paciente.diagnosticos.all().order_by('-fecha_inicio')
    citas = paciente.citas.all().order_by('-fecha_cita')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_paciente_{paciente.id}.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    # Título
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, y, "REPORTE DEL PACIENTE")
    y -= 40

    # Datos del paciente
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "DATOS DEL PACIENTE:")
    y -= 20
    pdf.setFont("Helvetica", 11)
    datos = [
        f"Nombre: {paciente.nombre} {paciente.apellido_paterno} {paciente.apellido_materno}",
        f"CI: {paciente.ci}",
        f"Género: {paciente.genero}",
        f"Fecha de nacimiento: {paciente.fecha_nacimiento}",
        f"Teléfono: {paciente.telefono}",
        f"Dirección: {paciente.direccion}",
        f"Fecha de ingreso: {paciente.fecha_ingreso}",
    ]
    for dato in datos:
        pdf.drawString(60, y, dato)
        y -= 15
    y -= 10

    # Anamnesis
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "ANAMNESIS:")
    y -= 20
    if anamnesis_list:
        data = [["Fecha", "Motivo Consulta", "Historia Enfermedad Actual", "Signos Vitales",
                 "Antecedentes Patológicos", "No Patológicos", "Gineco-Obstétricos", "Familiares"]]
        for a in anamnesis_list:
            row = [
                a.fecha_registro.strftime("%d/%m/%Y %H:%M"),
                a.motivo_consulta,
                a.historia_enfermedad_actual,
                a.signos_vitales,
                a.antecedentes_patologicos,
                a.antecedentes_no_patologicos,
                a.antecedentes_gineco_obstetricos or "",
                a.antecedentes_familiares,
            ]
            data.append(row)
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        w, h = table.wrapOn(pdf, width-100, y)
        table.drawOn(pdf, 50, y - h)
        y -= h + 20
    else:
        pdf.setFont("Helvetica", 11)
        pdf.drawString(60, y, "Sin registros de anamnesis.")
        y -= 20

    # Diagnósticos
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "DIAGNÓSTICOS:")
    y -= 20
    if diagnosticos:
        data = [["Fecha Inicio", "Descripción"]]
        for d in diagnosticos:
            data.append([d.fecha_inicio.strftime("%d/%m/%Y"), d.descripcion])
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgreen),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        w, h = table.wrapOn(pdf, width-100, y)
        table.drawOn(pdf, 50, y - h)
        y -= h + 20
    else:
        pdf.setFont("Helvetica", 11)
        pdf.drawString(60, y, "Sin registros de diagnósticos.")
        y -= 20

    # Citas médicas
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "CITAS MÉDICAS:")
    y -= 20
    if citas:
        data = [["Fecha Cita", "Motivo"]]
        for c in citas:
            data.append([c.fecha_cita.strftime("%d/%m/%Y %H:%M"), c.motivo])
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.orange),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        w, h = table.wrapOn(pdf, width-100, y)
        table.drawOn(pdf, 50, y - h)
        y -= h + 20
    else:
        pdf.setFont("Helvetica", 11)
        pdf.drawString(60, y, "Sin registros de citas.")
        y -= 20

    pdf.showPage()
    pdf.save()
    return response

# =============================
#      REPORTE GENERAL
# =============================
def reporte_general(request): 
    pacientes = Paciente.objects.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_general_pacientes.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 50

    # Título principal
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(width / 2, y, "REPORTE GENERAL DE PACIENTES")
    y -= 50

    for paciente in pacientes:
        if y < 100:  # Nueva página si no hay espacio
            pdf.showPage()
            y = height - 50

        # Nombre y CI del paciente
        pdf.setFont("Helvetica-Bold", 14)
        pdf.setFillColorRGB(0, 0.2, 0.5)  # Color azul oscuro
        pdf.drawString(50, y, f"{paciente.nombre} {paciente.apellido_paterno} {paciente.apellido_materno} - CI: {paciente.ci}")
        y -= 25

        # Información básica
        pdf.setFont("Helvetica", 12)
        pdf.setFillColorRGB(0, 0, 0)  # Negro
        pdf.drawString(60, y, f"Género: {paciente.genero}   Fecha Nac.: {paciente.fecha_nacimiento}")
        y -= 18
        pdf.drawString(60, y, f"Teléfono: {paciente.telefono}   Dirección: {paciente.direccion}")
        y -= 18
        pdf.drawString(60, y, f"Fecha de ingreso: {paciente.fecha_ingreso}")
        y -= 20

        # Estadísticas
        anam = paciente.anamnesis.count()
        diag = paciente.diagnosticos.count()
        citas = paciente.citas.count()
        pdf.setFont("Helvetica-Bold", 12)
        pdf.setFillColorRGB(0.5, 0.2, 0)  # Marrón oscuro
        pdf.drawString(60, y, f"Anamnesis: {anam}   Diagnósticos: {diag}   Citas: {citas}")
        y -= 25

        # Línea separadora
        pdf.setStrokeColorRGB(0.7, 0.7, 0.7)
        pdf.setLineWidth(0.5)
        pdf.line(50, y, width - 50, y)
        y -= 20

    pdf.showPage()
    pdf.save()
    return response
