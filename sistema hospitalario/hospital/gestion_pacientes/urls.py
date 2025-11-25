# gestion_pacientes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_pacientes, name='lista_pacientes'),
    path('agregar/', views.agregar_paciente, name='agregar_paciente'),
    path('editar/<int:paciente_id>/', views.editar_paciente, name='editar_paciente'),
    path('eliminar/<int:paciente_id>/', views.eliminar_paciente, name='eliminar_paciente'),
    path('anamnesis/', views.lista_pacientes_anamnesis, name='lista_pacientes_anamnesis'),
    
    path('anamnesis/<int:paciente_id>/', views.lista_anamnesis, name='lista_anamnesis'),
    path('anamnesis/agregar/<int:paciente_id>/', views.agregar_anamnesis, name='agregar_anamnesis'),
    path('anamnesis/editar/<int:anamnesis_id>/', views.editar_anamnesis, name='editar_anamnesis'),
    path('anamnesis/eliminar/<int:anamnesis_id>/', views.eliminar_anamnesis, name='eliminar_anamnesis'),
    
    path('diagnosticos/<int:paciente_id>/', views.lista_diagnosticos, name='lista_diagnosticos'),
    path('diagnosticos/agregar/<int:paciente_id>/', views.agregar_diagnostico, name='agregar_diagnostico'),
    path('diagnosticos/editar/<int:diagnostico_id>/', views.editar_diagnostico, name='editar_diagnostico'),
    path('diagnosticos/eliminar/<int:diagnostico_id>/', views.eliminar_diagnostico, name='eliminar_diagnostico'),
    
    path('citas/<int:paciente_id>/', views.lista_citas, name='lista_citas'),
    path('citas/agregar/<int:paciente_id>/', views.agregar_cita, name='agregar_cita'),
    path('citas/editar/<int:cita_id>/', views.editar_cita, name='editar_cita'),
    path('citas/eliminar/<int:cita_id>/', views.eliminar_cita, name='eliminar_cita'),
    
    path('reporte/<int:paciente_id>/', views.reporte_paciente, name='reporte_paciente'),
    path('reporte-general/', views.reporte_general, name='reporte_general'),


]
