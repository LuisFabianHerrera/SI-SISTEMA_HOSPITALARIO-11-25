from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse 
from .models import Factura, DetalleFactura, ServicioFacturable
from .forms import FacturaForm, DetalleFacturaForm, ServicioFacturableForm
from .forms import TransaccionForm
from .models import Transaccion 
from django.db.models import Sum
from django.utils import timezone
from django.contrib import messages

# --- CRUD de Servicios Facturables (Catálogo) ---

def lista_servicios(request):
    """Muestra el catálogo de servicios facturables."""

    servicios = ServicioFacturable.objects.all().order_by('nombre')
    context = {'servicios': servicios, 'titulo': 'Catálogo de Servicios'}
    # ✅ RUTA DE PLANTILLA CORREGIDA para que sea consistente
    return render(request, 'servicios/lista_servicios.html', context)

def crear_servicio(request):
    """Permite crear un nuevo servicio facturable."""
    if request.method == 'POST':
        form = ServicioFacturableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Servicio "{form.cleaned_data["nombre"]}" creado con éxito.')
            # 🚀 CORRECCIÓN CLAVE: Redireccionamos usando el nombre de la URL de manera absoluta.
            # El nombre es 'lista_servicios_facturables' (del urls.py)
            return redirect('lista_servicios_facturables') 
    else:
        form = ServicioFacturableForm()
    
    context = {'titulo': 'Crear Servicio', 'form': form}
    # ✅ RUTA DE PLANTILLA CORREGIDA para que sea consistente
    return render(request, 'servicios/servicio_form.html', context)

# --- FUNCIÓN AJAX para obtener precio de un servicio ---

def obtener_precio_servicio(request):
    """Devuelve el precio base de un ServicioFacturable dado su ID."""
    servicio_id = request.GET.get('servicio_id')
    try:
        servicio = ServicioFacturable.objects.get(pk=servicio_id)
        # Devolvemos el precio como JSON
        # Se corrigió el nombre del campo a precio_base si ese es el campo correcto
        return JsonResponse({'precio': servicio.precio_base}) 
    except ServicioFacturable.DoesNotExist:
        return JsonResponse({'precio': 0.00}, status=404)


# --- CRUD de Facturas ---

def lista_facturas(request):
    """Lista todas las facturas."""
    facturas = Factura.objects.all().order_by('-fecha_emision')
    context = {'facturas': facturas, 'titulo': 'Listado de Facturas'}
    return render(request, 'facturacion/facturas/lista_facturas.html', context)

def crear_factura(request):
    """Permite crear el encabezado de una factura."""
    if request.method == 'POST':
        form = FacturaForm(request.POST) 
        if form.is_valid():
            factura = form.save(commit=False)
            factura.fecha_emision = timezone.now()
            factura.save()
            # Redirigir a la vista de detalle para agregar ítems
            return redirect('detalle_factura', pk=factura.pk) 
    else:
        form = FacturaForm()

    context = {
        'titulo': 'Crear Nueva Factura',
        'form': form
    }
    return render(request, 'facturacion/facturas/factura_form.html', context)


