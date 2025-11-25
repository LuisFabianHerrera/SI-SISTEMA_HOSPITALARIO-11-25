from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.utils import timezone

def generar_pdf(titulo, contenido):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{titulo}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    ancho, alto = letter

    y = alto - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, titulo)

    p.setFont("Helvetica", 12)
    y -= 40

    for linea in contenido:
        if y < 50:
            p.showPage()
            y = alto - 50
        p.drawString(50, y, linea)
        y -= 20

    p.showPage()
    p.save()
    return response
