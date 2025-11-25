from django.urls import path
from . import views
from .views import TransaccionListView, TransaccionCreateView, TransaccionDetailView

urlpatterns = [
    # -----------------------------
    # Transacciones
    # -----------------------------
    path('transacciones/', TransaccionListView.as_view(), name='lista_transacciones'),
    path('transacciones/crear/', TransaccionCreateView.as_view(), name='crear_transaccion'),
    path('transacciones/<int:pk>/', TransaccionDetailView.as_view(), name='detalle_transaccion'),

    # -----------------------------
    # Panel Principal
    # -----------------------------
    path('seguros/', views.panel_seguros, name='panel_seguros'),

    # -----------------------------
    # Aseguradoras
    # -----------------------------
    path('aseguradoras/', views.lista_aseguradoras, name='lista_aseguradoras'),
    path('aseguradoras/crear/', views.crear_aseguradora, name='crear_aseguradora'),
    path('aseguradoras/<int:pk>/', views.detalle_aseguradora, name='detalle_aseguradora'),
    path('aseguradoras/<int:pk>/editar/', views.editar_aseguradora, name='editar_aseguradora'),
    path('aseguradoras/<int:pk>/eliminar/', views.eliminar_aseguradora, name='eliminar_aseguradora'),

    # -----------------------------
    # Planes de seguro
    # -----------------------------
    path('planes/', views.lista_planes_seguro, name='lista_planes_seguro'),
    path('planes/aseguradora/<int:aseguradora_id>/', views.lista_planes_seguro, name='lista_planes_seguro_por_aseguradora'),

    # Crear plan de seguro
    path('planes/crear/', views.crear_plan_seguro, name='crear_plan_seguro'),  # Crear sin aseguradora
    path('planes/crear/aseguradora/<int:aseguradora_id>/', views.crear_plan_seguro, name='crear_plan_seguro_con_aseguradora'),  # Crear con aseguradora predeterminada

    # Editar y eliminar plan
    path('planes/<int:pk>/editar/', views.editar_plan_seguro, name='editar_plan_seguro'),
    path('planes/<int:pk>/eliminar/', views.eliminar_plan_seguro, name='eliminar_plan_seguro'),
    # -----------------------------
    # Reclamaciones
    # -----------------------------
    path('reclamaciones/', views.lista_reclamaciones, name='lista_reclamaciones'), 
    path('reclamaciones/pendientes/', views.lista_reclamaciones_pendientes, name='lista_reclamaciones_pendientes'),
    path('reclamaciones/crear/', views.crear_reclamacion, name='crear_reclamacion'),
    path('reclamaciones/<int:pk>/', views.detalle_reclamacion, name='detalle_reclamacion'),
    path('reclamaciones/<int:pk>/revisar/', views.revisar_reclamacion, name='revisar_reclamacion'),

    # -----------------------------
    # Facturas
    # -----------------------------
    path('facturas/', views.lista_facturas, name='lista_facturas'),
    path('facturas/crear/', views.crear_factura, name='crear_factura'),
    path('facturas/<int:pk>/', views.detalle_factura, name='detalle_factura'),
    path('facturas/<int:pk>/eliminar/', views.eliminar_factura, name='eliminar_factura'),

    # -----------------------------
    # AJAX y Servicios Facturables
    # -----------------------------
    path('ajax/obtener-precio/', views.obtener_precio_servicio, name='obtener_precio_servicio'), 
    path('servicios/', views.lista_servicios, name='lista_servicios_facturables'),
    path('servicios/crear/', views.crear_servicio, name='crear_servicio_facturable'),
    path('servicios/<int:pk>/eliminar/', views.eliminar_servicio, name='eliminar_servicio_facturable'),
]