def detalle_factura(request, pk):
    """Muestra la factura, permite añadir detalles y registrar pagos."""
    factura = get_object_or_404(Factura, pk=pk)

    # Consultar los detalles asociados
    detalles = factura.detalles.all().order_by('id')

    # Formularios iniciales
    detalle_form = DetalleFacturaForm()
    pago_form = TransaccionForm(initial={
        'paciente': factura.paciente.pk if factura.paciente else None,
        'monto': factura.total if factura.total is not None else 0.00,
    })

    # ---------------------------------------------------------
    # 1. AGREGAR DETALLE A LA FACTURA
    # ---------------------------------------------------------
    if 'agregar_detalle' in request.POST:
        detalle_form = DetalleFacturaForm(request.POST)
        if detalle_form.is_valid():
            detalle = detalle_form.save(commit=False)
            detalle.factura = factura

            # Calculamos subtotal
            detalle.subtotal = detalle.cantidad * detalle.precio_unitario_facturado
            detalle.save()

            # Actualizamos total de la factura
            factura.total = factura.detalles.aggregate(
                total_sum=Sum('subtotal')
            )['total_sum'] or 0.00

            factura.save()
            return redirect('detalle_factura', pk=factura.pk)

    # ---------------------------------------------------------
    # 2. REGISTRAR EL PAGO DE LA FACTURA
    # ---------------------------------------------------------
    elif 'registrar_pago' in request.POST and not factura.transaccion_pago:
        pago_form = TransaccionForm(request.POST)
        if pago_form.is_valid():
            pago = pago_form.save(commit=False)

            # Asociar paciente si existe
            if factura.paciente:
                pago.paciente = factura.paciente

            pago.tipo = 'Ingreso'
            pago.monto = factura.total
            pago.estado = 'Completada'
            pago.save()

            # Asociamos la transacción a la factura
            factura.transaccion_pago = pago
            factura.estado = 'PAGADA'
            factura.save()

            messages.success(request, f'Pago por Factura #{pk} registrado con éxito.')

            # 🔥 REDIRECCIÓN AL LISTADO DE FACTURAS
            return redirect('lista_facturas')

    # ---------------------------------------------------------
    # 3. CONTEXTO DE LA VISTA
    # ---------------------------------------------------------
    context = {
        'titulo': f'Factura #{pk}',
        'factura': factura,
        'detalles': detalles,
        'detalle_form': detalle_form,
        'pago_form': pago_form,
    }

    return render(request, 'facturacion/facturas/detalle_factura.html', context)


def eliminar_factura(request, pk):
    """Permite eliminar una factura y redirige a la lista."""
    factura = get_object_or_404(Factura, pk=pk)
    
    # Restricción: Solo permitir eliminar si no está pagada (o si está, que se cancele el pago)
    if factura.estado != 'PAGADA':
        factura.delete()
        messages.success(request, f'Factura #{pk} eliminada con éxito.')
        return redirect('lista_facturas')
    else:
        messages.error(request, f'La Factura #{pk} no puede ser eliminada porque ya está PAGADA.')
        
    # Si la factura está pagada, redirigimos a detalle (se muestra el mensaje de error)
    return redirect('detalle_factura', pk=pk)

# --- Funcionalidad de Eliminación ---

