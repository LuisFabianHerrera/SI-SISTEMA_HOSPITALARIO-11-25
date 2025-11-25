from django.urls import path
from . import views

urlpatterns = [
    # 1. Índice que redirige según el rol (Ruta: /std/)
    path('', views.redireccion_principal_view, name='std_index'), 
    
    # 2. Dashboard Gerencial (Ruta: /std/dashboard/)
    path('dashboard/', views.dashboard_std_view, name='dashboard_std'),
    
    # 3. Reporte de Doctor (Ruta: /std/reportes/doctor/) - OPERACIONAL
    path('reportes/doctor/', views.reportes_doctor_view, name='reportes_doctor'),

    # 4. Reporte Financiero (Ruta: /std/reportes/financiero/) - GERENCIAL
    path('reportes/financiero/', views.reporte_financiero_view, name='reporte_financiero'),

    # 5. Reporte de Desempeño Médico (Ruta: /std/reportes/desempeno/) - GERENCIAL
    path('reportes/desempeno/', views.reporte_desempeno_view, name='reporte_desempeno'),

    # 6. Gestión de Citas (Ruta: /std/gestion/cita/ID/) - OPERACIONAL
    path('gestion/cita/<int:cita_id>/', views.gestion_cita_doctor_view, name='gestion_cita_doctor'),

    # RUTA FALTANTE EN VIEWS.PY (Ahora incluida en el archivo views.py)
    path('dashboard/general/', views.dashboard_empleado_general_view, name='dashboard_empleado_general'),
    # Reporte de Calificación de Pacientes (Ruta: /std/reporte/calificacion/) tengo que agreagr un boton en el dashboard gerencial
    path('reporte/calificacion/', views.reporte_calificacion_view, name='reporte_calificacion'),
    
    path('cita/<int:cita_id>/calificar/', views.calificar_cita_view, name='calificar_cita'),

]