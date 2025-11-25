# gestion_administrativa/urls.py
from django.urls import path
from . import views


urlpatterns = [

    # --- Inicio general y por rol ---
    path('home/', views.home, name='home'),
    path('admin_home/', views.admin_home, name='dashboard_std'),
    path('empleado_home/', views.empleado_home, name='empleado_home'),
    path('medico/', views.medico_home, name='medico_home'),
    path('enfermero/', views.enfermero_home, name='enfermero_home'),
    path('tecnico/', views.tecnico_home, name='tecnico_home'),
    path('recepcionista/', views.recepcionista_home, name='recepcionista_home'),
    path('farmaceutico/', views.farmaceutico_home, name='farmaceutico_home'),
    path('auxiliar/', views.auxiliar_home, name='auxiliar_home'),

    # --- CRUD Empleados ---
    path('empleados/', views.lista_empleados, name='lista_empleados'),
    path('empleados/registrar/', views.registrar_empleado, name='registrar_empleado'),
    path('empleados/editar/<int:empleado_id>/', views.editar_empleado, name='editar_empleado'),
    path('empleados/eliminar/<int:empleado_id>/', views.eliminar_empleado, name='eliminar_empleado'),

    # --- CRUD Turnos ---
    path('turnos/', views.lista_turnos, name='lista_turnos'),
    path('turnos/registrar/', views.registrar_turno, name='registrar_turno'),
    path('turnos/editar/<int:turno_id>/', views.editar_turno, name='editar_turno'),
    path('turnos/eliminar/<int:turno_id>/', views.eliminar_turno, name='eliminar_turno'),


    # --- Asignación de grupos ---
    path('asignar-grupo/<int:empleado_id>/', views.asignar_grupo_empleado, name='asignar_grupo_empleado'),

    # --- Departamentos y Grupos ---
    path('departamentos-grupos/', views.vista_departamentos_grupos, name='vista_departamentos_grupos'),
    path('departamentos/<str:departamento>/<str:grupo>/', views.empleados_por_departamento_y_grupo, name='empleados_por_departamento_y_grupo'),

    # --- Calendarios ---
    path('calendario-turnos/', views.calendario_turnos_mensual, name='calendario_turnos_actual'),
    path('calendario-turnos/<int:year>/<int:month>/', views.calendario_turnos_mensual, name='calendario_turnos'),
    path('departamentos/<str:departamento>/<str:grupo>/calendario/', views.calendario_turnos_por_grupo, name='calendario_turnos_por_grupo'),

#citas y colas 

    path('citas/', views.lista_citas, name='lista_citas'),
    path('citas/crear/', views.crear_cita, name='crear_cita'),
    path('citas/editar/<int:cita_id>/', views.editar_cita, name='editar_cita'),
    path('citas/eliminar/<int:cita_id>/', views.eliminar_cita, name='eliminar_cita'),
    
# check-in y cola
    path("citas/checkin/<int:cita_id>/", views.checkin_cita, name="checkin_cita"),
    path("citas/cola/<int:doctor_id>/", views.cola_espera, name="cola_espera"),
    path("citas/en_proceso/<int:doctor_id>/", views.citas_en_proceso, name="citas_en_proceso"),
    path("citas/atender/<int:doctor_id>/", views.atender_siguiente, name="atender_siguiente"),
    path('citas/atendidos/<int:usuario_id>/', views.pacientes_atendidos, name='pacientes_atendidos'),
    path("citas/colas/", views.colas_de_espera, name="colas_de_espera"),

    path("citas/comenzar/<int:cita_id>/", views.comenzar_cita, name="comenzar_cita"),
#tablero de citas en espera

    path("citas/tablero/", views.tablero_en_espera, name="tablero_en_espera"),

#------camas 

    # Registrar una nueva habitación
    path('habitaciones/registrar/', views.registrar_habitacion, name='registrar_habitacion'),

    # Listar todas las habitaciones
    path('habitaciones/', views.listar_habitaciones, name='listar_habitaciones'),

    # Editar habitación
    path('habitaciones/editar/<int:pk>/', views.editar_habitacion, name='editar_habitacion'),


    # Eliminar habitación
    path('habitaciones/eliminar/<int:habitacion_id>/', views.eliminar_habitacion, name='eliminar_habitacion'),


    #camas
    path("camas/", views.listar_camas, name="listar_camas"),
    path("camas/registrar/", views.registrar_cama, name="registrar_cama"),
    path("camas/editar/<int:cama_id>/", views.editar_cama, name="editar_cama"),
#asignar cama
    path("asignar/", views.asignar_cama, name="asignar_cama"),
    path("ajax/habitaciones/", views.get_habitaciones_por_departamento, name="ajax_habitaciones"),
    path("ajax/camas/", views.get_camas_por_habitacion, name="ajax_camas"),
    
    
    path("camas/asignadas/", views.listado_camas_asignadas, name="listado_camas_asignadas"),
    # Liberar cama
    path("camas/liberar/<int:asignacion_id>/", views.liberar_cama, name="liberar_cama"),
    path("camas/confirmar/<int:cama_id>/", views.confirmar_limpieza, name="confirmar_limpieza"),
    #---alerta
    
    path("alerta_camas/", views.verificar_camas_disponibles, name="verificar_camas_disponibles"),
]