def eliminar_servicio(request, pk):
    """Permite eliminar un servicio facturable."""
    servicio = get_object_or_404(ServicioFacturable, pk=pk)

    if request.method == 'POST':
        # Nota: Idealmente, usarías un formulario para la eliminación segura,
        # pero para simplicidad, simplemente eliminaremos y redirigiremos.
        try:
            nombre = servicio.nombre
            servicio.delete()
            messages.success(request, f'Servicio "{nombre}" eliminado con éxito.')
        except Exception as e:
            # Esto captura si el servicio está siendo usado por una Factura (ForeignKey)
            messages.error(request, f'Error al eliminar el servicio: {e}. Asegúrate de que no esté asociado a facturas.')
            
        return redirect('lista_servicios_facturables')
    
    # Renderizar una página de confirmación si se accede por GET (opcional pero recomendado)
    context = {
        'titulo': f'Confirmar Eliminación de Servicio: {servicio.nombre}',
        'servicio': servicio
    }
    # Asegúrate de crear esta plantilla de confirmación si quieres que funcione bien
    return render(request, 'facturacion/servicios/servicio_confirm_delete.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
# Importamos PlanSeguro por si se usa en otras funciones, pero no lo necesitamos aquí
# from django.db.models import Prefetch 
from .models import Aseguradora, PlanSeguro, Reclamacion
from .forms import AseguradoraForm, PlanSeguroForm, ReclamacionForm 
from gestion_pacientes.models import Paciente 
from datetime import timedelta 
from django.contrib import messages

# --- Vistas del Panel Principal ---

def panel_seguros(request):
    """Panel principal que muestra estadísticas y enlaces rápidos."""
    try:
        # Usando el estado 'ENVIADA' de tu modelo
        num_reclamaciones_pendientes = Reclamacion.objects.filter(estado='ENVIADA').count()
        num_aseguradoras = Aseguradora.objects.count()
    except Exception:
        num_reclamaciones_pendientes = 0
        num_aseguradoras = 0
    
    context = {
        'titulo': 'Módulo de Seguros',
        'num_reclamaciones_pendientes': num_reclamaciones_pendientes,
        'num_aseguradoras': num_aseguradoras,
    }
    return render(request, 'seguros/panel_seguros.html', context)


# --- CRUD de Aseguradoras ---

def lista_aseguradoras(request):
    """
    Muestra la lista de todas las aseguradoras y sus planes asociados.
    CORREGIDO: Usando prefetch_related('planes') según el related_name del modelo.
    """
    aseguradoras = Aseguradora.objects.all().prefetch_related('planes') 
    context = {
        'titulo': 'Listado de Aseguradoras y Planes',
        'aseguradoras': aseguradoras
    }
    return render(request, 'seguros/lista_aseguradoras.html', context)

def crear_aseguradora(request):
    """Permite registrar una nueva aseguradora."""
    if request.method == 'POST':
        form = AseguradoraForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_aseguradoras')
    else:
        form = AseguradoraForm()
    
    context = {
        'titulo': 'Registrar Nueva Aseguradora',
        'form': form
    }
    return render(request, 'seguros/crear_aseguradora.html', context)
    
def detalle_aseguradora(request, pk):
    """Muestra los detalles de una aseguradora y sus planes asociados."""
    # Usamos prefetch_related para obtener los planes de una sola vez
    aseguradora = get_object_or_404(Aseguradora.objects.prefetch_related('planes'), pk=pk)
    
    context = {
        'titulo': f'Detalle de {aseguradora.nombre}',
        'aseguradora': aseguradora
    }
    return render(request, 'seguros/detalle_aseguradora.html', context)


def editar_aseguradora(request, pk):
    """Permite modificar los datos de una aseguradora existente."""
    aseguradora = get_object_or_404(Aseguradora, pk=pk)
    
    if request.method == 'POST':
        form = AseguradoraForm(request.POST, instance=aseguradora)
        if form.is_valid():
            form.save()
            return redirect('seguros:lista_aseguradoras')
    else:
        form = AseguradoraForm(instance=aseguradora)
    
    context = {
        'titulo': f'Editar Aseguradora: {aseguradora.nombre}',
        'form': form
    }
    return render(request, 'seguros/crear_aseguradora.html', context)


def eliminar_aseguradora(request, pk):
    """Permite eliminar una aseguradora tras confirmación."""
    aseguradora = get_object_or_404(Aseguradora, pk=pk)

    if request.method == 'POST':
        aseguradora.delete()
        return redirect('seguros:lista_aseguradoras')

    context = {
        'titulo': f'Eliminar Aseguradora: {aseguradora.nombre}',
        'aseguradora': aseguradora
    }
    return render(request, 'seguros/confirmar_eliminacion.html', context)

# --- CRUD de Planes de Seguro ---

def lista_planes_seguro(request, aseguradora_id=None):
    """
    Muestra una lista de planes de seguro. 
    Si se recibe aseguradora_id, filtra los planes de esa aseguradora.
    """
    aseguradora = None
    if aseguradora_id:
        aseguradora = get_object_or_404(Aseguradora, pk=aseguradora_id)
        planes = PlanSeguro.objects.filter(aseguradora=aseguradora).select_related('aseguradora').order_by('nombre_plan')
        titulo = f'Planes de la Aseguradora: {aseguradora.nombre}'
    else:
        planes = PlanSeguro.objects.all().select_related('aseguradora').order_by('nombre_plan')
        titulo = 'Listado de Planes de Seguro'

    context = {
        'titulo': titulo,
        'planes': planes,
        'aseguradora': aseguradora
    }
    return render(request, 'seguros/lista_planes_seguro_por_aseguradora.html', context)


def crear_plan_seguro(request, aseguradora_id=None):
    aseguradora = None
    if aseguradora_id:
        aseguradora = get_object_or_404(Aseguradora, pk=aseguradora_id)

    if request.method == 'POST':
        form = PlanSeguroForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            if aseguradora:
                plan.aseguradora = aseguradora
            plan.save()
            if aseguradora:
                return redirect('lista_planes_seguro_por_aseguradora', aseguradora_id=aseguradora.id)
            else:
                return redirect('lista_planes_seguro')
    else:
        if aseguradora:
            form = PlanSeguroForm(initial={'aseguradora': aseguradora})
        else:
            form = PlanSeguroForm()

    context = {
        'titulo': f'Crear Plan para {aseguradora.nombre}' if aseguradora else 'Registrar Nuevo Plan de Seguro',
        'form': form,
        'aseguradora': aseguradora  # ← esto es clave
    }

    return render(request, 'seguros/crear_plan_seguro.html', context)


def editar_plan_seguro(request, pk):
    """Permite modificar un Plan de Seguro existente."""
    plan = get_object_or_404(PlanSeguro, pk=pk)
    
    if request.method == 'POST':
        form = PlanSeguroForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            return redirect('seguros:lista_planes_seguro')
    else:
        # Importante: Pasar la instancia para pre-llenar los campos
        form = PlanSeguroForm(instance=plan)
    
    context = {
        'titulo': f'Editar Plan: {plan.nombre_plan}', 
        'form': form
    }
    # Reutilizamos la plantilla de creación
    return render(request, 'seguros/crear_plan_seguro.html', context)


def eliminar_plan_seguro(request, pk):
    """Permite eliminar un Plan de Seguro tras confirmación."""
    plan = get_object_or_404(PlanSeguro, pk=pk)

    if request.method == 'POST':
        plan.delete()
        return redirect('seguros:lista_planes_seguro')

    context = {
        'titulo': f'Eliminar Plan de Seguro: {plan.nombre}',
        'plan': plan
    }
    return render(request, 'seguros/confirmar_eliminacion_plan.html', context)

# --- CRUD de Reclamaciones ---
# NOTA: Se ha corregido la duplicidad y la lógica de filtrado de las vistas de reclamación.

# 💡 VISTA DE LISTA GENERAL - Muestra todas las reclamaciones
def lista_reclamaciones(request):
    """Muestra la lista de todas las reclamaciones (claims)."""
    # Esta debería ser la lista general, no solo las pendientes
    reclamaciones = Reclamacion.objects.all().order_by('-fecha_servicio')
    context = {
        'titulo': 'Gestión de Reclamaciones (Todas)',
        'reclamaciones': reclamaciones
    }
    return render(request, 'seguros/lista_reclamaciones.html', context)

# 💡 VISTA DE PENDIENTES - Muestra solo las que necesitan revisión (la que estaba vacía)
def lista_reclamaciones_pendientes(request):
    """
    Muestra solo las reclamaciones que están pendientes de revisión.
    CORRECCIÓN: Incluye el estado 'ENVIADA' que es el estado inicial de creación.
    """
    reclamaciones = Reclamacion.objects.select_related(
        'plan_seguro__aseguradora'
    ).filter(
        estado__in=['ENVIADA', 'PENDIENTE', 'EN_REVISION'] # Filtro corregido
    ).order_by('fecha_servicio')
    
    context = {
        'titulo': 'Reclamaciones Pendientes de Revisión',
        'reclamaciones': reclamaciones,
        'es_pendiente': True
    }
    return render(request, 'seguros/lista_reclamaciones.html', context)


def crear_reclamacion(request):
    """Permite crear un nuevo registro de reclamación."""
    if request.method == 'POST':
        form = ReclamacionForm(request.POST)
        if form.is_valid():
            reclamacion = form.save(commit=False)
            reclamacion.estado = 'ENVIADA' # Estado inicial por defecto
            reclamacion.save()
            messages.success(request, '¡Reclamación creada y pendiente de revisión!')
            # ⬅️ CAMBIO CRÍTICO: Redirigir a la vista que sí tiene el filtro corregido
            return redirect('seguros:lista_reclamaciones_pendientes') 
    else:
        form = ReclamacionForm()

    context = {
        'titulo': 'Registrar Nueva Reclamación',
        'form': form
    }
    return render(request, 'seguros/form_reclamacion.html', context)


def detalle_reclamacion(request, pk):
    """Muestra los detalles y el estado de una reclamación."""
    reclamacion = get_object_or_404(Reclamacion, pk=pk)
    context = {
        'titulo': f'Detalle Reclamación #{pk}',
        'reclamacion': reclamacion
    }
    return render(request, 'seguros/detalle_reclamacion.html', context)


def revisar_reclamacion(request, pk):
    """Vista para que el personal revise y apruebe/deniegue el monto de la reclamación."""
    reclamacion = get_object_or_404(Reclamacion, pk=pk)
    
    if request.method == 'POST':
        monto_aprobado = request.POST.get('monto_aprobado')
        nuevo_estado = request.POST.get('estado')
        
        reclamacion.monto_aprobado = monto_aprobado
        reclamacion.estado = nuevo_estado
        reclamacion.save()
        return redirect('seguros:detalle_reclamacion', pk=pk) # Debe usar el namespace
        # return redirect('detalle_reclamacion', pk=pk) # Eliminada la línea duplicada y se usa el namespace

    context = {
        'titulo': f'Revisar Reclamación #{pk}',
        'reclamacion': reclamacion,
        'form_accion': True
    }
    return render(request, 'seguros/revisar_reclamacion.html', context)


from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages # <--- ¡AGREGAR ESTA IMPORTACIÓN!
from .models import Transaccion, MetodoPago 
from .forms import TransaccionForm 
from gestion_pacientes.models import Paciente 

# Vistas Basadas en Clases (CBVs) para Transacciones

class TransaccionListView(ListView):
    """Muestra la lista de todas las transacciones registradas."""
    model = Transaccion
    template_name = 'transacciones/lista_transacciones.html'
    context_object_name = 'transacciones'
    ordering = ['-fecha_transaccion'] 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registro de Transacciones'
        return context

class TransaccionDetailView(DetailView):
    """Muestra los detalles de una transacción específica."""
    model = Transaccion
    template_name = 'transacciones/detalle_transaccion.html'
    context_object_name = 'transaccion'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Detalle de Transacción #{self.object.id}'
        return context

class TransaccionCreateView(CreateView):
    """Permite registrar una nueva transacción."""
    model = Transaccion
    form_class = TransaccionForm
    template_name = 'transacciones/crear_transaccion.html'
    success_url = reverse_lazy('lista_transacciones') 

    # -------------------------------------------------------------
    # 🕵️ MÉTODOS DE DEBUGGING AGREGADOS AQUÍ 🕵️
    # -------------------------------------------------------------
    
    # Este método se ejecuta si el formulario NO es válido (POST)
    def form_invalid(self, form):
        # ⚠️ Muestra los errores detallados en la consola/terminal del servidor
        print("🔴 ERROR DE VALIDACIÓN DETECTADO:") 
        print(form.errors)
        # Muestra un mensaje de error visible al usuario
        messages.error(self.request, 'Hubo errores al guardar la transacción. Por favor, revisa los campos marcados.')
        return super().form_invalid(form) # Vuelve a mostrar el formulario con errores
    
    # Este método se ejecuta si el formulario es válido (POST)
    def form_valid(self, form):
        # Muestra un mensaje de éxito visible al usuario
        messages.success(self.request, '✅ ¡Transacción registrada con éxito!')
        # El método super().form_valid(form) guarda el objeto y redirige
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar Nueva Transacción'
        return context

# Puedes mantener la vista de Métodos de Pago (si la definimos)
# class MetodoPagoListView(ListView):
#     model = MetodoPago
# ...