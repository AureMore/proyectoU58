from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse, FileResponse, Http404
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView, View, FormView
from django.views.generic.edit import FormView
from django.db.models import Subquery, OuterRef, Sum, F, Q, Value,  Count, Min,Max, ExpressionWrapper, DecimalField, Case, When, FloatField, DurationField, DateField, CharField, Prefetch, IntegerField
from django.db.models.functions import Coalesce, TruncDate, Cast, TruncMonth, ExtractYear, ExtractMonth, Greatest, Substr
from django.db.models.expressions import Func
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from .models import CambioBcv, Paciente, Responsable, Convenio, DetalleConsumoCirugia,GrupoBaremo, Baremo, TipoProcedimiento, SubDetalleBaremo, Medico, Plantilla, ComposicionDetalle, Presupuesto, DetallePresupuesto, Cirugia, DetalleCirugia, Quirofano, NotaQuirurgica, Inventario, RequisitoIngreso, TiempoQuirofano,ConsumoCirugia, Tratamiento, Habitacion,CirugiaHabitacion, Proveedor, Retencion, AltaMedica, MedicoAltaMedica, KitInventario, TipoDocumento, FacturaProveedor, DetalleFacturaProveedor,PagoMedico, FormaPago, TempFecha,TablaImpuesto, Banco, BancoLocal, Transaccion, Moneda, RegistroDocumento, FacturaMedico, RetencionISLR, FormaPagoProveedor, CuentaxCobrar, DetalleCuentaCobrar, Pagador, OrigenPago,AbonoCuentaPagar, RetencionPendiente, DepositoUso, CategoriaInventario, LaboratorioMedicina, PresentacionMedicina, NotaEntregaCompra, DetalleNotaEntrega, Deposito, DepositoTransito, MontoIncremento, InventarioDescarga, TipoDescarga, DetallePrefactura, UnidadCompra, AtencionInmediata, InventarioSolicitud, InventarioHistoria, ImagenPhoto, TrasladoUci, LugarConsumo, LogInventario, LogDetallePresupuesto, InventarioCompuesto, PreIngreso,NotaCreditoCtaCobrar, PagadorUnico,DebitoCredito, ImagenCirugia, LogCuentaCobrar,LogEliminacion, NumeracionFactura, DetalleBaremo, DetalleSubBaremoConsumo,SubBaremo, NombreSubBaremo, TipoProveedor, BaremoVinculado, EstatusCirugia, MateriaPrimaInventario, PagoReciboFacturaMedico, AtencionInmediataCortesia, EvaluacionPreanestesia,Religion, ConsultaPreanestesia, RespuestaEvaluacion, LogDescuento, HistoriaClinica, EvolucionHistoria, DocumentoCirugia, RegistroPresupuestoPDF, HistoriaTransOperatoria, TransaccionFacturaMultiple, ReutilizacionInventario, DistribucionPagoMedico, Especialidad, UnidadProducto, CentroCostoFacturaCompra
from .models import BaremoPagoTercero
from .forms import PacienteForm, CirugiaForm, KitInventarioForm, MedicoForm, ProveedorForm, InventarioForm, DepositoUsoForm, BancoLocalForm, GrupoMedicoForm, SegurosForm
from datetime import datetime, timedelta, date, time
from reportlab.pdfgen import canvas
from django.utils.numberformat import format
from django.utils import timezone
from django.utils.dateparse import parse_date
from operator import attrgetter
from itertools import chain
from openpyxl import Workbook
import requests
import re
import time
import json
import math
import socket
from bs4 import BeautifulSoup
from itertools import groupby
from .utils import CambioDiaBcv, calcular_edad, calculo_neto_pagar_medico,calculo_neto_pagar_medico_bs, calculo_retencion, envioWhatsApp, envio_email, montoaretener, calculo_neto_pagar_factura_bs, calculo_neto_pagar_factura
from django.template.defaultfilters import default_if_none
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import io
from io import BytesIO
import base64
from PIL import Image, ImageDraw
#import pywhatkit
import win32clipboard
import pyautogui as pg
import webbrowser as web
from decimal import Decimal, ROUND_DOWN
from django.template.loader import render_to_string, get_template
from django.template import Context, RequestContext
from xhtml2pdf import pisa
from weasyprint import HTML, CSS
from img2pdf import convert
import img2pdf
import tempfile
from django.core.mail import EmailMessage
from django.core.files.base import ContentFile
from collections import defaultdict
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
#import pandas as pd
import os


# Create your views here.

def truncate_to_decimals(value, decimals):
    factor = 10 ** decimals
    return math.floor(value * factor) / factor


def pasarTodosBaremito(idCirugia, idDetalle, usuario_id, detalle_presupuesto_id):
    baremitos = SubBaremo.objects.filter(detalle_id = idDetalle)
    for baremito in baremitos:
        DetalleSubBaremoConsumo.objects.create(
            cantidad = 1,
            cirugia_id = idCirugia,
            detalle_id = idDetalle,
            subbaremo_id = baremito.id,
            usuario_id = usuario_id,
            detalle_presupuesto_id = detalle_presupuesto_id
        )
        
    return

def plural_to_singular(plural):
    plural_singular = {
        "administrativos":"administrador",
        "visitantes":"invitado",
        "empleados":"empleado",
    }
    
    return plural_singular.get(plural,"error")

def add_group_name_to_context(view_class):
    original_dispatch = view_class.dispatch 
    
    def dispatch(self, request, *args, **kwargs):
        user = self.request.user 
        group = user.groups.first()
        group_name = None
        status = 0
        color = None
        fecha_hoy = datetime.now()
        cambio = CambioBcv.objects.filter(fecha_cambio=datetime.now()).first()
        url = 'https://www.bcv.org.ve/'
        
        if not cambio:
            try:  
                response = requests.get(url,  verify=False) 
            
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    fecha_cambio = datetime.now().date()
                    # Buscar el div con id 'dolar'
                    tomar_cambio_pagina = 1
                    dolar_div = soup.find('div', id='dolar')
                    span = soup.find("span", {"class": "date-display-single"})
                    if span and span.has_attr("content"):
                        fecha_valor = span["content"]  # aquí extraes "2025-08-21T00:00:00-04:00"
                        fecha_obj = datetime.fromisoformat(fecha_valor).replace(tzinfo=None)
                        """ if fecha_obj.date() > datetime.now().date():
                            tomar_cambio_pagina = 0
                            print('se coloca el cambio de ultimo dia habil')
                        else:
                            if fecha_obj.date() == datetime.now().date():
                                tomar_cambio_pagina = 1
                                print('se coloca el cambio de fecha valor') """
                    
                    
                    if dolar_div:
                        # Dentro de ese div, buscar el <strong> que contiene el número
                        numero = dolar_div.find('strong').get_text(strip=True)
                        #return HttpResponse(f'Número extraído: {numero}')
                        cambiobcvdia = numero.replace(',','.')
                        if tomar_cambio_pagina == 1:
                            CambioBcv.objects.create(fecha_cambio=datetime.now(), cambio=cambiobcvdia)
                            print('coloco BCV WEB:', tomar_cambio_pagina)
                        else:
                            print('coloco BCV BD', tomar_cambio_pagina)
                            cambio_hoy = CambioBcv.objects.order_by('-id').first()
                            monto_cambio_hoy = cambio_hoy.cambio
                            CambioBcv.objects.create(fecha_cambio=datetime.now(), cambio=monto_cambio_hoy)
                            cambiobcvdia = monto_cambio_hoy
                            
                        print(cambiobcvdia)
                        print('Tasa Automatica de BCV')
                    else:
                        cambiobcvdia = 0

                else:
                    #return HttpResponse('Error al acceder a la página', status=response.status_code)
                    cambiobcvdia = 0
            except requests.exceptions.SSLError as e:
                return HttpResponse(f'Error de SSL: {str(e)}')
            except Exception as e:
                return HttpResponse(f'Ocurrió un error: {str(e)}')

        else:
            cambiobcvdia = cambio.cambio
        
            
        if group:
            group_name = group.name
        
        context = {
            'group_name': group_name,
            'color': color,
            'cambio':cambiobcvdia,
            'fecha_hoy':fecha_hoy,
        }

        self.extra_context = context
        
        return original_dispatch(self, request, *args, **kwargs)
        
    view_class.dispatch = dispatch
    return view_class


@add_group_name_to_context
class index(TemplateView):
    template_name = 'home.html'
    
def salir(request):
    logout(request)
    return redirect('/')

@add_group_name_to_context  
class pacientes(TemplateView):
    template_name = 'pacientes.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pacientes = Paciente.objects.all().exclude(status = 'X').order_by("-fecha_act")
        context['pacientes'] = pacientes
        return context
    
    

def dt_serverside(request):
    context = {}
    
    dt = request.GET 
    
    draw = int(dt.get("draw"))
    start = int(dt.get("start"))
    length = int(dt.get("length"))
    search = dt.get("search[value]")
    
    registros = Paciente.objects.all().exclude(status = 'X').order_by("-fecha_act")
    
    if search:
        registros = registros.filter(
            Q(id__icontains=search) |
            Q(cedula__icontains=search) |
            Q(nombre__icontains=search) |
            Q(apellido__icontains=search) 
        )
        
    recordsTotal = registros.count()
    recordsFiltered = recordsTotal
    
    context["draw"] = draw
    context["recordsTotal"] = recordsTotal
    context["recordsFiltered"] = recordsFiltered
    
    reg = registros[start:start + length]
    paginator = Paginator(reg, length)
    
    try:
        obj = paginator.page(draw).object_list
    except PageNotAnInteger:
        obj = paginator.page(draw).object_list
    except EmptyPage:
        obj = paginator.page(paginator.num_pages).object_list
        
    datos = [
        {
           "id" :d.id, "foto": d.fotoperfil.url if d.fotoperfil else None, "cedula" : d.cedula, "nombre" : d.nombre,"apellido" : d.apellido, "telefono1" : d.telefono1 
        } for d in obj
    ]
    

    context["datos"] = datos
    return JsonResponse(context,safe=False)


@add_group_name_to_context
class PacienteCreateView(LoginRequiredMixin, SuccessMessageMixin,CreateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'create_patient.html'
    success_url = reverse_lazy('pacientes')
    def form_valid(self, form):
        usuario_id = self.request.user.id
        cedula_rep = self.request.POST.get('cedula_rep')
        if len(cedula_rep) >= 2:
            nombre_rep = self.request.POST.get('nombre_rep')
            apellido_rep = self.request.POST.get('apellido_rep')
            direccion_rep = self.request.POST.get('direccion_rep')
            trabajo_rep = self.request.POST.get('trabajo_rep')
            sexo_rep = self.request.POST.get('sexo_rep')
            direccion_trabajo_rep = self.request.POST.get('direccion_trabajo_rep')
            telefono_rep = self.request.POST.get('telefono_rep')
            existe = Responsable.objects.filter(cedula = cedula_rep).first()
            if not existe:
                responsable = Responsable.objects.create(
                    cedula = cedula_rep,
                    nombre = nombre_rep,
                    apellido = apellido_rep,
                    direccion = direccion_rep ,
                    direccion_trabajo = direccion_trabajo_rep ,
                    telefono1 = telefono_rep ,
                    sexo = sexo_rep ,
                    trabajo = trabajo_rep ,
                    usuario_id =  usuario_id
                )
                responsable.save()
                form.instance.responsable = responsable
                
        form.instance.usuario = self.request.user
        form.save()
            
        messages.success(self.request, 'Paciente creado correctamente, en el menu de acciones dispone de otras opciones')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error revise campos')
        return self.render_to_response(self.get_context_data(form=form))
    
@add_group_name_to_context   
class PacienteEditView(UpdateView):
    model = Paciente
    form_class = PacienteForm
    template_name = 'edit_patient.html'
    success_url = reverse_lazy('pacientes')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id=self.object.id
        paciente = Paciente.objects.filter(id=paciente_id).first()
        if paciente.responsable:
            responsable = Responsable.objects.filter(id=paciente.responsable_id).first()
            context['responsable'] = responsable
            
        
        context['paciente'] = paciente
        return context
    
    
    def form_valid(self, form):
        paciente_id=self.object.id
        paciente = Paciente.objects.filter(id=paciente_id).first()
        usuario_id = self.request.user.id
        cedula_rep = self.request.POST.get('cedula_rep')
        nombre_rep = self.request.POST.get('nombre_rep')
        apellido_rep = self.request.POST.get('apellido_rep')
        direccion_rep = self.request.POST.get('direccion_rep')
        trabajo_rep = self.request.POST.get('trabajo_rep')
        sexo_rep = self.request.POST.get('sexo_rep')
        direccion_trabajo_rep = self.request.POST.get('direccion_trabajo_rep')
        telefono_rep = self.request.POST.get('telefono_rep')
        if cedula_rep:
            responsableexiste = Responsable.objects.filter(cedula = cedula_rep).first()
            if responsableexiste:
                responsable = Responsable.objects.filter(cedula = cedula_rep).update(
                    cedula = cedula_rep,
                    nombre = nombre_rep,
                    apellido = apellido_rep,
                    direccion = direccion_rep ,
                    direccion_trabajo = direccion_trabajo_rep ,
                    telefono1 = telefono_rep ,
                    sexo = sexo_rep ,
                    trabajo = trabajo_rep ,
                    usuario_id =  usuario_id,
                )
                responsable_id = responsableexiste.id
                form.instance.responsable_id = responsable_id
                form.save()
            else:
                responsable = Responsable.objects.create(
                cedula = cedula_rep,
                nombre = nombre_rep,
                apellido = apellido_rep,
                direccion = direccion_rep ,
                direccion_trabajo = direccion_trabajo_rep ,
                telefono1 = telefono_rep ,
                sexo = sexo_rep ,
                trabajo = trabajo_rep ,
                usuario_id =  usuario_id
                )
                responsable.save()
                form.instance.responsable = responsable
                form.save()
        else:
            form.save()

        
        messages.success(self.request, 'El paciente se ha actualizado correctamente')
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar el paciente revise campos')
        return self.render_to_response(self.get_context_data(form=form))
    
    
    
@add_group_name_to_context    
class AutorizacionPdf(TemplateView):
    template_name='pdf_planilla.html'
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id = self.kwargs['pk']
        paciente = Paciente.objects.filter(id=paciente_id).first()
        responsable = Responsable.objects.filter(id=paciente.responsable_id).first()
        context["responsable"]=responsable
        
        return context
    
@add_group_name_to_context    
class presupuestoPdf(TemplateView):
    template_name='pdf_presupuesto.html'
      
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        presupuesto_id = self.kwargs['pk']
        moneda = self.kwargs['moneda']

        presupuesto = Presupuesto.objects.filter(id=presupuesto_id).first()
        responsable  = Responsable.objects.filter(id=presupuesto.paciente.responsable_id).first()
        fecha_actual = datetime.now()
        if presupuesto.congelar_moneda:
            valor_bolivar_dia = presupuesto.cambio_congelado
        else:
            valor_bolivar_dia=CambioDiaBcv(fecha_actual)
        

        if moneda != 1:
            detallepresupuesto = DetallePresupuesto.objects.filter(
            presupuesto_id=presupuesto_id,
            precio__gt = 0
            ).annotate(
                bolivares=ExpressionWrapper(F('precio') * valor_bolivar_dia, output_field=DecimalField())
            ).order_by('detalle__posicion')
        else:
            detallepresupuesto = DetallePresupuesto.objects.filter(
            presupuesto_id=presupuesto_id,
            precio__gt = 0
            ).annotate(
                bolivares=ExpressionWrapper(F('precio') * 0, output_field=DecimalField())
            ).order_by('detalle__posicion')
        
        
        detallepresupuesto1 = DetallePresupuesto.objects.filter(
                presupuesto_id=presupuesto_id
            ).aggregate(total=Sum('precio'))

        total_general = detallepresupuesto1['total']
        
        grupos = [(k, list(g)) for k, g in groupby(detallepresupuesto, lambda x: x.grupo)]
        
        
        context['total_general'] = total_general
        context['grupos']=grupos
        context['moneda']=moneda
        context['presupuesto']=presupuesto
        context['responsable']=responsable
        context['valor_bolivar_dia']=valor_bolivar_dia
        context['detallepresupuesto']=detallepresupuesto

        
        
        return context    

@add_group_name_to_context
class UnautorizedUser(TemplateView):
    template_name = 'error_unautorized_user.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        error_imagen_path = os.path.join(settings.MEDIA_URL,'nop.png')
        context['error_imagen_path']=error_imagen_path
        return context


@add_group_name_to_context    
class baremo(UserPassesTestMixin,TemplateView):
    template_name='baremo_ppal.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='SuperAdministracion') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        convenios = Convenio.objects.all().order_by('id')
        grupos = GrupoBaremo.objects.all().order_by('nombre')
        baremos = Baremo.objects.filter(convenio_id = 1, plantilla_id=1).order_by('detalle__posicion')        
        plantillas = Plantilla.objects.all().order_by('id')   
        subdetalles = SubDetalleBaremo.objects.all().order_by('nombre')
        superUser = self.request.user.groups.filter(Q(name='SuperAdministracion')).exists()
        eliminarBaremo = self.request.user.groups.filter(Q(name='EliminarBaremo')).exists()
        verCostos = self.request.user.groups.filter(Q(name='verCostos')).exists()

        context['verCostos']=verCostos
        context['eliminarBaremo']=eliminarBaremo
        context['convenios']=convenios
        context['superUser']=superUser
        context['grupos']=grupos
        context['baremos']=baremos
        context['plantillas']=plantillas
        context['subdetalles']=subdetalles
        return context
    
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)    
        convenios = Convenio.objects.all().order_by('id')
        grupos = GrupoBaremo.objects.all().order_by('nombre')
        plantillas = Plantilla.objects.all().order_by('id') 
        
        
        convenio = request.POST['convenio']
        grupo = request.POST['grupo']
        plantilla_id = request.POST['plantilla']
        id_guardar = request.POST['name_idbaremo']
        if 'btn-guardar-check' in request.POST:
            if 'name_exento' in request.POST:
                Baremo.objects.filter(id=id_guardar).update(exento=True)
            else:
                Baremo.objects.filter(id=id_guardar).update(exento=False)
                
                
            if 'name_ntqx' in request.POST:
                Baremo.objects.filter(id=id_guardar).update(ntqx=True)
            else:
                Baremo.objects.filter(id=id_guardar).update(ntqx=False)
                
            if 'name_xcantidad' in request.POST:
                Baremo.objects.filter(id=id_guardar).update(xcantidad=True)
            else:
                Baremo.objects.filter(id=id_guardar).update(xcantidad=False)

            
           
           
        if not grupo:
            baremos = Baremo.objects.filter(convenio_id = convenio, plantilla_id = plantilla_id ).order_by('detalle__posicion')
        else:
            baremos = Baremo.objects.filter(grupo_id = grupo, convenio_id = convenio, plantilla_id = plantilla_id).order_by('detalle__posicion')
            
        superUser = self.request.user.groups.filter(Q(name='SuperAdministracion')).exists()
        eliminarBaremo = self.request.user.groups.filter(Q(name='EliminarBaremo')).exists()
             
        context['eliminarBaremo']=eliminarBaremo
        context['superUser']=superUser
        context['convenios']=convenios
        context['grupos']=grupos
        context['baremos']=baremos
        context['plantillas']=plantillas
        return render(request, 'baremo_ppal.html', context)
    
def filtroSubDetalle(request):
    convenio = request.GET.get('convenio')
    grupo = request.GET.get('grupo')
    detalle = request.GET.get('detalle')

    # Perform your filtering logic here
    filtered_data = Baremo.objects.filter(convenio_id=convenio, grupo_id=grupo, detalle_id=detalle, inactivar = False).order_by('cantidad')

    # Return the filtered data as JSON
    return JsonResponse(list(filtered_data.values()), safe=False)


def filtroComposicion(request):
    convenio = request.GET.get('convenio')
    detalle = request.GET.get('detalle')
    # Perform your filtering logic here
    filtered_data = ComposicionDetalle.objects.filter(convenio_id=convenio, detalle_id=detalle).order_by('cantidad')
    # Return the filtered data as JSON
    return JsonResponse(list(filtered_data.values()), safe=False)


def filtroConsumo(request):
    presupuesto = request.GET.get('presupuesto')
    detalle = request.GET.get('detalle') 
    iddetallepresupuesto = request.GET.get('iddetallepresupuesto') 
    print('detalle:', detalle)
    print('iddetallepresupuesto:', iddetallepresupuesto)
    # Perform your filtering logic here
    if detalle == '0':
        filtered_data = ConsumoCirugia.objects.filter(cirugia__presupuesto_id=presupuesto,consumo_id=2 ).order_by('hora')
        #filtered_data = ConsumoCirugia.objects.filter(cirugia__presupuesto_id=presupuesto,detalle_presupuesto_id = iddetallepresupuesto ).order_by('hora')
    else:
        if detalle == '3':
            filtered_data = ConsumoCirugia.objects.filter(cirugia__presupuesto_id=presupuesto,consumo_id = 7).order_by('hora')
        else:
            if detalle == '5':
                filtered_data = ConsumoCirugia.objects.filter(cirugia__presupuesto_id=presupuesto,compuesto__in = ['2','3'], consumo_id__in = [9,10]).order_by('hora')
            else:
                if detalle == '8':
                    filtered_data = ConsumoCirugia.objects.filter(cirugia__presupuesto_id=presupuesto,consumo_id = 8).order_by('hora')
                else:
                    filtered_data = ConsumoCirugia.objects.filter(cirugia__presupuesto_id=presupuesto,inventario__categoria_id__in = [1,2], consumo_id = 1).order_by('hora')
        
        
    data = []
    for consumo in filtered_data:
        data.append({
            'id': consumo.id,
            'cantidad_real_usada': consumo.cantidad_real_usada,
            'monto_unitario':round(consumo.precio_unitario,2),
            'monto_venta': (Decimal(round(consumo.precio_unitario,2)) * Decimal(consumo.cantidad_real_usada)),  # Calculado en Python
            'hora': consumo.fecha_act,
            'nombre': consumo.inventario.nombre,
            'categoria': consumo.inventario.categoria.nombre,
            'lugar': consumo.consumo.nombre
        })
    return JsonResponse(data, safe=False)

    
@add_group_name_to_context    
class CirugiaAdd(UserPassesTestMixin,TemplateView):
    template_name='cirugia.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Admision') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id = self.kwargs['paciente_id']
        user_id = self.request.user.id
        paciente = Paciente.objects.filter(id = paciente_id).first()
        convenios = Convenio.objects.all().order_by('id')
        grupos = GrupoBaremo.objects.all().order_by('nombre')
        tipos = TipoProcedimiento.objects.all().order_by('id')
        medicos = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        detalles = Baremo.objects.filter(inactivar = False).order_by('detalle') 
        plantillas = Plantilla.objects.all().order_by('id') 
        responsables = Responsable.objects.all().order_by('nombre')
        responsable = Responsable.objects.filter(id=paciente.responsable_id).first()
        if responsable:
             context['responsable']=responsable
            
        context['convenios']=convenios
        context['grupos']=grupos
        context['detalles']=detalles
        context['paciente']=paciente
        context['tipos']=tipos
        context['medicos']=medicos
        context['plantillas']=plantillas
        context['responsables']=responsables
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id = self.kwargs['paciente_id']
        valor_bolivar_dia=CambioDiaBcv(datetime.now())
        idConvenio = request.POST.get('convenio')
        baremo_values = request.POST.getlist('baremo_fila')
        nombre_procedimiento = request.POST.get('procedimiento')
        diagnostico = request.POST.get('diagnostico')
        tipo_procedimiento =  request.POST.get('tipo')
        plantilla_id =  request.POST.get('plantilla')
        medico_ppal =  request.POST.get('medico')
        fecha_procedimiento =  request.POST.get('fecha_procedimiento')
        hora_procedimiento =  request.POST.get('hora_procedimiento')
        dias_hospitalizacion =  request.POST.get('hospital')
        horas_qx =  request.POST.get('horasqx')
        usuario =  self.request.user.id
        paciente = Paciente.objects.filter(id=paciente_id).first()
        
        detalle_formateado = []
        for i in range(0,len(baremo_values),7):
            detalle = baremo_values[i] + '*' + baremo_values[i+1] + '*' + baremo_values[i+2]+ '*' + baremo_values[i+3]+ '*' + baremo_values[i+4]+ '*' + baremo_values[i+5]+ '*' + baremo_values[i+6]
            detalle_formateado.append(detalle)
            
        if detalle_formateado:
            nombre_pc = socket.gethostname()
            presupuesto = Presupuesto.objects.create(
                paciente_id = paciente_id,
                tipo_procedimiento_id = tipo_procedimiento,
                medico_ppal_id = medico_ppal,
                fecha_procedimiento = fecha_procedimiento,
                hora_procedimiento=hora_procedimiento,
                nombre_procedimiento = nombre_procedimiento,
                dias_hospitalizacion = dias_hospitalizacion,
                diagnostico = diagnostico,
                horas_qx = horas_qx,
                usuario_id = usuario,
                convenio_id = idConvenio,
                responsable_id = paciente.responsable_id,
                cambio_congelado = valor_bolivar_dia,
                fecha_cambio = datetime.now(),
                nombre_pc = nombre_pc
            )
            presupuesto.save()
            presupuesto_id = presupuesto.id
            detalles = detalle_formateado
            total_presupuesto = 0
            for detalle in detalles:
                cantidad,venta ,unidad,convenio_id,grupo_id,detalle_id,ntqx = detalle.split('*')
                if ntqx == "false" or ntqx == "true" :
                    if ntqx == "false":
                        ntqx = False 
                    else:
                        ntqx = True
                        
                total_presupuesto += float(venta.replace(',','.'))
                if cantidad == '':
                    cantidad = '1,00'

                if venta == '':
                    venta = '0,00'
                
                DetallePresupuesto.objects.create(
                    presupuesto_id = presupuesto_id,
                    convenio_id = convenio_id,
                    grupo_id = grupo_id,
                    detalle_id = detalle_id,
                    plantilla_id = plantilla_id,
                    usuario_id = usuario,
                    cantidad = cantidad.replace(',','.'),
                    precio = venta.replace(',','.'),
                    ntqx = ntqx
                )
                
            cuentacobrar = CuentaxCobrar.objects.create(
                paciente_id = paciente_id,
                presupuesto_id = presupuesto_id,
                usuario_id = self.request.user.id
            )
            cuentacobrar.save()
            cuentacobrar_id = cuentacobrar.id
            DetalleCuentaCobrar.objects.create(
                montocobrar = total_presupuesto,
                descripcion = 'Monto Total Procedimiento.:'+str(nombre_procedimiento),
                cuentacobrar_id = cuentacobrar_id,
                
            )
        return redirect('pacientes')
    
@add_group_name_to_context    
class CirugiaNew(TemplateView):
    template_name='cirugia_new.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        convenios = Convenio.objects.all().order_by('id')
        grupos = GrupoBaremo.objects.all().order_by('nombre')
        tipos = TipoProcedimiento.objects.all().order_by('id')
        medicos = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        detalles = Baremo.objects.filter(inactivar = False).order_by('detalle') 
        plantillas = Plantilla.objects.all().order_by('id') 
        responsables = Responsable.objects.all().order_by('nombre')
        context['convenios']=convenios
        context['grupos']=grupos
        context['detalles']=detalles
        context['tipos']=tipos
        context['medicos']=medicos
        context['plantillas']=plantillas
        context['responsables']=responsables
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        idConvenio = request.POST.get('convenio')
        cedula =  request.POST.get('new_paciente_cedula')
        nombre =  request.POST.get('new_paciente_nombre')
        apellido =  request.POST.get('new_paciente_apellido')
        telefono1 =  request.POST.get('new_paciente_telefono')
        direccion =  request.POST.get('new_paciente_direccion')
        cedularesp =  request.POST.get('cedula_resp')
        nombreresp =  request.POST.get('nombre_resp')
        apellidoresp =  request.POST.get('apellido_resp')
        telefonoresp =  request.POST.get('telefono_resp')
        baremo_values = request.POST.getlist('baremo_fila')
        nombre_procedimiento = request.POST.get('procedimiento')
        diagnostico = request.POST.get('diagnostico')
        tipo_procedimiento =  request.POST.get('tipo')
        plantilla_id =  request.POST.get('plantilla')
        medico_ppal =  request.POST.get('medico')
        fecha_procedimiento =  request.POST.get('fecha_procedimiento')
        hora_procedimiento =  request.POST.get('hora_procedimiento')
        dias_hospitalizacion =  request.POST.get('hospital')
        horas_qx =  request.POST.get('horasqx')
        usuario =  self.request.user.id
        paciente = Paciente.objects.filter(cedula = cedula).first()
        idresponsable = None
        responsable = Responsable.objects.filter(cedula=cedularesp).first()
        responsableexiste = Responsable.objects.filter(cedula=cedularesp).first()
        
        if responsable:
            responsable = Responsable.objects.filter(cedula=cedularesp).update(cedula = cedularesp, nombre=nombreresp, apellido=apellidoresp, telefono1=telefonoresp, usuario_id = usuario)
            idresponsable = responsableexiste.id
        else:
            responsable = Responsable.objects.create(cedula = cedularesp, nombre=nombreresp, apellido=apellidoresp, telefono1=telefonoresp, usuario_id = usuario)
            responsable.save()
            idresponsable = responsable.id

        if paciente:
            paciente_id = paciente.id
            paciente = Paciente.objects.filter(id=paciente.id).update(nombre=nombre, apellido=apellido,telefono1=telefono1,direccion=direccion, usuario_id = usuario, responsable_id = idresponsable )
        else:
            paciente = Paciente.objects.create(cedula=cedula,nombre=nombre, apellido=apellido,telefono1=telefono1,direccion=direccion, usuario_id = usuario, responsable_id = idresponsable)
            paciente.save()
            paciente_id = paciente.id
            
        
        
        detalle_formateado = []
        for i in range(0,len(baremo_values),7):
            detalle = baremo_values[i] + '*' + baremo_values[i+1] + '*' + baremo_values[i+2]+ '*' + baremo_values[i+3]+ '*' + baremo_values[i+4]+ '*' + baremo_values[i+5]+ '*' + baremo_values[i+6]
            detalle_formateado.append(detalle)
            
        if detalle_formateado:
            nombre_pc = socket.gethostname()
            presupuesto = Presupuesto.objects.create(
                paciente_id = paciente_id,
                tipo_procedimiento_id = tipo_procedimiento,
                medico_ppal_id = medico_ppal,
                fecha_procedimiento = fecha_procedimiento,
                hora_procedimiento=hora_procedimiento,
                nombre_procedimiento = nombre_procedimiento,
                diagnostico = diagnostico,
                dias_hospitalizacion = dias_hospitalizacion,
                horas_qx = horas_qx,
                usuario_id = usuario,
                convenio_id = idConvenio,
                responsable_id = idresponsable,
                nombre_pc = nombre_pc
            )
            presupuesto.save()
            presupuesto_id = presupuesto.id
            detalles = detalle_formateado
            total_presupuesto=0
            for detalle in detalles:
                cantidad,venta ,unidad,convenio_id,grupo_id,detalle_id, ntqx = detalle.split('*')
                
                if ntqx == "false" or ntqx == "true" :
                    if ntqx == "false":
                        ntqx = False 
                    else:
                        ntqx = True
                
                
                total_presupuesto += float(venta.replace(',','.'))
                if cantidad == '':
                    cantidad = '1,00'

                if venta == '':
                    venta = '0,00'


                DetallePresupuesto.objects.create(
                    presupuesto_id = presupuesto_id,
                    convenio_id = convenio_id,
                    grupo_id = grupo_id,
                    detalle_id = detalle_id,
                    plantilla_id = plantilla_id,
                    usuario_id = usuario,
                    cantidad = cantidad.replace(',','.'),
                    precio = venta.replace(',','.'),
                    ntqx = ntqx
                )
                
                
            cuentacobrar = CuentaxCobrar.objects.create(
                paciente_id = paciente_id,
                presupuesto_id = presupuesto_id,
                usuario_id = self.request.user.id
                )
            cuentacobrar.save()
            cuentacobrar_id = cuentacobrar.id
            DetalleCuentaCobrar.objects.create(
                    montocobrar = total_presupuesto,
                    descripcion = 'Monto Total Procedimiento..:'+str(nombre_procedimiento),
                    cuentacobrar_id = cuentacobrar_id,
                    
                )
                
                
        
        return redirect('presupuestosgeneral')


@add_group_name_to_context    
class Vercirugia(TemplateView):
    template_name='ver_cirugia.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        presupuesto_id = self.kwargs['presupuesto_id']
        user_id = self.request.user.id
        presupuesto = Presupuesto.objects.filter(id = presupuesto_id).first()
        fecha_actual = datetime.now()
        if presupuesto.congelar_moneda:
            valor_bolivar_dia = presupuesto.cambio_congelado
        else:
            valor_bolivar_dia=CambioDiaBcv(fecha_actual)
            
            
        detallepresupuesto = DetallePresupuesto.objects.filter(
            presupuesto_id=presupuesto_id
        ).annotate(
            bolivares=ExpressionWrapper(F('precio') * valor_bolivar_dia, output_field=DecimalField())
        ).order_by('detalle__posicion')
        
        detallepresupuesto1 = DetallePresupuesto.objects.filter(
                presupuesto_id=presupuesto_id
            ).aggregate(total=Sum('precio'))

        total_general = detallepresupuesto1['total']
        
        grupos = [(k, list(g)) for k, g in groupby(detallepresupuesto, lambda x: x.grupo)]
        responsable = Responsable.objects.filter(id=presupuesto.paciente.responsable_id).first()
        if responsable:
            context['responsable']=responsable
                
                
        context['total_general'] = total_general
        context['grupos']=grupos
        context['presupuesto']=presupuesto
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        presupuesto_id = self.kwargs['presupuesto_id']
        moneda =  request.POST.get('tipo_moneda')
        
        return redirect('presupuestopdf', pk = presupuesto_id, moneda = moneda )
        
    
    
def actualizar_precio(request):
    cantidad = request.GET.get('cantidad1')
    id_baremo = request.GET.get('idBaremo1')
    cantidad_entera = int(float(cantidad))  
    baremo = Baremo.objects.filter(id=id_baremo).first()
    # Realiza la operación que necesites con la cantidad y el baremo
    convenio_id = baremo.convenio_id
    precio_baremo = baremo.venta
    if baremo.xcantidad:
        precio_baremo = baremo.venta * cantidad_entera
        
        
    grupo_id = baremo.grupo_id
    detalle_id = baremo.detalle_id
    precio = ComposicionDetalle.objects.filter(convenio_id=convenio_id,grupo_id=grupo_id,detalle_id=detalle_id,cantidad=cantidad_entera).first()
    if precio:
        total_hr_qx=precio.venta
    else:
        total_hr_qx=precio_baremo
   
    return JsonResponse({'precio': total_hr_qx})


def Buscar_convenio(request):
    id_presupuesto = request.GET.get('selected_Id')
    presupuesto = Presupuesto.objects.filter(id=id_presupuesto).first()
    if presupuesto:
        nombre_convenio = presupuesto.convenio.nombre
        if presupuesto.medico_ppal is not None:
            medicoId = presupuesto.medico_ppal.id
        else:
            medicoId=0

        pacienteNombre = presupuesto.paciente.nombre + " " +presupuesto.paciente.apellido
        pacienteCedula = presupuesto.paciente.cedula
        procedimiento =presupuesto.nombre_procedimiento
        horaCirugia = presupuesto.hora_procedimiento
        fecha_procedimiento = presupuesto.fecha_procedimiento
    else:
        nombre_convenio = "ERROR EN PRESUPUESTO SIN CONVENIO"
        
    data = {
        'nombre_convenio': nombre_convenio,
        'medicoId' : medicoId,
        'pacienteNombre' : pacienteNombre,
        'pacienteCedula' : pacienteCedula,
        'procedimiento' : procedimiento,
        'horaCirugia' : horaCirugia,
        'fecha_procedimiento':fecha_procedimiento
    }
    
    return JsonResponse(data)

def filtrobaremopresupuesto(request):
    convenio = request.GET.get('convenio')
    plantilla = request.GET.get('plantilla')
    horaqx = request.GET.get('horaqx')
    horaho = request.GET.get('horaho')
    horaqx = int(horaqx)
    horaho = int(horaho)
    # Perform your filtering logic here
    if horaho > 0:
        filtered_data = Baremo.objects.filter(convenio_id=convenio, plantilla_id=plantilla, inactivar = False).exclude(id=35).order_by('detalle__posicion')
    else:
        filtered_data = Baremo.objects.filter(convenio_id=convenio, plantilla_id=plantilla, inactivar = False).exclude(id=36).order_by('detalle__posicion')
        
    # Return the filtered data as JSON
    data = list(filtered_data.values('id', 'grupo__nombre', 'detalle__nombre', 'cantidad', 'venta', 'unidad__nombre', 'convenio','grupo','detalle','ntqx','haymas','xcantidad' ))
    if horaho > 1:
        for hh in data:
            if hh['xcantidad']:
                tota_hr_hospital = hh['venta'] * horaho
                hh['venta'] = tota_hr_hospital
                hh['cantidad'] = horaho
    
    
    if horaqx > 1:
        for item in data:
            grupo_id=item['grupo']
            detalle_id = item['detalle']
           
            precio = ComposicionDetalle.objects.filter(convenio_id=convenio,grupo_id=grupo_id,detalle_id=detalle_id,cantidad=horaqx).first()
            if precio:
                total_hr_qx=precio.venta
                item['venta'] = total_hr_qx
                item['haymas'] = 1
         
                
    return JsonResponse(data, safe=False)


@add_group_name_to_context    
class ListaPresupuesto(TemplateView):
    template_name='listado_presupuesto_paciente.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id = self.kwargs['paciente_id']
        user_id = self.request.user.id
        """  presupuestos = Presupuesto.objects.filter(paciente_id = paciente_id).annotate(
                    total_venta=Sum('detallepresupuesto__precio')
                    ).order_by('fecha_procedimiento') """
        
        presupuestos = Presupuesto.objects.values_list('id','paciente__nombre','paciente__apellido','fecha_act', 'fecha_procedimiento', 'nombre_procedimiento','dias_hospitalizacion','horas_qx','estatus__nombre','cirugia__id','estatus','paciente_id'
                                                       ).filter(paciente_id = paciente_id).order_by('-fecha_act')

        context['presupuestos']=presupuestos
        return context
    
@add_group_name_to_context    
class ListaPresupuestoGeneral(TemplateView):
    template_name='listado_presupuesto_general.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        """ presupuestos = Presupuesto.objects.all().annotate(
                    total_venta=Sum('detallepresupuesto__precio')
                    ).order_by('-fecha_act') """
                    
        presupuestos = Presupuesto.objects.values_list('id','paciente__nombre','paciente__apellido','fecha_act', 'fecha_procedimiento', 'nombre_procedimiento','dias_hospitalizacion','horas_qx','estatus__nombre','cirugia__id','estatus','paciente_id'
                                                       ).filter(estatus_id__lte = 9 ).order_by('-fecha_act')
        
        

        eliminarPresupuesto = self.request.user.groups.filter(Q(name='EliminarPresupuesto')).exists()
        administrador = self.request.user.groups.filter(Q(name='Administradores')).exists()

        context['eliminarPresupuesto']=eliminarPresupuesto
        context['administrador']=administrador
        context['presupuestos']=presupuestos
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        presupuesto_id = request.POST['name_presupuesto_eliminar']
        eliminar_consumo = request.POST.get('name_eliminar_consumo')
        presupuesto = Presupuesto.objects.filter(id = presupuesto_id).first()
        cirugia = Cirugia.objects.filter(presupuesto_id = presupuesto_id).first()
        if cirugia:
            id_cirugia = cirugia.id
        else:
            id_cirugia = 0
            
        cantidad_consumos = 0
        if cirugia:
            cirugia_id = cirugia.id
            cantidad_consumos = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id).count()
            if eliminar_consumo:
                ConsumoCirugia.objects.filter(cirugia_id = cirugia_id).delete()
            else:
                cantidad_consumos = 0
         
         
        LogEliminacion.objects.create(
            descripcion = 'Eliminacion de Presupuesto en presupuesto :'+str(presupuesto_id)+' Viculado a cirugia: '+str(id_cirugia)+ ' y eliminacion de consumo en: '+str(eliminar_consumo)+' cantidad consumos eliminados: '+str(cantidad_consumos)+ ' del paciente:'+str(presupuesto.paciente),
            usuario_id = self.request.user.id
        )
           
        Presupuesto.objects.filter(id = presupuesto_id).delete()
        if cirugia:
            Cirugia.objects.filter(id = cirugia_id).delete()
        
        return redirect('presupuestosgeneral')
    
@add_group_name_to_context    
class AdmisionNew(TemplateView):
    template_name='admision.html'
    
    def get(self, request, *args, **kwargs):
        paciente_id = self.kwargs['paciente_id']
        paciente = Paciente.objects.filter(id=paciente_id).first()
        if paciente:
            cirugia = Cirugia.objects.filter(paciente_id=paciente.id).first()
            presupuesto = Presupuesto.objects.filter(paciente_id=paciente.id, estatus_id = 11).first()
            if cirugia:
                if cirugia.estatus_id in [2,3,4,5,6,9,10,11]:
                    messages.error(request, 'EXISTE UNA ADMISION ACTUAL CON ESE PACIENTE Y LA HISTORIA ES :'+str(cirugia.id)+' ESTATUS ACTUAL: '+str(cirugia.estatus)+'/ NOTA: NO PUEDE ADMITIR NUEVAMENTE ANTES DE EJECUTAR EL ALTA DEL PACIENTE')
                    return redirect('pacientes')

            if presupuesto:
                messages.error(request, 'EXISTE UN PREINGRESO ACTUAL CON ESE PACIENTE, ESTATUS ACTUAL: '+str(presupuesto.estatus)+'/ NOTA: NO PUEDE ADMITIR NUEVAMENTE ')
                return redirect('pacientes')
        
        # Si no hay redireccionamiento, llama al método get_context_data
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id = self.kwargs['paciente_id']
        paciente = Paciente.objects.filter(id=paciente_id).first()
        edad_paciente=calcular_edad(paciente.fecha_nac)
      
        presupuestos = Presupuesto.objects.filter(estatus_id=1, paciente_id = paciente_id)
        
        responsable = Responsable.objects.filter(id=paciente.responsable_id).first()
        if responsable:
            context['responsable'] = responsable
            
        
        cambio_hoy = CambioDiaBcv(datetime.now())
        fecha_hoy = datetime.now()
        medicos = Medico.objects.filter(grupo='M').exclude(tipopersonal_id = 9).order_by('nombre')
        imagen_paciente = ImagenPhoto.objects.filter(cedula = paciente.cedula ).first()
        if imagen_paciente:
            pass
        else:
            imagen_paciente = ImagenPhoto.objects.filter(cedula = 'VU58Image' ).first()

        
        context['edad_paciente'] = edad_paciente
        context['imagen_paciente'] = imagen_paciente
        context['paciente'] = paciente
        context['cambio_hoy'] = cambio_hoy
        context['fecha_hoy'] = fecha_hoy
        context['presupuestos'] = presupuestos
        context['medicos'] = medicos
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id = self.kwargs['paciente_id']
        user_id = self.request.user.id
        id_presupuesto_seleccionado = request.POST.get('seleccion')
        if not id_presupuesto_seleccionado:
            messages.warning(request, 'Debe seleccionar el presupuesto para proceder a la admision del paciente')
            return redirect('admision' , paciente_id = paciente_id ) 
        
        cambio_congelado = request.POST.get('monto_cambio_congelado')
        fecha_congelado = request.POST.get('fecha_cambio_congelado')
        medico_id = request.POST.get('medico')
        persona_contacto = request.POST.get('persona_contacto')
        if medico_id == "None":
            medico_id = None
        else:
            medico = Medico.objects.filter(id=medico_id).first()

        telefono_contacto = request.POST.get('telefono_contacto')
        registros_presupuesto = Presupuesto.objects.filter(id=id_presupuesto_seleccionado).first()
        responsable = Responsable.objects.filter(id=registros_presupuesto.paciente.responsable_id).first()
        if registros_presupuesto.congelar_moneda:
            Presupuesto.objects.filter(id=id_presupuesto_seleccionado).update(
                cambio_congelado = cambio_congelado.replace(',','.'),
                fecha_cambio = fecha_congelado
            )
            registros_presupuesto = Presupuesto.objects.filter(id=id_presupuesto_seleccionado).first()
            
            
        informe_med_ingreso = orden_ingreso = carta_compromiso = tramite_administrativo = examen_preoperatorio = evaluacion_cardio = evaluacion_preanestesica = False
        
        
        if 'informe_med_ingreso' in request.POST:
            informe_med_ingreso = True
            
        if 'orden_ingreso' in request.POST:
            orden_ingreso = True
            
        if 'carta_compromiso' in request.POST:
            carta_compromiso = True
            
        if 'tramite_administrativo' in request.POST:
            tramite_administrativo = True
            
        if 'examen_preoperatorio' in request.POST:
            examen_preoperatorio = True
            
        if 'evaluacion_cardio' in request.POST:
            evaluacion_cardio = True
            
        if 'evaluacion_preanestesica' in request.POST:
            evaluacion_preanestesica = True
            
        boton_presionado = request.POST.get('btn_aceptar')
        if boton_presionado == 'aceptar':
            cirugia_creada = Cirugia.objects.create(paciente_id=registros_presupuesto.paciente.id ,tipo_procedimiento_id =registros_presupuesto.tipo_procedimiento.id,medico_ppal_id = medico_id,
                                                fecha_procedimiento =registros_presupuesto.fecha_procedimiento  , hora_procedimiento =registros_presupuesto.hora_procedimiento,
                                                nombre_procedimiento  =registros_presupuesto.nombre_procedimiento ,dias_hospitalizacion  =registros_presupuesto.dias_hospitalizacion ,
                                                horas_qx =registros_presupuesto.horas_qx, notas =registros_presupuesto.notas ,usuario_id  = user_id , convenio_id  = registros_presupuesto.convenio_id,
                                                presupuesto_id = id_presupuesto_seleccionado, congelar_moneda = registros_presupuesto.congelar_moneda, cambio_congelado = registros_presupuesto.cambio_congelado,
                                                fecha_cambio = registros_presupuesto.fecha_cambio, precarga = 1, ultimo_estatus = 2, fecha_creacion=datetime.now())
            cirugia_creada.save()
            idHistoria = cirugia_creada.id

            objectos_detalle = []
            registros_detalle_presupuesto = DetallePresupuesto.objects.filter(presupuesto_id=id_presupuesto_seleccionado)
            for detalle in registros_detalle_presupuesto:
                if detalle.ntqx:
                    facturable = False
                else:
                    facturable = True
                    
                    
                objectos_detalle.append(DetalleCirugia(cirugia_id=idHistoria ,cantidad =detalle.cantidad ,precio = detalle.precio,
                                                detalle_id=detalle.detalle_id ,notas =detalle.notas  , tx =detalle.tx,
                                                fecha_cambio  =detalle.fecha_cambio ,convenio_id  =detalle.convenio_id ,
                                                grupo_id =detalle.grupo_id, plantilla_id =detalle.plantilla_id ,unidad_id  = 1, 
                                                usuario_id  = user_id, ntqx = detalle.ntqx, facturable=facturable
                                                ))
                
                
            DetalleCirugia.objects.bulk_create(objectos_detalle)
            Presupuesto.objects.filter(id=id_presupuesto_seleccionado).update(estatus_id=2)
            
            RequisitoIngreso.objects.create(
                cirugia_id = idHistoria,
                informe_med_ingreso = informe_med_ingreso,
                orden_ingreso = orden_ingreso,
                carta_compromiso = carta_compromiso,
                tramite_administrativo = tramite_administrativo,
                examen_preoperatorio = examen_preoperatorio,
                evaluacion_cardio = evaluacion_cardio,
                evaluacion_preanestesica = evaluacion_preanestesica
            )
            
            CuentaxCobrar.objects.filter(presupuesto_id = id_presupuesto_seleccionado).update(
                cirugia_id = idHistoria,
                usuario_id = self.request.user.id
            )


            
            return redirect('lista_cirugia') 
        else:
            imagen_paciente = ImagenPhoto.objects.filter(cedula = registros_presupuesto.paciente.cedula).first()
            if imagen_paciente:
                pass
            else:
                imagen_paciente = ImagenPhoto.objects.filter(cedula = 'VU58Image' ).first()
            
            if registros_presupuesto:
                edad_paciente=calcular_edad(registros_presupuesto.paciente.fecha_nac)
                context['telefono_contacto'] = telefono_contacto
                context['persona_contacto'] = persona_contacto
                context['registros_presupuesto'] = registros_presupuesto
                context['edad_paciente'] = edad_paciente
                context['responsable'] = responsable
                context['informe_med_ingreso'] = informe_med_ingreso
                context['orden_ingreso'] = orden_ingreso
                context['carta_compromiso'] = carta_compromiso
                context['tramite_administrativo'] = tramite_administrativo
                context['examen_preoperatorio'] = examen_preoperatorio
                context['evaluacion_cardio'] = evaluacion_cardio
                context['evaluacion_preanestesica'] = evaluacion_preanestesica
                context['medico'] = medico
                context['imagen_paciente'] = imagen_paciente

                if boton_presionado == 'imprimirconsentimiento':
                    fecha_hoy = datetime.now()
                    context['fecha_hoy'] = fecha_hoy
                    context['registros_presupuesto'] = registros_presupuesto
                    return render(request, 'consentimiento.html', context)
                else:
                    return render(request, 'hc1.html', context)
            else:
                return render(request, 'hc1.html')
        
        
    
@add_group_name_to_context    
class ListadoCirugia(TemplateView):
    template_name='listado_cirugia.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugias = Cirugia.objects.filter(estatus_id__gt=1, estatus_id__lt=4).order_by('-fecha_act')
        quirofanos = Quirofano.objects.all().order_by('NQx')
        baremo = Baremo.objects.filter(convenio_id=1,plantilla_id=2, grupo_id = 7, inactivar = False).order_by('detalle__posicion')
        disponible_deposito = []
        deposito_precarga = []
        deposito_precarga = Deposito.objects.filter(precarga=True).first()
        if deposito_precarga:
            disponible_deposito = DepositoUso.objects.filter(deposito_id = deposito_precarga.id, cantidad_deposito__gt = 0, inventario__producto_activo =True)

        context['baremo']=baremo
        context['cirugias']=cirugias
        context['quirofanos']=quirofanos
        context['deposito_precarga']=deposito_precarga
        context['disponible_deposito']=disponible_deposito
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        quirofano = request.POST.get('quirofano')
        notacirugia = request.POST.get('nota_en_cirugia')
        idCirugia = request.POST.get('id_cirugia')
        lista_nota = request.POST.getlist('lista_nota')
        detalle_formateado = []
        NotaQuirurgica.objects.filter(cirugia_id=idCirugia).exclude(participante_id=43).delete()
        Cirugia.objects.filter(id=idCirugia).update(notas=notacirugia, estatus_id=3, quirofano_id =quirofano )
        presupuesto = Cirugia.objects.filter(id=idCirugia).first()
        Presupuesto.objects.filter(id=presupuesto.presupuesto_id).update(estatus_id = 3)
        
        for i in range(0,len(lista_nota),5):
            detalle = lista_nota[i] + '*' + lista_nota[i+1] + '*' + lista_nota[i+2]+ '*' + lista_nota[i+3]+ '*' + lista_nota[i+4]
            detalle_formateado.append(detalle)
            
        if detalle_formateado:
            detalles = detalle_formateado
            for detalle in detalles:
                cirugia,detalle_id ,medico_id,nota,incluir = detalle.split('*')
                NotaQuirurgica.objects.create(cirugia_id=idCirugia, nota=nota, medico_id=medico_id, participante_id=detalle_id,
                                              quirofano_id=quirofano,incluir=incluir)
                
                    
        return redirect('lista_cirugia')
    
    
@add_group_name_to_context    
class ListadoCirugiaFinish(TemplateView):
    template_name='listado_cirugia.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugias = Cirugia.objects.filter(estatus_id__gt=3,estatus_id__lt=7 ).order_by('-fecha_act').annotate(
            tratamientos_no_cumplidos=Count('tratamiento', filter=Q(tratamiento__cumplido=False))
        )
       
        quirofanos = Quirofano.objects.all().order_by('NQx')
        disponible_deposito = []
        deposito_precarga = []

        deposito_precarga = Deposito.objects.filter(precarga=True).first()
        if deposito_precarga:
            disponible_deposito = DepositoUso.objects.filter(deposito_id = deposito_precarga.id, cantidad_deposito__gt = 0, inventario__producto_activo =True)


        
        context['cirugias']=cirugias
        context['quirofanos']=quirofanos
        context['deposito_precarga']=deposito_precarga
        context['disponible_deposito']=disponible_deposito

        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        quirofano = request.POST.get('quirofano')
        notacirugia = request.POST.get('nota_en_cirugia')
        idCirugia = request.POST.get('id_cirugia')
        lista_nota = request.POST.getlist('lista_nota')
        detalle_formateado = []
        NotaQuirurgica.objects.filter(cirugia_id=idCirugia).delete()
        Cirugia.objects.filter(id=idCirugia).update(notas=notacirugia, estatus_id=3, quirofano_id =quirofano )
        
        for i in range(0,len(lista_nota),5):
            detalle = lista_nota[i] + '*' + lista_nota[i+1] + '*' + lista_nota[i+2]+ '*' + lista_nota[i+3]+ '*' + lista_nota[i+4]
            detalle_formateado.append(detalle)
            
        if detalle_formateado:
            detalles = detalle_formateado
            for detalle in detalles:
                cirugia,detalle_id ,medico_id,nota,incluir = detalle.split('*')
                NotaQuirurgica.objects.create(cirugia_id=idCirugia, nota=nota, medico_id=medico_id, participante_id=detalle_id,
                                              quirofano_id=quirofano,incluir=incluir)
                
                    
        return redirect('lista_cirugia')


@add_group_name_to_context    
class ListadoHistoriaMedica(TemplateView):
    template_name='listado_historia_medica.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugias = Cirugia.objects.filter(estatus_id__in = [2, 9, 3, 11] ).order_by('-id')

        context['cirugias']=cirugias

        return context

@add_group_name_to_context    
class ListadoHistoriaClinica(TemplateView):
    template_name='listado_historia_clinica.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugias = Cirugia.objects.filter(estatus_id__in = [2, 3, 5, 6, 7, 9, 10, 11] ).order_by('-id')

        context['cirugias']=cirugias

        return context


@add_group_name_to_context    
class ListadoCirugiaAlta(TemplateView):
    template_name='listado_cirugia.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugias = Cirugia.objects.filter(estatus_id__gt=6,estatus_id__lt=9, id__gte = 1100  ).order_by('-fecha_act').annotate(
            tratamientos_no_cumplidos=Count('tratamiento', filter=Q(tratamiento__cumplido=False))
        )
       

        quirofanos = Quirofano.objects.all().order_by('NQx')
        context['cirugias']=cirugias
        context['quirofanos']=quirofanos
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        quirofano = request.POST.get('quirofano')
        notacirugia = request.POST.get('nota_en_cirugia')
        idCirugia = request.POST.get('id_cirugia')
        lista_nota = request.POST.getlist('lista_nota')
        detalle_formateado = []
        NotaQuirurgica.objects.filter(cirugia_id=idCirugia).delete()
        Cirugia.objects.filter(id=idCirugia).update(notas=notacirugia, estatus_id=3, quirofano_id =quirofano )
        
        for i in range(0,len(lista_nota),5):
            detalle = lista_nota[i] + '*' + lista_nota[i+1] + '*' + lista_nota[i+2]+ '*' + lista_nota[i+3]+ '*' + lista_nota[i+4]
            detalle_formateado.append(detalle)
            
        if detalle_formateado:
            detalles = detalle_formateado
            for detalle in detalles:
                cirugia,detalle_id ,medico_id,nota,incluir = detalle.split('*')
                NotaQuirurgica.objects.create(cirugia_id=idCirugia, nota=nota, medico_id=medico_id, participante_id=detalle_id,
                                              quirofano_id=quirofano,incluir=incluir)
                
                    
        return redirect('lista_cirugia')


@add_group_name_to_context    
class ListadoCirugiastandby(TemplateView):
    template_name='listado_cirugia_standby.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugias = Cirugia.objects.filter(estatus_id = 9 ).order_by('-fecha_act')
        context['cirugias']=cirugias
        return context
    
@add_group_name_to_context    
class ListadoCirugiaGeneral(UserPassesTestMixin, TemplateView):
    template_name='listado_cirugia_general.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='SuperAdministracion') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugias = Cirugia.objects.all().order_by('-id')
        estatus_cirugia = EstatusCirugia.objects.all()
        context['cirugias']=cirugias
        context['estatus_cirugia']=estatus_cirugia
        return context
    
    

def obtener_datos(request):
    id_cirugia = request.GET.get('idCirugia')
    filtered_data = DetalleCirugia.objects.filter(cirugia_id=id_cirugia, ntqx = True).exclude(detalle_id = 43)
    
    data = list(filtered_data.values('id', 'detalle_id', 'detalle__nombre', 'notas' ))
    
    return JsonResponse(data, safe=False)


def get_medicos(request):
    medicos = Medico.objects.filter(grupo='M').exclude(tipopersonal_id = 9).order_by('nombre')
    data = [{'id': medico.id, 'nombre': medico.nombre} for medico in medicos]
    return JsonResponse(data, safe=False)


@add_group_name_to_context    
class EntradaQuirofanoEmergencia(TemplateView):
    template_name='entrada_quirofano_emergencia.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quirofanos = Quirofano.objects.all().order_by('NQx')
        inventarios = Inventario.objects.filter(categoria_id__in=[1, 2], producto_activo=True).order_by('nombre')
        baremos = Baremo.objects.filter(inactivar = False).order_by('detalle__posicion')
        medicos = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        convenios = Convenio.objects.all().order_by('id')
        plantilla = Plantilla.objects.all().order_by('nombre')
        kit = KitInventario.objects.all().order_by('nombre')

        context['kit']=kit
        context['quirofanos']=quirofanos
        context['inventarios']=inventarios
        context['baremos']=baremos
        context['medicos']=medicos
        context['convenios'] = convenios
        context['plantilla'] = plantilla
        return context
    
def get_patient_data(request):
    patients = Paciente.objects.all().exclude(status = 'X').order_by("-fecha_act")
    data = []
    for patient in patients:
        data.append({
            'id': patient.id,
            'cedula': patient.cedula,
            'nombre': patient.nombre,
            'apellido': patient.apellido,
        })
    return JsonResponse(data, safe=False)

def calcular_precio(horasQx, convenio, detalle, grupo, venta):
    # Realiza el cálculo deseado con horasQx
    resultado = ComposicionDetalle.objects.filter(
        convenio_id = convenio,
        detalle_id = detalle,
        grupo_id = grupo,
        cantidad = horasQx
        ).aggregate(total_venta=Sum('venta')) # Ejemplo de cálculo
    

    
    if  resultado['total_venta'] is not None:
        montoventa = resultado['total_venta']
        cantidad = horasQx
    else:
        montoventa = venta
        cantidad = 1


    return {'total_venta': montoventa, 'cantidad': cantidad}


def guardar_baremo_seleccionado(request):
    user_id = request.user.id
    if request.method == 'POST':
        datos = request.body
        if datos:
            try:
                datos_json = json.loads(datos)
                tabla1 = datos_json['datos']['tabla1']
                tabla2 = datos_json['datos']['tabla2']
                # Procesar los datos aquí
                onetime = 0
                objectos_detalle = []
                for fila in tabla1:  # Acceder a la lista de filas
                    hora_entrada = fila['hora_entrada']
                    cronometro = fila['cronometro']
                    hora_salida = fila['hora_salida']
                    hora_cirugia = fila['hora_cirugia']
                    cronometro1 = fila['cronometro1']
                    salida_cirugia = fila['salida_cirugia']
                    
                    paciente_id = fila['idPaciente']
                    nroQuirofano = fila['nroQuirofano']
                    horasQx = fila['horasQx']
                    horaInicio = fila['horaInicio']
                    convenio_id = fila['convenio']
                    nombre_procedimiento= fila['nombreProcedimiento']
                    notasProcedimiento = fila['notasProcedimiento']
                    id_baremo = fila['id_baremo']
                    descripcion = fila['descripcion']
                    id_medico = fila['id_medico']
                    descripcion_medico = fila['descripcion_medico']
                    hora_actual = fila['hora_actual']
                    baremo = Baremo.objects.filter(id = id_baremo).first()
                    if onetime == 0:
                        onetime = 1
                        paciente = Paciente.objects.filter(id=paciente_id).first()
                        responsable_id = Responsable.objects.filter(id= paciente.responsable_id ).first()
                        presupuesto = Presupuesto.objects.create(
                            nombre_procedimiento = nombre_procedimiento,
                            horas_qx = horasQx,
                            paciente_id = paciente_id,
                            tipo_procedimiento_id = 4,
                            usuario_id = user_id,
                            notas = notasProcedimiento,
                            responsable_id = responsable_id,
                            hora_procedimiento = horaInicio ,
                            convenio_id = convenio_id,
                            estatus_id = 5
                        )
                        presupuesto_id = presupuesto.id
                        
                        cirugia_creada = Cirugia.objects.create(paciente_id=paciente_id ,tipo_procedimiento_id =4,
                                                hora_procedimiento =horaInicio,
                                                nombre_procedimiento  =nombre_procedimiento ,
                                                horas_qx = horasQx, notas =notasProcedimiento ,usuario_id  = user_id , convenio_id  = convenio_id,
                                                presupuesto_id = presupuesto_id, quirofano_id=nroQuirofano, estatus_id = 5, ultimo_estatus = 5, fecha_creacion = datetime.now() )
                        cirugia_creada.save()
                        idHistoria = cirugia_creada.id
                        
                        # tiempo de cirugia
                        tiempo_parts = cronometro.split('.')
                        hours, minutes, seconds = map(int, tiempo_parts[0].split(':'))
                        milliseconds = int(tiempo_parts[1])

                        tiempo_delta = timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)
                        
                        tiempo_parts = cronometro1.split('.')
                        hours, minutes, seconds = map(int, tiempo_parts[0].split(':'))
                        milliseconds = int(tiempo_parts[1])

                        tiempo_delta1 = timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

                        tiempo_quirofano = TiempoQuirofano(
                            cirugia_id = idHistoria,
                            hora_entrada= hora_entrada,
                            tiempo_qx = tiempo_delta,
                            hora_salida= hora_salida,
                            inicio_cirugia= hora_cirugia,
                            tiempo_cirugia = tiempo_delta1,
                            fin_cirugia= salida_cirugia,
                            
                        )
                        tiempo_quirofano.save()
                        #fin tiempo de cirugia
                        
                    resultado = calcular_precio(horasQx,convenio_id,baremo.detalle_id,baremo.grupo_id, baremo.venta )
                    precio_calculado = resultado['total_venta']
                    horas = resultado['cantidad']
                    DetallePresupuesto.objects.create(
                        presupuesto_id = presupuesto_id,
                        cantidad = horas,
                        precio = precio_calculado,
                        convenio_id = convenio_id,
                        detalle_id = baremo.detalle_id,
                        grupo_id = baremo.grupo_id,
                        ntqx = baremo.ntqx,
                        plantilla_id = baremo.plantilla_id,
                        usuario_id = user_id,
                        notas = notasProcedimiento
                        
                    )
                    
                    if baremo.ntqx:
                        if id_medico == '0':
                            id_medico = ''

                        NotaQuirurgica.objects.create(
                            nota = "Cirugia Emergencia",
                            cirugia_id = idHistoria,
                            participante_id = baremo.detalle_id,
                            quirofano_id = nroQuirofano,
                            medico_id = id_medico
                        )
                    
                    
                    objectos_detalle.append(DetalleCirugia(cirugia_id=idHistoria ,cantidad =horas ,precio = precio_calculado,
                                                detalle_id=baremo.detalle_id ,
                                                convenio_id  =baremo.convenio_id ,
                                                grupo_id =baremo.grupo_id, plantilla_id =baremo.plantilla_id ,unidad_id  = 1, 
                                                usuario_id  = user_id, ntqx = baremo.ntqx, facturable=True
                                                ))
                        
                
                DetalleCirugia.objects.bulk_create(objectos_detalle)

                total_uso_medicina=total_uso_mmq=0.0
                objectos_consumo = []
                for fila in tabla2:  # Acceder a la lista de filas
                    idInv = fila['idInv']
                    cantidad = fila['cantidad']
                    precio = fila['precio']
                    hora_actual = fila['hora_actual']
                    #TOTALIZAR POR TIPO DE MATERIAL
                    categoriaconsumo = Inventario.objects.filter(id=idInv).first() 
                    if categoriaconsumo.categoria_id == 1: #medicinas
                        total_uso_medicina = total_uso_medicina + float(precio)
                        
                    if categoriaconsumo.categoria_id == 2: #mmq
                        total_uso_mmq = total_uso_mmq + float(precio)
                        
                        
                    objectos_consumo.append(ConsumoCirugia(cirugia_id = idHistoria,
                                                            cantidad_uso = cantidad,
                                                            venta = precio,
                                                            inventario_id = idInv,
                                                            hora = hora_actual,
                                                            consumo_id=1
                                                            ) )
                    
                
                DetalleCirugia.objects.filter(cirugia_id = idHistoria, detalle_id='19' ).update(montoconsumo = total_uso_medicina ) ##monto cosumido farmacia          
                DetalleCirugia.objects.filter(cirugia_id = idHistoria, detalle_id='18' ).update(montoconsumo = total_uso_mmq ) ##monto cosumido MMQ          
                ConsumoCirugia.objects.bulk_create(objectos_consumo)
                return JsonResponse({'mensaje': 'Datos guardados correctamente'})
            except json.JSONDecodeError as e:
                return JsonResponse({'error': 'Error al deserializar datos'}, status=400)
        else:
            return JsonResponse({'error': 'No se recibieron datos'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    
@add_group_name_to_context
class EntradaQuirofano(TemplateView):
    template_name = 'entrada_quirofano.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['pk']
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        notaquirurgica = NotaQuirurgica.objects.filter(cirugia_id=cirugia_id, incluir=1 )
        medicos = Medico.objects.filter(grupo='M').exclude(tipopersonal_id = 9).order_by('nombre')
        inventarios = Inventario.objects.filter(categoria_id__in=[1, 2], producto_activo=True).order_by('nombre')
        kit = KitInventario.objects.all().order_by('nombre')
        baremo = Baremo.objects.filter(convenio_id=1, plantilla_id = 2, grupo_id=7, inactivar = False).order_by('detalle__posicion')
        tiempoquirofano = TiempoQuirofano.objects.filter(cirugia_id=cirugia_id).first()
        consumoquirofano = ConsumoCirugia.objects.filter(cirugia_id=cirugia_id, cantidad_real_usada__gt = 0).order_by('inventario')
        my_objects_asignado = ConsumoCirugia.objects.filter(cirugia_id=cirugia_id, farmacia = False).order_by('inventario__nombre')
        my_objects = ConsumoCirugia.objects.filter(cirugia_id=cirugia_id, cantidad_real_usada__gt = 0, consumo_id__in=[1,10])
        precarga_hecha = cirugia.precarga
        for myo in my_objects:
            myo.venta = myo.cantidad_real_usada * Decimal(myo.inventario.monto_venta)

        context['kit'] = kit
        context['baremo'] = baremo
        context['cirugia'] = cirugia
        context['medicos'] = medicos
        context['my_objects'] = my_objects
        context['inventarios'] = inventarios
        context['notaquirurgica'] = notaquirurgica
        context['tiempoquirofano'] = tiempoquirofano
        context['consumoquirofano'] = consumoquirofano
        context['precarga_hecha'] = precarga_hecha
        context['my_objects_asignado'] = my_objects_asignado
        # Agrega cualquier otro dato que necesites en el contexto
        return context
    
    
def guardar_datos_cirugia(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        cronometro = datos['cronometro']
        cronometro1 = datos['cronometro1']
        idCirugia = datos['idCirugia']
        total_horas = datos['total_horas']
        hora_entrada = datos['hora_entrada']
        hora_entrada = datos['hora_entrada']
        horasfacturadas = datos['horasfacturadas']
        tiempo_parts = cronometro.split('.')
        hours, minutes, seconds = map(int, tiempo_parts[0].split(':'))
        milliseconds = int(tiempo_parts[1])

        
        tiempo_delta = timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)
        
        tiempo_parts = cronometro1.split('.')
        hours, minutes, seconds = map(int, tiempo_parts[0].split(':'))
        milliseconds = int(tiempo_parts[1])

        tiempo_delta1 = timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

        TiempoQuirofano.objects.filter(cirugia_id = idCirugia).update(
            tiempo_qx = tiempo_delta,
            tiempo_cirugia = tiempo_delta1,
        )
            
        
        # Guardar Horas ciertas de quirofanos
        Cirugia.objects.filter(id=idCirugia).update(horas_qx = horasfacturadas, hora_procedimiento=hora_entrada, fecha_procedimiento=datetime.now(),precarga=False)
        
        detalle_cirugia = DetalleCirugia.objects.filter(cirugia_id=idCirugia)
        for dc in detalle_cirugia:
            precios_baremo = Baremo.objects.filter(convenio_id=dc.convenio_id, detalle_id = dc.detalle_id, grupo_id= dc.grupo_id).first()
            resultado = calcular_precio(horasfacturadas,precios_baremo.convenio_id,precios_baremo.detalle_id,precios_baremo.grupo_id, dc.precio )
            precio_calculado = resultado['total_venta']
            horas = resultado['cantidad']
            DetalleCirugia.objects.filter(id=dc.id).update(
                cantidad = horas,
                precio = precio_calculado,
            )
        

        return JsonResponse({'mensaje': 'Datos guardados correctamente en horarios de quirofanos y ajuste de hoas cirugia'})
    else:
        return JsonResponse({'mensaje': 'Error al guardar datos en horarios de quirofanos'})


def guardar_datos_tabla_consumo(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idCirugia = datos['idCirugia']
        idInv = datos['idInv']
        codigo = datos['codigo']
        cantidad = datos['cantidad']
        precio = datos['precio']
        hora_actual = datos['hora_actual']
        costo_inventario = 0
        inventario = Inventario.objects.filter(id = idInv).first()
        if inventario:
            costo_inventario = precio_costo_producto_inventario(inventario.id)
            

        ConsumoCirugia.objects.create( 
                                    cirugia_id = idCirugia,
                                    inventario_id = idInv ,
                                    cantidad_uso = cantidad,
                                    venta = precio,
                                    hora = hora_actual,
                                    consumo_id=1,
                                    precio_costo_unitario = costo_inventario,
                                    usuario_id = request.user.id
                                    )

        return JsonResponse({'mensaje': 'Datos guardados correctamente en consumo de cirugia'})
    else:
        return JsonResponse({'mensaje': 'Error al guardar datos en consumo de cirugia'})
    
def guardar_datos_notaqx(request):
    if request.method == 'POST':
        datos = request.body
        datos_json = json.loads(datos)
        for dato in datos_json:
            id_medico = dato['id_medico']
            if id_medico != "":
                NotaQuirurgica.objects.filter(id=dato['id_ntqx']).update(medico_id=id_medico, nota=dato['nota'] )
      
      
        return JsonResponse({'mensaje': 'Datos de medicos guardados correctamente'})
    else:
        return JsonResponse({'mensaje': 'No se recibieron medicos'}, status=400)
    
    
def cambiar_estatus_cirugia(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idCirugia = datos['idCirugia']
        estatus = datos['estatus']
        tipoHora = datos['tipoHora']
        if tipoHora == 'IQ':
            Cirugia.objects.filter(id=idCirugia).update(estatus_id=estatus)
            presupuesto = Cirugia.objects.filter(id=idCirugia).first()
            Presupuesto.objects.filter(id=presupuesto.presupuesto_id).update(estatus_id=estatus)
            
            tiempo = TiempoQuirofano.objects.filter(cirugia_id=idCirugia).first()
            if not tiempo:
                TiempoQuirofano.objects.create(cirugia_id=idCirugia, hora_entrada=datetime.now())
                
        if tipoHora == 'IC':
            tiempo = TiempoQuirofano.objects.filter(cirugia_id=idCirugia).first()
            if tiempo.inicio_cirugia is None:
                TiempoQuirofano.objects.filter(cirugia_id=idCirugia).update(inicio_cirugia=datetime.now())
            
        if tipoHora == 'FC':
            tiempo = TiempoQuirofano.objects.filter(cirugia_id=idCirugia).first()
            if tiempo.fin_cirugia is None:
                TiempoQuirofano.objects.filter(cirugia_id=idCirugia).update(fin_cirugia=datetime.now())
                
        if tipoHora == 'SQ':
            Cirugia.objects.filter(id=idCirugia).update(estatus_id=estatus)
            presupuesto = Cirugia.objects.filter(id=idCirugia).first()
            Presupuesto.objects.filter(id=presupuesto.presupuesto_id).update(estatus_id=estatus)
            tiempo = TiempoQuirofano.objects.filter(cirugia_id=idCirugia).first()
            if tiempo.hora_salida is None:
                TiempoQuirofano.objects.filter(cirugia_id=idCirugia).update(hora_salida=datetime.now())
                

        return JsonResponse({'mensaje': 'Datos guardados correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al guardar datos'})
    
    
@add_group_name_to_context    
class Imprimir_hc1(TemplateView):
    template_name='hc1.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context
    
    
def check_cedula_existance(request):
    cedula = request.GET.get('cedula')
    # Verificar si la cédula existe en la base de datos
    exists = Paciente.objects.filter(cedula=cedula).first()
    if exists:
        nombre = exists.nombre
        apellido = exists.apellido
        telefono = exists.telefono1
        direccion =exists.direccion
        data = {
            'nombre': nombre,
            'apellido' : apellido,
            'telefono' : telefono,
            'direccion' : direccion
            
        }
    else:
        data = {
            'nombre': 'Nombre',
            'apellido' : 'Apellidos',
            'telefono' : 'Telefono',
            'direccion' : 'Direccion'
        }
    
    return JsonResponse(data)



def check_cedula_existance_rep(request):
    cedula = request.GET.get('cedula')
    # Verificar si la cédula existe en la base de datos
    exists = Responsable.objects.filter(cedula=cedula).first()
    if exists:
        nombre = exists.nombre
        apellido = exists.apellido
        telefono = exists.telefono1
        direccion =exists.direccion
        data = {
            'nombre': nombre,
            'apellido' : apellido,
            'telefono' : telefono,
            'direccion' : direccion
            
        }
    else:
        data = {
            'nombre': 'Nombre',
            'apellido' : 'Apellidos',
            'telefono' : 'Telefono',
            'direccion' : 'Direccion'
        }
    
    return JsonResponse(data)



@add_group_name_to_context    
class PostOperatorio(UserPassesTestMixin,  TemplateView):
    template_name='post_operatorio.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Enfermeria') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['cirugia_id']
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        detallecirugia = DetalleCirugia.objects.filter(cirugia_id=cirugia_id, precio__gt = 0).order_by('detalle__posicion')
        tratamientos = Tratamiento.objects.filter(cirugia_id=cirugia_id).order_by('-id')
        #inventarios = Inventario.objects.filter(categoria_id__in=[1, 2]).order_by('categoria')
        habitaciones = Habitacion.objects.all().order_by('habitacion')
        consumohospital = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, consumo_id__in=[2,9] ).order_by('-id')
        compuestos = DepositoUso.objects.filter(deposito_id = 2,inventario__compuesto = '3', inventario__producto_activo =True).order_by('inventario__nombre')
        total_consumo_hospital = 0
        for consumoh in consumohospital:
            #inventario = Inventario.objects.filter(id = consumoh.inventario_id).first()
            #consumoh.precio_unitario = Decimal(round(inventario.monto_venta,2))
            if consumoh.cantidad_real_usada > 0:
                consumoh.precio_unitario = consumoh.venta / consumoh.cantidad_real_usada
            else:
                consumoh.precio_unitario = 0
                
            total_consumo_hospital = total_consumo_hospital + (Decimal(round(consumoh.venta,2))) 
        
        farmacocirugia = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, consumo_id__in=[1,10]).order_by('inventario__categoria')
        total_consumo_cirugia = 0
        for consumoh in farmacocirugia:
            #inventario = Inventario.objects.filter(id = consumoh.inventario_id).first()
            #consumoh.precio_unitario = Decimal(round(inventario.monto_venta,2))
            if consumoh.cantidad_real_usada > 0:
                consumoh.precio_unitario = consumoh.venta / consumoh.cantidad_real_usada
            else:
                consumoh.precio_unitario = 0
                
            total_consumo_cirugia = total_consumo_cirugia + (Decimal(round(consumoh.venta,2)) ) 
        
        
        habitacion_asignada = CirugiaHabitacion.objects.filter(cirugia_id=cirugia_id, status='O').first()
        kit = KitInventario.objects.all().order_by('nombre')


        # pediente las condiciones de la asignacion de la habitacion y la fecha
        
        total_precio = 0
        for dt in detallecirugia:
                total_precio = total_precio + dt.precio
            
        medicos = Medico.objects.filter(grupo='M').exclude(tipopersonal_id = 9).order_by('nombre')
        edad_paciente=calcular_edad(cirugia.paciente.fecha_nac)
        depositos_correspondiente_postoperatorio = DepositoUso.objects.filter(deposito_id__in=[2], inventario__producto_activo =True)
        depositos_asignados = Deposito.objects.filter(id__in=[2]).order_by('nombre')
        procedimientos = TipoProcedimiento.objects.all().order_by('nombre')
        
        
        context['kit'] = kit
        context['cirugia'] = cirugia
        context['medicos'] = medicos
        context['compuestos'] = compuestos
        context['habitaciones'] = habitaciones
        context['total_precio'] = total_precio
        context['tratamientos'] = tratamientos
        context['edad_paciente'] = edad_paciente
        context['procedimientos'] = procedimientos
        context['farmacocirugia'] = farmacocirugia
        context['detallecirugia'] = detallecirugia
        context['consumohospital'] = consumohospital
        context['depositos_asignados'] = depositos_asignados
        context['habitacion_asignada'] = habitacion_asignada
        context['total_consumo_cirugia'] = total_consumo_cirugia
        context['total_consumo_hospital'] = total_consumo_hospital
        context['depositos_correspondiente_postoperatorio'] = depositos_correspondiente_postoperatorio
        
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)  
        cirugia_id = self.kwargs['cirugia_id'] 
        lugar_consumo = 9 
        if request.POST['botonpresionado'] == 'compuesto':
            seleccionados = request.POST.getlist('seleccionados')
            for codigo in seleccionados:
                costo_inventario = 0
                inventario = Inventario.objects.filter(id = codigo).first()
                if inventario:
                    costo_inventario = precio_costo_producto_inventario(codigo)
                    

                cantidad = request.POST.get(f'cantidad_{codigo}', 1)  # Obtiene la cantidad
                cantidad = float(cantidad)
                deposito = DepositoUso.objects.filter(inventario_id = codigo, deposito_id = 2).first()
                disponible = total_venta = 0
                compuesto = '1'
                if deposito:
                    disponible = deposito.existenciaUnd
                    total_venta = deposito.inventario.monto_venta
                    compuesto = deposito.inventario.compuesto
                
                if  cantidad > float(disponible):
                    cantidad = disponible
                    
                if cantidad > 0:
                    consumoexiste = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, consumo_id = lugar_consumo, inventario_id = codigo, compuesto = compuesto).first()
                    if consumoexiste:
                        ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, consumo_id = lugar_consumo, inventario_id = codigo, compuesto = compuesto).update(
                            cantidad_uso = F('cantidad_uso') + cantidad,
                            cantidad_real_usada = F('cantidad_real_usada') + cantidad,
                            usuario_id = request.user.id,
                            hora_uso = datetime.now().time(),
                            hora = datetime.now().time(),
                            solicitante_id = request.user.id,
                            precio_costo_unitario = costo_inventario
                        )
                        InventarioDescarga.objects.filter(consumocirugia_id = consumoexiste.id).update(
                            cantidad = F('cantidad') + cantidad,
                            usuario_id = request.user.id,
                        )
                        
                        if compuesto == '3':
                            InventarioCompuesto.objects.filter(consumo_id = consumoexiste.id).update(
                                usuario_id = request.user.id,
                                cantidad = F('cantidad') + cantidad,
                            )
                    else:
                        consumonuevo = ConsumoCirugia.objects.create(
                            cirugia_id = cirugia_id,
                            cantidad_real_usada = cantidad,
                            cantidad_uso = cantidad,
                            venta = float(total_venta) * cantidad,
                            inventario_id = codigo,
                            farmacia = True,
                            consumo_id = lugar_consumo,
                            usuario_id = request.user.id,
                            solicitante_id = request.user.id,
                            hora_uso = datetime.now().time(),
                            hora = datetime.now().time(),
                            precio_unitario = total_venta,
                            deposito_id = 2,
                            nota = 'ASIGNADO EN HOSPITALIZACION',
                            compuesto = compuesto,
                            precio_costo_unitario = costo_inventario

                        )
                        
                        InventarioDescarga.objects.create(
                            cantidad = cantidad,
                            nota = 'ASIGNADO EN HOSPITALIZACION',
                            deposito_id = 2,
                            inventario_id = codigo,
                            usuario_id = request.user.id,
                            tipodescarga_id = 12,
                            cirugia_id = cirugia_id,
                            persona_id = request.user.id,
                            consumocirugia_id = consumonuevo.id
                        )
                        Tratamiento.objects.create(tratamiento='Aplicar :'+deposito.inventario.nombre, 
                                                    cirugia_id=cirugia_id, inventario_id=codigo,cantidad_uso=cantidad,
                                                    consumo_id=consumonuevo.id, medico_aplicante_id = request.user.id, medico_orden_id=request.user.id,
                                                    lugar_consumo_id = lugar_consumo )
                        
                        if compuesto == '3':
                            InventarioCompuesto.objects.create(
                                consumo_id = consumonuevo.id,
                                usuario_id = request.user.id,
                                cantidad = cantidad
                            )
            
            return redirect('postoperatorio' , cirugia_id = cirugia_id )
    
    
    
    

def obtener_datos_consumo(request,id ):
    datos = ConsumoCirugia.objects.filter(cirugia_id=id, consumo_id=2).order_by('hora')
    
    data = list(datos.values('id', 'cantidad_uso', 'venta', 'hora', 'inventario__nombre', 'inventario__categoria__nombre', 'consumo__nombre', 'fecha_act' ))
   
    return JsonResponse(data, safe=False)

def obtener_datos_tratamiento(request,idCirugia ):
    datos = Tratamiento.objects.filter(cirugia_id=idCirugia).order_by('fecha_act')
    
    data = list(datos.values('id', 'tratamiento', 'fecha_act', 'baremo', 'inventario', 'inventario__nombre', 'medico_aplicante__nombre', 'medico_orden__nombre', 'cantidad_uso', 'cumplido'))
   
    return JsonResponse(data, safe=False)


def medicos_list(request):
    medicos = Medico.objects.all().order_by('nombre')
    data = [{'id': medico.id, 'nombre': medico.nombre} for medico in medicos]
    return JsonResponse(data, safe=False)


def guardar_farmaco_hospital(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idinventario=datos['id']
        cantidad_uso=datos['cantidad']
        venta=datos['precio']
        cirugia_id=datos['idCirugia']
        deposito_id=datos['deposito_id']
        cantidad_uso = float(cantidad_uso)
        precio_costo_unitario = 0
        inventario = Inventario.objects.filter(id=idinventario).first()
        if inventario:
            precio_costo_unitario = precio_costo_producto_inventario(idinventario)


        monto_total_venta = Decimal(inventario.monto_venta) * Decimal(cantidad_uso)
        categoria=inventario.categoria_id
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        usuario_logueado = request.user.id
        user = User.objects.get(id=usuario_logueado)
        medico = Medico.objects.filter(user_id=usuario_logueado).first()
        existencia_deposito = DepositoUso.objects.filter(inventario_id = idinventario, deposito_id = deposito_id , inventario__producto_activo =True).first()
        if existencia_deposito:
            cantidad_existencia = existencia_deposito.existenciaUnd
        else:
            cantidad_existencia = 0
        
        
        if medico:
            medico = medico.id
        else:
            medico = None
            
        detalle_afectado = 0
        if cirugia.tipo_procedimiento == 1 or cirugia.tipo_procedimiento == 4:
            detalle_afectado = 33
                
        if cirugia.tipo_procedimiento == 2:
            detalle_afectado = 32
            
        if inventario.compuesto == '2':
            compuesto = '2'
            lugar_consumo = 9
        else:
            compuesto = '1'
            lugar_consumo = 2
            
        if cantidad_uso <= cantidad_existencia:
            consumocirugia=ConsumoCirugia.objects.create(inventario_id = idinventario, cantidad_uso=cantidad_uso,cantidad_real_usada = cantidad_uso ,venta=monto_total_venta, consumo_id=lugar_consumo,
                                        cirugia_id=cirugia_id, hora=datetime.now().time(),deposito_id=deposito_id ,solicitante_id=usuario_logueado, entregado_id=usuario_logueado , 
                                        farmacia=False, usuario_id=usuario_logueado, nota = 'USO EN HOSPITALIZACION', compuesto = compuesto, precio_unitario = Decimal(inventario.monto_venta),
                                        precio_costo_unitario = precio_costo_unitario
                                          )

            Tratamiento.objects.create(tratamiento='Aplicar :'+inventario.nombre, 
                                                    cirugia_id=cirugia_id, inventario_id=idinventario,cantidad_uso=cantidad_uso,
                                                    consumo_id=consumocirugia.id, medico_aplicante_id = medico, medico_orden_id=medico,
                                                    lugar_consumo_id = 2 )
            
            InventarioDescarga.objects.create(
                        cantidad = cantidad_uso,
                        nota = 'APLICADO EN HOSPITALIZACION',
                        deposito_id = deposito_id,
                        inventario_id = idinventario,
                        usuario_id = request.user.id,
                        tipodescarga_id = 13 ,
                        cirugia_id = cirugia_id,
                        persona_id = request.user.id,
                        consumocirugia_id = consumocirugia.id
                    )
            
            if compuesto == '2':
                InventarioCompuesto.objects.create(
                                consumo_id = consumocirugia.id,
                                usuario_id = request.user.id,
                                cantidad = cantidad_uso
                            )
        
        
        
        return JsonResponse({'mensaje': 'Farmaco hospital guardado con éxito'})
    
    
    return JsonResponse({'mensaje': 'Error al guardar farmaco hospital'})



def guardar_tratamiento(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idCirugia=datos['idCirugia']
        tratamiento=datos['tratamiento']
        usuario_logueado = request.user.id
        user = User.objects.get(id=usuario_logueado)
        medico = Medico.objects.filter(user_id=usuario_logueado).first()
        if medico:
            medico = medico.id
        else:
            medico = None
            
        Tratamiento.objects.create(tratamiento=tratamiento, cirugia_id=idCirugia, cantidad_uso=1,medico_aplicante_id = medico, medico_orden_id=medico )
        return JsonResponse({'mensaje': 'Tratamiento hospital guardado con éxito'})
    
    
    return JsonResponse({'mensaje': 'Error al guardar Tratamiento hospital'})


def guardar_tratamiento_medico(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idCirugia=datos['idCirugia']
        tratamiento=datos['tratamiento']
        usuario_logueado = request.user.id
        user = User.objects.get(id=usuario_logueado)
        medico = Medico.objects.filter(user_id=usuario_logueado).first()
        if medico:
            medico = medico.id
        else:
            medico = None
            
        Tratamiento.objects.create(tratamiento=tratamiento, cirugia_id=idCirugia, cantidad_uso=1, medico_orden_id=medico )
        return JsonResponse({'mensaje': 'Tratamiento hospital guardado con éxito'})
    
    
    return JsonResponse({'mensaje': 'Error al guardar Tratamiento hospital'})


def eliminar_consumo(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idEliminar=datos['idEliminar']
        cumplido = Tratamiento.objects.filter(consumo_id=idEliminar).first()
        if cumplido:
            if not cumplido.cumplido:
                ConsumoCirugia.objects.filter(id=idEliminar).delete()
                DetalleCirugia.objects.filter(cirugia_id=cumplido.cirugia_id, detalle_id = 33).update(excedentehospital=0)
                DetalleCirugia.objects.filter(cirugia_id=cumplido.cirugia_id, detalle_id = 32).update(excedentehospital=0)
                return JsonResponse({'mensaje': 'Farmaco hospital eliminado con éxito'})
            else:
                return JsonResponse({'mensaje': 'CUMPLIDO'})
            
    
    return JsonResponse({'mensaje': 'Error al eliminar farmaco hospital'})


def eliminar_tratamiento(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idEliminar=datos['idEliminar']
        medicina = Tratamiento.objects.filter(id=idEliminar).first()
        if medicina.consumo_id:
            ConsumoCirugia.objects.filter(id=medicina.consumo_id).delete()
            

        Tratamiento.objects.filter(id=idEliminar).delete()
        
        return JsonResponse({'mensaje': 'tratamiento solo hospital eliminado con éxito'})
    
    
    return JsonResponse({'mensaje': 'Error al eliminar tratamiento solo hospital'})


def update_tratamiento(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idTratamiento=datos['idTratamiento']
        tratamiento=datos['tratamiento']
        Tratamiento.objects.filter(id=idTratamiento).update(tratamiento=tratamiento)
        return JsonResponse({'mensaje': 'Update tratamiento hospital guardado con éxito'})
    
    
    return JsonResponse({'mensaje': 'Error al guardar farmaco hospital'})
   
   

def cumplido_tratamiento(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idCumplido=datos['idCumplido']
        
        usuario_logueado = request.user.id
        print('usuario_logeado',usuario_logueado )
        user = User.objects.get(id=usuario_logueado)
        medico = Medico.objects.filter(user_id=usuario_logueado).first()
        if medico:
            medico = medico.id
        else:
            medico = None
        
        tratamiento = Tratamiento.objects.filter(id=idCumplido).first()
        Tratamiento.objects.filter(id=idCumplido).update(cumplido=True,medico_aplicante_id=medico, fecha_aplicacion=datetime.now(), usuario_id = request.user.id )
        ConsumoCirugia.objects.filter(id = tratamiento.consumo_id ).update(
            conciliada = True
        )
        
        return JsonResponse({'mensaje': 'Update cumplido el tratamiento hospital guardado con éxito'})
    
    
    return JsonResponse({'mensaje': 'Error al guardar farmaco hospital'})


@add_group_name_to_context    
class pdfCorteCuenta(TemplateView):
    template_name='pdf_cortecuenta.html'
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['pk']
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        responsable = Responsable.objects.filter(id=cirugia.paciente.responsable_id).first()
        #detallepresupuesto = DetalleCirugia.objects.filter(cirugia_id=cirugia.id, precio__gt = 0 ).order_by('detalle__posicion')
        detallepresupuesto = DetallePresupuesto.objects.filter(presupuesto_id=cirugia.presupuesto_id, precio_usado__gt = 0 ).order_by('detalle__posicion')
            
        fecha_actual = datetime.now()
        valor_bolivar_dia=CambioDiaBcv(fecha_actual)
        if cirugia.congelar_moneda:
            valor_bolivar_dia = cirugia.cambio_congelado 
            
       
        context['detallepresupuesto'] = detallepresupuesto
        context['valor_bolivar_dia'] = valor_bolivar_dia
        context['fecha_actual'] = fecha_actual
        context['responsable'] = responsable
        context['cirugia'] = cirugia
        return context


def filtrar_plantilla(request):
    idPlantilla = request.GET.get('idPlantilla')
    idconvenio = request.GET.get('idconvenio')
    # Filtro de datos según sea necesario
    datos_filtrados = Baremo.objects.filter(convenio_id=idconvenio, plantilla_id=idPlantilla, inactivar = False).values_list('id', 'detalle__nombre','ntqx','convenio__nombre', 'detalle_id' ).order_by('detalle__posicion')  # reemplazar con tu filtro
    return JsonResponse(list(datos_filtrados), safe=False)


def buscar_responsable(request):
    cedula = request.GET.get('cedula')
    filtered_data = Responsable.objects.filter(cedula=cedula)
    if filtered_data:
        data = list(filtered_data.values('id', 'cedula', 'nombre', 'apellido','direccion','sexo','telefono1', 'direccion_trabajo','trabajo' ))
    else:
        data = []
    
    return JsonResponse(data, safe=False)



def asignar_habitacion(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idCirugia=datos['idCirugia']
        fechaAsignada=datos['fechaAsignada']
        numeroHabitacion=datos['numeroHabitacion']
        estatus = 'D'
        if numeroHabitacion:
            estatus = 'O'
        else:
            numeroHabitacion=None
            
        habitacion_asignada = CirugiaHabitacion.objects.filter(cirugia_id=idCirugia).first()
        cirugia=Cirugia.objects.filter(id=idCirugia).first()
        Presupuesto.objects.filter(id=cirugia.presupuesto_id).update(estatus=6)
        Cirugia.objects.filter(id=idCirugia).update(estatus=6)
        
        if not habitacion_asignada:
            CirugiaHabitacion.objects.create(
                habitacion_id = numeroHabitacion,
                cirugia_id = idCirugia,
                fecha_asignacion = fechaAsignada,
                status = estatus
            )
        else:
             CirugiaHabitacion.objects.filter(cirugia_id=idCirugia).update(
                habitacion_id = numeroHabitacion,
                status = estatus
                )
            
        return JsonResponse({'mensaje': 'Update habitacion asignada guardado con éxito'})
    
    
    return JsonResponse({'mensaje': 'Error al guardar habitacion hospital'})


@add_group_name_to_context    
class tratamiento_medico(TemplateView):
    template_name='tratamiento_medico.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        cirugia_id = self.kwargs['pk']
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        fecha_hoy = datetime.now()
        usuario_logueado = self.request.user.id
        user = User.objects.get(id=usuario_logueado)
        medico = Medico.objects.filter(user_id=usuario_logueado).first()

            
        tratamiento = Tratamiento.objects.filter(cirugia_id=cirugia_id).order_by('-id')
        tratamiento_no_cumplido = Tratamiento.objects.filter(cirugia_id=cirugia_id, cumplido=False).count()
        consumo_no_conciliados = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, conciliada = False).count()
        #inventarios = Inventario.objects.filter(categoria_id__in=[1, 2]).order_by('categoria')
        edad_paciente=calcular_edad(cirugia.paciente.fecha_nac)
        medicosaltamedica = NotaQuirurgica.objects.filter(cirugia_id=cirugia_id, medico__participaalta=True).order_by('medico__nombre')
        depositos_correspondiente_farmacia = DepositoUso.objects.filter(deposito_id__in=[2], cantidad_deposito__gt = 0, inventario__producto_activo =True)
        depositos_asignados = Deposito.objects.filter(id__in=[2])
        
        context['medico']=medico
        context['cirugia']=cirugia
        context['fecha_hoy']=fecha_hoy
        context['depositos_correspondiente_farmacia']=depositos_correspondiente_farmacia
        context['tratamiento']=tratamiento
        context['edad_paciente']=edad_paciente
        context['medicosaltamedica']=medicosaltamedica
        context['depositos_asignados']=depositos_asignados
        context['consumo_no_conciliados']=consumo_no_conciliados
        context['tratamiento_no_cumplido']=tratamiento_no_cumplido
        context['depositos_correspondiente_farmacia']=depositos_correspondiente_farmacia
        
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['pk']
        usuario_logueado = self.request.user.id
        user = User.objects.get(id=usuario_logueado)
        medicosaltamedica = NotaQuirurgica.objects.filter(cirugia_id=cirugia_id, medico__participaalta=True).order_by('medico__nombre')
        medico = Medico.objects.filter(user_id=usuario_logueado).first()
        if medico:
            medico_id = medico.id
        else:
            medico_id = None
            
        fecha_salida = request.POST.get('fecha-egreso-datetime')
        condiciones_egreso = request.POST.get('condicion-egreso')
        diagnostico_egreso = request.POST.get('diag-egreso')
        diagnostico_ingreso = request.POST.get('diag-ingreso')
        tratamiento_recibido = request.POST.get('tratamiento-recibido')
        altamedicaguardar = AltaMedica.objects.create(
                            fecha_salida = fecha_salida,
                            condiciones_egreso = condiciones_egreso,
                            diagnostico_egreso = diagnostico_egreso,
                            cirugia_id=cirugia_id,
                            medico_egreso_id=medico_id,
                            diagnostico_ingreso=diagnostico_ingreso,
                            tratamiento_recibido=tratamiento_recibido,
                            usuario_id = self.request.user.id
                            )
        
        altamedicaguardar.save()
        id_altamedica = altamedicaguardar.id
        for mda in medicosaltamedica:
           MedicoAltaMedica.objects.create(
               altamedica_id = id_altamedica,
               medico_tratamiento_id = mda.medico_id
           )
        
        Cirugia.objects.filter(id=cirugia_id).update(alta_medica=True, estatus=7)
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        fecha_hoy = datetime.now()
        usuario_logueado = self.request.user.id
        user = User.objects.get(id=usuario_logueado)
        medico = Medico.objects.filter(user_id=usuario_logueado).first()
        
        tratamiento = Tratamiento.objects.filter(cirugia_id=cirugia_id).order_by('-id')
        inventarios = Inventario.objects.filter(categoria_id__in=[1, 2]).order_by('categoria')
        edad_paciente=calcular_edad(cirugia.paciente.fecha_nac)
        
        context['medico']=medico
        context['cirugia']=cirugia
        context['fecha_hoy']=fecha_hoy
        context['inventarios']=inventarios
        context['tratamiento']=tratamiento
        context['edad_paciente']=edad_paciente
        context['medicosaltamedica']=medicosaltamedica
        return redirect('tratamiento_medico', pk = cirugia_id )
        
    
def guardar_farmaco_hospital_medico(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idinventario=datos['id']
        codigo=datos['codigo']
        cantidad_uso=datos['cantidad']
        deposito=datos['deposito']
        venta=datos['precio']
        cirugia_id=datos['idCirugia']
        fechayhorainicio_str = datos['fechayhorainicio']
        idintervalohoras = datos['idintervalohoras']
        idtopecantidadmedicina = datos['idtopecantidadmedicina']
        vecesmedicina = int(idtopecantidadmedicina)
        # Now you can use fechayhorainicio_str_result as needed
        fechayhorainicio = datetime.strptime(fechayhorainicio_str, '%Y-%m-%dT%H:%M')
        fechayhorainicio_mas_cuatro_horas = fechayhorainicio + timedelta(hours=int(idintervalohoras))
        fechayhorainicio_str_result = fechayhorainicio_mas_cuatro_horas.strftime('%Y-%m-%d %H:%M:%S')
        
        
        venta = float(venta.replace(',','.'))
        monto_total_venta = venta * float(cantidad_uso)
        inventario = Inventario.objects.filter(id=idinventario).first()
        costo_inventario = 0
        if inventario:
            costo_inventario = precio_costo_producto_inventario(inventario.id)
            

        categoria=inventario.categoria_id
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        usuario_logueado = request.user.id
        user = User.objects.get(id=usuario_logueado)
        medico = Medico.objects.filter(user_id=usuario_logueado).first()
        if medico:
            medico = medico.id
        else:
            medico = None
        detalle_afectado = 0
                
        if cirugia.tipo_procedimiento == 2:
            detalle_afectado = 32
        else:
            detalle_afectado = 33
            
            
        fechayhorainicio = datetime.strptime(fechayhorainicio_str, '%Y-%m-%dT%H:%M')
        for i in range(1, vecesmedicina+1):
            consumocirugia=ConsumoCirugia.objects.create(inventario_id = idinventario, cantidad_uso=cantidad_uso,cantidad_real_usada=cantidad_uso , venta=monto_total_venta, consumo_id=2,
                                      cirugia_id=cirugia_id, hora=datetime.now().time(),farmacia=False,usuario_id=request.user.id, deposito_id=deposito, entregado_id=request.user.id, solicitante_id=request.user.id,
                                      precio_costo_unitario = costo_inventario
                                      )
            
            idconsumocirugia=consumocirugia.id
            fechayhorainicio_mas_cuatro_horas = fechayhorainicio + timedelta(hours=int(idintervalohoras)*i)
            fechayhorainicio_str_result = fechayhorainicio_mas_cuatro_horas.strftime('%Y-%m-%d %H:%M:%S')
            Tratamiento.objects.create(tratamiento='Aplicar :'+inventario.nombre, 
                                                 cirugia_id=cirugia_id, inventario_id=idinventario,cantidad_uso=cantidad_uso,
                                                 consumo_id=idconsumocirugia, medico_orden_id=medico, fecha_act=fechayhorainicio_str_result)
        
        
        
        return JsonResponse({'mensaje': 'Farmaco hospital guardado con éxito'})
    
    
    return JsonResponse({'mensaje': 'Error al guardar farmaco hospital'})


def save_image_2(request):
    if request.method == 'POST':
        # Obtener la imagen desde la solicitud
        image_data = request.POST.get('image')
        filename = request.POST.get('filename') 
        # Decodificar la imagen desde base64
        image_data_decoded = base64.b64decode(image_data.split(',')[1])
        # Leer la imagen en un objeto Image de Pillow
        image = Image.open(io.BytesIO(image_data_decoded))
        image = image.convert('RGB')
        # Guardar la imagen en un archivo
        directory_path = 'c:/archivos_uq58/'
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            
        image = image.resize((image.width * 2, image.height * 2), resample=Image.BICUBIC)
        image.save(directory_path+filename,format='JPEG', compress_level=9, quality=99)
        
        ### CONVERSION A PDF
          # reemplaza con la ruta de tu imagen
        pdf_bytes = convert(directory_path+filename)
        pdf_file_path = directory_path+filename+'.pdf'  # reemplaza con la ruta donde deseas guardar el archivo PDF
        with open(pdf_file_path, 'wb') as f:
            f.write(pdf_bytes)
    
        #FIN CONVERSION
        # enviar a whatsapp 
        image_path = directory_path+filename
        
        caption = 'Grupo Quirurgico U58! le envia para sus registros. Gracias!'
        # Activar para numero de telefono del cliente PENDIENTE **************************************************************
        phone_number = '+584129093619' 
        #envio_email(pdf_file_path)
        #pywhatkit.sendwhats_image(phone_number,"c:/archivos_uq58/filepdf.pdf")
        return HttpResponse(status=200)

    return HttpResponse(status=405) # Método no permitido


@add_group_name_to_context    
class listado_consumo(TemplateView): 
    
    template_name='listado_consumo.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consumo = ConsumoCirugia.objects.all().order_by('-id')
        cirugias = Cirugia.objects.filter(estatus__gt = 3, id__gte = 1600).order_by('-id')
        atencion_medica = AtencionInmediata.objects.all().order_by('-id')
        atencion_medica_cortesia = AtencionInmediataCortesia.objects.all().order_by('-id')

        """ cirugias_prueba = Cirugia.objects.filter(estatus__gt=3).order_by('-id').values(
            'id', 'presupuesto_id' , 'estatus' ,'paciente__nombre', 'paciente__responsable__nombre' , 'medico_ppal__nombre', 'nombre_procedimiento', 'fecha_procedimiento', 'dias_hospitalizacion', 'horas_qx'
        )
        atencion_medica_prueba = AtencionInmediata.objects.all().order_by('-id').values(
            'codigo',  'estatus' ,'paciente__nombre', 'paciente__responsable__nombre' , 'medico_ppal__nombre', 'motivo_atencion', 'fecha_procedimiento', 'dias_hospitalizacion'
        ) """

        resultados = list(chain(cirugias, atencion_medica, atencion_medica_cortesia))
        i=0
        for r in resultados:
            if r.tipo_procedimiento_id == 5:
                if r.codigo[:3] == 'AMC':
                    r.tipo_atencion = 'AMC'
                else:
                    r.tipo_atencion = 'AMI'
        

        context['consumo'] = consumo
        context['cirugias'] = cirugias
        context['resultados'] = resultados
        context['atencion_medica'] = atencion_medica

        return context
    
    
@add_group_name_to_context    
class listado_consumo_paciente(UserPassesTestMixin, TemplateView): 
    template_name='listado_consumo_paciente.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Farmacia') | Q(name='Inventario') | Q(name='Enfermeria') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')   
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['pk']
        tp = self.kwargs['tp']
        
        depositos_descarga = DepositoUso.objects.filter(deposito_id__in=[1,2], inventario__producto_activo =True).order_by('inventario_id','deposito_id')
        if int(tp) == 5:
            cirugia = AtencionInmediata.objects.filter(id=cirugia_id).first()
            consumos = ConsumoCirugia.objects.filter(atencion_inmediata_id=cirugia_id, conciliada = True).order_by('inventario__nombre')
            detalle_baremo = []
        else:
            cirugia = Cirugia.objects.filter(id=cirugia_id).first()
            ConsumoCirugia.objects.filter(cirugia_id=cirugia_id).update(
            seleccionado = False
            )
            consumos = ConsumoCirugia.objects.filter(cirugia_id=cirugia_id, conciliada = True).order_by('inventario__nombre')
            #consumos = ConsumoCirugia.objects.filter(cirugia_id=cirugia_id, conciliada = True).order_by('inventario__nombre')
            detalle_baremo = Baremo.objects.filter(inactivar = False, plantilla_id__gt = 1).exclude(detalle_id__in = [18,19,32,33,40,85,90,94]).order_by('detalle__nombre')
            detalle_presupuesto = DetallePresupuesto.objects.filter(detalle_id = 33, presupuesto_id = cirugia.presupuesto_id).first()
            baremo_cobro_hospital = None
            if detalle_presupuesto:
                baremo_cobro_hospital = 33
            else:
                detalle_presupuesto = DetallePresupuesto.objects.filter(detalle_id = 32, presupuesto_id = cirugia.presupuesto_id).first()
                if detalle_presupuesto:
                    baremo_cobro_hospital = 32
            
        total_usd=0
        for consumo in consumos:
            if not consumo.baremo_cobro:
                if consumo.consumo_id == 2:
                    consumo.baremo_cobro_id = baremo_cobro_hospital
                elif consumo.consumo_id == 1:
                    consumo.baremo_cobro_id = 90
                elif consumo.consumo_id == 8:
                    consumo.baremo_cobro_id = 94
                elif consumo.consumo_id == 7:
                    consumo.baremo_cobro_id = 85
                elif consumo.consumo_id == 9 or consumo.consumo_id == 10:
                    consumo.baremo_cobro_id = 40
                else:
                    consumo.baremo_cobro_id = None
                    
                
        
        superUser = self.request.user.groups.filter(Q(name='SuperAdministracion')).exists()
        medicinaEspecial = self.request.user.groups.filter(Q(name='MedicinaEspecial')).exists()
        verPrecioCosto = self.request.user.groups.filter(Q(name='VerCostos')).exists()

        context['tp'] = tp
        context['consumo'] = consumos
        context['cirugia'] = cirugia
        context['superUser'] = superUser
        context['detalle_baremo'] = detalle_baremo
        context['verPrecioCosto'] = verPrecioCosto
        context['medicinaEspecial'] = medicinaEspecial
        context['depositos_descarga'] = depositos_descarga
        
        
        return context
    
    
    
    
### INVENTARIOS VISTAS Y FUNCIONES

def add_record_inventory(request):
     return render(request, 'admin/inventario.html')


### FIN VISTAS Y FUNCIONES DE INVENTARIO

##vistas de administracion
@add_group_name_to_context    
class montos_cirugias(UserPassesTestMixin, TemplateView): 
    
    template_name='montos_cirugias.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. Traemos las cuentas con los datos necesarios (Añadimos select_related para evitar más N+1)
        cuentasxcobrar = CuentaxCobrar.objects.filter(
            Q(cirugia_id__isnull=False) | Q(atencion_inmediata__isnull=False)
        ).select_related('presupuesto', 'cirugia')

        # 2. Obtenemos TODOS los detalles existentes de estas cuentas de una sola vez
        # Creamos un mapeo {cuentacobrar_id: objeto_detalle}
        ids_cuentas = cuentasxcobrar.values_list('id', flat=True)
        detalles_existentes = {
            d.cuentacobrar_id: d 
            for d in DetalleCuentaCobrar.objects.filter(
                cuentacobrar_id__in=ids_cuentas, 
                montocobrar__gte=0
            )
        }

        detalle_updates = []
        detalle_creations = []

        for cuenta in cuentasxcobrar:
            total_newcxc = cuenta.presupuesto.total_monto_precio_usado if cuenta.presupuesto else 0
            
            # Validamos condición lógica
            if cuenta.cirugia_id is not None and total_newcxc > 0:
                existedetalle = detalles_existentes.get(cuenta.id)

                if existedetalle:
                    # Si existe, actualizamos el atributo en el objeto de la memoria
                    existedetalle.montocobrar = total_newcxc
                    detalle_updates.append(existedetalle)
                else:
                    # Si no existe, preparamos el objeto para creación
                    detalle_creations.append(DetalleCuentaCobrar(
                        montocobrar=total_newcxc,
                        descripcion=f"Monto Total Procedimiento...:{cuenta.cirugia.nombre_procedimiento}",
                        cuentacobrar_id=cuenta.id,
                    ))

        # 3. Ejecución en bloque dentro de una transacción para asegurar integridad y velocidad
        with transaction.atomic():
            if detalle_updates:
                # Actualiza 10,000 registros en un par de consultas SQL
                DetalleCuentaCobrar.objects.bulk_update(detalle_updates, ['montocobrar'])
            
            if detalle_creations:
                # Crea todos los faltantes de un solo golpe
                DetalleCuentaCobrar.objects.bulk_create(detalle_creations)

        
        cuentaxcobrar = CuentaxCobrar.objects.filter(
            Q(cirugia_id__isnull=False) | Q(atencion_inmediata__isnull=False)
        ).exclude(
            cirugia_id__lte=1100
        ).annotate(
            total_detalle=Coalesce(
                Sum('detallecuentacobrar__montocobrar'),
                Value(0),
                output_field=DecimalField()
            ),
            total_nc=Coalesce(
                Sum(
                    'detallecuentacobrar__notacredito_origen__saldo',
                    filter=Q(detallecuentacobrar__notacredito_origen__aplicada=False)
                ),
                Value(0),
                output_field=DecimalField()
            )
        ).annotate(
            total_cobrar=F('total_detalle') + F('total_nc')
        ).values(
            'id',
            'paciente_id',
            'cirugia_id',
            'cirugia__medico_ppal__nombre',
            'cirugia__nombre_procedimiento',
            'presupuesto__nombre_procedimiento',
            'atencion_inmediata__estatus__nombre',
            'cirugia__estatus__nombre',
            'presupuesto_id',
            'presupuesto__paciente__nombre',
            'atencion_inmediata_id',
            'atencion_inmediata__codigo',
            'presupuesto__fecha_procedimiento',
            'paciente__nombre',
            'paciente__apellido',
            'paciente__cedula',
            'total_cobrar'
        ).order_by('-id')


        eliminarPresupuesto = self.request.user.groups.filter(Q(name='EliminarPresupuesto')).exists()
        print('fin', datetime.now())
        context['cuentaxcobrar'] = cuentaxcobrar
        context['eliminarPresupuesto'] = eliminarPresupuesto
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        presupuesto_id = request.POST['name_presupuesto_eliminar']
        eliminar_consumo = request.POST.get('name_eliminar_consumo')
        presupuesto = Presupuesto.objects.filter(id = presupuesto_id).first()
        cirugia = Cirugia.objects.filter(presupuesto_id = presupuesto_id).first()
        
        if cirugia:
            id_cirugia = cirugia.id
        else:
            id_cirugia = 0
            
        cantidad_consumos = 0
        if cirugia:
            cirugia_id = cirugia.id
            id_cirugia = cirugia_id
            cantidad_consumos = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id).count()
            if eliminar_consumo:
                ConsumoCirugia.objects.filter(cirugia_id = cirugia_id).delete()
                
        else:
            if presupuesto.atencion_inmediata:
                id_cirugia = 'AMI'+str(presupuesto.atencion_inmediata_id).zfill(4)
                cantidad_consumos = ConsumoCirugia.objects.filter(atencion_inmediata_id = presupuesto.atencion_inmediata_id).count()
                AtencionInmediata.objects.filter(id=presupuesto.atencion_inmediata_id).delete()
         
        LogEliminacion.objects.create(
            descripcion = 'Eliminacion de Presupuesto :'+str(presupuesto_id)+' Viculado a cirugia: '+str(id_cirugia)+ ' y eliminacion de consumo en: '+str(eliminar_consumo)+'cantidad consumos eliminados: '+str(cantidad_consumos)+ ' del paciente:'+str(presupuesto.paciente),
            usuario_id = self.request.user.id
        )
           
        Presupuesto.objects.filter(id = presupuesto_id).delete()
        if cirugia:
            Cirugia.objects.filter(id = cirugia_id).delete()
            
            
        
        return redirect('index')
    
     

@add_group_name_to_context    
class documento_new_cxp(UserPassesTestMixin,TemplateView): 
    
    template_name='documento_new_cxp.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medicos = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        retenciones = Retencion.objects.all().order_by('nombre')
        tipodocumento = TipoDocumento.objects.all().order_by('nombre')
        FacturaProveedor.objects.filter(numerodocumento__isnull=True).delete()
        facturas = FacturaProveedor.objects.filter(tipodocumento_id = 4).order_by('-id')
        tasa_hoy = CambioDiaBcv(datetime.now())
        fecha_hoy = datetime.now()
        context['medicos'] = medicos
        context['facturas'] = facturas
        context['tasa_hoy'] = tasa_hoy
        context['fecha_hoy'] = fecha_hoy
        context['retenciones'] = retenciones
        context['tipodocumento'] = tipodocumento
        return context
    
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)    
        medico = request.POST['medico']
        nrodocumento = request.POST['nrodocumento']
        nrocontrol = request.POST['nrocontrol']
        fechaentrega = request.POST['fechaentrega'] 
        retencion = request.POST['retencion']
        baseimponible = request.POST['baseimponible']
        p_rentencion = request.POST['p_rentencion']
        m_retencion = request.POST['m_retencion'] 
        monto_pagar_neto = request.POST['monto_pagar_neto']
        selected_facturas = request.POST.getlist('id_factura_documento')
        cambio_congelado = CambioDiaBcv(datetime.now())

        factura_proveedor = FacturaProveedor.objects.create(
            fecha_entrega = fechaentrega,
            numerodocumento = nrodocumento,
            numerocontrol = nrocontrol,
            nota= 'Factura creada por recibos de pago',
            porcentaje_retencion_islr = p_rentencion.replace(',','.'),
            concepto_id = retencion,
            proveedor_id = medico,
            tipodocumento_id = 1,
            tipomoneda_id = 2,
            usuario_id = self.request.user.id,
            estatus = 'PAG',
            tipo = 'FM',
            fecha_cambio = datetime.now(),
            cambio_congelado = cambio_congelado

        )

        id_factura = factura_proveedor.id
        for factura in  selected_facturas:
            FacturaProveedor.objects.filter(id = factura ).update(
                estatus = 'PAG'
            )
            detalle_factura = DetalleFacturaProveedor.objects.filter(factura_id = factura)
            for detalle in detalle_factura:
                DetalleFacturaProveedor.objects.create(
                    cantidad = detalle.cantidad,
                    precio_unitario = detalle.precio_unitario,
                    porc_iva = detalle.porc_iva,
                    descripcion = detalle.descripcion + ' Recibo  : '+str(detalle.factura.numerodocumento) ,
                    factura_id = id_factura,
                    cirugia_id = detalle.cirugia_id,
                    detalle_id = detalle.detalle_id,
                    manual = detalle.manual,
                    gastos = detalle.gastos,
                    montoiva = detalle.montoiva,
                    precio_bs = detalle.precio_bs,
                    subtotal = detalle.subtotal,
                    cambio_bcv = detalle.cambio_bcv,
                    congelar_moneda = detalle.congelar_moneda,
                    gastos_bs = detalle.gastos_bs,
                    precio_modificado = detalle.precio_modificado,
                    detallenotaentrega_id = detalle.detallenotaentrega_id,
                    subtotal_bs = detalle.subtotal_bs,
                    subtotal_dl = detalle.subtotal_dl,
                    precio_dl = detalle.precio_dl,
                    usuario_id = self.request.user.id,
                    

                )

        FacturaMedico.objects.create(
            fecha_entrega = fechaentrega,
            numerodocumento = nrodocumento,
            numerocontrol = nrocontrol,
            pretencion = p_rentencion.replace(',','.'),
            baseimponible = baseimponible.replace(',','.'),
            montoretenido = m_retencion.replace(',','.'),
            netopagado = monto_pagar_neto.replace(',','.'),
            concepto_id = retencion,
            medico_id = medico,
            factura_id = id_factura,
            usuario_id = self.request.user.id,
            
        )
        """ factura_medico.save()
        id_factura = factura_medico.id
        for factura in  selected_facturas:
            RegistroDocumento.objects.filter(factura_id = factura).update(
                facturamedico_id = id_factura
            ) """
                    
        
        return redirect('documento_new_cxp')

    
### llamada desde javascript
def modificacion_corte_cuenta(request):
    if request.method == 'POST':
        print('llego')
        datos = json.loads(request.body)
        id_presupuesto = datos['id_presupuesto']
        precio_usado = datos['precio_usado']
        detalle = datos['detalle']
        id_cirugia = datos['id_cirugia']
        detalle_presupuesto = DetallePresupuesto.objects.filter(id=id_presupuesto).first()
        detalle_cirugia = DetalleCirugia.objects.filter(cirugia_id=id_cirugia, detalle_id=detalle).first()
        if detalle_cirugia:
            if detalle_cirugia.pagado:
                return JsonResponse({'mensaje': 'pagado'})


            DetalleCirugia.objects.filter(cirugia_id=id_cirugia, detalle_id=detalle).update(precio=precio_usado.replace(',','.'),alertaexcedente=False,manual=True)
            if detalle_cirugia.medico:
                NotaQuirurgica.objects.filter(medico_id = detalle_cirugia.medico_id, cirugia_id = id_cirugia ).update(
                    montopendiente = float(precio_usado),
                    usuario_id = request.user.id,
                )
                
            DetallePresupuesto.objects.filter(id=id_presupuesto).update(alertaexcedente=False, precio_usado = precio_usado.replace(',','.'))
            LogEliminacion.objects.create(
                descripcion = 'Cambiado el monto y se desactiva la directiva de calculo automatico y de alertar excedentes en cirugia:'+str(id_cirugia), 
                usuario_id = request.user.id
                )
        else:
            print('aqui debo crear de nuevo en detalle de cirugia', precio_usado, detalle)
            if detalle_presupuesto:
                DetallePresupuesto.objects.filter(id=id_presupuesto).update(cantidad_usada = detalle_presupuesto.cantidad, precio_usado = precio_usado.replace(',','.'), usuario_id = request.user.id)
                DetalleCirugia.objects.create(
                    cantidad = detalle_presupuesto.cantidad,
                    precio = precio_usado,
                    fecha_cambio = detalle_presupuesto.fecha_cambio,
                    cirugia_id = id_cirugia,
                    convenio_id = detalle_presupuesto.convenio_id,
                    detalle_id = detalle_presupuesto.detalle_id,
                    grupo_id = detalle_presupuesto.grupo_id,
                    plantilla_id = detalle_presupuesto.plantilla_id,
                    unidad_id = detalle_presupuesto.unidad_id,
                    usuario_id = request.user.id,
                    ntqx = detalle_presupuesto.ntqx,
                    facturable = True,
                    montoconsumo = detalle_presupuesto.montoconsumo,
                    medico_id = detalle_presupuesto.medico_id,
                    excedente = detalle_presupuesto.excedente,
                    alertaexcedente = detalle_presupuesto.alertaexcedente,
                    montotope = detalle_presupuesto.montotope,
                    manual = True

                )

            

        return JsonResponse({'mensaje': 'Datos guardados correctamente en moficicacion de corte de cuenta'})
    else:
        return JsonResponse({'mensaje': 'Error al guardar en modificacion de corte de cuenta'})

        
        
@add_group_name_to_context    
class pdfAltamedica(TemplateView):
    template_name='pdf_altamedica.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        usuario_elabora = '('+ self.request.user.username + ') '+ self.request.user.first_name +' '+ self.request.user.last_name
        cirugia_id = self.kwargs['pk']
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        fecha_hoy = datetime.now()
        usuario_logueado = self.request.user.id
        user = User.objects.get(id=usuario_logueado)
        medico = Medico.objects.filter(user_id=usuario_logueado).first()
        altamedica = AltaMedica.objects.filter(cirugia_id =cirugia_id ).first()
        tratamiento = Tratamiento.objects.filter(cirugia_id=cirugia_id).order_by('-id')
        inventarios = Inventario.objects.filter(categoria_id__in=[1, 2],producto_activo=True).order_by('categoria')
        edad_paciente=calcular_edad(cirugia.paciente.fecha_nac)
        medicosaltamedica = MedicoAltaMedica.objects.filter(altamedica_id = altamedica.id).order_by('medico_tratamiento__nombre')
        
        
        context['medico']=medico
        context['cirugia']=cirugia
        context['fecha_hoy']=fecha_hoy
        context['altamedica']=altamedica
        context['tratamiento']=tratamiento
        context['edad_paciente']=edad_paciente
        context['usuario_elabora']=usuario_elabora
        context['medicosaltamedica']=medicosaltamedica
        return context
   
   
def guardar_item_corte_cuenta(request):
    if request.method == 'POST':
        
        datos = json.loads(request.body)
        idBaremo = datos['idBaremo']
        idDetalle = datos['idDetalle']
        idGrupo = datos['idGrupo']
        idPlantilla = datos['idPlantilla']
        cantidad = datos['cantidad']
        precio = datos['precio']
        idConvenio = datos['idConvenio']
        idCirugia = datos['idCirugia']
        idPresupuesto = datos['idPresupuesto']
        ntqx = datos['ntqx']
        unidad = datos['unidad']
        usuario_id = request.user.id
        cantidad_number =  Decimal(cantidad.replace(',', '.'))
        cirugia= Cirugia.objects.filter(id=idCirugia).first()
        
        #existe_item = DetalleCirugia.objects.filter(cirugia_id = cirugia.id, detalle_id = idDetalle ).exists()
        
        cuentacobrar = CuentaxCobrar.objects.filter(cirugia_id = idCirugia).first()
        saldo_cuenta = 0
        if cuentacobrar:
            monto_cirugia = DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuentacobrar.id, montocobrar__gte = 0).first()
            if monto_cirugia is None:
                monto_total = 0
            else:
                precio_nuevo=precio.replace(',','.')
                monto_total = monto_cirugia.montocobrar + Decimal(precio_nuevo)
                DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuentacobrar.id, montocobrar__gte = 0).update(
                  montocobrar = F('montocobrar')  +  Decimal(precio_nuevo)
                )
                
                
            total_pagado = DetalleCuentaCobrar.objects.filter(
                                        cuentacobrar_id=cuentacobrar.id,
                                        montocobrar__lt=0
                                    ).aggregate(total=Sum('montocobrar'))['total']
            
                                    # Si no hay resultados, total_pagado será None, así que puedes manejarlo si es necesario
            if total_pagado is None:
                total_pagado = 0
            
            
            
            saldo_cuenta = monto_total + total_pagado

                
            
        quirofano_id=None
        if cirugia:
            quirofano_id = cirugia.quirofano_id

        if cantidad_number == 0.0 or cantidad_number == 0:
            cantidad = 1.00
        else:
            cantidad = cantidad_number
            
        detalle_nuevo = DetallePresupuesto.objects.create(cantidad=cantidad,precio=0, convenio_id=idConvenio, detalle_id=idDetalle, grupo_id=idGrupo, 
                                          plantilla_id=idPlantilla,presupuesto_id=idPresupuesto,ntqx = ntqx, usuario_id=usuario_id, unidad_id=unidad ) 
        DetalleCirugia.objects.create(cantidad=cantidad, precio=precio.replace(',','.'), convenio_id=idConvenio, detalle_id=idDetalle, grupo_id=idGrupo, 
                                          plantilla_id=idPlantilla,cirugia_id=idCirugia,ntqx = ntqx, usuario_id=usuario_id, unidad_id=unidad ) 

        
        print('ntqx', ntqx)
        if ntqx == 'True':
            print('creo ntqx', ntqx)
            NotaQuirurgica.objects.create(
                cirugia_id=idCirugia,
                fecha_elaboracion = datetime.now(),
                participante_id = idDetalle,
                quirofano_id = quirofano_id,
                incluir = True,
                montopendiente = precio.replace(',','.'),
                detallepresupuesto_id = detalle_nuevo.id,
                nota= 'Agregado en corte de cuenta',
                usuario_id = request.user.id
            )
        
       
        return JsonResponse({'mensaje': 'Datos guardados correctamente en moficicacion de corte de cuenta'})
    else:
        return JsonResponse({'mensaje': 'Error al guardar en modificacion de corte de cuenta'})


def cambiar_medico_en_cortecuenta(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idNotaQx = datos['idNotaQx']
        idMedico = datos['idMedico']
        id_cirugia = datos['id_cirugia']
        medico_nuevo = Medico.objects.filter(id=idMedico).first()
        if medico_nuevo:
            nombrenuevo = medico_nuevo.nombre
        else:
            nombrenuevo = 'Ninguno'
        

        nota_anterior = NotaQuirurgica.objects.filter(id=idNotaQx).first()
        NotaQuirurgica.objects.filter(id=idNotaQx).update(
            medico_id = idMedico
        )
        LogEliminacion.objects.create(
            descripcion = 'Cambio de medico de nota quirugica en estado de cuenta, medico anterior :'+str(nota_anterior.medico)+' Medico nuevo:'+str(nombrenuevo)
        )
       
        return JsonResponse({'mensaje': 'Datos guardados correctamente en moficicacion de corte de cuenta medicos'})
    else:
        return JsonResponse({'mensaje': 'Error al guardar en modificacion de corte de cuenta medicos'})


def precio_costo_producto_inventario(id_inventario):
    costo_inventario = 0.01
    inventario = Inventario.objects.filter(id = id_inventario).first()
    if inventario:
        costo_iva = inventario.costo * (inventario.piva / 100)
        costo_inventario = (costo_iva + inventario.costo) / (inventario.unidad_conversion)
        if costo_inventario <= 0.01:
            costo_inventario = 0.01
    
    return costo_inventario


def asignar_kit(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idKit = datos['idKit']
        idCirugia = datos['idCirugia']
        itemdekit = Inventario.objects.filter(kit_id = idKit)
        usuario_logueado = request.user.id
        user = User.objects.get(id=usuario_logueado)
        medico = Medico.objects.filter(user_id=usuario_logueado).first()
        if not medico:
            medico = None
        else:
            medico = medico.id

        for ikit in itemdekit:
            precio_costo_unitario = precio_costo_producto_inventario(ikit.id)
            consumocirugia=ConsumoCirugia.objects.create(inventario_id = ikit.id, cantidad_uso=ikit.cantidad_kit, venta=ikit.venta_kit, consumo_id=2,
                                      cirugia_id=idCirugia, hora=datetime.now().time(), farmacia=True,precio_costo_unitario = precio_costo_unitario
                                      
                                      )
            consumocirugia.save()
            idconsumocirugia=consumocirugia.id
            Tratamiento.objects.create(tratamiento='Aplicar :'+ ikit.nombre, 
                                                 cirugia_id=idCirugia, inventario_id=ikit.id,cantidad_uso=ikit.cantidad_kit,
                                                 consumo_id=idconsumocirugia, medico_aplicante_id = medico, medico_orden_id=medico)
            
        
        return JsonResponse({'mensaje': 'Datos guardados correctamente en KIT de HOSPITAL'})
    else:
        return JsonResponse({'mensaje': 'Error al guardar KIT de HOSPITAL'})
    
    
def filtrar_kits_cirugia(request):
    idKit = request.GET.get('idKit')
    if idKit:
        kits = Inventario.objects.filter(kit_id=idKit).order_by('nombre')  # Reemplaza con tu condición
        datos = []
        for kit in kits:
            datos.append({
                'id': kit.id,
                'codigo': kit.codigo,
                'categoria' : kit.categoria.nombre,
                'nombre': kit.nombre,
                'cantidad': kit.cantidad_unitaria,
                'venta': kit.venta,
                
                # Agregar más columnas según sea necesario
            })
        return JsonResponse(datos, safe=False)
    else:
        return JsonResponse({'error': 'Error al deserializar datos'}, status=400)
    
    
def guardar_medico_notaqx(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idNotaqx = datos['idNotaqx']
        idMedico = datos['idMedico']
        NotaQuirurgica.objects.filter(id=idNotaqx).update(medico_id=idMedico)

        return JsonResponse({'mensaje': 'Datos guardados correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al guardar datos'})
    
    
def refresh_table(request):
    id_filter = request.GET.get('id_filter')
    cirugia = Cirugia.objects.filter(id=id_filter).first()
    total_precio = 0
    my_objects = ConsumoCirugia.objects.filter(cirugia_id=id_filter, cantidad_real_usada__gt = 0, consumo_id__in = [1,10])
    for myo in my_objects:
        myo.venta = myo.cantidad_real_usada * Decimal(round(myo.inventario.monto_venta,2))
        total_precio = Decimal(total_precio) + Decimal(myo.venta)
        
        
    return render(request, 'my_table.html', {'my_objects': my_objects, 'total_precio': total_precio, 'cirugia': cirugia})


def refresh_table_medicos(request):
    id_filter = request.GET.get('id_filter')
    cirugia = Cirugia.objects.filter(id=id_filter).first()
    notaquirurgica = NotaQuirurgica.objects.filter(cirugia_id=id_filter)
    medicos = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
    
    return render(request, 'tabla_medicos_qx.html', {'notaquirurgica': notaquirurgica, 'medicos':medicos})


def cirugia_standby(request):
    idCirugia = request.GET.get('idCirugia')
    cirugia = Cirugia.objects.filter(id=idCirugia).update(
        estatus_id = 9
    )
    
    return JsonResponse({'mensaje': 'Datos Update correctamente'})



def eliminar_detalle_cortecuenta(request):
    idDetallePresupuestoDelete = request.GET.get('idDetallePresupuestoDelete')

    presupuesto=DetallePresupuesto.objects.filter(id=idDetallePresupuestoDelete).first()
    
    presupuesto_id = presupuesto.presupuesto_id
    detalle_id = presupuesto.detalle_id
    cirugia = Cirugia.objects.filter(presupuesto_id = presupuesto_id ).first()
    superUser = request.user.groups.filter(Q(name='SuperAdministracion')).exists()
    pagado_detalle = DetalleCirugia.objects.filter(cirugia_id=cirugia.id, detalle_id = detalle_id ).first() 
    if pagado_detalle:
        if pagado_detalle.pagado:
            return JsonResponse({'mensaje': "pagado"})


        if presupuesto.precio == 0:
            DetallePresupuesto.objects.filter(id=idDetallePresupuestoDelete).delete()
        else:
            DetallePresupuesto.objects.filter(id=idDetallePresupuestoDelete).update(
                    precio_usado = 0
            )
            
        if cirugia:
            precio = DetalleCirugia.objects.filter(cirugia_id=cirugia.id, detalle_id = detalle_id ).first()
            if precio:
                precio_menos = precio.precio
                nombreitem = precio.detalle
            else:
                precio_menos = 0
                nombreitem = 'N/A'
                
                
            
            DetalleCirugia.objects.filter(cirugia_id=cirugia.id, detalle_id = detalle_id ).delete()
            idCirugia = cirugia.id
            
            LogEliminacion.objects.create(
                descripcion = 'Eliminacion de item en corte de cuenta cirugia: '+str(cirugia.id)+ ' paciente:'+str(cirugia.paciente)+' del item '+str(nombreitem),
                usuario_id = request.user.id
            )        
            ####
            cuentacobrar = CuentaxCobrar.objects.filter(cirugia_id = idCirugia).first()
            saldo_cuenta = 0
            if cuentacobrar:
                monto_cirugia = DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuentacobrar.id, montocobrar__gte = 0).first()
                if monto_cirugia is None:
                    monto_total = 0
                else:
                    monto_total = monto_cirugia.montocobrar - Decimal(precio_menos)
                    if monto_total < 0:
                        monto_total = 0
                        
                    DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuentacobrar.id, montocobrar__gte = 0).update(
                    montocobrar = monto_total
                    )
                    
                    
                total_pagado = DetalleCuentaCobrar.objects.filter(
                                            cuentacobrar_id=cuentacobrar.id,
                                            montocobrar__lt=0
                                        ).aggregate(total=Sum('montocobrar'))['total']
                
                                        # Si no hay resultados, total_pagado será None, así que puedes manejarlo si es necesario
                if total_pagado is None:
                    total_pagado = 0
                
                saldo_cuenta = monto_total + total_pagado
                
                       
            ###

    return JsonResponse({'mensaje': 'Datos eliminado en corte cuenta correctamente'})



def cirugia_readmitir(request):
    idCirugia = request.GET.get('idCirugia')
    cirugia = Cirugia.objects.filter(id=idCirugia).update(
        estatus_id = 2
    )
    
    return JsonResponse({'mensaje': 'Datos Update correctamente'})


def refresh_table_asignado_qx(request):
    id_filter = request.GET.get('id_filter')
    my_objects_asignado = ConsumoCirugia.objects.filter(cirugia_id=id_filter, farmacia = False).order_by('inventario')
    if my_objects_asignado:
        total_precio = my_objects_asignado.aggregate(Sum('venta'))['venta__sum']
    else:
        total_precio =0.00
        
        
    return render(request, 'my_table_asignado_farmacia.html', {'my_objects_asignado': my_objects_asignado, 'total_precio': total_precio})

def refresh_table_farmacia(request):
    idCirugia = request.GET.get('idCirugia')
    lugar_consumo = 1
    consumosolicitado = ConsumoCirugia.objects.filter(cirugia_id = idCirugia, farmacia=True, consumo_id__in = [1,10]).order_by('-id')
    consumo = ConsumoCirugia.objects.filter(cirugia_id = idCirugia, farmacia=False, consumo_id__in = [1,10]).order_by('inventario__nombre')
    cirugias = Cirugia.objects.filter(id=idCirugia).first()
    total_cantidad = consumosolicitado.aggregate(Sum('cantidad_uso'))['cantidad_uso__sum']
    
    return render(request, 'tabla_farmacia.html', {'consumosolicitado': consumosolicitado, 'total_cantidad':total_cantidad, 'cirugias':cirugias, 'consumo':consumo})

def refresh_table_pagos_medicos(request):
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
    fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    
    TempFecha.objects.all().delete()
    TempFecha.objects.create(
        fecha_desde = fecha_desde,
        fecha_hasta = fecha_hasta
    )
    """
    montomedicos = NotaQuirurgica.objects.filter(pagado=False,cirugia__fecha_procedimiento__range=[fecha_desde, fecha_hasta] )
    for med in montomedicos:
        precio_cirugia = 0
        pordesc = 0
        porcentajedescuento = Medico.objects.filter(id=med.medico_id).first()
        if porcentajedescuento:
            pordesc = porcentajedescuento.por_descuento
            
            
            
        precio = DetalleCirugia.objects.filter(cirugia_id=med.cirugia_id, detalle_id = med.participante_id, cirugia__fecha_procedimiento__range=[fecha_desde, fecha_hasta]).first()
        if precio:
            descuento = precio.precio * Decimal(pordesc/100)
            precio_cirugia = precio.precio - descuento
            NotaQuirurgica.objects.filter(id=med.id).update(montopendiente=precio_cirugia)
                
        
    mediconotaqx = NotaQuirurgica.objects.filter(pagado=False, cirugia__fecha_procedimiento__range=[fecha_desde, fecha_hasta]).annotate(
                    monto_pendiente_total=Sum('montopendiente')
                ).values('medico_id', 'medico__nombre', 'medico__cedula', 'monto_pendiente_total').annotate(
                    count=Count('id')
                ).order_by('medico__nombre')
        
    total_pendiente = mediconotaqx.aggregate(total_pendiente=Sum('monto_pendiente_total')) """
    
    total_general_pendiente = 0
    medicos = Medico.objects.filter(grupo='M').exclude(tipopersonal_id = 9).order_by('nombre')
    for medico in medicos:
        # Total facturado: suma de precios de detallecirugia del médico
        medico.total_facturado = medico.detallecirugia_set.filter(cirugia__fecha_procedimiento__range=[fecha_desde, fecha_hasta]).aggregate(
            total=Sum('precio')
        )['total'] or 0

        medico.participaciones = medico.detallecirugia_set.filter(cirugia__fecha_procedimiento__range=[fecha_desde, fecha_hasta]).count()

        # Total pendiente: suma de montopendiente de notaquirurgica donde pagado=False
        medico.total_pagado = medico.notaquirurgica_set.filter(cirugia__fecha_procedimiento__range=[fecha_desde, fecha_hasta], pagado=True).aggregate(
            total=Sum('montopendiente')
        )['total'] or 0

        medico.total_pendiente = medico.total_facturado - medico.total_pagado
        total_general_pendiente += medico.total_pendiente


    
    return render(request, 'tabla_pagos_medicos.html', {'mediconotaqx': medicos, 'total_general_pendiente':total_general_pendiente})


def eliminar_consumo_cirugia(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idConsumo = datos['idConsumo']
        whoElimina = datos['whoElimina']
        if whoElimina == 'Qx':
            ConsumoCirugia.objects.filter(id=idConsumo, conciliada=False).update(
                cantidad_real_usada = 0,
            )
        else:
            ConsumoCirugia.objects.filter(id=idConsumo, conciliada=False).delete()

        return JsonResponse({'mensaje': 'Datos eliminados correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al eliminar datos'})
    

def guardar_consumo_cirugia(request):
    if request.method == 'POST':
        print('guardar_consumo_cirugia')
        datos = json.loads(request.body)
        filaId = datos['filaId']
        cantidad = datos['cantidad']
        idCirugia = datos['idCirugia']
        venta = datos['venta']
        farmacia = datos['farmacia']
        deposito = datos['deposito']
        medico_entregado = datos['medico_entregado']
        nota = datos['nota']
        usuario_logueado = request.user.id
        medico = Medico.objects.filter(user_id=usuario_logueado).first()
        if not medico:
            medico = None
        else:
            medico = medico.id

        if not medico_entregado:
            medico_entregado = None

        
        total_venta = float(cantidad) * float(venta.replace(',','.'))
        precio_costo_unitario = precio_costo_producto_inventario(filaId)
        ConsumoCirugia.objects.create(
            cirugia_id=idCirugia,
            cantidad_uso = cantidad,
            venta = total_venta,
            inventario_id = filaId,
            hora = datetime.now(),
            consumo_id=1,
            farmacia = farmacia,
            solicitante_id = medico,
            usuario_id = usuario_logueado,
            entregado_id = medico_entregado,
            nota = nota,
            precio_unitario = venta.replace(',','.'),
            deposito_id = deposito,
            precio_costo_unitario = precio_costo_unitario

        )
                    
        return JsonResponse({'mensaje': 'Datos GUARDADOS EN CONSUMO correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al GUARDAR CONSUMO datos'})
    
    
def guardar_kit_cirugia(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idKit = datos['idKit']
        idCirugia = datos['idCirugia']
        farmacia = datos['farmacia']
        usuario_logueado = request.user.id
        medico = Medico.objects.filter(user_id=usuario_logueado).first()
        if not medico:
            medico = None
        else:
            medico = medico.id
            
            
        buscarkit = Inventario.objects.filter(kit_id = idKit).order_by('nombre')
        for kit in buscarkit:
            precio_costo_unitario = precio_costo_producto_inventario(kit.id)
            ConsumoCirugia.objects.create(
                  cirugia_id=idCirugia,
                  cantidad_uso = kit.cantidad_kit,
                  venta = kit.venta_kit,
                  inventario_id = kit.id,
                  hora = datetime.now(),
                  consumo_id=1,
                  farmacia = farmacia,
                  solicitante_id = medico,
                  precio_costo_unitario = precio_costo_unitario
                )
        
        return JsonResponse({'mensaje': 'Datos GUARDADOS EN CONSUMO correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al GUARDAR CONSUMO datos'})
    
    
    
def guardar_kit_farmacia(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idKit = datos['idKit']
        idCirugia = datos['idCirugia']
        usuario_logueado = request.user.id
        medico = Medico.objects.filter(user_id=usuario_logueado).first()
        if not medico:
            medico = None
        else:
            medico = medico.id
            
            
        #buscarkit = Inventario.objects.filter(kit_id = idKit).order_by('nombre')
        buscarkitDeposito = DepositoUso.objects.filter(inventario__kit_id=idKit, deposito_id = 1, inventario__producto_activo =True).order_by('inventario__nombre')
        for kit in buscarkitDeposito:
            nota_asignacion = 'ASIGNADO x KIT EN CIRUGIA'
            advertencia = False
            existencia_deposito = kit.existenciaUnd
            cantidad_usar = 0
            cantidad_usar = kit.inventario.cantidad_kit
            
            if Decimal(cantidad_usar) > Decimal(existencia_deposito): 
                cantidad_usar = Decimal(existencia_deposito)
                nota_asignacion = 'SOLO CANTIDAD DISPONIBLE, NO HAY CANTIDAD SOLICITADA EN KIT'
                advertencia = True
                
            if cantidad_usar > 0:
                precio_costo_unitario = precio_costo_producto_inventario(kit.inventario_id)
                consumonuevo = ConsumoCirugia.objects.create(
                    cirugia_id=idCirugia,
                    cantidad_uso = cantidad_usar,
                    venta = kit.inventario.venta_kit,
                    inventario_id = kit.inventario_id,
                    hora = datetime.now(),
                    consumo_id=1,
                    farmacia = True,
                    solicitante_id = request.user.id,
                    precio_unitario = kit.inventario.monto_venta, ## modificado el 05/12/2025
                    usuario_id = request.user.id,
                    deposito_id = 1,
                    nota=nota_asignacion,
                    advertencia = advertencia,
                    precio_costo_unitario = precio_costo_unitario
                )
                
                InventarioDescarga.objects.create(
                    cantidad = cantidad_usar,
                    nota = nota_asignacion,
                    deposito_id = 1,
                    inventario_id = kit.inventario_id,
                    usuario_id = request.user.id,
                    tipodescarga_id = 6,
                    cirugia_id = idCirugia,
                    persona_id = request.user.id,
                    consumocirugia_id = consumonuevo.id
                )
                

                          
        return JsonResponse({'mensaje': 'Datos GUARDADOS EN CONSUMO correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al GUARDAR CONSUMO datos'})
    
    
    
@add_group_name_to_context    
class mantenimiento_kit(TemplateView):
    template_name='mantenimiento_kit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        depositos = Deposito.objects.all().order_by('nombre')
        productos = KitInventario.objects.all().order_by('nombre')
        inventario = []
        inventario_total = []
        total_precio = 0
        """ 
        
        producto_uno = productos.first()
        inventario = [Inventario.objects.filter(kit_id=producto_uno.id).order_by('nombre')]
        inventario_total = Inventario.objects.all().order_by('categoria', 'nombre')
        if inventario:
            total_precio = inventario.aggregate(Sum('venta_kit'))['venta_kit__sum']
        else:
            total_precio =0.00
         """
        
        context['productos'] = productos
        context['depositos'] = depositos
        context['inventario'] = inventario
        context['total_precio'] = total_precio
        context['inventario_total'] = inventario_total
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)    
        nombre = request.POST['nuevo_kit']
        nuevokit = KitInventario.objects.filter(nombre = nombre).first()
        if not nuevokit:
            nuevokit = KitInventario.objects.create(nombre = nombre)
            nuevokit.save()
            inventario = Inventario.objects.filter(kit_id=nuevokit.id).order_by('nombre')
        else:
            inventario = Inventario.objects.filter(kit_id=1).order_by('nombre')
            
        productos = KitInventario.objects.all().order_by('-id')
        inventario_total = Inventario.objects.all().order_by('categoria', 'nombre')
        if inventario:
            total_precio = inventario.aggregate(Sum('venta'))['venta__sum']
        else:
            total_precio =0.00
        
        depositos = Deposito.objects.all().order_by('nombre')
        context['productos'] = productos
        context['inventario'] = inventario
        context['total_precio'] = total_precio
        context['inventario_total'] = inventario_total
        context['depositos'] = depositos
        
        return render(request, 'mantenimiento_kit.html', context)
    

def eliminar_kit_inventario(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        inventarioId = datos['inventarioId']
        Inventario.objects.filter(id=inventarioId).update(kit_id = None)

        return JsonResponse({'mensaje': 'Desasignado del kit correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al desagsignar kit de inventario datos'})
    
    
def refresh_table_kit(request):
    idKit = request.GET.get('idKit')
    total_precio =0.00
    depositos = Deposito.objects.all().order_by('nombre')
    if idKit:
        inventario = Inventario.objects.filter(kit_id=idKit).order_by('nombre')
        if inventario:
            total_precio = inventario.aggregate(Sum('venta_kit'))['venta_kit__sum']
    
    else:
        inventario =[]
            
        
    return render(request, 'tabla_kit.html', {'inventario': inventario, 'total_precio': total_precio, 'depositos':depositos})
    
  
def refresh_table_extras(request):
    cirugia_id = request.GET.get('idCirugua')
    notaquirurgica = NotaQuirurgica.objects.filter(cirugia_id=cirugia_id, incluir=1 )
    medicos = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
    
    return render(request, 'tabla_medicos_qx.html', {'notaquirurgica': notaquirurgica, 'medicos':medicos})  


def refresh_table_extras_eliminar(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        notaqx_id = datos['idNotaqx']
        NotaQuirurgica.objects.filter(id=notaqx_id).delete()

        return JsonResponse({'mensaje': 'Eliminado medico de nota qx'})
    else:
        return JsonResponse({'mensaje': 'Error al eliminar medico de notaqx'})
    


def agregar_kit_inventario(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idInventario = datos['idInventario']
        idKit = datos['idKit']
        inventario = Inventario.objects.filter(id=idInventario).first()
        Inventario.objects.filter(id=idInventario).update(
            kit_id = idKit,
            venta_kit = inventario.monto_venta,
            cantidad_kit = 1,
            )

        return JsonResponse({'mensaje': 'Desasignado del kit correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al desagsignar kit de inventario datos'})
    
def agregar_personal_extra(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idBaremo = datos['idBaremo']
        idCirugua = datos['idCirugua']
        cirugia = Cirugia.objects.filter(id=idCirugua).first()
        baremo = Baremo.objects.filter(id=idBaremo).first()
        NotaQuirurgica.objects.create(
            cirugia_id = idCirugua,
            participante_id = baremo.detalle_id,
            quirofano_id = cirugia.quirofano_id,
            incluir = True,
        )

        return JsonResponse({'mensaje': 'Desasignado del kit correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al desagsignar kit de inventario datos'})


def update_kit_inventario(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idInventario = datos['idInventario']
        nCantidad = datos['nCantidad']
        inventario = Inventario.objects.filter(id=idInventario).first()
        Inventario.objects.filter(id=idInventario).update(
            cantidad_kit = nCantidad,
            venta_kit =  Decimal(round(inventario.monto_venta,2)) * Decimal(nCantidad)
            )

        return JsonResponse({'mensaje': 'Update del kit correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al Update kit de inventario datos'})
    
    
    
@add_group_name_to_context    
class pedido_farmacia(TemplateView):
    template_name='pedido_farmacia.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['pk']
        medicos = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        fecha_hoy = datetime.now()
        cirugias = Cirugia.objects.filter(id=cirugia_id).first()
        consumosolicitado = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, farmacia=True, consumo_id__in = [1,10]).order_by('-id')
        compuestos = DepositoUso.objects.filter(deposito_id = 1,inventario__compuesto = '3', inventario__producto_activo =True).order_by('inventario__nombre')
        consumo = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, farmacia=False, consumo_id__in = [1,10] ).order_by('-id')
        total_cantidad = consumosolicitado.aggregate(Sum('cantidad_uso'))['cantidad_uso__sum']
        total_cantidad_entregada = consumo.aggregate(Sum('cantidad_uso'))['cantidad_uso__sum']
        kit = KitInventario.objects.all().order_by('nombre')

        #depositos_correspondiente_farmacia = DepositoUso.objects.filter(deposito_id = 1, cantidad_deposito__gt = 0)
        depositos_asignados = Deposito.objects.filter(id=1)
        context['kit'] = kit
        context['medicos'] = medicos
        context['consumo'] = consumo
        context['cirugias'] = cirugias
        context['fecha_hoy'] = fecha_hoy
        context['compuestos'] = compuestos
        context['total_cantidad'] = total_cantidad
        context['consumosolicitado'] = consumosolicitado
        context['depositos_asignados'] = depositos_asignados
        context['total_cantidad_entregada'] = total_cantidad_entregada
        #context['depositos_correspondiente_farmacia'] = depositos_correspondiente_farmacia
        
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)  
        cirugia_id = self.kwargs['pk']  
        entregado = request.POST['medico_entrega']
        nota =  request.POST['nota_entrega']
        tasa_bcv_calculo = CambioDiaBcv(datetime.now())
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        total_usd = 0
        if request.POST['botonpresionado'] == 'entregar':
            ConsumoCirugia.objects.filter(cirugia_id=cirugia_id,farmacia=True ).update(farmacia=False, entregado_id = entregado, nota=nota )
            return redirect('pedido_farmacia' , pk = cirugia_id )
        
        if request.POST['botonpresionado'] == 'compuesto':
            seleccionados = request.POST.getlist('seleccionados')
            for codigo in seleccionados:
                cantidad = request.POST.get(f'cantidad_{codigo}', 1)  # Obtiene la cantidad
                cantidad = float(cantidad)
                deposito = DepositoUso.objects.filter(inventario_id = codigo, deposito_id = 1, inventario__producto_activo =True).first()
                disponible = total_venta = 0
                compuesto = '1'
                lugar_consumo = 10
                if deposito:
                    disponible = deposito.existenciaUnd
                    total_venta = deposito.inventario.monto_venta
                    compuesto = deposito.inventario.compuesto
                
                if  cantidad > float(disponible):
                    cantidad = float(disponible)
                    
                if cantidad > 0:
                    consumoexiste = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, consumo_id = lugar_consumo, inventario_id = codigo, compuesto = compuesto).first()
                    precio_costo_unitario = precio_costo_producto_inventario(codigo)
                    if consumoexiste:
                        ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, consumo_id = lugar_consumo, inventario_id = codigo, compuesto = compuesto).update(
                            cantidad_uso = F('cantidad_uso') + cantidad,
                            cantidad_real_usada = F('cantidad_real_usada') + cantidad,
                            usuario_id = request.user.id,
                            hora_uso = datetime.now().time(),
                            solicitante_id = request.user.id,
                            precio_costo_unitario = precio_costo_unitario
                        )
                        InventarioDescarga.objects.filter(consumocirugia_id = consumoexiste.id).update(
                            cantidad = F('cantidad') + cantidad,
                            usuario_id = request.user.id,
                        )
                        if compuesto == '3':
                            InventarioCompuesto.objects.filter(consumo_id = consumoexiste.id).update(
                                usuario_id = request.user.id,
                                cantidad = F('cantidad') + cantidad,
                            )
                    else:
                        
                        consumonuevo = ConsumoCirugia.objects.create(
                            cirugia_id = cirugia_id,
                            cantidad_real_usada = cantidad,
                            cantidad_uso = cantidad,
                            venta = float(total_venta) * float(cantidad),
                            inventario_id = codigo,
                            farmacia = True,
                            consumo_id = lugar_consumo,
                            usuario_id = request.user.id,
                            solicitante_id = request.user.id,
                            hora_uso = datetime.now().time(),
                            precio_unitario = total_venta,
                            deposito_id = 1,
                            nota = 'ASIGNADO EN FARMACIA',
                            compuesto = compuesto,
                            precio_costo_unitario = precio_costo_unitario
                        )
                        
                        InventarioDescarga.objects.create(
                            cantidad = cantidad,
                            nota = 'ASIGNADO EN FARMACIA',
                            deposito_id = 1,
                            inventario_id = codigo,
                            usuario_id = request.user.id,
                            tipodescarga_id = 6,
                            cirugia_id = cirugia_id,
                            persona_id = request.user.id,
                            consumocirugia_id = consumonuevo.id
                        )
                        if compuesto == '3':
                            InventarioCompuesto.objects.create(
                                consumo_id = consumonuevo.id,
                                usuario_id = request.user.id,
                                cantidad = cantidad
                            )
                        
                    
                                  
            
            return redirect('pedido_farmacia' , pk = cirugia_id )
        
        if request.POST['botonpresionado'] == 'imprimir':
            consumos = ConsumoCirugia.objects.filter(cirugia_id=cirugia_id, consumo_id = 1).order_by('fecha_act','inventario__categoria')
            for consumo in consumos:
                monto_venta = round(consumo.inventario.monto_venta,2)  # Asegúrate de que 'inventario' es el campo de relación
                subtotal = consumo.cantidad_real_usada * monto_venta
                total_usd = Decimal(total_usd) + Decimal(subtotal)
                consumo.subtotal = subtotal  # Puedes agregarlo como un atributo temporal
                consumo.subtotal_bs = Decimal(subtotal) * Decimal(tasa_bcv_calculo) # Puedes agregarlo como un atributo temporal
            
            
            context['consumos'] = consumos
            context['cirugia'] = cirugia
            context['user'] = self.request.user.username
            html_string = render_to_string("pdf_entrega_farmacia.html", context)
            html_string = html_string.replace('/static/', request.build_absolute_uri('/static/'))

            html = HTML(string=html_string)
            pdf = html.write_pdf()  # Genera el PDF en memoria
            nombre_archivo = f"consumo_farmacia_historia_{cirugia_id}.pdf"
            # Crea la respuesta HTTP con el PDF
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename='+nombre_archivo
            return response


@add_group_name_to_context    
class descarga_inventario(UserPassesTestMixin, TemplateView):
    template_name='descarga_inventario.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='CambiarInventario') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medicos = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        fecha_hoy = datetime.now()
        motivos = TipoDescarga.objects.all().order_by('nombre')
        
        inventarios = Inventario.objects.all().order_by('nombre')
        codigo_descarga = InventarioDescarga.objects.all().count()
        codigo_download = 'CODE' + str(codigo_descarga).zfill(6)
        
        descargainventario = InventarioDescarga.objects.filter(descargamanual=codigo_download, cirugia_id__isnull = True)
        
        context['inventarios'] = inventarios
        context['medicos'] = medicos
        context['motivos'] = motivos
        context['fecha_hoy'] = fecha_hoy
        context['codigo_descarga'] = codigo_download
        context['descargainventario'] = descargainventario

        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)  
        
        
        return redirect('listado_producto_inventario')
        #return redirect('imprimir_entrega_farmacia' , cirugia_id = cirugia_id )
                    
    
    
@add_group_name_to_context    
class listado_cirugia_farmacia(TemplateView):
    template_name='listado_cirugia_farmacia.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        Cirugia.objects.filter(estatus_id__gt=1, estatus_id__lt = 7).update(pendiente=False)
        consumopendiente = ConsumoCirugia.objects.filter(farmacia = True, consumo_id__in = [1,10])
        for cp in consumopendiente:
            Cirugia.objects.filter(id = cp.cirugia_id).update(pendiente = True)

        #cirugias = Cirugia.objects.filter(estatus_id__gt=1, estatus_id__lt=7).order_by('-fecha_act')
        cirugias = Cirugia.objects.filter(estatus_id__gt=1, estatus_id__lt=7).annotate(
            consumos_no_conciliados=Count('consumocirugia', filter=Q(consumocirugia__conciliada=False, consumocirugia__consumo_id__in=[1,10]))
        ).order_by('-fecha_act')


        context['cirugias']=cirugias
        return context
    
    
@add_group_name_to_context    
class imprimir_conciliacion_farmacia(TemplateView):
    template_name='pdf_conciliacion_farmacia.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['cirugia_id']
        fecha_hoy = datetime.now()
        cirugia = Cirugia.objects.filter(id = cirugia_id).first()
        entrega = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, farmacia=False).exclude(cantidad_uso=F('cantidad_real_usada'))
        context['entrega'] = entrega
        context['cirugia'] = cirugia
        context['fecha_hoy'] = fecha_hoy
        return context
    
    
@add_group_name_to_context    
class CorteCuenta2(UserPassesTestMixin, TemplateView):
    template_name='corte_cuenta.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion') | Q(name='Admision') | Q(name='CorteCuenta')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['cirugia_id']
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        medicos = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        horasquirofano = TiempoQuirofano.objects.filter(cirugia_id=cirugia_id).first()
        if horasquirofano:
            dias_hospitalizacion = cirugia.dias_hospitalizacion
            hora_entrada = horasquirofano.hora_entrada
            hora_salida = horasquirofano.hora_salida
            fecha_actual = datetime.now().date()
            datetime_entrada = datetime.combine(fecha_actual, hora_entrada)
            datetime_salida = datetime.combine(fecha_actual, hora_salida)
            delta = datetime_salida - datetime_entrada
            horasejecutadas = delta.seconds // 3600
            minutosejecutados = (delta.seconds // 60) % 60
        else:
            horasejecutadas = 0
            minutosejecutados = 0
            dias_hospitalizacion = 0
            
        if horasejecutadas == 0:
            horasejecutadas = 1
        else:
            if minutosejecutados > 20:
                horasejecutadas = horasejecutadas +1
        
        Cirugia.objects.filter(id=cirugia_id).update(horas_qx = horasejecutadas)
        if cirugia.horas_qx_facturable > 0:
            horasejecutadas = cirugia.horas_qx_facturable
        
        
        # Cobros especiales totalizar
        detalle_id_cobro = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, consumo_id__in = [11]).first()   
        cobros_especiales = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, consumo_id__in = [11])
        total_venta = cobros_especiales.aggregate(total=Sum('venta'))['total'] or 0
        if total_venta > 0 and detalle_id_cobro:
                print('cobros especiales')
                DetallePresupuesto.objects.filter(detalle_id = detalle_id_cobro.baremo_cobro_id, presupuesto_id = cirugia.presupuesto_id ).update(
                    precio = total_venta,
                    precio_usado = total_venta
                )
                DetalleCirugia.objects.filter(detalle_id = detalle_id_cobro.baremo_cobro_id, cirugia_id = cirugia_id ).update(
                    precio = total_venta,
                    
                )
                
            
            
        # Fin cobros especiales
        
        unidad_dolor = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, compuesto__in = ['2','3'], consumo_id__in = [9,10])
        if unidad_dolor:
            baremounidaddolor = Baremo.objects.filter(detalle_id = 40, convenio_id = 1, grupo_id = 11, inactivar = False).first()
            baremounidaddolor_equipo = Baremo.objects.filter(detalle_id = 41, convenio_id = 1, grupo_id = 11, inactivar = False).first()
            creada_unidad_dolor_cir = DetalleCirugia.objects.filter(cirugia_id=cirugia_id,detalle_id = 40)
            creada_unidad_dolor_cir_41 = DetalleCirugia.objects.filter(cirugia_id=cirugia_id,detalle_id = 41)
            if not creada_unidad_dolor_cir_41:
                DetalleCirugia.objects.create(
                            cantidad = 1,
                            precio = baremounidaddolor_equipo.venta,
                            fecha_cambio = datetime.now().date(),
                            cirugia_id = cirugia_id,
                            convenio_id = baremounidaddolor_equipo.convenio_id,
                            detalle_id = baremounidaddolor_equipo.detalle_id,
                            grupo_id = baremounidaddolor_equipo.grupo_id,
                            plantilla_id = baremounidaddolor_equipo.plantilla_id,
                            unidad_id = baremounidaddolor_equipo.unidad_id,
                            usuario_id = self.request.user.id,
                            facturable = True,
                            alertaexcedente = True,
                            montotope = baremounidaddolor_equipo.topedia,
                        ) 
                
            
            if not creada_unidad_dolor_cir:
                if baremounidaddolor:
                    DetalleCirugia.objects.create(
                            cantidad = 1,
                            precio = baremounidaddolor.venta,
                            fecha_cambio = datetime.now().date(),
                            cirugia_id = cirugia_id,
                            convenio_id = baremounidaddolor.convenio_id,
                            detalle_id = baremounidaddolor.detalle_id,
                            grupo_id = baremounidaddolor.grupo_id,
                            plantilla_id = baremounidaddolor.plantilla_id,
                            unidad_id = baremounidaddolor.unidad_id,
                            usuario_id = self.request.user.id,
                            facturable = True,
                            alertaexcedente = True,
                            montotope = baremounidaddolor.topedia,
                        ) 
            
            creada_unidad_dolor_cir_41 = DetallePresupuesto.objects.filter(presupuesto_id=cirugia.presupuesto_id,detalle_id = 41)
            if not creada_unidad_dolor_cir_41:
                DetallePresupuesto.objects.create(
                            cantidad = 1,
                            precio = 0,
                            fecha_cambio = datetime.now().date(),
                            presupuesto_id = cirugia.presupuesto_id,
                            convenio_id = baremounidaddolor_equipo.convenio_id,
                            detalle_id = baremounidaddolor_equipo.detalle_id,
                            grupo_id = baremounidaddolor_equipo.grupo_id,
                            plantilla_id = baremounidaddolor_equipo.plantilla_id,
                            unidad_id = baremounidaddolor_equipo.unidad_id,
                            usuario_id = self.request.user.id,
                            alertaexcedente = True,
                        )
                      
            creada_unidad_dolor_pre = DetallePresupuesto.objects.filter(presupuesto_id=cirugia.presupuesto_id,detalle_id = 40)
            if not creada_unidad_dolor_pre:
                if baremounidaddolor:
                    DetallePresupuesto.objects.create(
                            cantidad = 1,
                            precio = 0,
                            fecha_cambio = datetime.now().date(),
                            presupuesto_id = cirugia.presupuesto_id,
                            convenio_id = baremounidaddolor.convenio_id,
                            detalle_id = baremounidaddolor.detalle_id,
                            grupo_id = baremounidaddolor.grupo_id,
                            plantilla_id = baremounidaddolor.plantilla_id,
                            unidad_id = baremounidaddolor.unidad_id,
                            usuario_id = self.request.user.id,
                            alertaexcedente = True,
                        )   
                    
                    
        
        detalle_cirugia = DetalleCirugia.objects.filter(cirugia_id=cirugia_id)
        for dc in detalle_cirugia:
            if not dc.manual:
                precios_baremo = Baremo.objects.filter(convenio_id=dc.convenio_id, detalle_id = dc.detalle_id, grupo_id= dc.grupo_id, inactivar = False).first()
                resultado = calcular_precio(horasejecutadas,precios_baremo.convenio_id,precios_baremo.detalle_id,precios_baremo.grupo_id, dc.precio )
                precio_calculado = resultado['total_venta']
                horas = resultado['cantidad']
                DetalleCirugia.objects.filter(id=dc.id).update(
                    cantidad = horas,
                    precio = precio_calculado,
                )
            
        
        presupuesto = Presupuesto.objects.filter(id=cirugia.presupuesto_id).first()
        ntqxFacturable=NotaQuirurgica.objects.filter(cirugia_id=cirugia_id, incluir=True)
        existe_hospitalizacion = DetalleCirugia.objects.filter(cirugia_id = cirugia_id, detalle_id__in = ('32','33'))
        if existe_hospitalizacion:
            #ids_existentes = existe_hospitalizacion.values_list('detalle_id', flat=True)
            baremo = Baremo.objects.filter(convenio_id=cirugia.convenio_id, inactivar = False).exclude(detalle_id__in=['32','33']).order_by('detalle__posicion')
        else:
            baremo = Baremo.objects.filter(convenio_id=cirugia.convenio_id, inactivar = False).order_by('detalle__posicion')
            
            
        for nt in ntqxFacturable:
            DetalleCirugia.objects.filter(cirugia_id=cirugia_id,detalle_id = nt.participante_id).update(facturable=True,medico_id=nt.medico_id)
            DetallePresupuesto.objects.filter(presupuesto_id=presupuesto.id,detalle_id = nt.participante_id).update(medico_id=nt.medico_id)

        if dias_hospitalizacion == 0:
            dias_minimo = 1
        else:
            dias_minimo = dias_hospitalizacion

        DetalleCirugia.objects.filter(cirugia_id = cirugia_id, detalle_id = 33).update(cantidad = dias_minimo)
        #DetalleCirugia.objects.filter(cirugia_id = cirugia_id, detalle_id=32).update(cantidad = dias_hospitalizacion)
        
        
                 
        todo_consumo_hospitalizacion = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id,consumo_id=2, compuesto = '1')
        #total_venta_hospitalizacion = sum((Decimal(round(consumo.inventario.monto_venta,2))*Decimal(consumo.cantidad_real_usada)) for consumo in todo_consumo_hospitalizacion)
        total_venta_hospitalizacion = sum((Decimal(round(consumo.venta,2))) for consumo in todo_consumo_hospitalizacion)
        
        venta_hospitalizacion = total_venta_hospitalizacion
        if venta_hospitalizacion is None:
            venta_hospitalizacion=0
        
        consumo_farmacia_cirugia = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, inventario__categoria_id=1, consumo_id=1, compuesto = '1')
        #total_venta_farmacia=sum((Decimal(round(consumo.inventario.monto_venta,2))*Decimal(consumo.cantidad_real_usada)) for consumo in consumo_farmacia_cirugia)
        total_venta_farmacia=sum((Decimal(round(consumo.venta,2))) for consumo in consumo_farmacia_cirugia)
        
        consumo_mmq_cirugia = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, inventario__categoria_id=2,consumo_id=1, compuesto = '1')
        #total_venta_mmq=sum((Decimal(round(consumo.inventario.monto_venta,2))*Decimal(consumo.cantidad_real_usada)) for consumo in consumo_mmq_cirugia) 
        total_venta_mmq=sum((Decimal(round(consumo.venta,2))) for consumo in consumo_mmq_cirugia) 
        
        consumo_general_cirugia_mmq = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, inventario__categoria_id__in = [1,2] ,consumo_id=1, compuesto = '1')
        #total_venta_cirugia_mmq=sum((Decimal(round(consumo.inventario.monto_venta,2))*Decimal(consumo.cantidad_real_usada)) for consumo in consumo_general_cirugia_mmq)
        total_venta_cirugia_mmq=sum((Decimal(round(consumo.venta,2))) for consumo in consumo_general_cirugia_mmq)
        
        consumo_general_unidaddolor = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, compuesto__in = ['2','3'], consumo_id__in = [9,10])
        #total_venta_unidaddolor=sum((Decimal(round(consumo.inventario.monto_venta,2))*Decimal(consumo.cantidad_real_usada)) for consumo in consumo_general_unidaddolor)
        total_venta_unidaddolor=sum((Decimal(round(consumo.venta,2))) for consumo in consumo_general_unidaddolor)
        
        venta_farmacia = 0
        venta_mmq=0
        
        consumo_total_uci = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, consumo_id = 7, compuesto ='1')
        #total_venta_uci=sum((Decimal(round(uci.inventario.monto_venta,2))*Decimal(uci.cantidad_real_usada)) for uci in consumo_total_uci)
        total_venta_uci=sum((Decimal(round(uci.venta,2))) for uci in consumo_total_uci)
        
        consumo_total_preingreso = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, consumo_id = 8, compuesto ='1')
        #total_venta_preingreso=sum((Decimal(round(pre.inventario.monto_venta,2))*Decimal(pre.cantidad_real_usada)) for pre in consumo_total_preingreso)
        total_venta_preingreso=sum((Decimal(round(pre.venta,2))) for pre in consumo_total_preingreso)

        if total_venta_cirugia_mmq is not None:
            venta_cirugia_mmq = total_venta_cirugia_mmq
            
        if total_venta_farmacia is not None:
            venta_farmacia = total_venta_farmacia
            
        if total_venta_mmq is not None:
            venta_mmq=total_venta_mmq
            
        if total_venta_unidaddolor is not None:
            venta_unidaddolor=total_venta_unidaddolor
            
        
        presupuesto_id=cirugia.presupuesto_id
        DetallePresupuesto.objects.filter(presupuesto_id = presupuesto_id , detalle_id = 18).update(montoconsumo = venta_mmq)
        DetallePresupuesto.objects.filter(presupuesto_id = presupuesto_id , detalle_id = 19).update(montoconsumo = venta_farmacia) 
        DetallePresupuesto.objects.filter(presupuesto_id = presupuesto_id , detalle_id = 90).update(montoconsumo = venta_cirugia_mmq)
        DetallePresupuesto.objects.filter(presupuesto_id = presupuesto_id , detalle_id__in = [32,33]).update(montoconsumo = venta_hospitalizacion)
        DetallePresupuesto.objects.filter(presupuesto_id = presupuesto_id , detalle_id = 40).update(montoconsumo = venta_unidaddolor)
        DetallePresupuesto.objects.filter(presupuesto_id = presupuesto_id , detalle_id = 85).update(montoconsumo = total_venta_uci)
        DetallePresupuesto.objects.filter(presupuesto_id = presupuesto_id , detalle_id = 94).update(montoconsumo = total_venta_preingreso)
        
        
        DetalleCirugia.objects.filter(cirugia_id = cirugia_id , detalle_id = 90).update(
            montoconsumo = venta_cirugia_mmq,
            montotope =  F('precio')
            )
        
        DetalleCirugia.objects.filter(cirugia_id = cirugia_id , detalle_id = 18).update(
            montoconsumo = venta_mmq,
            montotope =  F('precio')
            )
        DetalleCirugia.objects.filter(cirugia_id = cirugia_id , detalle_id = 19).update(
            montoconsumo = venta_farmacia,
            montotope =  F('precio')
            ) 
        DetalleCirugia.objects.filter(cirugia_id = cirugia_id , detalle_id = 40).update(
            montoconsumo = venta_unidaddolor,
            montotope =  F('precio')
            ) 
        
        DetalleCirugia.objects.filter(cirugia_id = cirugia_id , detalle_id__in = [32,33]).update(montoconsumo = venta_hospitalizacion)
        """ DetalleCirugia.objects.filter(cirugia_id = cirugia_id , detalle_id = 32).update(montoconsumo = venta_hospitalizacion) """
        DetalleCirugia.objects.filter(cirugia_id = cirugia_id , detalle_id = 85).update(montoconsumo = total_venta_uci)
        DetalleCirugia.objects.filter(cirugia_id = cirugia_id , detalle_id = 94).update(montoconsumo = total_venta_preingreso)
        
        
        montodia_33 = Baremo.objects.filter(convenio_id = cirugia.convenio_id, detalle_id = 33 ).first()
        montodia_32 = Baremo.objects.filter(convenio_id = cirugia.convenio_id, detalle_id = 32 ).first()  
        montodia_94 = Baremo.objects.filter(convenio_id = cirugia.convenio_id, detalle_id = 94 ).first()
        
        montopordia=0  
        if montodia_94:
            montopordia = (montodia_94.topedia)
            baremo_precio = Baremo.objects.filter(detalle_id = 94, convenio_id = 1, inactivar = False).first()
            DetalleCirugia.objects.filter(cirugia_id = cirugia_id , detalle_id = 94).update(
                precio = baremo_precio.venta,
                montotope = montopordia)   
            
        if montodia_33:
            if dias_hospitalizacion == 0:
                hospital_dia = 1
            else:
                hospital_dia = dias_hospitalizacion
                
            montopordia = (montodia_33.topedia * hospital_dia)
            DetalleCirugia.objects.filter(cirugia_id = cirugia_id , detalle_id = 33).update(montotope = montopordia)
            
            
        if montodia_32:
            cantidad_ambulatorio = 1
            ambulatorio = DetalleCirugia.objects.filter(cirugia_id = cirugia_id , detalle_id = 32).first()
            if ambulatorio:
               cantidad_ambulatorio =  ambulatorio.cantidad
               
            montopordia = (montodia_32.topedia * cantidad_ambulatorio)
            DetalleCirugia.objects.filter(cirugia_id = cirugia_id , detalle_id = 32).update(montotope = montopordia)
            
            
        ajuste_en_presupuesto = DetalleCirugia.objects.filter(cirugia_id = cirugia_id)
        for ajuste in ajuste_en_presupuesto:
            precio_cirugia = ajuste.precio
            monto_excedente = 0
            if ajuste.montoconsumo > ajuste.montotope:
                precio_cirugia = ajuste.precio + (ajuste.montoconsumo - ajuste.montotope )
                monto_excedente =  ajuste.montotope - ajuste.montoconsumo
                
            medico_corte = NotaQuirurgica.objects.filter(participante_id = ajuste.detalle_id, cirugia_id = ajuste.cirugia_id).first()
            idMedico = None
            if medico_corte:
                idMedico = medico_corte.medico_id
                if not ajuste.pagado:
                    NotaQuirurgica.objects.filter(participante_id =  ajuste.detalle_id, medico_id = idMedico, cirugia_id = ajuste.cirugia_id).update(
                        montopendiente = ajuste.precio,
                        usuario_id = self.request.user.id
                    )
                
            if not ajuste.manual:  
                DetallePresupuesto.objects.filter(presupuesto_id = presupuesto.id, detalle_id = ajuste.detalle_id).update(
                    excedente =  monto_excedente,
                    precio_usado = precio_cirugia,
                    cantidad_usada = ajuste.cantidad,
                    precio_congelado_cirugia = precio_cirugia * presupuesto.cambio_congelado,
                    precio_congelado_presupuesto = F('precio') * presupuesto.cambio_congelado,
                    precio_congelado_excedente = monto_excedente * presupuesto.cambio_congelado,
                    medico_id = idMedico,
                )
            
            detalle_presupuesto_preingresos = DetallePresupuesto.objects.filter(presupuesto_id = presupuesto.id, preingreso_id__isnull = False)
             
            if detalle_presupuesto_preingresos:
                
                for detalle_presupuesto_preingreso in detalle_presupuesto_preingresos:
                    monto_causado_consumo_por_baremo =  detalle_presupuesto_preingreso.total_consumo_preingreso
                    if monto_causado_consumo_por_baremo > 0:
                        detalle_en_cirugia = DetalleCirugia.objects.filter(cirugia_id = cirugia_id, detalle_id = detalle_presupuesto_preingreso.detalle_id).first()
                        print('detalle_en_cirugia.precio', detalle_en_cirugia.precio)
                        precio_usado_cirugia = detalle_en_cirugia.precio
                        monto_tope_presupuesto = detalle_presupuesto_preingreso.montotope
                        monto_excedente =  monto_tope_presupuesto - monto_causado_consumo_por_baremo
                        if monto_excedente > 0:
                            monto_excedente = 0
                        
                        if not detalle_en_cirugia.manual:
                            DetallePresupuesto.objects.filter(id=detalle_presupuesto_preingreso.id).update(
                                excedente = monto_excedente,
                                precio_usado = precio_usado_cirugia + (monto_excedente*-1),
                                montoconsumo = monto_causado_consumo_por_baremo
                                )

                        """ detalle_warning =  DetallePresupuesto.objects.filter(id=detalle_presupuesto_preingreso.id).first()

                        if detalle_presupuesto_preingreso.detalle_id == 51:
                            print('detallepresupuesto_id',detalle_presupuesto_preingreso.id )
                            print('monto_excedente', monto_excedente )
                            print('precio_usado', detalle_warning.precio_usado ) """

                    
        
                
        detallepresupuesto = DetallePresupuesto.objects.filter(presupuesto_id=cirugia.presupuesto_id, cantidad__gt = 0).order_by('detalle__posicion')
        servicios_disponible = Baremo.objects.filter(grupo__nombre__icontains = 'servicio', inactivar = False).order_by('detalle__nombre')
        superUser = self.request.user.groups.filter(Q(name='SuperAdministracion')).exists()
        casosCerrados = self.request.user.groups.filter(Q(name='CasosCerrados')).exists()
        trasladoServicio = self.request.user.groups.filter(Q(name='TrasladoServicio')).exists()
        autorizacion = self.request.user.groups.filter(Q(name='AplicarDescuento')).exists()
        context['autorizacion'] = autorizacion
        context['superUser'] = superUser
        context['casosCerrados'] = casosCerrados
        context['trasladoServicio'] = trasladoServicio
        context['ntqxFacturable'] = ntqxFacturable 
        context['detallepresupuesto']=detallepresupuesto
        context['presupuesto']=presupuesto
        context['cirugia']=cirugia
        context['medicos']=medicos
        context['baremo']=baremo
        context['servicios_disponible']=servicios_disponible
        
        
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)  
        cirugia_id = self.kwargs['cirugia_id']
        
        if 'cambiar_Horas' in request.POST:
            horasejecutadas = request.POST['hr_facturable']
            Cirugia.objects.filter(id=cirugia_id).update(horas_qx_facturable = horasejecutadas)
        else:
            pass
            

        return redirect('cortecuenta',cirugia_id = cirugia_id )    
##########
@add_group_name_to_context    
class medico_edocta(UserPassesTestMixin , TemplateView):
    template_name='medico_edocta.html' 

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #medico = Medico.objects.filter(grupo='M').order_by('nombre')
        TempFecha.objects.all().delete()
        medicos = Medico.objects.filter(grupo='M').exclude(tipopersonal_id = 9).order_by('nombre')
        total_general_pendiente = 0
        for medico in medicos:
            # Total facturado: suma de precios de detallecirugia del médico
            """ medico.total_facturado = medico.detallecirugia_set.aggregate(
                total=Sum('precio', filter=Q(pagado=1))
            )['total'] or 0 """
            medico.total_facturado = medico.notaquirurgica_set.aggregate(
                total=Sum('montopendiente')
            )['total'] or 0

            medico.participaciones = medico.detallecirugia_set.count()

            # Total pendiente: suma de montopendiente de notaquirurgica donde pagado=False
            medico.total_pagado = medico.notaquirurgica_set.filter(pagado=True).aggregate(
                total=Sum('montopendiente')
            )['total'] or 0

            medico.total_pendiente = medico.total_facturado - medico.total_pagado
            total_general_pendiente += medico.total_pendiente


        
        #total_pendiente = mediconotaqx.aggregate(total_pendiente=Sum('monto_pendiente_total'))
        superUser = self.request.user.groups.filter(Q(name='SuperAdministracion')).exists()

        context['superUser'] = superUser
        context['mediconotaqx'] = medicos
        context['total_general_pendiente'] = total_general_pendiente

        #context['total_pendiente'] = total_pendiente['total_pendiente']
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)  
        medico_id = request.POST['cod-medico']
        print('id', medico_id )
            

        return redirect('medico_edocta_detalle',medico_id = medico_id )

    
    
        
@add_group_name_to_context    
class medico_edocta_detalle(TemplateView):
    template_name='medico_edocta_detalle.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medico_id = self.kwargs['medico_id']
        medico = Medico.objects.filter(id=medico_id).first()
        fechas_filtro = TempFecha.objects.first()
        if fechas_filtro:
            medicoennotaqx = NotaQuirurgica.objects.filter(medico_id=medico_id, pagado=False,  cirugia__fecha_procedimiento__range=[fechas_filtro.fecha_desde, fechas_filtro.fecha_hasta]).order_by('cirugia_id')
        else:
            medicoennotaqx = NotaQuirurgica.objects.filter(medico_id=medico_id, pagado=False).exclude(Q(montopendiente=0) & Q(cirugia_id__isnull=False)).order_by('cirugia_id')

            
        total_pendiente = medicoennotaqx.aggregate(total_pendiente=Sum('montopendiente'))
        FacturaProveedor.objects.filter(tipo = 'FM', numerodocumento__isnull=True ).delete()
        for nota in medicoennotaqx:
            cirugia_id = nota.cirugia_id
            atencion_inmediata_id = nota.atencion_inmediata_id
            monto_cobrado_cirugia = 0
            monto_total_cirugia = 0
            moneda_pago = 'Ninguna'
            if cirugia_id:
                cuentacobrar = CuentaxCobrar.objects.filter(cirugia_id=cirugia_id).first()
                if cuentacobrar:
                    cobrado = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id, montocobrar__lt=0)
                    totalcirugia = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id, montocobrar__gt=0)
                    
                    if cobrado.exists():  # Verificamos si hay resultados
                        tipos_destino_pago = cobrado.values('destino_pago__moneda_id').distinct().count()
                        if tipos_destino_pago > 1:
                            moneda_pago = 'Mixta'

                        if tipos_destino_pago == 1:
                            moneda = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id, montocobrar__lt=0).first()
                            if moneda.destino_pago:
                                moneda_pago = moneda.destino_pago.moneda

                        monto_cobrado_cirugia = cobrado.aggregate(total=Sum('montocobrar'))['total'] or 0  # Usamos or 0 para manejar None
                    
                    if totalcirugia:
                        monto_total_cirugia = totalcirugia.aggregate(total=Sum('montocobrar'))['total'] or 0  # Usamos or 0 para manejar None
            else:
                cuentacobrar = CuentaxCobrar.objects.filter(atencion_inmediata_id=atencion_inmediata_id).first()
                if cuentacobrar:
                    cobrado = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id, montocobrar__lt=0)
                    totalcirugia = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id, montocobrar__gt=0)
                    
                    if cobrado.exists():  # Verificamos si hay resultados
                        tipos_destino_pago = cobrado.values('destino_pago__moneda_id').distinct().count()
                        if tipos_destino_pago > 1:
                            moneda_pago = 'Mixta'

                        if tipos_destino_pago == 1:
                            moneda = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id, montocobrar__lt=0).first()
                            moneda_pago = moneda.destino_pago.moneda

                        monto_cobrado_cirugia = cobrado.aggregate(total=Sum('montocobrar'))['total'] or 0  # Usamos or 0 para manejar None
                    
                    if totalcirugia:
                        monto_total_cirugia = totalcirugia.aggregate(total=Sum('montocobrar'))['total'] or 0  # Usamos or 0 para manejar None
                
                

            # Añadimos el monto_cobrado_cirugia como un nuevo atributo al objeto nota
            nota.monto_cobrado_cirugia = (monto_cobrado_cirugia * -1)
            nota.monto_total_cirugia = monto_total_cirugia
            nota.moneda_pago = moneda_pago
            nota.cuentacobrar_id = cuentacobrar.id

        
        context['medico'] = medico
        #context['cirugias'] = cirugias
        context['medicoennotaqx'] = medicoennotaqx
        context['total_pendiente'] = total_pendiente['total_pendiente']

        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)  
        medico_id = self.kwargs['medico_id']  
        #entregado = request.POST['medico_entrega']
        selected_cirugias = request.POST.getlist('selected_cirugias')
        cambio_congelado = CambioDiaBcv(datetime.now())
        montos_modificados = {}
        concepto_porcentaje = Retencion.objects.filter(id = 3).first()
        if concepto_porcentaje:
            porcentaje_islr = concepto_porcentaje.natural 
        else:
            porcentaje_islr = 0


        if selected_cirugias:
            facturaautomatica = FacturaProveedor.objects.create(
                    proveedor_id = medico_id,
                    tipodocumento_id = 5,
                    concepto_id = 3,
                    administrativo = 0,
                    fecha_entrega = datetime.now(),
                    tipo = 'FM',
                    usuario_id = self.request.user.id,
                    cambio_congelado = cambio_congelado,
                    fecha_cambio = datetime.now(),
                    porcentaje_retencion_islr = porcentaje_islr

                )
            factura_id = facturaautomatica.id
             
        total_pago_cirugias = 0
        for ids in selected_cirugias:
                monto_modificado = request.POST.get(f'montomodificado_{ids}').replace(',','.')  # Obtiene el monto modificado para cada ID
                if float(monto_modificado) == 0:
                    itemnotaqx = NotaQuirurgica.objects.filter(id=ids).update(
                        pagado = True,
                        pagoeliminado = True,
                        notaeliminacion = 'Pago eliminado por usuario:'+str(self.request.user.username)
                    )
                    return redirect('medico_edocta_detalle', medico_id = medico_id)



                cambio_congelado=CambioDiaBcv(datetime.now())
                itemnotaqx = NotaQuirurgica.objects.filter(id=ids).first()

                congelar_moneda = False
                if itemnotaqx.cirugia_id:
                    if itemnotaqx.cirugia.congelar_moneda:
                        cambio_congelado = itemnotaqx.cirugia.cambio_congelado
                        congelar_moneda = True

                    monto_cirugia = itemnotaqx.montopendiente
                    precio_bs = monto_cirugia * cambio_congelado 
                    descripcion_pago = 'Honorarios a terceros Cirugia:'+str(itemnotaqx.cirugia_id)+ ' Procedimiento:'+str(itemnotaqx.cirugia.nombre_procedimiento)+' Funcion:'+str(itemnotaqx.participante)+' H.Qx:'+str(itemnotaqx.cirugia.horas_qx)
                    DetalleFacturaProveedor.objects.create(
                        cantidad = 1,
                        precio_unitario = monto_cirugia,
                        precio_modificado = itemnotaqx.montopendiente,
                        gastos = monto_cirugia * Decimal('0.00'),
                        gastos_bs = precio_bs * Decimal('0.00'),
                        factura_id = factura_id,
                        descripcion = descripcion_pago[:450],
                        cirugia_id = itemnotaqx.cirugia_id,
                        detalle_id = itemnotaqx.participante_id, 
                        congelar_moneda = congelar_moneda,
                        cambio_bcv = cambio_congelado,
                        precio_bs = precio_bs,
                        subtotal_bs = 1 * precio_bs
                    )
                        
        
        if selected_cirugias:
            return redirect('factura_automatica_medico', factura_id = factura_id )
        else:
            facturaautomatica = FacturaProveedor.objects.create(
                    proveedor_id = medico_id,
                    tipodocumento_id = 5,
                    concepto_id = 3,
                    administrativo = 0,
                    fecha_entrega = datetime.now(),
                    tipo = 'FM',
                    usuario_id = self.request.user.id,
                    cambio_congelado = cambio_congelado,
                    fecha_cambio = datetime.now(),
                    tipomoneda_id = 2,
                    porcentaje_retencion_islr = porcentaje_islr
                )
            factura_id = facturaautomatica.id 
            print('crear nueva factura id ',factura_id )
            return redirect('factura_automatica_medico', factura_id = factura_id )


@add_group_name_to_context    
class factura_automatica_medico(TemplateView): 
    template_name='factura_automatica_medico.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        factura_id = self.kwargs['factura_id']
        factura = FacturaProveedor.objects.filter(id = factura_id, tipo = 'FM').first()

        distribucion = DistribucionPagoMedico.objects.filter(factura_id = factura.id).order_by('id')
        nuevo_registro = DistribucionPagoMedico.objects.filter(factura_id = factura.id, monto = 0).exists()
        if not nuevo_registro and Decimal(factura.saldo_dl_distribucion_pago) > 0.01:
            DistribucionPagoMedico.objects.create(
            factura_id = factura.id,
            monto = 0,
            usuario_id = self.request.user.id
            ) 


        cambio_hoy=CambioDiaBcv(datetime.now())
        retencionpendiente = RetencionPendiente.objects.filter(medico_id = factura.proveedor_id, aplicado = False)
        
        DetalleFacturaProveedor.objects.filter(factura_id=factura_id, precio_unitario__lt = 0).delete()
        baseimponible_bs = 0
        baseimponible_usd = 0
        if retencionpendiente:
            baseimponible_bs = retencionpendiente.aggregate(total_bs=Sum('baseimponible'))['total_bs']
            baseimponible_usd = retencionpendiente.aggregate(total_usd=Sum('baseimponible_usd'))['total_usd']
            
        total_baseimponible=0
        facturadetalle = DetalleFacturaProveedor.objects.filter(factura_id=factura_id, precio_unitario__gt = 0).order_by('id')
        if facturadetalle:
            baseimponibleactual = facturadetalle.aggregate(baseimponible=Sum(F('precio_bs')*F('cantidad')))['baseimponible']
            gastos = facturadetalle.aggregate(totalgastos=Sum('gastos_bs'))['totalgastos']
            total_baseimponible = baseimponible_bs + (baseimponibleactual-gastos)
        
        resultado = montoaretener(total_baseimponible, 'N',factura.concepto_id )
        monto_retencion = resultado['monto_retener']
        sustraendo = resultado['sustraendo']
        porcentaje_retencion_islr = resultado['porcentaje']
        neto_retener = monto_retencion - sustraendo 

        if factura.tipodocumento_id in [1, 5]:
            FacturaProveedor.objects.filter(id = factura_id, tipo = 'FM').update(
                porcentaje_retencion_islr = porcentaje_retencion_islr,
                sustraendo_bs = sustraendo
            )
        else:
            FacturaProveedor.objects.filter(id = factura_id, tipo = 'FM').update(
                porcentaje_retencion_islr = 0,
                sustraendo_bs = 0
            )

        factura = FacturaProveedor.objects.filter(id = factura_id, tipo = 'FM').first()

        bancolocal = BancoLocal.objects.filter(activo = True).order_by('banco') 
        moneda_congelada = DetalleFacturaProveedor.objects.filter(factura_id=factura_id, congelar_moneda = True).count()
        facturadetalle = DetalleFacturaProveedor.objects.filter(factura_id=factura_id).order_by('id')
        if facturadetalle:
            total_gastos = facturadetalle.aggregate(total_gastos=Sum('gastos'))
            total_gastos_bs = facturadetalle.aggregate(total_gastos_bs=Sum('gastos_bs'))
            total_factura = facturadetalle.aggregate(total_factura=Sum(F('precio_unitario')*F('cantidad')))
            total_factura_bs = facturadetalle.aggregate(total_factura_bs=Sum(F('precio_bs')*F('cantidad')))
            total_gastos = total_gastos['total_gastos']
            total_gastos_bs = total_gastos_bs['total_gastos_bs']
            total_factura = total_factura['total_factura']
            total_factura_bs = total_factura_bs['total_factura_bs']
        else:
            total_gastos = 0
            total_gastos_bs = 0
            total_factura = 0
            total_factura_bs = 0

        proveedores = Medico.objects.filter(grupo='M').exclude(tipopersonal_id = 9).order_by('nombre')
        moneda = Moneda.objects.all()
        retenciones = Retencion.objects.all().order_by('nombre')
        tipodocumento = TipoDocumento.objects.filter(activo_factura_medico = True).order_by('nombre')
        retencion = Retencion.objects.filter(id=factura.concepto_id).first()
        if moneda_congelada > 0:
            pagomedico = PagoMedico.objects.filter(medico_id=factura.proveedor,moneda_id = 2 ).order_by('nombre')
        else:
            pagomedico = PagoMedico.objects.filter(medico_id=factura.proveedor).order_by('nombre')
            
        ##
        gastos = factura.administrativo
        tasa_bcv_calculo = CambioDiaBcv(datetime.now())
        if factura.congelar_moneda:
                tasa_bcv_calculo = factura.cambio_congelado
        
        
        pretencion=0
        montoretencion = 0
        fecha_hoy = datetime.now().date()
        formapago = FormaPago.objects.all().order_by('nombre')
        bancos = Banco.objects.all().order_by('nombre')

        registro_documento_factura = FacturaMedico.objects.filter(factura_id = factura.id, medico_id = factura.proveedor_id ).first()
        comprobante_retencion = 0
        if registro_documento_factura:
            if registro_documento_factura.comprobante:
                comprobante_retencion = 1

        monto_total_pagado = monto_correcto_a_pagar_con_retencion_aplicada = 0
        montoretencion_retencion_islr = factura.retencion_islr_monto_bs
        if montoretencion_retencion_islr < 0:
            montoretencion_retencion_islr = montoretencion_retencion_islr * -1
        
        total_monto_recibos = factura.total_pagos_recibos_bs

        if total_monto_recibos < 0:
            total_monto_recibos = total_monto_recibos * -1
            
        monto_total_pagado = total_monto_recibos + factura.total_transacciones_bs
        monto_correcto_a_pagar_con_retencion_aplicada = monto_total_pagado - montoretencion_retencion_islr
        nota_credito_favor_clinica = monto_correcto_a_pagar_con_retencion_aplicada - monto_total_pagado
        

        pagos_realizados = Transaccion.objects.filter(cuentapagar_id = factura.id).order_by('fecha_act')
        if not pagos_realizados:
            facturas_recibo_ids = PagoReciboFacturaMedico.objects.filter(
                factura_legal_id=factura.id
            ).values_list('factura_recibo_id', flat=True)
            pagos_realizados = Transaccion.objects.filter(cuentapagar_id__in=facturas_recibo_ids).order_by('fecha_act')

        baremoterceros = BaremoPagoTercero.objects.all().order_by('nombre')
        
        context['moneda'] = moneda
        context['bancos'] = bancos
        context['baremoterceros'] = baremoterceros
        context['bancolocal'] = bancolocal
        context['formapago'] = formapago
        context['factura'] = factura
        context['gastosadm'] = total_gastos
        context['fecha_hoy'] = fecha_hoy
        context['total_gastos_bs'] = total_gastos_bs
        context['tasa_bcv_calculo'] = tasa_bcv_calculo
        context['proveedores'] = proveedores
        context['pagomedico'] = pagomedico
        context['pretencion'] = pretencion
        context['distribucion'] = distribucion
        context['retenciones'] = retenciones
        context['tipodocumento'] = tipodocumento
        context['neto_pagar'] = total_factura - total_gastos
        context['neto_pagar_bolivar'] = total_factura_bs - total_gastos_bs
        context['montoretencion'] = montoretencion
        context['facturadetalle'] = facturadetalle
        context['moneda_congelada'] = moneda_congelada
        context['pagos_realizados'] = pagos_realizados
        context['comprobante_retencion'] = comprobante_retencion
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)  
        factura_id = self.kwargs['factura_id'] 
        factura = FacturaProveedor.objects.filter(id = factura_id).first()
        if 'guardar_prefactura' in request.POST:
            nrodocumento = request.POST['nrodocumento']
            nrocontrol = request.POST['nrocontrol']
            tipodocumento = request.POST['tipodocumento'] 
            fechaentrega = request.POST['fechaentrega']
            tasa_pago = float(request.POST['tasa_pago'])

            FacturaProveedor.objects.filter(id=factura_id).update(
                numerodocumento= nrodocumento,
                numerocontrol= nrocontrol,
                tipodocumento_id = tipodocumento,
                fecha_entrega = fechaentrega,
                usuario_id = self.request.user.id,
                cambio_congelado = float(tasa_pago),
                tipo = 'FM'
            )

            factura_medico =  FacturaMedico.objects.filter(factura_id = factura_id, medico_id = factura.proveedor_id ).first()
            if not factura_medico:
                FacturaMedico.objects.create(
                    fecha_entrega = fechaentrega,
                    numerodocumento= nrodocumento,
                    numerocontrol= nrocontrol,
                    medico_id = factura.proveedor_id,
                    usuario_id = self.request.user.id,
                    factura_id = factura.id
                )
            else:
                FacturaMedico.objects.filter(factura_id = factura_id, medico_id = factura.proveedor_id ).update(
                    fecha_entrega = fechaentrega,
                    numerodocumento= nrodocumento,
                    numerocontrol= nrocontrol,
                    medico_id = factura.proveedor_id,
                    usuario_id = self.request.user.id,
                    factura_id = factura.id 
                )

            
            cirugiaspagadas = DetalleFacturaProveedor.objects.filter(factura_id=factura_id, precio_unitario__gt = 0)
            for cirpag in cirugiaspagadas:
                NotaQuirurgica.objects.filter(cirugia_id=cirpag.cirugia_id, participante_id=cirpag.detalle_id, medico_id = cirpag.factura.proveedor_id).update(
                    pagado=True,
                    usuario_id = self.request.user.id,
                )


        
        return redirect('lista_factura_pagada')

def agregar_medico(request):
    if request.method == 'POST':
        form = MedicoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listado_medico')
    else:
        form = MedicoForm()
        
    return render(request, 'medico_new.html', {'form': form})

def agregar_enfermeria(request):
    if request.method == 'POST':
        form = MedicoForm(request.POST)
        if form.is_valid():
            medico = form.save(commit=False)  # No guarda todavía
            medico.grupo = 'E'
            form.save()
            return redirect('listado_enfermeria')
    else:
        form = MedicoForm()
        
    return render(request, 'enfermeria_new.html', {'form': form})

def agregar_grupomedico(request):
    if request.method == 'POST':
        form = GrupoMedicoForm(request.POST)
        if form.is_valid():
            medico = form.save(commit=False)  # No guarda todavía
            medico.grupo = 'G'
            form.save()
            return redirect('listado_grupo_medico')
        else:
            print('Formulario no válido')
            print('Errores por campo:')
            for field, errors in form.errors.items():
                print(f"- Campo: {field}")
                for error in errors:
                    print(f"  Error: {error}")

            print('Errores no asociados a un campo específico:')
            print(form.non_field_errors())
    else:
        form = GrupoMedicoForm()
        
    return render(request, 'grupomedico_new.html', {'form': form})

def agregar_segurootro(request):
    if request.method == 'POST':
        form = SegurosForm(request.POST)
        if form.is_valid():
            medico = form.save(commit=False)  # No guarda todavía
            medico.grupo = 'S'
            form.save()
            return redirect('listado_seguro_otro')
        else:
            print('Formulario no válido')
            print('Errores por campo:')
            for field, errors in form.errors.items():
                print(f"- Campo: {field}")
                for error in errors:
                    print(f"  Error: {error}")

            print('Errores no asociados a un campo específico:')
            print(form.non_field_errors())
    else:
        form = SegurosForm()
        
    return render(request, 'segurootro_new.html', {'form': form})


@add_group_name_to_context    
class conciliar_farmacia(TemplateView):
    template_name='conciliar_farmacia.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['pk']
        medicos = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        fecha_hoy = datetime.now()
        cirugias = Cirugia.objects.filter(id=cirugia_id).first()
        consumo = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, farmacia=False, conciliada=False, consumo_id__in = [1,10]).order_by('inventario__nombre')
        total_cantidad_entregada = 0
        total_real_usado=0
        if consumo:
            total_cantidad_entregada = consumo.aggregate(Sum('cantidad_uso'))['cantidad_uso__sum']
            total_real_usado = consumo.aggregate(Sum('cantidad_real_usada'))['cantidad_real_usada__sum']
            
            
        inventarios = Inventario.objects.all().order_by('nombre')
        total_devolucion = total_cantidad_entregada - total_real_usado
        context['medicos'] = medicos
        context['consumo'] = consumo
        context['cirugias'] = cirugias
        context['fecha_hoy'] = fecha_hoy
        context['inventarios'] = inventarios
        context['total_devolucion'] = total_devolucion
        context['total_cantidad_entregada'] = total_cantidad_entregada
        return context
    
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)  
        cirugia_id = self.kwargs['pk']  
        
        consumos = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, conciliada = False, consumo_id__in = [1,10], cantidad_real_usada__gt = 0)
        for consumo in consumos:
            cantidad_rebajar = consumo.cantidad_real_usada
            inventario_id = consumo.inventario_id
            inventario = Inventario.objects.filter(id=inventario_id).first()
            monto_venta = 0
            if inventario:
                monto_venta = inventario.monto_venta
                
            if cantidad_rebajar > 0:
                ConsumoCirugia.objects.filter(id = consumo.id ).update(
                    cantidad_uso = consumo.cantidad_real_usada,
                    venta =  Decimal(consumo.cantidad_real_usada) * Decimal(monto_venta),
                    conciliada = True
                )
                

                InventarioDescarga.objects.filter(consumocirugia_id = consumo.id).update(
                    cantidad = consumo.cantidad_real_usada,
                    nota = 'CONCILIACION DE CONSUMO EN CIRUGIA',
                    usuario_id = self.request.user.id
                )
                
                DetalleConsumoCirugia.objects.create(
                        cantidad_uso = consumo.cantidad_real_usada,
                        precio_unitario = monto_venta,
                        hora = datetime.now().time(),
                        consumocirugia_id = consumo.id,
                        inventario_id = inventario_id,
                        usuario_cirugia_id = request.user.id,
                        usuario_farmacia_id = request.user.id,
                        nota = 'Conciliado en Farmacia'
                        
                    )
                
        ConsumoCirugia.objects.filter(cirugia_id=cirugia_id, cantidad_real_usada = 0).delete()
                 

        return redirect('listado_cirugia_farmacia')
        

    
@csrf_exempt
def guardar_conciliacion(request):
    if request.method == "POST":
        data = json.loads(request.body)
        for row in data:
            id_consumo=row["id"]
            cantidad_usada=row["cantidad_usada"]
            diferencia=row["diferencia"]
            ConsumoCirugia.objects.filter(id=id_consumo).update(
                cantidad_real_usada = cantidad_usada,
                diferencia = diferencia,
                usuario_id = request.user.id
            )
            
            # Crea una nueva instancia de tu modelo para cada fila
        return JsonResponse({"mensaje": "Datos guardados con éxito"})
    return JsonResponse({"mensaje": "Solicitud inválida"})



@add_group_name_to_context    
class listado_medico(TemplateView):
    template_name='listado_medico.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medicos = Medico.objects.filter(grupo = 'M' ).order_by('nombre')
        context['medicos'] = medicos
        return context

@add_group_name_to_context    
class listado_enfermeria(TemplateView):
    template_name='listado_enfermeria.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medicos = Medico.objects.filter(grupo = 'E' ).order_by('nombre')
        context['medicos'] = medicos
        return context

@add_group_name_to_context    
class listado_grupo_medico(TemplateView):
    template_name='listado_grupo_medico.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medicos = Medico.objects.filter(grupo = 'G' ).order_by('nombre')
        context['medicos'] = medicos
        return context

@add_group_name_to_context    
class listado_seguro_otro(TemplateView):
    template_name='listado_seguro_otro.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medicos = Medico.objects.filter(grupo = 'S' ).order_by('nombre')
        context['medicos'] = medicos
        return context
    
    
@add_group_name_to_context   
class MedicoEditView(UpdateView):
    model = Medico
    form_class = MedicoForm
    template_name = 'medico_edit.html'
    success_url = reverse_lazy('listado_medico')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medico_id=self.object.id
        pagomedico = PagoMedico.objects.filter(medico_id=medico_id).order_by('-id')
        forma_pago_options = FormaPago.objects.all().order_by('nombre')
        bancos = Banco.objects.all().order_by('nombre')
        monedas = Moneda.objects.all()
        context['bancos'] = bancos
        context['monedas'] = monedas
        context['pagomedico'] = pagomedico
        context['forma_pago_options'] = forma_pago_options
        return context
    
    def form_valid(self, form):
        medico_id=self.object.id
        if 'guardar_medico' in self.request.POST:
        # Guardar button was pressed
            messages.success(self.request, 'El Personal se ha actualizado correctamente')
        elif 'guardar_pago' in self.request.POST:
            nombre_para_pago = self.request.POST.get('nombre_para_pago')
            numerocuenta = self.request.POST.get('numerocuenta')
            numeropago = self.request.POST.get('numeropago')
            formapago = self.request.POST.get('formapago')
            correo_pago = self.request.POST.get('correo_pago')
            cedulapago = self.request.POST.get('cedula_pago')
            bancopago = self.request.POST.get('banco') 
            moneda = self.request.POST.get('moneda')
            mediopagomedico = PagoMedico.objects.filter(
                medico_id = medico_id,
                numerocuenta = numerocuenta,
                moneda_id = moneda,
                formapago_id = formapago,
            )

            if mediopagomedico:
                messages.error(self.request, 'Ya existe ese medio de pago!')
                return self.render_to_response(self.get_context_data(form=form))

            PagoMedico.objects.create(
                medico_id = medico_id,
                nombre = nombre_para_pago,
                numerocuenta = numerocuenta,
                numeropago = numeropago,
                correo = correo_pago,
                formapago_id = formapago,
                cedulapago = cedulapago,
                bancopago_id = bancopago,
                moneda_id = moneda
            )
            # Agregar button was pressed
            #messages.success(self.request, 'Pago agregado correctamente')
            return self.render_to_response(self.get_context_data(form=form))
        
        
        form.save()
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar el Personal revise campos')
        return self.render_to_response(self.get_context_data(form=form))
    

@add_group_name_to_context   
class EnfermeriaEditView(UpdateView):
    model = Medico
    form_class = MedicoForm
    template_name = 'edit_enfermeria.html'
    success_url = reverse_lazy('listado_enfermeria')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medico_id=self.object.id
        pagomedico = PagoMedico.objects.filter(medico_id=medico_id).order_by('-id')
        forma_pago_options = FormaPago.objects.all().order_by('nombre')
        bancos = Banco.objects.all().order_by('nombre')
        monedas = Moneda.objects.all()
        context['bancos'] = bancos
        context['monedas'] = monedas
        context['pagomedico'] = pagomedico
        context['forma_pago_options'] = forma_pago_options
        return context
    
    def form_valid(self, form):
        medico_id=self.object.id
        if 'guardar_medico' in self.request.POST:
        # Guardar button was pressed
            messages.success(self.request, 'El Personal se ha actualizado correctamente')
        elif 'guardar_pago' in self.request.POST:
            nombre_para_pago = self.request.POST.get('nombre_para_pago')
            numerocuenta = self.request.POST.get('numerocuenta')
            numeropago = self.request.POST.get('numeropago')
            formapago = self.request.POST.get('formapago')
            correo_pago = self.request.POST.get('correo_pago')
            cedulapago = self.request.POST.get('cedula_pago')
            bancopago = self.request.POST.get('banco') 
            moneda = self.request.POST.get('moneda')
            PagoMedico.objects.create(
                medico_id = medico_id,
                nombre = nombre_para_pago,
                numerocuenta = numerocuenta,
                numeropago = numeropago,
                correo = correo_pago,
                formapago_id = formapago,
                cedulapago = cedulapago,
                bancopago_id = bancopago,
                moneda_id = moneda
                
            )
            # Agregar button was pressed
            #messages.success(self.request, 'Pago agregado correctamente')
            return self.render_to_response(self.get_context_data(form=form))
        
        
        form.save()
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar el Personal revise campos')
        return self.render_to_response(self.get_context_data(form=form))
    
@add_group_name_to_context   
class GrupomedicoEditView(UpdateView):
    model = Medico
    form_class = GrupoMedicoForm
    template_name = 'edit_grupomedico.html'
    success_url = reverse_lazy('listado_grupo_medico')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medico_id=self.object.id
        pagomedico = PagoMedico.objects.filter(medico_id=medico_id).order_by('-id')
        forma_pago_options = FormaPago.objects.all().order_by('nombre')
        bancos = Banco.objects.all().order_by('nombre')
        monedas = Moneda.objects.all()
        context['bancos'] = bancos
        context['monedas'] = monedas
        context['pagomedico'] = pagomedico
        context['forma_pago_options'] = forma_pago_options
        return context
    
    def form_valid(self, form):
        medico_id=self.object.id
        if 'guardar_medico' in self.request.POST:
        # Guardar button was pressed
            messages.success(self.request, 'El Personal se ha actualizado correctamente')
        elif 'guardar_pago' in self.request.POST:
            nombre_para_pago = self.request.POST.get('nombre_para_pago')
            numerocuenta = self.request.POST.get('numerocuenta')
            numeropago = self.request.POST.get('numeropago')
            formapago = self.request.POST.get('formapago')
            correo_pago = self.request.POST.get('correo_pago')
            cedulapago = self.request.POST.get('cedula_pago')
            bancopago = self.request.POST.get('banco') 
            moneda = self.request.POST.get('moneda')
            PagoMedico.objects.create(
                medico_id = medico_id,
                nombre = nombre_para_pago,
                numerocuenta = numerocuenta,
                numeropago = numeropago,
                correo = correo_pago,
                formapago_id = formapago,
                cedulapago = cedulapago,
                bancopago_id = bancopago,
                moneda_id = moneda
                
            )
            # Agregar button was pressed
            #messages.success(self.request, 'Pago agregado correctamente')
            return self.render_to_response(self.get_context_data(form=form))
        
        
        form.save()
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar el Personal revise campos')
        return self.render_to_response(self.get_context_data(form=form))

@add_group_name_to_context   
class SeguroEditView(UpdateView):
    model = Medico
    form_class = SegurosForm
    template_name = 'edit_segurootro.html'
    success_url = reverse_lazy('listado_seguro_otro')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medico_id=self.object.id
        pagomedico = PagoMedico.objects.filter(medico_id=medico_id).order_by('-id')
        forma_pago_options = FormaPago.objects.all().order_by('nombre')
        bancos = Banco.objects.all().order_by('nombre')
        monedas = Moneda.objects.all()
        context['bancos'] = bancos
        context['monedas'] = monedas
        context['pagomedico'] = pagomedico
        context['forma_pago_options'] = forma_pago_options
        return context
    
    def form_valid(self, form):
        medico_id=self.object.id
        if 'guardar_medico' in self.request.POST:
        # Guardar button was pressed
            messages.success(self.request, 'El Personal se ha actualizado correctamente')
        elif 'guardar_pago' in self.request.POST:
            nombre_para_pago = self.request.POST.get('nombre_para_pago')
            numerocuenta = self.request.POST.get('numerocuenta')
            numeropago = self.request.POST.get('numeropago')
            formapago = self.request.POST.get('formapago')
            correo_pago = self.request.POST.get('correo_pago')
            cedulapago = self.request.POST.get('cedula_pago')
            bancopago = self.request.POST.get('banco') 
            moneda = self.request.POST.get('moneda')
            PagoMedico.objects.create(
                medico_id = medico_id,
                nombre = nombre_para_pago,
                numerocuenta = numerocuenta,
                numeropago = numeropago,
                correo = correo_pago,
                formapago_id = formapago,
                cedulapago = cedulapago,
                bancopago_id = bancopago,
                moneda_id = moneda
                
            )
            # Agregar button was pressed
            #messages.success(self.request, 'Pago agregado correctamente')
            return self.render_to_response(self.get_context_data(form=form))
        
        
        form.save()
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar el Personal revise campos')
        return self.render_to_response(self.get_context_data(form=form))
    
    
def guardar_consumo_cantidad_real(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nCant = datos['nCant']
        idConsumo = datos['idConsumo']
        consumo = ConsumoCirugia.objects.filter(id=idConsumo).first()
        if (Decimal(consumo.cantidad_real_usada)+Decimal(nCant)) > Decimal(consumo.cantidad_uso):
            return JsonResponse({'mensaje': 'MAYOR A LO DISPONIBLE'})
        else:
            consumofarmacia = ConsumoCirugia.objects.filter(id=idConsumo).first()
            precio_costo_unitario = precio_costo_producto_inventario(consumo.inventario_id)
            ConsumoCirugia.objects.filter(id=idConsumo).update(
                cantidad_real_usada = F('cantidad_real_usada') + nCant,
                venta =  F('cantidad_real_usada') *  F('precio_unitario'),
                hora_uso = datetime.now(),
                precio_costo_unitario = precio_costo_unitario
            )
            
            DetalleConsumoCirugia.objects.create(
                    consumocirugia_id=idConsumo,
                    precio_unitario = consumo.precio_unitario * int(nCant) ,
                    cantidad_uso = nCant,
                    hora = datetime.now(),
                    inventario_id = consumo.inventario_id,
                    usuario_cirugia_id = request.user.id,
                    usuario_farmacia_id = consumofarmacia.usuario_id,

            )
        
        
        return JsonResponse({'mensaje': 'CANTIDAD REAL GUARDADOS EN CONSUMO correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al GUARDAR CANTIDAD REAL EN CONSUMO datos'})
    

def congelar_cambio(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        cambio_congelado = datos['cambio_congelado']
        presupuestoId = datos['presupuestoId']
        Presupuesto.objects.filter(id=presupuestoId).update(
            congelar_moneda = cambio_congelado,
        )
        
        return JsonResponse({'mensaje': 'CAMBIO CONGELADO correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error CAMBIO CONGELADO datos'})
    
    
def guardar_detalle_factura(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idFactura = datos['idFactura']
        cantidad = datos['cantidad']
        descripcion = datos['descripcion']
        id_moneda = datos['id_moneda_pago']
        producto_id = datos['producto_id']
        precio = datos['precio']
        iva = datos['iva']
        guardar = datos['guardar']
        gastos = datos['gastos'].replace(',','.')
        gastos = Decimal(gastos) / Decimal('100.00')
        cantidad = Decimal(cantidad)
        precio = Decimal(precio)
        iva = iva.replace(',','.')
        
            
        factura = FacturaProveedor.objects.filter(id = idFactura).first()
        
        if factura:
            cambioTx = factura.cambio_congelado
            if int(id_moneda) == 1:
                precio_dl = precio
                subtotal_dl = precio_dl * cantidad
                gasto_dl = subtotal_dl * gastos
                precio_bs = precio * cambioTx
                subtotal_bs = subtotal_dl * cambioTx
                gasto_bs = gasto_dl * cambioTx
            else:
                precio_bs = precio 
                subtotal_bs = precio_bs * cantidad
                gasto_bs = subtotal_bs * gastos
                precio_dl = precio_bs / cambioTx
                subtotal_dl = subtotal_bs / cambioTx
                gasto_dl = gasto_bs / cambioTx

            if guardar:
                baremonuevo = BaremoPagoTercero.objects.create(
                    nombre=descripcion,
                    precio = precio_dl,
                    usuario_id = request.user.id,

                )
                producto_id = baremonuevo.id
            
            DetalleFacturaProveedor.objects.create(
                factura_id = idFactura,
                usuario_id = request.user.id,
                precio_unitario = precio_dl,
                descripcion = descripcion,
                cantidad = cantidad,
                porc_iva = iva,
                cambio_bcv = cambioTx,
                gastos = gasto_dl, 
                gastos_bs = gasto_bs ,
                precio_bs = float(precio_bs),
                subtotal = subtotal_dl,
                subtotal_bs = subtotal_bs,
                precio_dl = precio_dl,
                subtotal_dl = subtotal_dl,
                manual = True,
                montoiva = float(subtotal_bs) * (float(iva)/100),
                montoiva_dl = float(subtotal_dl) * (float(iva)/100),
                congelar_moneda = True,
                moneda_pago_id = id_moneda,
                baremo_pago_tercero_id = producto_id,
            )

            

        
        
        return JsonResponse({'mensaje': 'DETALLE FACTURA GUARDADO correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al GUARDAR DETALLE FACTURA'})
    


def refresh_table_detalle_factura(request):
    idFactura = request.GET.get('idFactura')
    factura = FacturaProveedor.objects.filter(id=idFactura).first()
    facturadetalle = DetalleFacturaProveedor.objects.filter(factura_id=idFactura)
    tasacambio= CambioDiaBcv(datetime.now())

    if facturadetalle:
        total_factura = facturadetalle.aggregate(total_factura=Sum('subtotal'))
        total_gastos = facturadetalle.aggregate(total_gastos=Sum(F('gastos')*F('cantidad')))
        moneda_congelada = DetalleFacturaProveedor.objects.filter(factura_id=idFactura, congelar_moneda = True).count()
        total_factura = total_factura['total_factura']
        total_gastos=total_gastos['total_gastos']
       
    else:
        total_factura = 0
        total_gastos=0
        total_factura_bs = 0
        total_gastos_bs = 0
        moneda_congelada = 0

    
    
    total_factura_bs = ((total_factura) * tasacambio)
            
    return render(request, 'tabla_factura.html', {'facturadetalle': facturadetalle, 
                                                    'total_factura':total_factura,
                                                    'neto_pagar':total_factura   ,
                                                    'neto_pagar_bolivar':total_factura_bs ,
                                                    'factura' : factura,
                                                    'gastosadm':total_gastos ,
                                                    'montoretencion':0,
                                                    'moneda_congelada':moneda_congelada
                                                  })
    
    
    
def refresh_table_resumen_factura(request):
    idFactura = request.GET.get('idFactura')
    factura = FacturaProveedor.objects.filter(id=idFactura).first()
    facturadetalle = DetalleFacturaProveedor.objects.filter(factura_id=idFactura, precio_unitario__gt=0)
    if facturadetalle:
        total_factura = facturadetalle.aggregate(total_factura=Sum('precio_unitario'))
        total_factura_bs = facturadetalle.aggregate(total_factura_bs=Sum('precio_bs'))
        gastos = facturadetalle.aggregate(gastos=Sum('gastos'))
        gastos_bs = facturadetalle.aggregate(gastos_bs=Sum('gastos_bs'))
        total_factura = total_factura['total_factura']
        total_factura_bs = total_factura_bs['total_factura_bs']
        gastos = gastos['gastos']
        gastos_bs = gastos_bs['gastos_bs']
    else:
        total_factura = 0
        total_factura_bs = 0
        gastos = 0
        gastos_bs = 0


    
    """ 
    impuestos = TablaImpuesto.objects.first()
    if impuestos:
        montos_mayores = impuestos.montotope
        if factura.tipodocumento_id == 5:
            sustraendo = 0
        else:
            sustraendo = impuestos.sustraendo
    else:
        montos_mayores = 0
        sustraendo = 0
         """
        
    
    neto_pagar = total_factura - gastos
    neto_pagar_bolivar = total_factura_bs - gastos_bs
    return render(request, 'tabla_resumen_factura.html', {
                                                    'neto_pagar':neto_pagar ,
                                                    'neto_pagar_bolivar':neto_pagar_bolivar,
                                                    'factura':factura
                                                    
                                                  })
    
    

def cambia_gastos_administrativo(request):
    idFactura = request.GET.get('idFactura')
    newGasto = request.GET.get('newGasto')
    FacturaProveedor.objects.filter(id=idFactura).update(
        administrativo = newGasto
    )
    newGasto = float(newGasto)
    DetalleFacturaProveedor.objects.filter(factura_id=idFactura,precio_unitario__lt = 0 ).delete()
    DetalleFacturaProveedor.objects.filter(factura_id=idFactura, precio_unitario__gt = 0).update(
        gastos = F('precio_unitario') * (Decimal(newGasto) /100),
        gastos_bs = F('precio_bs') * (Decimal(newGasto) /100)
    )
    
    return redirect('factura_automatica_medico',factura_id = idFactura )
    #return render(request, 'tabla_resumen_factura.html')



def eliminar_detalle_factura(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idDetalleFactura = datos['idDetalleFactura']
        detalle_reversar_nqx = DetalleFacturaProveedor.objects.filter(id=idDetalleFactura).first()
        if detalle_reversar_nqx:
            NotaQuirurgica.objects.filter(participante_id = detalle_reversar_nqx.detalle_id, 
                                          cirugia_id = detalle_reversar_nqx.cirugia_id, 
                                          medico_id = detalle_reversar_nqx.factura.proveedor_id).update(
                                            pagado = False,
                                            usuario_id = request.user.id
                                          )

        DetalleFacturaProveedor.objects.filter(id=idDetalleFactura).delete()

        return JsonResponse({'mensaje': 'DETALLE FACTURA GUARDADO correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al GUARDAR DETALLE FACTURA'})
    

def cambiar_tipo_documento(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idFactura = datos['idFactura']
        tipoDocumento = datos['tipoDocumento']

        FacturaProveedor.objects.filter(id=idFactura).update(
            tipodocumento = tipoDocumento,

        )
        return JsonResponse({'mensaje': 'CAMBIO DE TIPO DOCUMENTO FACTURA GUARDADO correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al TIPO DOCUMENTO EN  FACTURA'})


    
    
@csrf_exempt
def save_selected_rows(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        for row in data:
            id = row['id']
            quantity = row['quantity']
            quantity = quantity.replace(',','.')
            quantity = float(quantity)
            consumo = ConsumoCirugia.objects.filter(id=id).first()
            cantidad_disponible = consumo.cantidad_uso - consumo.cantidad_real_usada
            if quantity > cantidad_disponible:
                quantity = cantidad_disponible
                
                
            ConsumoCirugia.objects.filter(id=id).update(
                cantidad_real_usada = F('cantidad_real_usada') + quantity,
                venta = consumo.inventario.monto_venta,
                hora_uso = datetime.now()
                )
            
            DetalleConsumoCirugia.objects.create(
                consumocirugia_id=id,
                precio_unitario = consumo.inventario.monto_venta * int(quantity),
                cantidad_uso = quantity,
                hora = datetime.now(),
                inventario_id = consumo.inventario_id
            )
           
            
        return JsonResponse({'message': 'Datos guardados con éxito'})
    
    return JsonResponse({'message': 'Solicitud inválida'})



@add_group_name_to_context    
class listado_detalle_consumo_cirugia(TemplateView):
    template_name='listado_detalle_consumo_cirugia.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['pk']
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        detalleconsumo = DetalleConsumoCirugia.objects.filter(consumocirugia__cirugia_id = cirugia_id, consumocirugia__cantidad_real_usada__gt = 0).order_by('inventario__nombre')
        total_precio = detalleconsumo.aggregate(total_precio=Sum('precio_unitario'))
        total_cantidad = detalleconsumo.aggregate(total_cantidad=Sum('cantidad_uso'))
        
        context['cirugia'] = cirugia
        context['detalleconsumo'] = detalleconsumo
        context['total_precio'] = total_precio['total_precio']
        context['total_cantidad'] = total_cantidad['total_cantidad']
        return context
    
@add_group_name_to_context    
class listado_pagado(UserPassesTestMixin ,  TemplateView): 
    template_name='listado_pagado.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        factura = FacturaProveedor.objects.filter(numerodocumento__isnull=False).first()
        #facturas = FacturaProveedor.objects.filter(numerodocumento__isnull=False).order_by('-id')
        """ facturas = FacturaProveedor.objects.filter(numerodocumento__isnull=False) \
                                   .annotate(total_precio_unitario=Sum('detallefacturaproveedor__precio_unitario')) \
                                   .order_by('-id') """
        facturas = FacturaMedico.objects.filter(factura__tipodocumento_id__gt = 1).order_by('-id')
                                   
        context['factura'] = factura
        context['facturas'] = facturas
        return context
    
    
def refresh_table_detalle_pagado(request):
    idFactura = request.GET.get('idFactura')
    factura = FacturaProveedor.objects.filter(id=idFactura).first()
    #registro = RegistroDocumento.objects.filter(factura_id = idFactura ).first()
    facturadetalle = DetalleFacturaProveedor.objects.filter(factura_id=idFactura)
    total_factura = facturadetalle.aggregate(total_factura=Sum(F('precio_unitario')*F('cantidad')))
    total_gasto = facturadetalle.aggregate(total_gasto=Sum('gastos'))
    total_factura_bs = facturadetalle.aggregate(total_factura_bs=Sum(F('precio_bs')*F('cantidad')))
    total_gasto_bs = facturadetalle.aggregate(total_gasto_bs=Sum('gastos_bs'))
    neto_factura = total_factura['total_factura'] - total_gasto['total_gasto']
    neto_factura_bs = total_factura_bs['total_factura_bs'] - total_gasto_bs['total_gasto_bs']
    
    
    transaccion = Transaccion.objects.filter(cuentapagar_id=idFactura).annotate(
                monto_positivo=ExpressionWrapper(F('monto') * -1, output_field=FloatField()),
                monto_bs_positivo=ExpressionWrapper(F('monto_dolar') * -1, output_field=FloatField())
            )
    
    
    return render(request, 'tabla_detalle_factura_pagado.html', {'facturadetalle': facturadetalle, 
                                                    'factura' : factura,
                                                    'neto_factura': neto_factura,
                                                    'total_a_pagar': neto_factura,
                                                    'netopagar_dl': neto_factura_bs,
                                                    'retencion_dl': 0,
                                                    'transaccion': transaccion
                                                  })
    

@add_group_name_to_context    
class pdf_recibo_pago_proveedor(TemplateView): 
    template_name='pdf_recibo_pago_proveedor.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        factura_id = self.kwargs['factura_id']
        facturaproveedor = FacturaProveedor.objects.filter(id=factura_id).first()
        #registro = RegistroDocumento.objects.filter(factura_id = factura_id ).first()
        tasa = facturaproveedor.cambio_congelado
        fecha_hoy = datetime.now()
        detallefactura = DetalleFacturaProveedor.objects.filter(factura_id=factura_id).order_by('-id')
        total_usd = detallefactura.aggregate(total_usd=Sum(F('precio_unitario')*F('cantidad')))
        total_gasto = detallefactura.aggregate(total_gasto=Sum('gastos'))
        total_bs = detallefactura.aggregate(total_bs=Sum(F('precio_bs')*F('cantidad')))
        total_gasto_bs = detallefactura.aggregate(total_gasto_bs=Sum('gastos_bs'))
        
        total_neto_bs = total_bs['total_bs']
        total_neto_usd = total_usd['total_usd']
        transaccion = Transaccion.objects.filter(cuentapagar_id = factura_id).annotate(
                monto_positivo=ExpressionWrapper(F('monto') * -1, output_field=FloatField()),
                monto_bs_positivo=ExpressionWrapper(F('monto_dolar') * -1, output_field=FloatField())
            )

        
        
        context['fecha_hoy'] = fecha_hoy
        context['transaccion'] = transaccion
        context['detallefactura'] = detallefactura
        context['total_neto_usd'] = total_neto_usd
        context['total_neto_bs'] = total_neto_bs
        context['facturaproveedor'] = facturaproveedor
        return context
    
    
def refresh_table_recibos(request):
    idmedico = request.GET.get('idmedico')
    facturas = FacturaProveedor.objects.filter(tipodocumento_id = 4, proveedor_id = idmedico, estatus = 'PEN' ).order_by('-id')
    
    
    return render(request, 'tabla-convertir-factura-medico.html', {
                                            'facturas': facturas, 
                                                })

@add_group_name_to_context    
class lista_factura_pagada(UserPassesTestMixin,TemplateView): 
    template_name='lista_factura_pagada.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        facturaspagadas = FacturaMedico.objects.filter(factura__tipodocumento_id__in = [1,5]).order_by('-id')
        """ total_imponible = facturaspagadas.aggregate(total_imponible=Sum('baseimponible'))
        total_retencion = facturaspagadas.aggregate(total_retencion=Sum('montoretenido'))
        total_pagado = facturaspagadas.aggregate(total_pagado=Sum('netopagado')) """
        
        """ context['total_pagado'] = total_pagado['total_pagado']
        context['total_retencion'] = total_retencion['total_retencion']
        context['total_imponible'] = total_imponible['total_imponible'] """
        context['facturaspagadas'] = facturaspagadas
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)  
        
        ultimocomprobante = RetencionISLR.objects.count()+1
        nuevocomprobante_str = f"{ultimocomprobante:06d}"
        current_date = datetime.now()
        year_str = str(current_date.year)
        month_str = f"{current_date.month:02d}"
        nrocomprobante = year_str + month_str + nuevocomprobante_str
        selected_fps = request.POST.getlist('name_checkretencion')
        if selected_fps:
            comprobanteislr = RetencionISLR.objects.create(
                comprobante = nrocomprobante,
                periodo = month_str + year_str,
                usuario_id = self.request.user.id,
            )
            id_comprobante = comprobanteislr.id
            total_baseimponible = total_montoretencion = porcentaje_retencion = 0      
            for sid in selected_fps:
                medico = FacturaMedico.objects.filter(id=sid).first()
                if medico:
                    total_baseimponible += medico.factura.subtotal_factura_bs
                    total_montoretencion +=  medico.factura.retencion_islr_monto_bs
                    porcentaje_retencion = medico.factura.porcentaje_retencion_islr
                    FacturaMedico.objects.filter(id=sid).update(
                        comprobante_id = id_comprobante
                    )

            
            if total_baseimponible > 0:
                RetencionISLR.objects.filter(id = id_comprobante).update(
                    baseimponible = total_baseimponible,
                    montoretencion = total_montoretencion,
                    porcentaje_retencion = porcentaje_retencion
                    
                )
                
            
            return redirect('pdf_retencion', comprobante_id = id_comprobante)
        else:
            return redirect('lista_factura_pagada')
        
        
    
    
    
    
@add_group_name_to_context    
class pdf_retencion(TemplateView): 
    def get_template_names(self):
        comprobante_id = self.kwargs['comprobante_id']
        comprobante = RetencionISLR.objects.filter(id=comprobante_id).first()

        if comprobante.tipo_comprobante == 'FM':
            return ['pdf_retencion.html']     # plantilla para médicos
        else:
            return ['pdf_retencion_compra.html'] # plantilla para proveedores

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comprobante_id = self.kwargs['comprobante_id']
        comprobante = RetencionISLR.objects.filter(id=comprobante_id).first()
        proveedor =[]
        if comprobante.tipo_comprobante == 'FM':
            facturaretencion = FacturaMedico.objects.filter(comprobante_id = comprobante_id)
            total_retenido = RetencionISLR.objects.filter(id=comprobante_id).first()
            medicos = FacturaMedico.objects.filter(comprobante_id = comprobante_id).first()
            medico = Medico.objects.filter(id=medicos.medico_id).first()
            monto_retenido = total_retenido.montoretencion
        else:
            proveedor = FacturaProveedor.objects.filter(comprobante_id = comprobante_id).first()
            facturaretencion = FacturaProveedor.objects.filter(comprobante_id = comprobante_id)
            total_retenido = comprobante.montoretencion
            medico = Proveedor.objects.filter(id=proveedor.proveedor_compra_id).first()
            monto_retenido = total_retenido

        
        context['medico'] = medico
        context['proveedor'] = proveedor
        context['comprobante'] = comprobante
        context['total_retenido'] = monto_retenido
        context['facturaretencion'] = facturaretencion
        return context
        
@add_group_name_to_context    
class documento_new_cxp_proveedor(UserPassesTestMixin,TemplateView): 
    
    template_name='documento_new_cxp_proveedor.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proveedores = Proveedor.objects.filter(activo = True).order_by('nombre')
        retenciones = Retencion.objects.all().order_by('nombre')
        tipodocumento = TipoDocumento.objects.all().order_by('nombre')
        moneda = Moneda.objects.all()
        FacturaProveedor.objects.filter(numerodocumento__isnull=True).delete()
        facturas = RegistroDocumento.objects.filter(tipodocumento = 4, facturamedico__isnull = True).order_by('-id')
        notaspendientes = NotaEntregaCompra.objects.filter(activo=False).order_by('-id')
        centrocosto = CentroCostoFacturaCompra.objects.all().order_by('nombre')
        fecha_hoy = datetime.now()
        cambio_hoy = CambioDiaBcv(datetime.now())
        context['moneda'] = moneda
        context['proveedores'] = proveedores
        context['facturas'] = facturas
        context['fecha_hoy'] = fecha_hoy
        context['cambio_hoy'] = cambio_hoy
        context['retenciones'] = retenciones
        context['centrocosto'] = centrocosto
        context['tipodocumento'] = tipodocumento
        context['notaspendientes'] = notaspendientes
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        proveedor = request.POST.get('proveedor')
        nrodocumento = request.POST.get('nrodocumento')
        nrocontrol = request.POST.get('nrocontrol')
        centrocosto = request.POST.get('centrocosto')
        fechaentrega = request.POST.get('fechaentrega')
        retencion = request.POST.get('retencion')
        pretencion = request.POST.get('p_rentencion')
        tipodocumento = request.POST.get('tipodocumento')
        monto_total_documento = request.POST.get('monto_total_documento')
        porc_iva = request.POST.get('porc_iva')
        moneda_documento = request.POST.get('moneda_documento')
        monto_total_documento = float(monto_total_documento.replace(',','.'))
        porc_iva = float(porc_iva.replace(',','.'))

        proveedor_tipo_persona = Proveedor.objects.filter(id = proveedor).first()
        monto_sustraendo = Retencion.objects.filter(id = retencion).first()
        monto_sustraendo_bs = 0
        if proveedor_tipo_persona:
            if proveedor_tipo_persona.rif[:1] == 'J' or proveedor_tipo_persona.rif[:1] == 'G':
                if monto_sustraendo:
                    monto_sustraendo_bs = monto_sustraendo.sustraendojuridica
            else:
                if monto_sustraendo:
                    monto_sustraendo_bs = monto_sustraendo.sustraendonatural
                
        
        #date_object = datetime.strptime(fechaentrega, "%Y-%m-%d")
        fechaentrega_str = datetime.strptime(fechaentrega, '%Y-%m-%d')
        cambio_factura = CambioDiaBcv(fechaentrega_str)
        cambio_factura = float(cambio_factura)
        if moneda_documento == '9999':
            moneda_documento = 2
            
        error = 0    
        valores_filas = request.POST.getlist('detalle_factura')
        detalle_formateado = []
        for i in range(0,len(valores_filas),6):
            detalle = valores_filas[i] + '~' + valores_filas[i+1] + '~' + valores_filas[i+2] + '~' + valores_filas[i+3] + '~' + valores_filas[i+4] + '~' + valores_filas[i+5]
            detalle_formateado.append(detalle)
            

        if detalle_formateado:
            nuevafactura = FacturaProveedor.objects.create(
                fecha_entrega =  fechaentrega,
                numerodocumento =  nrodocumento.strip(),
                numerocontrol =  nrocontrol.strip(),
                concepto_id = retencion,
                proveedor_compra_id = proveedor,
                tipodocumento_id = tipodocumento,
                tipomoneda_id = moneda_documento,
                porcentaje_retencion_islr = pretencion.replace(',','.'),
                tipo = 'FC',
                usuario_id = self.request.user.id,
                fecha_cambio = fechaentrega,
                congelar_moneda = True,
                cambio_congelado = cambio_factura,
                sustraendo_bs = monto_sustraendo_bs,
                centro_costo_id = centrocosto
                )            
            
            factura_id = nuevafactura.id
            
            detalles = detalle_formateado
            for detalle in detalles:
                cantidad,descripcion,precio_unitario,subtotal,porc_iva,monto_iva  = detalle.split('~')
                if subtotal == '':
                    porc_iva = 0
                
                if monto_iva == '':
                    monto_iva = 0

                if precio_unitario == '':
                    precio_unitario = '0'

                precio_unitario = float(precio_unitario.replace(',','.'))
                monto_iva = float(monto_iva)
                subtotal = float(subtotal.replace(',','.'))

                if monto_iva == 0 or monto_iva == '0' :
                   porc_iva = 0

                if porc_iva == 0 or porc_iva == '0' :
                   monto_iva = 0

                if moneda_documento == 1:
                    precio_unitario_bs = precio_unitario * cambio_factura
                    precio_unitario_dl = precio_unitario
                    subtotal_bs = subtotal * cambio_factura
                    subtotal_dl = subtotal
                else:
                    precio_unitario_bs = precio_unitario 
                    precio_unitario_dl = precio_unitario / cambio_factura
                    subtotal_bs = subtotal  
                    subtotal_dl = subtotal / cambio_factura
                  
                
                DetalleFacturaProveedor.objects.create(
                    cantidad = cantidad,
                    precio_unitario = precio_unitario_dl,
                    precio_bs = precio_unitario_bs,
                    precio_dl = precio_unitario_dl,
                    subtotal_bs = subtotal_bs,
                    subtotal_dl = subtotal_dl,
                    porc_iva = porc_iva,
                    descripcion = descripcion,
                    factura_id = factura_id,
                    montoiva = monto_iva,
                    subtotal = subtotal_bs,
                    cambio_bcv = cambio_factura,
                    congelar_moneda = True,
                    
                )


            return redirect('lista_factura_compra')
        

@add_group_name_to_context    
class mantenimiento_proveedor(UserPassesTestMixin, TemplateView): 
    
    template_name='mantenimiento_proveedor.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Inventario') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proveedores = Proveedor.objects.filter(activo=True).order_by('-id')
        context['proveedores'] = proveedores
        return context
    
    
@add_group_name_to_context   
class ProveedorEditView(UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'edit_proveedor.html'
    success_url = reverse_lazy('mantenimiento_proveedor')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proveedor_id=self.object.id
        pagoproveedor = FormaPagoProveedor.objects.filter(proveedor_id=proveedor_id, activo=True).order_by('-id')
        forma_pago_options = FormaPago.objects.all().order_by('nombre')
        bancos = Banco.objects.all().order_by('nombre')
        monedas = Moneda.objects.all()
        context['bancos'] = bancos
        context['monedas'] = monedas
        context['pagoproveedor'] = pagoproveedor
        context['forma_pago_options'] = forma_pago_options
        return context
    
    def form_valid(self, form):
        proveedor_id=self.object.id
        if 'guardar_proveedor' in self.request.POST:
        # Guardar button was pressed
            messages.success(self.request, 'El Personal se ha actualizado correctamente')
        elif 'guardar_pago' in self.request.POST:
            nombre_para_pago = self.request.POST.get('nombre_para_pago')
            numerocuenta = self.request.POST.get('numerocuenta')
            numeropago = self.request.POST.get('numeropago')
            formapago = self.request.POST.get('formapago')
            correo_pago = self.request.POST.get('correo_pago')
            cedulapago = self.request.POST.get('cedula_pago')
            bancopago = self.request.POST.get('banco') 
            moneda = self.request.POST.get('moneda')

            mediopagoproveedor = FormaPagoProveedor.objects.filter(
                proveedor_id = proveedor_id,
                numerocuenta = numerocuenta,
                moneda_id = moneda,
                formapago_id = formapago,
            )

            if mediopagoproveedor:
                messages.error(self.request, 'Ya existe ese medio de pago en este proveedor!')
                return self.render_to_response(self.get_context_data(form=form))

            FormaPagoProveedor.objects.create(
                proveedor_id = proveedor_id,
                nombre = nombre_para_pago,
                numerocuenta = numerocuenta,
                numeropago = numeropago,
                correo = correo_pago,
                formapago_id = formapago,
                cedulapago = cedulapago,
                bancopago_id = bancopago,
                moneda_id = moneda
                
            )
            # Agregar button was pressed
            #messages.success(self.request, 'Pago agregado correctamente')
            return redirect('edit_proveedor', pk = proveedor_id )
        
        
        form.save()
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar el Personal revise campos')
        return self.render_to_response(self.get_context_data(form=form))
    

@add_group_name_to_context   
class ProveedorNewView(CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'create_proveedor.html'
    success_url = reverse_lazy('mantenimiento_proveedor')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def form_valid(self, form):
        form.save()
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar el Personal revise campos')
        return self.render_to_response(self.get_context_data(form=form))

@add_group_name_to_context   
class create_warehouse(UserPassesTestMixin,TemplateView):
    model = Deposito
    template_name = 'create_warehouse.html'
    success_url = reverse_lazy('index')
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Inventario') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        depositos = Deposito.objects.all().order_by('nombre')

        context['depositos']=depositos
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        inventario = Inventario.objects.all()
        nombredeposito = self.request.POST.get('nombredeposito')
        ubicaciondeposito = self.request.POST.get('ubicaciondeposito')
        if nombredeposito:
            deposito = Deposito.objects.filter(nombre=nombredeposito).first()
            if not deposito:
                depositonuevo = Deposito.objects.create(
                    nombre=nombredeposito,
                    ubicacion=ubicaciondeposito
                )
                depositonuevo.save()
                depositoidnew = depositonuevo.id
                DepositoUso.objects.create(
                        deposito_id = depositoidnew,
                        cantidad_deposito = 0,
                        usuario_id = self.request.user.id
                    )

                for producto in inventario:
                    DepositoUso.objects.create(
                        inventario_id = producto.id,
                        deposito_id = depositoidnew,
                        cantidad_deposito = 0,
                        usuario_id = self.request.user.id
                    )


        depositos = Deposito.objects.all().order_by('nombre')
        context['depositos']=depositos
        return redirect('create_warehouse' )
    
    
@add_group_name_to_context   
class create_provider_type(UserPassesTestMixin,TemplateView):
    model = TipoProveedor
    template_name = 'create_provider_type.html'
    success_url = reverse_lazy('index')
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores')  
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tipoproveedor = TipoProveedor.objects.filter(activo=True).order_by('nombre')

        context['tipoproveedor']=tipoproveedor
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        nombretipo = self.request.POST.get('nombredeposito')
        descripciontipo = self.request.POST.get('descripcionproveedor')
        if nombretipo:
            tipo = TipoProveedor.objects.filter(nombre=nombretipo).first()
            if not tipo:
                TipoProveedor.objects.create(
                    nombre=nombretipo,
                    descripcion=descripciontipo
                )
                
                
        tipoproveedor = TipoProveedor.objects.filter(activo=True).order_by('nombre')       
        context['tipoproveedor']=tipoproveedor
        return redirect('create_provider_type' )
    

@add_group_name_to_context   
class create_rooms( UserPassesTestMixin,TemplateView):
    model = Habitacion
    template_name = 'create_rooms.html'
    success_url = reverse_lazy('index')
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores')  
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        habitaciones = Habitacion.objects.all().order_by('habitacion')

        context['habitaciones']=habitaciones
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        habitacion = self.request.POST.get('habitacion')
        descripcion = self.request.POST.get('descripcion')
        if habitacion:
            habitaciones = Habitacion.objects.filter(habitacion=habitacion).first()
            if not habitaciones:
                Habitacion.objects.create(
                    habitacion=habitacion,
                    nota=descripcion
                )

        habitaciones = Habitacion.objects.all().order_by('habitacion')
        context['habitaciones']=habitaciones
        return redirect('create_rooms' )
    

@add_group_name_to_context   
class download_inventory(TemplateView):
    model = TipoDescarga
    template_name = 'download_inventory.html'
    success_url = reverse_lazy('index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tipos = TipoDescarga.objects.all().order_by('nombre')

        context['tipos']=tipos
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        nombre = self.request.POST.get('tipodescarga')
        descripcion = self.request.POST.get('descripcion')
        comprobante = self.request.POST.get('comprobante')
        if comprobante is not None:
            comprobante = True
        else:
            comprobante = False

        if nombre:
            tipos = TipoDescarga.objects.filter(nombre=nombre).first()
            if not tipos:
                TipoDescarga.objects.create(
                    nombre=nombre,
                    descripcion=descripcion,
                    comprobante = comprobante
                )

        tipos = TipoDescarga.objects.all().order_by('nombre')
        context['tipos']=tipos
        return redirect('download_inventory' )


    
@add_group_name_to_context    
class movimiento_caja(UserPassesTestMixin , TemplateView): 
    
    template_name='movimiento_caja.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bancoslocales = BancoLocal.objects.filter(activo = True).order_by('-id')
        transaccion = Transaccion.objects.all().order_by('-fecha_act')
        context['transaccion'] = transaccion
        context['bancoslocales'] = bancoslocales
        return context
    
    
def refresh_table_movimientos(request):
    idBanco = request.GET.get('idBanco')
    moneda = BancoLocal.objects.filter(id=idBanco).first()
    transaccion = Transaccion.objects.filter(bancolocal_id = idBanco).order_by('-fecha_act')
        
    return render(request, 'tabla_movimiento_banco.html', {'transaccion': transaccion, 'moneda':moneda})


@add_group_name_to_context    
class cirugia_porcobrar(TemplateView): 
    template_name='cirugia_porcobrar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cxc_id = self.kwargs['cxc_id']
        cuentaxcobrar = CuentaxCobrar.objects.filter(id=cxc_id).first()
        
        bancolocal = BancoLocal.objects.filter(activo = True).order_by('nombrecuenta')
        bancos = Banco.objects.all().order_by('nombre')
        formapago = FormaPago.objects.all().order_by('nombre')
        fecha_cambio_bcv = datetime.now()
        monto_truncar_decimales = CambioDiaBcv(datetime.now())

        if cuentaxcobrar.cirugia:
            detalle_cirugia_montos = DetalleCirugia.objects.filter(cirugia_id = cuentaxcobrar.cirugia_id)
        else:
            numero_presupuesto_ami = cuentaxcobrar.presupuesto_id
            detalle_cirugia_montos = DetallePresupuesto.objects.filter(presupuesto_id = numero_presupuesto_ami)
            
        
        
        if cuentaxcobrar.presupuesto.congelar_moneda:
            fecha_cambio_bcv = cuentaxcobrar.presupuesto.fecha_cambio
            monto_truncar_decimales = cuentaxcobrar.presupuesto.cambio_congelado
            formapago = FormaPago.objects.filter(moneda_id=2).order_by('nombre')
            bancolocal = BancoLocal.objects.filter(moneda_id=2, activo = True).order_by('nombrecuenta')
            
            
        monto_cambio_congelado = truncate_to_decimals(monto_truncar_decimales, 2)
        retencion = Retencion.objects.all().order_by('nombre')
        medicofrecuente = Medico.objects.filter(pagofrecuente = True).order_by('nombre')
        detallexcobrar = DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cxc_id).order_by('fecha_act')
        montogenerados = DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cxc_id, montocobrar__gt = 0).exists()
        total_nc_pendientes = 0
        for notacredito in detallexcobrar:
            nc_pendiente = NotaCreditoCtaCobrar.objects.filter(detallecuentaxcobrar_id = notacredito.id, aplicada = False)
            if nc_pendiente:
                monto_pendiente_aplicar = nc_pendiente.aggregate(saldo_total_nc=Sum('saldo'))
                if monto_pendiente_aplicar['saldo_total_nc']:
                    #nota_credito_id = nc_pendiente.id
                    total_nc_pendientes += monto_pendiente_aplicar['saldo_total_nc']
                else:
                    total_nc_pendientes += 0
                
        
        saldo_total = detallexcobrar.aggregate(saldo_total=Sum('montocobrar'))
        
        if saldo_total['saldo_total'] + total_nc_pendientes < 0:
            saldo_total = 0
        else:
            saldo_total = saldo_total['saldo_total'] + total_nc_pendientes

        """ if total_nc_pendientes > 0:
            print('aqui hay que preguntar si quiere aplicarla') """
        
        total_precios_con_retencion_topes = total_precios_sin_retencion_topes = total_detalle_cirugia_montos = 0
        for detalle in detalle_cirugia_montos:
            if detalle.cantidad == 0 and detalle.precio > 0:
                detalle.cantidad = 1

            exedente = 0
            if detalle.montoconsumo > detalle.montotope and detalle.alertaexcedente:
                exedente = detalle.montoconsumo - detalle.montotope

            if detalle.detalle.activar_retencion:
                total_precios_con_retencion_topes += ((detalle.precio ) + exedente)
            else:
                total_precios_sin_retencion_topes += ((detalle.precio ) + exedente)
        

        #verificar si hay pagos anteriores por diferencial cambiario
        monto_cobrado_anteriores_bs = 0
        activar_diferencial_cambiario = False
        if cuentaxcobrar:
            monto_cobrado_anteriores_bs = cuentaxcobrar.total_monto_pagado_bs
            monto_cobrado_anteriores_dl = cuentaxcobrar.total_monto_pagado
            activar_diferencial_cambiario = True

        

        total_detalle_cirugia_montos = total_precios_sin_retencion_topes + total_precios_con_retencion_topes

        context['total_precios_sin_retencion_topes'] = total_precios_sin_retencion_topes
        context['total_precios_con_retencion_topes'] = total_precios_con_retencion_topes
        context['activar_diferencial_cambiario'] = activar_diferencial_cambiario
        context['total_detalle_cirugia_montos'] = total_detalle_cirugia_montos
        context['monto_cobrado_anteriores_bs'] = monto_cobrado_anteriores_bs * -1
        context['monto_cobrado_anteriores_dl'] = monto_cobrado_anteriores_dl * -1
        context['monto_cambio_congelado'] = monto_cambio_congelado
        context['total_nc_pendientes'] = total_nc_pendientes
        context['fecha_cambio_bcv'] = fecha_cambio_bcv
        context['medicofrecuente'] = medicofrecuente
        context['detallexcobrar'] = detallexcobrar
        context['cuentaxcobrar'] = cuentaxcobrar
        context['montogenerados'] = montogenerados
        context['notascreditocliente'] = nc_pendiente
        context['saldo_total'] = saldo_total
        context['bancolocal'] = bancolocal
        context['retencion'] = retencion
        context['formapago'] = formapago
        context['bancos'] = bancos
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        cxc_id = self.kwargs['cxc_id'] 
        
        if 'registrar_cobro' in request.POST:
            cuentaxc = CuentaxCobrar.objects.filter(id=cxc_id).first()
            nombre_paciente = cuentaxc.presupuesto.paciente
            tasadia = request.POST['tasa-cambio']
            baseimponible = request.POST['neto-cobrado-usd']
            fechatasa = request.POST['fecha-cambio-bcv']
            montocobrado = request.POST['neto-cobrado-bs']
            descripcion = request.POST['nota-cobrado']
            cedulapagador = request.POST['cedula-pagador']
            nombrepagador = request.POST['nombre-pagador']
            telefonopagador = request.POST['telefono-pagador']
            formapago_id = request.POST['forma-pago']
            bancopago_id = request.POST['banco-pago']
            referencia = request.POST['referencia-pago']
            bancolocal_id = request.POST['destino_cobro']
            monto_retenido = request.POST['monto-retencion']
            porc_retenido = request.POST['porc-retencion']
            concepto_retencion = request.POST['concepto-retencion']
            nroretencion = request.POST['nro-retencion']
            tasadia = tasadia.replace(',','.')
            tasadia = float(tasadia)
            monto_retenido_usd = float(monto_retenido) / tasadia
            montocobrado = float(montocobrado.replace(',','.'))
            baseimponible = float(baseimponible.replace(',','.'))
            monto_retenido_bs = float(monto_retenido) 
            nota_adicional = descripcion
            activar_diferencial_cambiario = request.POST['activar_diferencial_cambiario']
            if activar_diferencial_cambiario and monto_retenido_bs > 0:
                DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cxc_id, montocobrar__lt = 0).update(
                    montocobrar = F('montocobrar_bs') / tasadia,
                    tasa_bcv = tasadia,
                    descripcion = "PAGO DE CIRUGIA DE: "+str(cuentaxc.cirugia.nombre_procedimiento)[:30] +" - HC: "+str(cuentaxc.cirugia_id)+'Cambio USD x diferencial cambiario'

                )
            
            if cuentaxc.cirugia:
                numero_historia =' HC: '+str(cuentaxc.cirugia_id)
                descripcion = "PAGO DE CIRUGIA DE: "+str(cuentaxc.cirugia.nombre_procedimiento)[:70] +" - HC: "+str(cuentaxc.cirugia_id)+' nota:'+str(nota_adicional)
                motivo = 'Cirugia'
            else:
                descripcion = 'PAGO ATENCION INMEDIATA'+' nota:'+str(nota_adicional)
                motivo = 'Atencion Inmediata'
                if cuentaxc.atencion_inmediata_id:
                    numero_historia =' CONTROL: '+str(cuentaxc.atencion_inmediata.codigo)
                else:
                    numero_historia =' PRESUPUESTO: '+str(cuentaxc.presupuesto_id)+' '

            transaccion = Transaccion.objects.create(
                monto_dolar = (baseimponible) ,
                monto = montocobrado,
                fechatransaccion = datetime.now(),
                descripcion = 'ABONO/PAGO:'+ str(cuentaxc.presupuesto.nombre_procedimiento)+str(numero_historia)+str(cuentaxc.presupuesto.paciente),
                referencia = referencia,
                bancolocal_id = bancolocal_id,
                nota = descripcion,
                usuario_id =  self.request.user.id,
                tasa_bcv = tasadia,
                fechatasa = fechatasa,
                cuentacobrar_id = cuentaxc.id,
                mediomoneda_id = formapago_id
            )
            
            transaccion_id = transaccion.id
            bancoreceptor = BancoLocal.objects.filter(id=bancolocal_id).first()
            fp = FormaPago.objects.filter(id=formapago_id).first()
            formadepago = fp.nombre
            moneda_pago = fp.moneda.nombre
            origenpago = OrigenPago.objects.create(
                        nombre =  descripcion,
                        numeropago = referencia,
                        bancopago_id = bancopago_id,
                        formapago_id = formapago_id
                        )
            origenpago.save()
            origenpago_id = origenpago.id
            
            ## debitocredito
            nombrebanco = ''
            if bancopago_id:
                bancoorigenpago = Banco.objects.filter(id=bancopago_id).first()
                if bancoorigenpago:
                    nombrebanco=bancoorigenpago.nombre
                
            if fp.moneda_id == 1:
                monto_unico = baseimponible
                monto_dolar = baseimponible
                monto_bolivares = 0
            else:
                monto_unico = montocobrado
                monto_bolivares = montocobrado
                monto_dolar = 0
                
            
            ## debitocredito fin
            monto_nota_credito = monto_nota_credito_bs = 0
            saldo_deudor = cuentaxc.total_cobrar_monto

            baseimponible = Decimal(str(baseimponible)).quantize(Decimal('0.01'))
            saldo_deudor = Decimal(str(saldo_deudor)).quantize(Decimal('0.01'))
            if baseimponible > saldo_deudor:
                monto_a_pagar = saldo_deudor
                monto_nota_credito = Decimal(baseimponible) - Decimal(saldo_deudor)
                monto_a_pagar_bs = Decimal(saldo_deudor) * Decimal(tasadia)
                monto_nota_credito_bs =  (Decimal(baseimponible) - Decimal(saldo_deudor)) * Decimal(tasadia)
            else:
                monto_a_pagar = baseimponible
                monto_a_pagar_bs = montocobrado
                
                
            detallecxc = DetalleCuentaCobrar.objects.create(
                montocobrar = (monto_a_pagar * -1),
                montocobrar_bs = (monto_a_pagar_bs * -1),
                descripcion = descripcion,
                cuentacobrar_id = cxc_id,
                destino_pago_id = bancolocal_id,
                origen_pago_id = origenpago_id,
                transaccion_id =  transaccion_id,
                tasa_bcv = tasadia,
                usuario_id = self.request.user.id
            )
            
            detallecxc.save()
            iddetallecxc = detallecxc.id
            
            pagador = Pagador.objects.create(
                cedula = cedulapagador,
                nombre = nombrepagador,
                telefono = telefonopagador,
                detallecuentaxcobrar_id = iddetallecxc
            )
            pagador.save()
            pagador_id = pagador.id
            
            pagadorunico = PagadorUnico.objects.filter(cedula = cedulapagador).first()
            if pagadorunico:
                PagadorUnico.objects.filter(cedula = cedulapagador).update(
                    nombre = nombrepagador,
                    telefono = telefonopagador
                )
                pagadorunico_id = pagadorunico.id
            else:
                pagadorunico = PagadorUnico.objects.create(
                    cedula = cedulapagador,
                    nombre = nombrepagador,
                    telefono = telefonopagador,
                )
                pagadorunico_id = pagadorunico.id
            
            # Guardar la retencion
            if monto_retenido_bs > 0:
                DetalleCuentaCobrar.objects.create(
                    montocobrar = (monto_retenido_usd * -1),
                    montocobrar_bs = (monto_retenido_bs * -1),
                    descripcion = 'Retencion aplicada al pago de: '+porc_retenido+'% ',
                    retencion_id = concepto_retencion ,
                    cuentacobrar_id = cxc_id,
                    destino_pago_id = bancolocal_id,
                    origen_pago_id = origenpago_id,
                    tasa_bcv = tasadia,
                    transaccion_id =  transaccion_id,
                    nroretencion = nroretencion
                )
                

            #if cuentaxc.cirugia_id is not None:
            #detallexcobrar = DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cxc_id)
            #saldo_total = detallexcobrar.aggregate(saldo_total=Sum('montocobrar'))
            #saldo = saldo_total['saldo_total']
            #estatus_actual = Cirugia.objects.filter(id=cuentaxc.cirugia_id).first()
            
            if cuentaxc.cirugia:  
                numero_control = 'Nota de Credito AutoGenerada por Cirugia:'+str(cuentaxc.cirugia_id )  
            else:
                numero_control = 'Nota de Credito AutoGenerada por AMI:'+str(cuentaxc.atencion_inmediata.codigo )  
            
            nota_credito_nueva_id = None      
            if monto_nota_credito > 0:
                nueva_nota_creada = DetalleCuentaCobrar.objects.create(
                    montocobrar = (monto_nota_credito * -1),
                    montocobrar_bs = (monto_nota_credito_bs * -1 ) ,
                    descripcion = 'NOTA DE CREDITO: a Favor de Cliente por pago realizado de:'+str(baseimponible),
                    cuentacobrar_id = cxc_id,
                    destino_pago_id = bancolocal_id,
                    origen_pago_id = origenpago_id,
                    transaccion_id =  transaccion_id,
                    tasa_bcv = tasadia,
                    notacredito = True,
                    
                )
                nota_credito_nueva = NotaCreditoCtaCobrar.objects.create(
                    saldo = monto_nota_credito ,
                    detallecuentaxcobrar_id = nueva_nota_creada.id,
                    pagador_id = pagadorunico_id,
                    usuario_id = self.request.user.id,
                    descripcion = numero_control,
                    saldo_bs = monto_nota_credito_bs ,
                    tasa = tasadia,
                    fechatasa = fechatasa,
                    fecha_pago = fechatasa,
                    autogenerada = True
                )
                nota_credito_nueva_id = nota_credito_nueva.id
                Pagador.objects.create(
                    cedula = cedulapagador,
                    nombre = nombrepagador,
                    telefono = telefonopagador,
                    detallecuentaxcobrar_id = nueva_nota_creada.id
                )
                
            DebitoCredito.objects.create(
                transaccion_id = transaccion_id,
                cuenta_destino = bancoreceptor.nombrecuenta,
                cuenta_origen = nombrebanco  ,
                medico_proveedor =  numero_historia,
                monto_bolivares = monto_bolivares,
                monto_dolar = monto_dolar,
                tasa_bcv = tasadia,
                movimiento = 'Credito',
                fechatransaccion =  datetime.now(),
                descripcion = 'ABONO/PAGO :'+ str(cuentaxc.presupuesto.nombre_procedimiento)+str(numero_historia),
                referencia = referencia,
                usuario = self.request.user.id,
                formapago = formadepago ,
                moneda = moneda_pago,
                monto_unico = monto_unico,
                dolares = baseimponible,
                motivo = motivo,
                notacredito_id = nota_credito_nueva_id
                
            )
                
                 
            fecha_ejecucion = datetime.now()
            mensajeCobro = 'U58 informa se registro un cobro al paciente: '+str(nombre_paciente) + ', por un monto de :'+str(baseimponible)+' , forma de pago:'+str(formadepago)  + ', el '+str(fecha_ejecucion)
            
            #envioWhatsApp(mensajeCobro, "04126157881")
        
            #return redirect('pdf_recibocxc', cuentacobrar_id=cxc_id, transaccion_id = transaccion_id  )
        return redirect('cirugia_porcobrar', cxc_id=cxc_id  )
        
    

def buscar_cambio_desde_js(request):
    fecha_cambio_congelado = request.GET.get('fecha_cambio_congelado')
    date_object = datetime.strptime(fecha_cambio_congelado, "%Y-%m-%d %H:%M:%S.%f")
    # Query your database to retrieve the corresponding date
    monto = CambioDiaBcv(date_object)
    return JsonResponse({'monto': monto})


@add_group_name_to_context    
class pdf_recibocxc(TemplateView): 
    template_name='pdf_recibocxc.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        detalle_id = self.kwargs['pk']
        cuentacobrar = DetalleCuentaCobrar.objects.filter(id=detalle_id).first()
        cuentacobrar_id = cuentacobrar.cuentacobrar_id
        cuentaxcobrar = CuentaxCobrar.objects.filter(id=cuentacobrar_id).first()
        pagador = Pagador.objects.filter(detallecuentaxcobrar_id = cuentacobrar.id).first()
        transaccion_id = cuentacobrar.transaccion_id
        if transaccion_id:
            detallexcobrar = DetalleCuentaCobrar.objects.filter(transaccion_id=transaccion_id).first()
            transaccion = Transaccion.objects.filter(id=transaccion_id).first()
            movimientodetalle = DetalleCuentaCobrar.objects.filter(transaccion_id=transaccion_id)
        else:
            transaccion = []
            detallexcobrar = DetalleCuentaCobrar.objects.filter(id = detalle_id).first()
            movimientodetalle = DetalleCuentaCobrar.objects.filter(id = detalle_id)
            
        
        saldocliente = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar_id).aggregate(total_monto=Sum('montocobrar'))
        total_monto_value = saldocliente['total_monto']
        
        fecha_hoy = datetime.now()
        context['fecha_hoy'] = fecha_hoy
        context['pagador'] = pagador
        context['transaccion'] = transaccion
        context['cuentaxcobrar'] = cuentaxcobrar
        context['detallexcobrar'] = detallexcobrar
        context['total_monto_value'] = total_monto_value
        context['movimientodetalle'] = movimientodetalle
        return context
    
    
@add_group_name_to_context    
class pdf_recibocxc_detalle(TemplateView): 
    template_name='pdf_recibocxc_detalle.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        detalle_id = self.kwargs['pk']
        cuentacobrar = DetalleCuentaCobrar.objects.filter(id=detalle_id).first()
        cuentacobrar_id = cuentacobrar.cuentacobrar_id
        cuentaxcobrar = CuentaxCobrar.objects.filter(id=cuentacobrar_id).first()
        pagador = Pagador.objects.filter(detallecuentaxcobrar_id = cuentacobrar.id).first()
        transaccion_id = cuentacobrar.transaccion_id
        if transaccion_id:
            detallexcobrar = DetalleCuentaCobrar.objects.filter(transaccion_id=transaccion_id).first()
            transaccion = Transaccion.objects.filter(id=transaccion_id).first()
            movimientodetalle = DetalleCuentaCobrar.objects.filter(transaccion_id=transaccion_id)
        else:
            transaccion = []
            detallexcobrar = DetalleCuentaCobrar.objects.filter(id = detalle_id).first()
            movimientodetalle = DetalleCuentaCobrar.objects.filter(id = detalle_id)
            
        
        detalle_cobrado = []
        subtotal_detalle = 0
        if cuentaxcobrar:
            presupuesto_id = cuentaxcobrar.presupuesto_id
            detalle_cobrado = DetallePresupuesto.objects.filter(presupuesto_id = presupuesto_id, precio_usado__gt = 0).aggregate(total_monto=Sum('precio_usado'))
            subtotal_detalle = detalle_cobrado['total_monto']
            detalle_cobrado = DetallePresupuesto.objects.filter(presupuesto_id = presupuesto_id, precio_usado__gt = 0)
            
            if not subtotal_detalle:
                detalle_cobrado = DetallePresupuesto.objects.filter(presupuesto_id = presupuesto_id, precio_usado__gt = 0).aggregate(total_monto=Sum('precio'))
                subtotal_detalle = detalle_cobrado['total_monto']
                detalle_cobrado = DetallePresupuesto.objects.filter(presupuesto_id = presupuesto_id, precio__gt = 0)
            
            
        
        saldocliente = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar_id).aggregate(total_monto=Sum('montocobrar'))
        total_monto_value = saldocliente['total_monto']
        
        fecha_hoy = datetime.now()
        context['fecha_hoy'] = fecha_hoy
        context['pagador'] = pagador
        context['transaccion'] = transaccion
        context['cuentaxcobrar'] = cuentaxcobrar
        context['detallexcobrar'] = detallexcobrar
        context['detalle_cobrado'] = detalle_cobrado
        context['subtotal_detalle'] = subtotal_detalle
        context['total_monto_value'] = total_monto_value
        context['movimientodetalle'] = movimientodetalle
        return context
    


@add_group_name_to_context    
class pdf_estadocuenta(TemplateView): 
    template_name='pdf_estadocuenta.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cuentacobrar_id = self.kwargs['cuentacobrar_id']
        cuentaxcobrar = CuentaxCobrar.objects.filter(id=cuentacobrar_id).first()
        detallexcobrar = DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuentacobrar_id )
        saldocliente = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar_id).aggregate(total_monto=Sum('montocobrar'))
        total_monto_value = saldocliente['total_monto']
        bancolocal = BancoLocal.objects.filter(activo = True).order_by('nombrecuenta')
        bancos = Banco.objects.all().order_by('nombre')
        formapago = FormaPago.objects.all().order_by('nombre')
        fecha_hoy = datetime.now()
        monto_cambio = CambioDiaBcv(datetime.now())
        
        context['fecha_hoy'] = fecha_hoy
        context['total_monto_value'] = total_monto_value
        context['cuentaxcobrar'] = cuentaxcobrar
        context['detallexcobrar'] = detallexcobrar
        return context

@add_group_name_to_context    
class pdf_estadocuenta2(TemplateView): 
    template_name='pdf_estadocuenta.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['cirugia_id']
        cuentaxcobrar = CuentaxCobrar.objects.filter(cirugia_id=cirugia_id).first()
        cuentacobrar_id = cuentaxcobrar.id
        detallexcobrar = DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuentacobrar_id )
        saldocliente = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar_id).aggregate(total_monto=Sum('montocobrar'))
        total_monto_value = saldocliente['total_monto']
        bancolocal = BancoLocal.objects.filter(activo = True).order_by('nombrecuenta')
        bancos = Banco.objects.all().order_by('nombre')
        formapago = FormaPago.objects.all().order_by('nombre')
        fecha_hoy = datetime.now()
        monto_cambio = CambioDiaBcv(datetime.now())
        
        context['fecha_hoy'] = fecha_hoy
        context['total_monto_value'] = total_monto_value
        context['cuentaxcobrar'] = cuentaxcobrar
        context['detallexcobrar'] = detallexcobrar
        return context
        


@add_group_name_to_context    
class lista_factura_compra(UserPassesTestMixin,TemplateView): 
    
    template_name='lista_factura_compra.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion') | Q(name='Inventario') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        FacturaProveedor.objects.filter(numerodocumento__isnull=True, tipo__in = ['FC','FI']).delete()
        #facturascompra = FacturaProveedor.objects.filter(tipo__in = ['FC','FI']).order_by('-id')
        #context['facturascompra'] = facturascompra
        return context

@add_group_name_to_context    
class pago_multiples_facturas(UserPassesTestMixin,TemplateView): 
    
    template_name='pago_multiples_facturas.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proveedor_factura_id = self.kwargs['proveedor_compra_id']
        factura = FacturaProveedor.objects.filter(proveedor_compra_id = proveedor_factura_id).first()
        facturas_proveedor = FacturaProveedor.objects.filter(proveedor_compra_id = proveedor_factura_id).order_by('-fecha_entrega')
        cantidad = sum(
            1 for f in facturas_proveedor
            if f.saldo_neto_factura_proveedor_bs > 0
        )
        tasacambio = CambioDiaBcv(datetime.now())
        cuentaproveedor = FormaPagoProveedor.objects.filter(proveedor_id = proveedor_factura_id, activo = True )
        cuentas = BancoLocal.objects.filter(activo = True).order_by('nombrecuenta')

        context['facturas_proveedor'] = facturas_proveedor
        context['cuentaproveedor'] = cuentaproveedor
        context['tasa_dia'] = tasacambio
        context['cantidad'] = cantidad
        context['factura'] = factura
        context['cuentas'] = cuentas
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        proveedor_factura_id = self.kwargs['proveedor_compra_id']
        facturas_ids = request.POST.getlist("facturas_ids")

        id_mediodepago = request.POST.getlist("fracciones_mediopago[]")
        fracciones_usd = request.POST.getlist("fracciones_usd[]")
        fracciones_bs = request.POST.getlist("fracciones_bs[]")
        fracciones_ref = request.POST.getlist("fracciones_ref[]")
        fracciones_nota = request.POST.getlist("fracciones_nota[]")
        fracciones_fecha = request.POST.getlist("fracciones_fecha[]")

        banco_local = request.POST.getlist("fracciones_origen[]")
        banco = request.POST.getlist("fracciones_destino[]")
        tasa_cambio = request.POST.getlist("fracciones_tasa[]")
        
        for i in range(len(fracciones_bs)):
            monto_bs = Decimal(fracciones_bs[i])
            monto_usd = Decimal(fracciones_usd[i])
            referencia = fracciones_ref[i]
            descripcion = fracciones_nota[i]
            fecha_tasa = fracciones_fecha[i]
            banco_local_id = banco_local[i]
            monto_tasa = float(tasa_cambio[i])
            banco_id = banco[i]
            id_mediodepago = id_mediodepago[i]

            transaccion = Transaccion.objects.create(
                bancolocal_id = banco_local_id,
                banco_id = banco_id,
                monto = monto_bs*-1,
                monto_dolar = monto_usd * -1,
                fechatransaccion = datetime.now(),
                descripcion=descripcion,
                usuario_id=self.request.user.id,
                nota="Pago múltiples facturas",
                referencia=referencia,
                multiple_factura=True,
                fechatasa = fecha_tasa,
                tasa_bcv = monto_tasa,
                mediomoneda_id = id_mediodepago,
                )

            abono_cta_pagar = AbonoCuentaPagar.objects.create(
                montopago = monto_usd,
                montopago_bs = monto_bs,
                descripcion = descripcion + str(' *(Pago a multiples facturas)*'),
                tasa_bcv = monto_tasa,
                destino_pago_id = banco_id,
                origen_pago_id = banco_local_id,
                factura_pago_multiple = True,
                transaccion_id = transaccion.id,
                usuario_id = self.request.user.id,
                referencia = referencia,
                fecha_pago = datetime.now(),
            )

            monto_por_factura = monto_bs / len(facturas_ids)
            for factura in facturas_ids:
                TransaccionFacturaMultiple.objects.create(
                    transaccion_id=transaccion.id,
                    abono_id = abono_cta_pagar.id,
                    factura_id=factura,
                )

        """ for factura_id in facturas_ids:
            factura = FacturaProveedor.objects.get(id=factura_id)
            #print('factura', factura_id) """
        return redirect("lista_factura_compra")

@add_group_name_to_context    
class factura_editar(TemplateView): 
    template_name='factura_editar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        factura_id = self.kwargs['pk']
        facturascompra = FacturaProveedor.objects.filter(id=factura_id).first()
        cuentas = BancoLocal.objects.filter(activo = True).order_by('nombrecuenta')
        cuentaproveedor = FormaPagoProveedor.objects.filter(proveedor_id = facturascompra.proveedor_compra_id, activo = True )
        detallefactura = DetalleFacturaProveedor.objects.filter(factura_id=factura_id)
        total_monto_iva = DetalleFacturaProveedor.objects.filter(factura_id=factura_id).aggregate(total_iva=Sum('montoiva'))
        total_iva = total_monto_iva['total_iva']
        total_iva = float(total_iva)
        total_subtotal = DetalleFacturaProveedor.objects.filter(factura_id=factura_id).aggregate(subtotal=Sum('subtotal'))
        subtotal = total_subtotal['subtotal']
        subtotal = float(subtotal)
        porc_retencion = float(facturascompra.administrativo)
        monto_retener = subtotal * (porc_retencion/100)
        total_pagar =(subtotal-monto_retener)+total_iva
        montopagado = 0
        abonos = AbonoCuentaPagar.objects.filter(factura_id = factura_id ).order_by('id')
        if abonos:
            totalpagos = abonos.aggregate(total=Sum('montopago'))
            pagado = totalpagos['total']
            totalpagosbs = abonos.aggregate(total=Sum('montopago_bs'))
            pagado_bs = totalpagosbs['total']
            if facturascompra.tipomoneda_id == 2:
                montopagado = pagado_bs
            else:
                montopagado = pagado
        
        saldo_actual = total_pagar - float(montopagado)
        
        context['abonos'] = abonos
        context['cuentas'] = cuentas
        context['subtotal'] = subtotal
        context['total_iva'] = total_iva
        context['monto_retener'] = monto_retener
        context['total_pagar'] = total_pagar
        context['saldo_actual'] = saldo_actual
        context['facturascompra'] = facturascompra
        context['detallefactura'] = detallefactura
        context['porc_retencion'] = porc_retencion
        context['cuentaproveedor'] = cuentaproveedor
        
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        factura_id = self.kwargs['pk']
        
        if 'registrar_pago' in request.POST:
            facturascompra = FacturaProveedor.objects.filter(id=factura_id).first()
            idOrigenFondos = request.POST['idOrigenFondos']
            idDestinoFondos = request.POST['idDestinoFondos']
            montopagar = request.POST['idmontopagar']
            referenciapago = request.POST['idreferenciapago']
            notapago = request.POST['idnotapago']
            montopagar = float(montopagar.replace(',','.'))
            monto = 0
            monto_bs = 0
            txdia = CambioDiaBcv(datetime.now())
            bancolocal = BancoLocal.objects.filter(id=idOrigenFondos).first()
            if bancolocal:
                if bancolocal.moneda_id == 2:
                    monto_bs = montopagar
                    monto = montopagar / float(txdia)
                else:
                    monto = montopagar
                    monto_bs = montopagar * float(txdia)
                
                
            if facturascompra:
                transaccion = Transaccion.objects.create(
                    monto = (monto_bs * -1),
                    monto_dolar = (monto * -1) ,
                    fechatransaccion = datetime.now(),
                    descripcion = "PAGO DE COMPRA A PROVEEDORES :"+str(notapago),
                    referencia = referenciapago,
                    bancolocal_id = idOrigenFondos,
                    usuario_id = self.request.user.id,
                    nota = notapago,
                    fechatasa = datetime.now(),
                    tasa_bcv = txdia,
                    banco_id = idDestinoFondos,
                    cuentapagar_id = factura_id,
                        
                    )
                
                transaccion.save()
                transaccion_id = transaccion.id
                
                AbonoCuentaPagar.objects.create(
                    montopago = monto,
                    montopago_bs = monto_bs,
                    descripcion = notapago,
                    tasa_bcv = txdia,
                    destino_pago_id = idDestinoFondos,
                    factura_id = factura_id,
                    origen_pago_id = idOrigenFondos,
                    usuario_id = self.request.user.id,
                    transaccion_id = transaccion_id
                )
                
            fecha_ejecucion = datetime.now()
            nombre_proveedor = facturascompra.proveedor_compra
            mensajeCompra = 'U58 informa se registro pago a proveedor: '+str(nombre_proveedor) + ', por un monto de :'+str(montopagar) + ', el '+str(fecha_ejecucion)
            
            #envioWhatsApp(mensajeCompra, "04126157881")  
            
        
        
        
        return redirect('factura_editar', pk=factura_id  )

""" 
def imagen_to_pdf(request):
    image_path = 'c:/pruebapdf/imagen.jpg'  # reemplaza con la ruta de tu imagen
    pdf_bytes = convert(image_path)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="imagen.pdf"'
    return response """

def imagen_to_pdf(request):
    image_path = 'c:/pruebapdf/imagen.jpg'  # reemplaza con la ruta de tu imagen
    pdf_bytes = convert(image_path)
    pdf_file_path = 'c:/pruebapdf/imagen.pdf'  # reemplaza con la ruta donde deseas guardar el archivo PDF
    with open(pdf_file_path, 'wb') as f:
        f.write(pdf_bytes)
    return redirect('pacientes')
 

@add_group_name_to_context    
class AgregarProductoView(UserPassesTestMixin , TemplateView):
    template_name = 'agregar_producto.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Inventario') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        laboratorios = LaboratorioMedicina.objects.all().order_by('nombre')
        proveedores = Proveedor.objects.filter(activo=True).order_by('nombre')
        categorias = CategoriaInventario.objects.all().order_by('nombre')
        clasificacion = UnidadProducto.objects.all().order_by('nombre')
        presentaciones = PresentacionMedicina.objects.filter(activo = True).order_by('nombre')
        productos = Inventario.objects.filter(producto_activo = True).order_by('nombre')
        depositos = Deposito.objects.all().order_by('nombre')
        incremento = MontoIncremento.objects.first()
        unidadcompra = UnidadCompra.objects.filter(activo = True).order_by('nombre')
        action = 'A'
        tasa_hoy = CambioDiaBcv(datetime.now())
        
        context['presentaciones'] = presentaciones
        context['laboratorios'] = laboratorios
        context['proveedores'] = proveedores
        context['unidadcompra'] = unidadcompra
        context['clasificacion'] = clasificacion
        context['categorias'] = categorias
        context['fecha_hoy'] = datetime.now()
        context['incremento'] =incremento
        context['productos'] = productos
        context['depositos'] = depositos
        context['tasa_hoy'] = tasa_hoy
        context['action'] = action
        return context


def agregarInventario(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nroDocumento = datos['nroDocumento']
        idProveedor = datos['idProveedor']
        fechaEntrega = datos['fechaEntrega']
        categoria = datos['categoria']
        clasificacion = datos['clasificacion']
        costo = datos['costo']
        venta = datos['venta']
        idInventario = datos['idInventario']
        presentacion_salida = datos['presentacion_salida']
        lote = datos['lote']
        laboratorio = datos['laboratorio']
        fechaelabora = datos['fechaelabora']
        fechavence = datos['fechavence']
        nombreProducto = datos['nombreProducto']
        piva = datos['piva']
        depositocarga = datos['depositocarga']
        conversion = datos['conversion']
        unidad_compra = datos['unidad_compra']
        nombrecomercial = datos['nombrecomercial']
        cantidadcompra = datos['cantidadcompra']
        tasa_aplicable = datos['tasa_aplicable']
        moneda_factura = datos['moneda_factura']
        cantidad_critica = datos['cantidad_critica']
        cantidad_minima = datos['cantidad_minima']

        costo = float(str(costo.replace(',','.')))
        tasa_aplicable = float(tasa_aplicable)

        categorianombre = CategoriaInventario.objects.filter(id=categoria).first()
        if idInventario:
            producto = Inventario.objects.filter(id=idInventario).first()
            codigonew = producto.codigo
        else:
            idInventario = 0
            proximocodigo = Inventario.objects.aggregate(Max('id'))['id__max']
            proximocodigo = int(proximocodigo)
            proximocodigo = proximocodigo + 1
            codigonew = categorianombre.nombre[:3].upper()
            codigonew = codigonew + str(proximocodigo).zfill(10)

        #detalles = datos.get('detalles')
        if int(moneda_factura) == 1:
            costo_dl = Decimal(costo)
            costo_bs = Decimal(costo) * Decimal(tasa_aplicable)
            #costo_bs = costo_bs.quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        else:
            costo_bs = costo
            costo_dl = costo / tasa_aplicable
        
        notaexiste = NotaEntregaCompra.objects.filter(numerodocumento = nroDocumento, proveedor_compra_id = idProveedor, activo = False).first()
        
        if notaexiste:
            NotaEntregaCompra.objects.filter(numerodocumento = nroDocumento, proveedor_compra_id = idProveedor).update(
                numerodocumento=nroDocumento,
                proveedor_compra_id = idProveedor,
                fecha_entrega = fechaEntrega,
                usuario_id = request.user.id,
                tasaaplicable = tasa_aplicable,
                moneda_factura = moneda_factura,

                )
            
            notaentrega_id = notaexiste.id
        else:
            notaentrega = NotaEntregaCompra.objects.create(
                    numerodocumento=nroDocumento,
                    proveedor_compra_id = idProveedor,
                    fecha_entrega = fechaEntrega,
                    usuario_id = request.user.id,
                    tasaaplicable = tasa_aplicable,
                    moneda_factura = moneda_factura,
                )
            
            notaentrega.save()
            notaentrega_id = notaentrega.id
        
        factor_capsulado = UnidadCompra.objects.filter(id = int(unidad_compra)).first()
        if factor_capsulado:
            factor = factor_capsulado.cantidad_unidad_bulto
        else:
            factor = 0

        if idInventario == 0:
            nuevoproducto = Inventario.objects.create(
                codigo = codigonew,
                usuario_id = request.user.id,
                proveedor_id = idProveedor,
                costo = costo_dl,
                venta = venta,
                piva = piva,
                categoria_id = categoria,
                clasificacion_id = clasificacion,
                nombre = nombreProducto,
                lote = lote,
                fecha_elaboracion  = fechaelabora,
                fecha_vencimiento  = fechavence,
                laboratorio_id = laboratorio,
                presentacion_salida_id = presentacion_salida,
                unidad_conversion  = 0,
                unidadcompra_id  = unidad_compra,
                nombre_comercial  = nombrecomercial,
                cantidad_unitaria  = cantidadcompra,
                cantidad_min  = cantidad_minima,
                cantidad_cri = cantidad_critica,
                )
            
            nuevoproducto.save()
            idInventario = nuevoproducto.id
            generardepositos = Deposito.objects.all()
            for depo in generardepositos:
                DepositoUso.objects.create(
                   inventario_id = idInventario,
                   usuario_id = request.user.id,
                   deposito_id = depo.id,
                )
            
            
        detallenota = DetalleNotaEntrega.objects.create(
            codigo = codigonew,
            notaentrega_id = notaentrega_id,
            usuario_id = request.user.id,
            costo_dl = costo_dl,
            costo_bs = costo_bs,
            venta_dl = venta,
            piva = piva,
            categoria_id = categoria,
            nombre = nombreProducto,
            inventario_id = idInventario,
            lote = lote,
            fechaelaboracion = fechaelabora,
            fechavencimiento = fechavence,
            laboratorio_id = laboratorio,
            clasificacion_id = clasificacion,
            presentacion_salida_id = presentacion_salida,
            unidad_conversion  = factor,
            unidadcompra_id  = unidad_compra,
            nombre_comercial  = nombrecomercial,
            cantidad  = cantidadcompra,
            deposito_id = depositocarga,
            cambioaplicado = tasa_aplicable,
        )
        
        detallenota.save()
        detalle_id = detallenota.id

        
            
        data = {'idNota' : notaentrega_id}
        return JsonResponse(data)
    else:
        return JsonResponse({'mensaje': 'Error al GUARDAR Nota de entrega'})
    
    
    
def eliminarProductoNotaEntrega(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        producto_id = datos['producto_id']
        notadetalle = DetalleNotaEntrega.objects.filter(id = producto_id).first()
        DetalleNotaEntrega.objects.filter(id = producto_id).delete()
        data = {'idNota' : notadetalle.notaentrega_id}
        return JsonResponse(data)

def eliminarProductoFactura(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        producto_id = datos['producto_id']
        notadetalle = DetalleFacturaProveedor.objects.filter(id = producto_id).first()
        DetalleFacturaProveedor.objects.filter(id = producto_id).delete()
        data = {'idNota' : notadetalle.factura_id}
        return JsonResponse(data)
    
    
def refresh_table_detallenota(request):
    idNota = request.GET.get('idNota')
    detallenota = DetalleNotaEntrega.objects.filter(notaentrega_id = idNota)
    notaentrega = NotaEntregaCompra.objects.filter(id=idNota).first()

    return render(request, 'tabla_inventario.html', {'detallenota': detallenota, 'notaentrega':notaentrega})


def refresh_table_deposito(request):
    idDetalle = request.GET.get('idDetalle')
    depositotransito = DepositoTransito.objects.filter(detallenota_id = idDetalle)
    
    return render(request, 'tabla_deposito.html', {'depositotransito': depositotransito})


@add_group_name_to_context    
class entregas_transito(UserPassesTestMixin , TemplateView):
    template_name = 'entregas_transito.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Inventario') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        """ notasentrega = NotaEntregaCompra.objects.filter(Q(cantidad_inventario_actualizado = False) | Q(convertida_factura = False) | Q(convertida_factura_total = False)
        ).values('id','numerodocumento','proveedor_compra_id','fecha_entrega', 'proveedor_compra__nombre','proveedor_compra__rif','usuario__username','cantidad_inventario_actualizado','convertida_factura',
                 'convertida_factura_total'
        ).order_by('-id') """


        detalles = DetalleNotaEntrega.objects.filter(
            notaentrega=OuterRef('pk')
        )

        # Base imponible
        base_sub = detalles.filter(piva__gt=0).values('notaentrega').annotate(
            total=Sum(
                ExpressionWrapper(
                    F('cantidad') * F('costo_bs'),
                    output_field=DecimalField()
                )
            )
        ).values('total')[:1]

        # IVA
        iva_sub = detalles.values('notaentrega').annotate(
            total=Sum(
                ExpressionWrapper(
                    (F('cantidad') * F('costo_bs')) *
                    (F('piva') / Value(100.0)),
                    output_field=DecimalField()
                )
            )
        ).values('total')[:1]

        # Exento
        exento_sub = detalles.filter(piva=0).values('notaentrega').annotate(
            total=Sum(
                ExpressionWrapper(
                    F('cantidad') * F('costo_bs'),
                    output_field=DecimalField()
                )
            )
        ).values('total')[:1]


        notasentrega = NotaEntregaCompra.objects.filter(
            Q(cantidad_inventario_actualizado=False) |
            Q(convertida_factura=False) |
            Q(convertida_factura_total=False)
        ).select_related('proveedor_compra').annotate(

            total_base_imponible_bs_q=Coalesce(
                Subquery(base_sub, output_field=DecimalField()),
                Value(0),
                output_field=DecimalField()
            ),

            total_iva_bs_q=Coalesce(
                Subquery(iva_sub, output_field=DecimalField()),
                Value(0),
                output_field=DecimalField()
            ),

            total_exento_bs_q=Coalesce(
                Subquery(exento_sub, output_field=DecimalField()),
                Value(0),
                output_field=DecimalField()
            ),

        ).annotate(

            total_operacion_bs_ant=ExpressionWrapper(
                F('total_base_imponible_bs_q') +
                F('total_iva_bs_q') +
                F('total_exento_bs_q'),
                output_field=DecimalField()
            ),

            total_operacion_dl_ant=ExpressionWrapper(
                F('total_operacion_bs_ant') / F('tasaaplicable'),
                output_field=DecimalField()
            )

        ).order_by('-id')

        context['notasentrega'] = notasentrega
        return context
    
    
@add_group_name_to_context    
class generar_factura_multiples_notas(UserPassesTestMixin , TemplateView):
    template_name = 'notas_entrega_disponibles_factura.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Inventario') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proveedor_id = self.kwargs['proveedor_id']
        
        notasentrega = NotaEntregaCompra.objects.filter(proveedor_compra_id = proveedor_id, convertida_factura_total = False).order_by('-id')
        total_dolares = total_bolivares = 0
        
        for nota in notasentrega:
            total_dolares += nota.total_operacion_dl
            total_bolivares += nota.total_operacion_bs

        context['notasentrega'] = notasentrega
        context['total_dolares'] = total_dolares
        context['total_bolivares'] = total_bolivares
        
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        proveedor_id = self.kwargs['proveedor_id']
        action_button = request.POST.get("post_button")

        # Obtener la lista de IDs seleccionados
        selected_ids = request.POST.getlist('factura_ids')
        if not selected_ids:
            return redirect('generar_factura_multiples_notas', proveedor_id = proveedor_id )

        DetalleNotaEntrega.objects.filter(marca = True).update(
            marca = False
        )
        NotaEntregaCompra.objects.filter(marca = True).update(
            marca = False
        )
        notas_seleccionadas = NotaEntregaCompra.objects.filter(id__in=selected_ids)
        NotaEntregaCompra.objects.filter(id__in=selected_ids).update(
            marca = True,
            usuario_id = self.request.user.id
        )
        notaentrega = NotaEntregaCompra.objects.filter(proveedor_compra_id=proveedor_id, marca=True).order_by('-fecha_act').first()
        nota_id = notaentrega.id
        for nota in notas_seleccionadas:
            DetalleNotaEntrega.objects.filter(notaentrega_id=nota.id).update(
                marca = True,
                usuario_id = self.request.user.id
            )
        
        if action_button == "one_invoice":
            return redirect('conversion_nota_a_factura', nota_id = nota_id)
        
        if action_button == "multiple_invoice":
            return redirect('conversion_nota_a_factura_multiple', nota_id = nota_id)

    
    
    
@add_group_name_to_context    
class editar_nota_entrega(UserPassesTestMixin,  TemplateView):
    template_name = 'editar_nota_entrega.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Inventario') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nota_id = self.kwargs['nota_id']
        notaentrega = NotaEntregaCompra.objects.filter(id = nota_id).first()
        detallenota = DetalleNotaEntrega.objects.filter(notaentrega_id = nota_id).order_by('id')

        proveedores = Proveedor.objects.filter(activo=True).order_by('nombre')
        laboratorios = LaboratorioMedicina.objects.all().order_by('nombre')
        categorias = CategoriaInventario.objects.all().order_by('nombre')
        presentaciones = PresentacionMedicina.objects.filter(activo = True).order_by('nombre')
        productos = Inventario.objects.filter(producto_activo = True).order_by('nombre')
        depositos = Deposito.objects.all().order_by('nombre')
        #depositotransito = DepositoTransito.objects.filter(detallenota_id = nota_id)
        incremento = MontoIncremento.objects.first()
        unidadcompra = UnidadCompra.objects.filter(activo=True).order_by('nombre')
        clasificacion = UnidadProducto.objects.all().order_by('nombre')
         
        context['laboratorios'] = laboratorios
        context['clasificacion'] = clasificacion
        context['proveedores'] = proveedores
        context['notaentrega'] = notaentrega
        context['detallenota'] = detallenota
        context['categorias'] = categorias
        context['unidadcompra'] = unidadcompra
        context['presentaciones'] = presentaciones
        context['productos'] = productos
        context['incremento'] = incremento
        context['depositos'] = depositos
        return context
    
    def post(self, request, *args, **kwargs):
        nota_id = self.kwargs['nota_id']
        if 'accion' in request.POST:
            tasacambiofactura = request.POST['tasacambiofactura']
            cambioaplicado = Decimal(tasacambiofactura.replace(',','.'))
            moneda_factura = request.POST['moneda_factura']
            if request.POST['accion'] == 'eliminar':
                nota_id = self.kwargs['nota_id']
                NotaEntregaCompra.objects.filter(id=nota_id).delete()
                return redirect('entregas_transito')
            
            if request.POST['accion'] == 'tasanew':
                NotaEntregaCompra.objects.filter(id=nota_id).update(
                    tasaaplicable = cambioaplicado,
                    usuario = self.request.user.id,
                )
                DetalleNotaEntrega.objects.filter(notaentrega_id=nota_id).update(
                    cambioaplicado = cambioaplicado,
                    costo_bs = (F('costo_dl')) * cambioaplicado,
                )

            if request.POST['accion'] == 'monedanew':
                if moneda_factura == '2':
                    NotaEntregaCompra.objects.filter(id=nota_id).update(
                        tasaaplicable = cambioaplicado,
                        usuario = self.request.user.id,
                        moneda_factura = moneda_factura
                    )
                    DetalleNotaEntrega.objects.filter(notaentrega_id=nota_id).update(
                        costo_bs = (F('costo_dl')),
                        costo_dl = (F('costo_bs')/cambioaplicado),
                        cambioaplicado = cambioaplicado,
                        )
                else:
                    NotaEntregaCompra.objects.filter(id=nota_id).update(
                        tasaaplicable = cambioaplicado,
                        usuario = self.request.user.id,
                        moneda_factura = moneda_factura
                    )
                    DetalleNotaEntrega.objects.filter(notaentrega_id=nota_id).update(
                        costo_dl = (F('costo_bs')),
                        costo_bs = (F('costo_dl')*cambioaplicado),
                        cambioaplicado = cambioaplicado,
                        )

                    

            """ if request.POST['accion'] == 'modificar':
                nombrecomercialUpdate = request.POST['nombrecomercialUpdate']
                cantidadcompraUpdate = request.POST['cantidadcompraUpdate']
                categoriaUpdate = request.POST['categoriaUpdate']
                presentacion_entradaUpdate = request.POST['presentacion_entradaUpdate']
                unidad_compraUpdate = request.POST['unidad_compraUpdate']
                pivaUpdate = request.POST['pivaUpdate']
                conversionUpdate = request.POST['conversionUpdate']
                costoUpdate = request.POST['costoUpdate']
                ventaUpdate = request.POST['ventaUpdate']
                presentacion_salidaUpdate = request.POST['presentacion_salidaUpdate']
                cantidad_minimaUpdate = request.POST['cantidad_minimaUpdate']
                cantidad_criticaUpdate = request.POST['cantidad_criticaUpdate']
                laboratorioUpdate = request.POST['laboratorioUpdate']
                loteUpdate = request.POST['loteUpdate']
                fechaelaboraUpdate = request.POST['fechaelaboraUpdate']
                fechavenceUpdate = request.POST['fechavenceUpdate']
                depositoUpdate = request.POST['depositoUpdate']
                tasacambiofactura = request.POST['tasacambiofactura']
                idDetalle = request.POST['idDetalle']

                numeronota = request.POST['numeronota']
                proveedor = request.POST['proveedor']
                
                if not laboratorioUpdate:
                    laboratorioUpdate = None
                    
               
                
                piva = Decimal(pivaUpdate.replace(',','.'))
                unidad_conversion = Decimal(conversionUpdate.replace(',','.'))
                cambioaplicado = Decimal(tasacambiofactura.replace(',','.'))
                costoUpdateProducto = Decimal(costoUpdate.replace(',','.'))
                cantidad_unitaria = Decimal(cantidadcompraUpdate.replace(',','.'))
                venta_dl = Decimal(ventaUpdate.replace(',','.'))
                if moneda_factura == '1':
                    costo_dl = costoUpdateProducto
                    costo_bs = costoUpdateProducto * cambioaplicado
                else:
                    costo_bs = costoUpdateProducto
                    costo_dl = costoUpdateProducto / cambioaplicado

                NotaEntregaCompra.objects.filter(id=nota_id).update(
                    numerodocumento = numeronota,
                    proveedor_compra_id = proveedor,
                    tasaaplicable = cambioaplicado,
                    usuario = self.request.user.id,
                    moneda_factura = moneda_factura
                )

                DetalleNotaEntrega.objects.filter(id=idDetalle).update(
                    laboratorio_id = laboratorioUpdate,
                    presentacion_id = presentacion_entradaUpdate,
                    presentacion_salida_id = presentacion_salidaUpdate,
                    categoria_id = categoriaUpdate,
                    costo_dl = costo_dl,
                    venta_dl = venta_dl,
                    costo_bs = costo_bs,
                    cambioaplicado = cambioaplicado,
                    piva = piva,
                    lote = loteUpdate,
                    fechaelaboracion = fechaelaboraUpdate,
                    fechavencimiento = fechavenceUpdate,
                    unidad_conversion = unidad_conversion,
                    cantidad = cantidad_unitaria,
                    unidadcompra_id = unidad_compraUpdate,
                    nombre_comercial = nombrecomercialUpdate,
                    usuario_id = self.request.user.id,
                    deposito_id = depositoUpdate
                ) """



            return redirect('editar_nota_entrega', nota_id = nota_id )
            

@add_group_name_to_context    
class editar_factura(TemplateView):
    template_name = 'editar_factura.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nota_id = self.kwargs['nota_id']
        cambio_hoy = CambioDiaBcv(datetime.now())
        proveedores = Proveedor.objects.filter(activo=True).order_by('nombre')
        notaentrega = NotaEntregaCompra.objects.filter(id=nota_id).first()
        detallenota = DetalleNotaEntrega.objects.filter(notaentrega_id=nota_id).order_by('-id')
       
        retenciones = Retencion.objects.all().order_by('nombre')
        
        total_baseimponible = total_monto_iva = 0
        for detalle in detallenota:
            total_baseimponible = total_baseimponible + detalle.subtotal()
            total_monto_iva = total_monto_iva + detalle.montoiva()
            
        
        total_neto_pagar = total_baseimponible +  total_monto_iva
        porcentaje_retencion = 0
        monto_retener = 0


        context['cambio_hoy'] = cambio_hoy
        context['proveedores'] = proveedores
        context['notaentrega'] = notaentrega
        context['detallenota'] = detallenota
        context['retenciones'] = retenciones
        context['monto_retener'] = monto_retener
        context['total_monto_iva'] = total_monto_iva
        context['total_neto_pagar'] = total_neto_pagar
        context['total_baseimponible'] = total_baseimponible
        context['porcentaje_retencion'] = porcentaje_retencion
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        nota_id = self.kwargs['nota_id']
        numerodocumento = request.POST.get('nrodocumento')
        numerocontrol = request.POST.get('nrocontrol')
        fecha_entrega = request.POST.get('fechaentrega')
        concepto_id = request.POST.get('retencion')
        tipodocumento_id = 1
        tipomoneda_id = 2
        tipo = 'FC'

        notaentrega = NotaEntregaCompra.objects.filter(id=nota_id).first()
        if notaentrega:
            proveedor_id=notaentrega.proveedor_compra_id
            facturanueva = FacturaProveedor.objects.create(
                fecha_entrega = fecha_entrega,
                numerodocumento = numerodocumento,
                numerocontrol = numerocontrol,
                concepto_id =concepto_id,
                tipodocumento_id = tipodocumento_id,
                tipomoneda_id = tipomoneda_id,
                tipo = tipo,
                proveedor_compra_id = proveedor_id

            )
            facturanueva.save()
            factura_id = facturanueva.id

            detallenota = DetalleNotaEntrega.objects.filter(notaentrega_id=nota_id).order_by('-id')
            for detalle in detallenota:
                detalle_id = detalle.id
                nombre = detalle.nombre
                lote = detalle.lote
                codigo = detalle.codigo
                costo = detalle.costo
                venta = detalle.venta
                fechaelaboracion = detalle.fechaelaboracion
                fechavencimiento = detalle.fechavencimiento
                categoria_id = detalle.categoria_id
                laboratorio_id = detalle.laboratorio_id
                presentacion_id = detalle.presentacion_id
                presentacion_salida_id = detalle.presentacion_salida_id
                notaentrega_id = detalle.notaentrega_id
                proveedor_id = detalle.notaentrega.proveedor_compra_id
                piva = detalle.piva
                #agregar en tabla inventario 
                cantidad_total = DepositoTransito.objects.filter(detallenota_id=detalle_id).aggregate(total_cantidad=Sum('cantidad_deposito'))
                deposito_descarga = DepositoTransito.objects.filter(detallenota_id=detalle_id)
                cantidad_comprada = cantidad_total['total_cantidad']
                if codigo:
                    inventario = Inventario.objects.filter(codigo = codigo).first()
                    if inventario:
                        inventario_id = inventario.id
                        Inventario.objects.filter(codigo = codigo).update(
                            cantidad_unitaria = 1,
                            lote = lote,
                            fecha_elaboracion = fechaelaboracion,
                            fecha_vencimiento = fechavencimiento,
                            nombre = nombre,
                            costo = costo,
                            venta = venta,
                            categoria_id =categoria_id,
                            laboratorio_id = laboratorio_id,
                            presentacion_id = presentacion_id,
                            presentacion_salida_id = presentacion_salida_id,
                            proveedor_id = proveedor_id,
                            piva =piva
                        )
                    else:
                        inventario = Inventario.objects.create(
                            codigo = codigo,
                            cantidad_unitaria = 1,
                            lote = lote,
                            fecha_elaboracion = fechaelaboracion,
                            fecha_vencimiento = fechavencimiento,
                            nombre = nombre,
                            costo = costo,
                            venta = venta,
                            categoria_id =categoria_id,
                            laboratorio_id = laboratorio_id,
                            presentacion_id = presentacion_id,
                            presentacion_salida_id = presentacion_salida_id,
                            proveedor_id = proveedor_id,
                            piva =piva
                        )
                        inventario.save()
                        inventario_id = inventario.id

                    #Agregar en los depositos de uso
                    for ddd in deposito_descarga:
                        cantidad_deposito = ddd.cantidad_deposito
                        deposito_id = ddd.deposito_id
                        deposito_carga = DepositoUso.objects.filter(deposito_id=deposito_id,inventario_id=inventario_id).first()
                        if deposito_carga:
                            DepositoUso.objects.filter(deposito_id=deposito_id,inventario_id=inventario_id).update(
                                cantidad_deposito = F('cantidad_deposito') + cantidad_deposito
                            )
                        else:
                            DepositoUso.objects.create(
                                cantidad_deposito = cantidad_deposito,
                                deposito_id = deposito_id,
                                inventario_id = inventario_id,
                                usuario_id = self.request.user.id
                            )
                        
                        if cantidad_deposito > 0:
                            InventarioDescarga.objects.create(
                                cantidad=cantidad_deposito,
                                nota = 'Carga desde Nota entrega :'+str(detalle_id),
                                inventario_id = inventario_id,
                                usuario_id = self.request.user.id,
                                tipodescarga_id = 4,
                                depositoentrada_id= deposito_id
                            )


                DetalleFacturaProveedor.objects.create(
                    factura_id = factura_id,
                    cantidad = cantidad_comprada,
                    precio_unitario = detalle.costo,
                    porc_iva = detalle.piva,
                    descripcion = detalle.nombre,
                    montoiva = ((cantidad_comprada*detalle.costo) * (detalle.piva/100)),
                    precio_bs = detalle.costo,
                    subtotal = (detalle.costo * cantidad_comprada)

                )
               





        NotaEntregaCompra.objects.filter(id=nota_id).update(
            activo = True
        )

        return redirect('entregas_transito')


    
    
def obtener_producto_inventario(request):
     if request.method == 'POST':
        datos = json.loads(request.body)
        producto_id = datos['producto_id']
        producto = Inventario.objects.filter(id=producto_id).first()
        tasa_hoy = CambioDiaBcv(datetime.now())
        if producto:
            print('encontre productos')
        else:
            print('No hay, producto nuevo')


        data = {
            'codigo': producto.codigo,
            'lote': producto.lote,
            'laboratorio': producto.laboratorio_id,
            'categoria': producto.categoria_id,
            'clasificacion': producto.clasificacion_id,
            'costo': producto.costo,
            'costo_bs': Decimal(producto.costo) * Decimal(tasa_hoy),
            'venta': producto.monto_venta,
            'venta_bs': Decimal(producto.monto_venta) * Decimal(tasa_hoy),
            'presentacion': producto.presentacion_id,
            'presentacion_salida': producto.presentacion_salida_id,
            'piva': producto.piva,
            'fecha_elaboracion': producto.fecha_elaboracion,
            'fecha_vencimiento': producto.fecha_vencimiento,
            'nombrecomercial': producto.nombre_comercial,
            'unidad_compra': producto.unidadcompra_id,
            'conversion': producto.unidad_conversion,
            'existencia': producto.existencia ,
            'salida_producto': producto.cantidad_total_descarga ,
            'cantidad_producidas' : producto.cantidad_total_producto,
        }
        # Agrega aquí los campos que deseas mostrar
        return JsonResponse(data)
    
    
    
def get_medico_byid(request):
    idmedico = request.GET.get('id')
    # Verificar si la cédula existe en la base de datos
    medico = Medico.objects.filter(id=idmedico).first()
    if medico:
        nombre = medico.nombre
       
        data = {
            'nombre': nombre,
        }
    else:
        data = {
            'nombre': 'No existe codigo',
        }
    
    return JsonResponse(data)

@add_group_name_to_context    
class updatepresupuesto(TemplateView):
    template_name='updatepresupuesto.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='SuperAdministracion') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        presupuesto_id = self.kwargs['presupuesto_id']
        user_id = self.request.user.id
        presupuesto = Presupuesto.objects.filter(id = presupuesto_id).first()
        detalles = Baremo.objects.filter(convenio_id=1, inactivar = False).order_by('detalle__posicion')
        tipos = TipoProcedimiento.objects.all().order_by('nombre')
        medicos = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        fecha_actual = datetime.now()
        pdfs = RegistroPresupuestoPDF.objects.filter(presupuesto_id = presupuesto_id).order_by('fecha_creacion')
        if presupuesto.congelar_moneda:
            valor_bolivar_dia = presupuesto.cambio_congelado
        else:
            valor_bolivar_dia=CambioDiaBcv(fecha_actual)
            
            
        detallepresupuesto = DetallePresupuesto.objects.filter(
            presupuesto_id=presupuesto_id
        ).annotate(
            bolivares=ExpressionWrapper(F('precio') * valor_bolivar_dia, output_field=DecimalField())
        ).order_by('detalle__posicion')
        
        detallepresupuesto1 = DetallePresupuesto.objects.filter(
                presupuesto_id=presupuesto_id
            ).aggregate(total=Sum('precio'))

        total_general = detallepresupuesto1['total']
        
        #grupos = [(k, list(g)) for k, g in groupby(detallepresupuesto, lambda x: x.grupo)]
        responsable = Responsable.objects.filter(id=presupuesto.paciente.responsable_id).first()
        if responsable:
            context['responsable']=responsable

        grupos_con_totales = []

        for grupo, items in groupby(detallepresupuesto, lambda x: x.grupo):
            items = list(items)

            total_precio = Decimal('0.00')
            total_ajuste = Decimal('0.00')
            total_precio_bs = Decimal('0.00')

            for d in items:
                total_precio += d.precio or Decimal('0.00')
                total_precio_bs += (d.precio * valor_bolivar_dia) or Decimal('0.00')
                
                total_ajuste += d.monto_descuento_pr or Decimal('0.00')

            grupos_con_totales.append({
                'grupo': grupo,
                'detalles': items,
                'total_precio': total_precio,
                'total_ajuste': total_ajuste,
                'total_precio_bs':total_precio_bs,
            })

        context['grupos'] = grupos_con_totales
        context['tipos']=tipos
        context['medicos']=medicos
        context['detalles']=detalles
        context['total_general'] = total_general
        context['pdfs']=pdfs
        context['presupuesto']=presupuesto
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        presupuesto_id = self.kwargs['presupuesto_id']
        moneda =  request.POST.get('tipo_moneda')
        
        return redirect('presupuestopdf', pk = presupuesto_id, moneda = moneda )

def obtener_ruta_pdf_versionada(carpeta, pk):
    base_name = f'presupuesto_{pk}'
    version = 1

    while True:
        if version == 1:
            filename = f'{base_name}.pdf'
        else:
            filename = f'{base_name}_v{version}.pdf'

        file_path = os.path.join(carpeta, filename)

        if not os.path.exists(file_path):
            return file_path, filename, version

        version += 1

def presupuesto_autogenerado_pdf(request, pk, moneda):
    presupuesto = Presupuesto.objects.select_related('paciente').get(id=pk)

    paciente = presupuesto.paciente
    cedula = paciente.cedula

    # 👉 tu tasa (ejemplo)

    tasa_tx = presupuesto.cambio_congelado if presupuesto.cambio_congelado > 0 else CambioDiaBcv(datetime.now())
    fecha_tasa_tx = presupuesto.fecha_cambio if presupuesto.cambio_congelado > 0 else datetime.now()

    detalles = DetallePresupuesto.objects.filter(
        presupuesto_id=pk,
        precio__gt=0
    ).select_related('grupo', 'detalle').order_by(
        'detalle__posicion', 'grupo' 
    )

    grupos = []

    for grupo, items in groupby(detalles, key=attrgetter('grupo')):
        items = list(items)

        for i in items:
            i.precio_bs = (i.precio * tasa_tx).quantize(Decimal('0.01'))
            i.total_bs = (i.precio * tasa_tx).quantize(Decimal('0.01'))

        total_usd = sum(
            (i.precio  for i in items),
            Decimal('0.00')
        )

        total_bs = sum(
            (i.total_bs for i in items),
            Decimal('0.00')
        )

        grupos.append({
            'grupo': grupo,
            'items': items,
            'total_usd': total_usd,
            'total_bs': total_bs,
        })

    total_general_usd = sum(
        (g['total_usd'] for g in grupos),
        Decimal('0.00')
    )

    total_general_bs = sum(
        (g['total_bs'] for g in grupos),
        Decimal('0.00')
    )

    context = {
        'presupuesto': presupuesto,
        'grupos': grupos,
        'total_general_usd': total_general_usd,
        'total_general_bs': total_general_bs,
        'tasa_tx': tasa_tx,
        'moneda': moneda,
        'fecha': datetime.now(),
        'fecha_tasa_tx' : fecha_tasa_tx
    }

    # Render HTML
    html_string = render_to_string(
        'presupuesto_auto_pdf.html',
        context
    )

    # Carpeta por cédula
    carpeta = os.path.join(
        settings.MEDIA_ROOT,
        'presupuestos',
        str(cedula)
    )
    os.makedirs(carpeta, exist_ok=True)

    #filename = f'presupuesto_{pk}.pdf'
    file_path, filename, version = obtener_ruta_pdf_versionada(carpeta, pk)

    HTML(
        string=html_string,
        base_url=request.build_absolute_uri('/')
    ).write_pdf(file_path)

    RegistroPresupuestoPDF.objects.create(
        presupuesto=presupuesto,
        archivo=f'presupuestos/{cedula}/{filename}',
        version=version,
        usuario=request.user if request.user.is_authenticated else None
    )

    return redirect('presupuestopdf_ver', pk =  pk, moneda = moneda )

def ver_presupuesto_pdf(request, pdf_id):
    try:
        pdf = RegistroPresupuestoPDF.objects.get(id=pdf_id)
    except RegistroPresupuestoPDF.DoesNotExist:
        raise Http404("PDF no encontrado")

    file_path = os.path.join(settings.MEDIA_ROOT, pdf.archivo)
    if not os.path.exists(file_path):
        raise Http404("Archivo no existe")

    return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        

def eliminardetallepresupuesto(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idDetalle = datos['idDetalle']
        
        detalle_presupuesto = DetallePresupuesto.objects.filter(id=idDetalle).first()
        DetallePresupuesto.objects.filter(id=idDetalle).delete()
        LogEliminacion.objects.create(
            descripcion = 'Eliminacion de item en presupuesto :'+str(detalle_presupuesto.presupuesto_id)+' del paciente:'+str(detalle_presupuesto.presupuesto.paciente_id),
            usuario_id = request.user.id
        )
        
        if detalle_presupuesto:
            actualizarCuentaxCobrar(detalle_presupuesto.presupuesto_id,detalle_presupuesto.presupuesto.paciente_id, request.user.id )



        data = {
            'nombre': 'No existe codigo',
        }

        return JsonResponse(data)
    else:
        return JsonResponse({'mensaje': 'Error al eliminar detalle'})


def actualizardatospresupuesto(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idPresupuesto = datos['idPresupuesto']
        tipoProcedimiento = datos['tipoProcedimiento']
        medicoPpal = datos['medicoPpal']
        diagnostico = datos['diagnostico']
        procedimiento = datos['procedimiento']
        fechaProcedimiento = datos['fechaProcedimiento']
        horaProcedimiento = datos['horaProcedimiento']
        hospital = datos['hospital']
        horasQx = datos['horasQx']
        
        Presupuesto.objects.filter(id=idPresupuesto).update(
            fecha_procedimiento = fechaProcedimiento,
            tipo_procedimiento_id = tipoProcedimiento,
            medico_ppal_id = medicoPpal,
            diagnostico = diagnostico,
            nombre_procedimiento = procedimiento,
            dias_hospitalizacion = hospital,
            horas_qx = horasQx,
            hora_procedimiento = horaProcedimiento,
            usuario_id = request.user.id
        )
        """ hospital = int(hospital)
        if hospital == 0:
            DetallePresupuesto.objects.filter(presupuesto_id = idPresupuesto, detalle_id = 33).delete()
            ambulatorio = DetallePresupuesto.objects.filter(presupuesto_id = idPresupuesto, detalle_id = 32).exists()   
            if not ambulatorio:
                baremo = Baremo.objects.filter(detalle_id = 32).first()
                if baremo:
                    DetallePresupuesto.objects.create(
                        cantidad = baremo.cantidad,
                        precio = baremo.venta,
                        fecha_cambio = datetime.now(),
                        convenio_id = baremo.convenio_id,
                        detalle_id = baremo.detalle_id,
                        grupo_id = baremo.grupo_id,
                        plantilla_id = baremo.plantilla_id,
                        unidad_id = baremo.unidad_id,
                        usuario_id = request.user.id,
                        presupuesto_id = idPresupuesto,
                        ntqx = baremo.ntqx,
                        alertaexcedente = True,
                    )
        else:
            DetallePresupuesto.objects.filter(presupuesto_id = idPresupuesto, detalle_id = 32).delete()
            hospital24 = DetallePresupuesto.objects.filter(presupuesto_id = idPresupuesto, detalle_id = 33).first()
            baremo = Baremo.objects.filter(detalle_id = 33).first()
            if baremo:
                if baremo.xcantidad:
                    venta_total = baremo.venta * hospital
                else:
                    venta_total = baremo.venta
                        
            if hospital24:
                if hospital24.cantidad != hospital:
                    DetallePresupuesto.objects.filter(presupuesto_id = idPresupuesto, detalle_id = 33).update(
                        cantidad = hospital,
                        precio = venta_total,
                        usuario_id = request.user.id,
                    )
                    
            else:
                    DetallePresupuesto.objects.create(
                        cantidad = hospital,
                        precio = venta_total,
                        fecha_cambio = datetime.now().date(),
                        convenio_id = baremo.convenio_id,
                        detalle_id = baremo.detalle_id,
                        grupo_id = baremo.grupo_id,
                        plantilla_id = baremo.plantilla_id,
                        unidad_id = baremo.unidad_id,
                        usuario_id = request.user.id,
                        presupuesto_id = idPresupuesto,
                        ntqx = baremo.ntqx,
                        alertaexcedente = True,
                    ) """
        
        """ detalle_horasqx = DetallePresupuesto.objects.filter(presupuesto_id = idPresupuesto)           
        for detalle in detalle_horasqx:
            precio = ComposicionDetalle.objects.filter(convenio_id=detalle.convenio_id,grupo_id=detalle.grupo_id,detalle_id=detalle.detalle_id,cantidad=horasQx).first()
            if precio:
                DetallePresupuesto.objects.filter(id = detalle.id ).update(
                    precio = precio.venta,
                    cantidad = horasQx,
                    usuario_id = request.user.id,
                ) """

        data = {
            'nombre': 'No existe codigo',
        }

        return JsonResponse(data)
    else:
        return JsonResponse({'mensaje': 'Error al eliminar detalle'})

def actualizardatospresupuestoHosp(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idPresupuesto = datos['idPresupuesto']
        tipoProcedimiento = datos['tipoProcedimiento']
        medicoPpal = datos['medicoPpal']
        diagnostico = datos['diagnostico']
        procedimiento = datos['procedimiento']
        fechaProcedimiento = datos['fechaProcedimiento']
        horaProcedimiento = datos['horaProcedimiento']
        hospital = datos['hospital']
        horasQx = datos['horasQx']
        
        Presupuesto.objects.filter(id=idPresupuesto).update(
            fecha_procedimiento = fechaProcedimiento,
            tipo_procedimiento_id = tipoProcedimiento,
            medico_ppal_id = medicoPpal,
            diagnostico = diagnostico,
            nombre_procedimiento = procedimiento,
            dias_hospitalizacion = hospital,
            horas_qx = horasQx,
            hora_procedimiento = horaProcedimiento,
            usuario_id = request.user.id
        )
        hospital = int(hospital)
        if hospital == 0:
            DetallePresupuesto.objects.filter(presupuesto_id = idPresupuesto, detalle_id = 33).delete()
            ambulatorio = DetallePresupuesto.objects.filter(presupuesto_id = idPresupuesto, detalle_id = 32).exists()   
            if not ambulatorio:
                baremo = Baremo.objects.filter(detalle_id = 32).first()
                if baremo:
                    DetallePresupuesto.objects.create(
                        cantidad = baremo.cantidad,
                        precio = baremo.venta,
                        fecha_cambio = datetime.now(),
                        convenio_id = baremo.convenio_id,
                        detalle_id = baremo.detalle_id,
                        grupo_id = baremo.grupo_id,
                        plantilla_id = baremo.plantilla_id,
                        unidad_id = baremo.unidad_id,
                        usuario_id = request.user.id,
                        presupuesto_id = idPresupuesto,
                        ntqx = baremo.ntqx,
                        alertaexcedente = True,
                    )
        else:
            DetallePresupuesto.objects.filter(presupuesto_id = idPresupuesto, detalle_id = 32).delete()
            hospital24 = DetallePresupuesto.objects.filter(presupuesto_id = idPresupuesto, detalle_id = 33).first()
            baremo = Baremo.objects.filter(detalle_id = 33).first()
            if baremo:
                if baremo.xcantidad:
                    venta_total = baremo.venta * hospital
                else:
                    venta_total = baremo.venta
                        
            if hospital24:
                if hospital24.cantidad != hospital:
                    DetallePresupuesto.objects.filter(presupuesto_id = idPresupuesto, detalle_id = 33).update(
                        cantidad = hospital,
                        precio = venta_total,
                        usuario_id = request.user.id,
                        porcentaje_descuento_pr = 0,
                        monto_descuento_pr = 0
                    )
                    
            else:
                    DetallePresupuesto.objects.create(
                        cantidad = hospital,
                        precio = venta_total,
                        fecha_cambio = datetime.now().date(),
                        convenio_id = baremo.convenio_id,
                        detalle_id = baremo.detalle_id,
                        grupo_id = baremo.grupo_id,
                        plantilla_id = baremo.plantilla_id,
                        unidad_id = baremo.unidad_id,
                        usuario_id = request.user.id,
                        presupuesto_id = idPresupuesto,
                        ntqx = baremo.ntqx,
                        alertaexcedente = True,
                    )
        
        """ detalle_horasqx = DetallePresupuesto.objects.filter(presupuesto_id = idPresupuesto)           
        for detalle in detalle_horasqx:
            precio = ComposicionDetalle.objects.filter(convenio_id=detalle.convenio_id,grupo_id=detalle.grupo_id,detalle_id=detalle.detalle_id,cantidad=horasQx).first()
            if precio:
                DetallePresupuesto.objects.filter(id = detalle.id ).update(
                    precio = precio.venta,
                    cantidad = horasQx,
                    usuario_id = request.user.id,
                ) """

        data = {
            'nombre': 'No existe codigo',
        }

        return JsonResponse(data)
    else:
        return JsonResponse({'mensaje': 'Error al eliminar detalle'})

def actualizardatospresupuestoHqx(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idPresupuesto = datos['idPresupuesto']
        tipoProcedimiento = datos['tipoProcedimiento']
        medicoPpal = datos['medicoPpal']
        diagnostico = datos['diagnostico']
        procedimiento = datos['procedimiento']
        fechaProcedimiento = datos['fechaProcedimiento']
        horaProcedimiento = datos['horaProcedimiento']
        hospital = datos['hospital']
        horasQx = datos['horasQx']
        
        Presupuesto.objects.filter(id=idPresupuesto).update(
            horas_qx = horasQx,
            usuario_id = request.user.id
        )
       
        
        detalle_horasqx = DetallePresupuesto.objects.filter(presupuesto_id = idPresupuesto)           
        for detalle in detalle_horasqx:
            precio = ComposicionDetalle.objects.filter(convenio_id=detalle.convenio_id,grupo_id=detalle.grupo_id,detalle_id=detalle.detalle_id,cantidad=horasQx).first()
            if precio:
                DetallePresupuesto.objects.filter(id = detalle.id ).update(
                    precio = precio.venta,
                    cantidad = horasQx,
                    usuario_id = request.user.id,
                    porcentaje_descuento_pr = 0,
                    monto_descuento_pr = 0
                )

        data = {
            'nombre': 'No existe codigo',
        }

        return JsonResponse(data)
    else:
        return JsonResponse({'mensaje': 'Error al eliminar detalle'})


def actualizar_precio_detalle(request):
    cantidad = request.GET.get('cantidad1')
    idDetalle = request.GET.get('idDetalle')
    datosdetalle = DetallePresupuesto.objects.filter(id=idDetalle).first()
    convenio_id = datosdetalle.convenio_id
    grupo_id = datosdetalle.grupo_id
    detalle_id=datosdetalle.detalle_id
    cantidad_entera = int(float(cantidad))  
    baremo = Baremo.objects.filter(detalle_id=detalle_id,grupo_id=grupo_id,convenio_id=convenio_id).first()
    id_baremo = baremo.id
    # Realiza la operación que necesites con la cantidad y el baremo
    convenio_id = baremo.convenio_id
    precio_baremo = baremo.venta
    if baremo.xcantidad:
        precio_baremo = baremo.venta * cantidad_entera
        
        
    grupo_id = baremo.grupo_id
    detalle_id = baremo.detalle_id
    precio = ComposicionDetalle.objects.filter(convenio_id=convenio_id,grupo_id=grupo_id,detalle_id=detalle_id,cantidad=cantidad_entera).first()
    if precio:
        total_hr_qx=precio.venta
    else:
        total_hr_qx=precio_baremo
    
    detalle_presupuesto = DetallePresupuesto.objects.filter(id=idDetalle).first()
    DetallePresupuesto.objects.filter(id=idDetalle).update(
        cantidad = cantidad,
        precio = total_hr_qx,
        usuario_id = request.user.id
    )
    
    LogEliminacion.objects.create(
        descripcion='Modificacion de la cantidad en detalle de presupuesto '+str(detalle_presupuesto.presupuesto_id)+ ' detalle: '+str(detalle_presupuesto.detalle),
        usuario_id = request.user.id
    )
    
    if datosdetalle:
        actualizarCuentaxCobrar(datosdetalle.presupuesto_id,datosdetalle.presupuesto.paciente_id, request.user.id )
    

    return JsonResponse({'precio': total_hr_qx})

def actualizar_precio_detalle_cirugia_presupuesto(request):
    cantidad = request.GET.get('cantidad1')
    idDetalle = request.GET.get('idDetalle')
    cirugia_id = request.GET.get('cirugia_id')
    datosdetalle = DetallePresupuesto.objects.filter(id=idDetalle).first()
    convenio_id = datosdetalle.convenio_id
    grupo_id = datosdetalle.grupo_id
    detalle_id=datosdetalle.detalle_id
    cantidad_entera = int(float(cantidad))  
    baremo = Baremo.objects.filter(detalle_id=detalle_id,grupo_id=grupo_id,convenio_id=convenio_id, inactivar = False).first()
    # Realiza la operación que necesites con la cantidad y el baremo
    convenio_id = baremo.convenio_id
    precio_baremo = baremo.venta
    if baremo.xcantidad:
        precio_baremo = baremo.venta * cantidad_entera
        
 
    grupo_id = baremo.grupo_id
    detalle_id = baremo.detalle_id
    precio = ComposicionDetalle.objects.filter(convenio_id=convenio_id,grupo_id=grupo_id,detalle_id=detalle_id,cantidad=cantidad_entera).first()
    if precio:
        total_hr_qx=precio.venta
    else:
        total_hr_qx=precio_baremo
    
    DetallePresupuesto.objects.filter(id=idDetalle).update(
        cantidad_usada = cantidad,
        precio_usado = total_hr_qx,
        usuario_id = request.user.id
    ) 
    DetalleCirugia.objects.filter(cirugia_id = cirugia_id, detalle_id = detalle_id, grupo_id= grupo_id, convenio_id = convenio_id  ).update(
        cantidad = cantidad,
        precio = total_hr_qx
    )
    
    
    if datosdetalle.detalle_id == 33 or datosdetalle.detalle_id == 32:
        Cirugia.objects.filter(id = cirugia_id).update(
            dias_hospitalizacion = cantidad,
            usuario_id = request.user.id
        )
        Presupuesto.objects.filter(id = datosdetalle.presupuesto_id).update(
            dias_hospitalizacion = cantidad,
            usuario_id = request.user.id
        )
    

    return JsonResponse({'precio': 0})


def actualizarCuentaxCobrar(presupuesto_id, paciente_id, usuario_id):
    presupuesto_actualizar = Presupuesto.objects.filter(id = presupuesto_id).first()
    if presupuesto_actualizar:
        monto_nuevo = presupuesto_actualizar.total_monto_precio
    else:
        monto_nuevo = 0
        
    cuentaxcobrar = CuentaxCobrar.objects.filter(presupuesto_id = presupuesto_id ).first()
    if cuentaxcobrar and monto_nuevo > 0:
        DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuentaxcobrar.id, montocobrar__gte = 0).update(
            montocobrar = monto_nuevo,
            
        )
        LogCuentaCobrar.objects.create(
            monto_dl = monto_nuevo,
            usuario_id = usuario_id,
            presupuesto_id = presupuesto_id,
            nota = 'modificacion de actualizar_solo_precio_detalle de un presupuesto'
        )
        
    return


def actualizar_solo_precio_detalle(request):
    cantidad = request.GET.get('cantidad1')
    idDetalle = request.GET.get('idDetalle')
    DetallePresupuesto.objects.filter(id=idDetalle).update(
        precio = cantidad,
        usuario_id = request.user.id,
        porcentaje_descuento_pr = 0,
        monto_descuento_pr = 0

    )
    detalle_presupuesto = DetallePresupuesto.objects.filter(id=idDetalle).first()
    LogEliminacion.objects.create(
        descripcion='Modificacion de solo monto en detalle de presupuesto '+str(detalle_presupuesto.presupuesto_id)+ ' detalle: '+str(detalle_presupuesto.detalle),
        usuario_id = request.user.id
    )
    if detalle_presupuesto:
        actualizarCuentaxCobrar(detalle_presupuesto.presupuesto_id,detalle_presupuesto.presupuesto.paciente_id, request.user.id )
        
    

    return JsonResponse({'precio': cantidad})


def agregar_baremo_presupuesto(request):
    idBaremo = request.GET.get('idBaremo')
    idPresupuesto = request.GET.get('idPresupuesto')
    
    baremo = Baremo.objects.filter(id=idBaremo).first()
    presupuesto = Presupuesto.objects.filter(id=idPresupuesto).first()
    if baremo.cantidad == 0:
        cantidad_presupuesto = 1
    else:
        cantidad_presupuesto = baremo.cantidad

    if baremo.detalle_id == 33 or baremo.detalle_id == 32:
        if presupuesto.dias_hospitalizacion == 0:
            Presupuesto.objects.filter(id=idPresupuesto).update(
                dias_hospitalizacion = 1
            )


    DetallePresupuesto.objects.create(
        presupuesto_id = idPresupuesto,
        cantidad = cantidad_presupuesto,
        precio = baremo.venta,
        notas = 'Agregado en modificacion',
        convenio_id = baremo.convenio_id ,
        detalle_id = baremo.detalle_id,
        grupo_id = baremo.grupo_id,
        plantilla_id = baremo.plantilla_id ,
        usuario_id = request.user.id,

    )
    
    if baremo:
        vinculados = BaremoVinculado.objects.filter(detalle_principal_id = baremo.detalle_id)
        for vinculado in vinculados:
            baremovinculado = Baremo.objects.filter(inactivar = False, detalle_id = vinculado.detalle_baremo_id).first()
            if baremovinculado:
                DetallePresupuesto.objects.create(
                    presupuesto_id = idPresupuesto,
                    cantidad = cantidad_presupuesto,
                    precio = baremovinculado.venta,
                    notas = 'Agregado en modificacion',
                    convenio_id = baremovinculado.convenio_id ,
                    detalle_id = baremovinculado.detalle_id,
                    grupo_id = baremovinculado.grupo_id,
                    plantilla_id = baremovinculado.plantilla_id ,
                    usuario_id = request.user.id,

                )
    
    
    if presupuesto:
        actualizarCuentaxCobrar(presupuesto.id,presupuesto.paciente_id, request.user.id )
    
    

    return JsonResponse({'precio': idBaremo})


@add_group_name_to_context    
class ListadoSeguroPaciente(View): 
    template_name = 'listado_seguro_paciente.html'
    
    def get_context_data(self, cirugia_id):
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        total_items = ConsumoCirugia.objects.filter(cirugia_id=cirugia_id).count()
        
        if cirugia.congelar_moneda:
            tasa_bcv_calculo = cirugia.cambio_congelado
        else:
            tasa_bcv_calculo = CambioDiaBcv(datetime.now())

        total_usd = 0
        total_general_costo = 0
        subtotal_qx = subtotal_hp = subtotal_ud = 0
        consumos = ConsumoCirugia.objects.filter(cirugia_id=cirugia_id, conciliada = True).order_by(  'consumo__posicion', 'inventario__categoria', 'inventario__nombre')
        for consumo in consumos:
            #monto_venta = round(consumo.inventario.monto_venta,2)  # Asegúrate de que 'inventario' es el campo de relación
            #subtotal = consumo.cantidad_real_usada * Decimal(monto_venta)
            if consumo.venta == 0:
                consumo.venta = consumo.precio_unitario * consumo.cantidad_real_usada
                
                
            subtotal = consumo.venta
            if consumo.consumo_id == 1 or consumo.consumo_id == 5 or consumo.consumo_id == 8:
                subtotal_qx += subtotal

            if consumo.consumo_id == 2:
                subtotal_hp += subtotal

            if consumo.consumo_id == 10 or consumo.consumo_id == 9:
                subtotal_ud += subtotal

            subcosto = consumo.precio_costo_unitario
            if consumo.cantidad_real_usada > 0:
                consumo.precio_unitario = consumo.venta / consumo.cantidad_real_usada
            else:
                if consumo.cantidad_uso > 0:
                    consumo.precio_unitario = consumo.venta / consumo.cantidad_uso
                else:
                    consumo.precio_unitario = 0
            
            total_usd = Decimal(total_usd) + Decimal(subtotal)
            
            consumo.costo = subcosto
            consumo.subtcosto = Decimal(subcosto)*Decimal(consumo.cantidad_real_usada)
            consumo.subtotal = subtotal  # Puedes agregarlo como un atributo temporal
            consumo.subtotal_bs = Decimal(subtotal) * Decimal(tasa_bcv_calculo) # Puedes agregarlo como un atributo temporal
            total_general_costo += Decimal(subcosto)*Decimal(consumo.cantidad_real_usada)
        
        
        total_general_bs = total_usd * tasa_bcv_calculo
        total_general_usd = total_usd
        
        fecha_hoy = datetime.now()
        user = self.request.user 
        verCostos = self.request.user.groups.filter(Q(name='VerCostos')).exists()


        return {
            'verCostos': verCostos,
            'cirugia': cirugia,
            'subtotal_qx': subtotal_qx,
            'subtotal_ud' : subtotal_ud,
            'subtotal_hp' :subtotal_hp,
            'user': user,
            'tasa_bcv_calculo': tasa_bcv_calculo,
            'total_items': total_items,
            'total_general_bs': total_general_bs,
            'total_general_usd': total_general_usd,
            'total_general_costo': total_general_costo,
            'consumos': consumos,
            'fecha_hoy': fecha_hoy,
        }

    def get(self, request, **kwargs):
        # Aquí puedes manejar la lógica de la vista si es necesario
        cirugia_id = self.kwargs['cirugia_id']
        context = self.get_context_data(cirugia_id)
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        cirugia_id = self.kwargs['cirugia_id']
        context = self.get_context_data(cirugia_id)

        html_string = render_to_string(self.template_name, context)
        html_string = html_string.replace('/static/', request.build_absolute_uri('/static/'))

        html = HTML(string=html_string)
        pdf = html.write_pdf()  # Genera el PDF en memoria
        nombre_archivo = f"consumo_historia_{cirugia_id}.pdf"
        # Crea la respuesta HTTP con el PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename='+nombre_archivo
        return response

@add_group_name_to_context    
class Presupuesto_PDF(View): 
    template_name = 'pdf_presupuesto.html'
    
    def get_context_data(self, presupuesto_id, moneda):
        #cirugia = Cirugia.objects.filter(id=presupuesto_id).first()
        presupuesto = Presupuesto.objects.filter(id=presupuesto_id).first()
        responsable  = Responsable.objects.filter(id=presupuesto.paciente.responsable_id).first()
        fecha_actual = datetime.now()
        if presupuesto.congelar_moneda:
            valor_bolivar_dia = presupuesto.cambio_congelado
        else:
            valor_bolivar_dia=CambioDiaBcv(fecha_actual)

        if moneda != 1:
            detallepresupuesto = DetallePresupuesto.objects.filter(
            presupuesto_id=presupuesto_id,
            precio__gt = 0
            ).annotate(
                bolivares=ExpressionWrapper(F('precio') * valor_bolivar_dia, output_field=DecimalField())
            ).order_by('detalle__posicion')
        else:
            detallepresupuesto = DetallePresupuesto.objects.filter(
            presupuesto_id=presupuesto_id,
            precio__gt = 0
            ).annotate(
                bolivares=ExpressionWrapper(F('precio') * 0, output_field=DecimalField())
            ).order_by('detalle__posicion')


        detallepresupuesto1 = DetallePresupuesto.objects.filter(
                presupuesto_id=presupuesto_id
            ).aggregate(total=Sum('precio'))

        total_general = detallepresupuesto1['total']
        
        grupos = [(k, list(g)) for k, g in groupby(detallepresupuesto, lambda x: x.grupo)]
        

        return {
            'total_general': total_general,
            'grupos': grupos,
            'moneda': moneda,
            'presupuesto': presupuesto,
            'responsable': responsable,
            'valor_bolivar_dia': valor_bolivar_dia,
            'detallepresupuesto': detallepresupuesto,
        }

    def get(self, request, **kwargs):
        # Aquí puedes manejar la lógica de la vista si es necesario
        presupuesto_id = self.kwargs['presupuesto_id']
        moneda = self.kwargs['moneda']
        context = self.get_context_data(presupuesto_id, moneda)
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        presupuesto_id = self.kwargs['presupuesto_id']
        moneda = self.kwargs['moneda']
        context = self.get_context_data(presupuesto_id, moneda)
        presupuesto = Presupuesto.objects.filter(id=presupuesto_id).first()
        destinatario_email = request.POST.get('destinatario_email')
        cc_emails = ['und.vizcaya@gmail.com']
        html_string = render_to_string(self.template_name, context)
        html_string = html_string.replace('/static/', request.build_absolute_uri('/static/'))

        html = HTML(string=html_string)
        pdf = html.write_pdf()  # Genera el PDF en memoria
        nombre_archivo = f"presupuesto_{presupuesto.paciente}.pdf"
        accion = request.POST.get('accion')
        if accion == 'btn_generar_enviar':
            email = EmailMessage(
                subject='Presupuesto Quirurgico',
                body='Adjunto encontrarás el presupuesto en formato PDF.',
                from_email='aemoreno1970@gmail.com',  # Cambia esto por tu correo
                to=[destinatario_email],  # Cambia esto por el correo del destinatario
                cc=cc_emails,
            )
            #email.attach(nombre_archivo, pdf, 'application/pdf')
            #email.send()
            
         
        # Crea la respuesta HTTP con el PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename='+nombre_archivo
        return response
       
@add_group_name_to_context    
class listado_producto_notaentrega(TemplateView): 
    template_name = 'listado_producto_notaentrega.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        productos_no_conciliados = ConsumoCirugia.objects.filter(conciliada=False, deposito__isnull = False )
       
        context['productos_no_conciliados'] = productos_no_conciliados
        return context


@add_group_name_to_context    
class listado_producto_inventario(TemplateView): 
    template_name = 'listado_producto_inventario.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        #productos = DetalleNotaEntrega.objects.filter(eninventario = False).order_by('nombre', 'categoria', 'notaentrega__proveedor_compra')
        #productos = Inventario.objects.all().prefetch_related('depositouso_set').order_by('nombre', 'categoria', 'proveedor')
        productos = Inventario.objects.filter(lote = 'xxx').order_by('-fecha_act')
        
        productos_solicitados = InventarioSolicitud.objects.filter(pendiente=True)
        if productos_solicitados:
            productos_solicitados = True
        else:
            productos_solicitados = False
       
        context['productos'] = productos
        context['productos_solicitados'] = productos_solicitados
        return context



def is_blank(variable):
    return not variable or variable.strip() == ''

def es_fecha_valida(fecha_str):
    try:
        # Intenta convertir la cadena a un objeto datetime
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')  # Cambia el formato según tus necesidades
        return True
    except ValueError:
        # Si ocurre un ValueError, la fecha no es válida
        return False

def convertir_a_fecha(fecha_str):
    # Mapeo de abreviaturas de meses a números
    meses = {
        'ene': 1,
        'feb': 2,
        'mar': 3,
        'abr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'ago': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dic': 12
    }
    
    # Extraer el mes y el año de la cadena
    mes_str, anio_str = fecha_str.split('-')
    
    # Convertir el mes a número y el año a cuatro dígitos
    mes = meses.get(mes_str)
    anio = int('20' + anio_str)  # Asumiendo que '24' se refiere a 2024

    if mes is None:
        raise ValueError("Mes no válido")

    # Crear un objeto datetime
    fecha = datetime(year=anio, month=mes, day=1)  # Usamos el día 1 como ejemplo
    return fecha


def corrida(request):
    noconciliado = ConsumoCirugia.objects.filter(conciliada=False,cirugia_id__lte = 882)
    if noconciliado:
        for noc in noconciliado:
            cantidad_rebajar = noc.cantidad_real_usada
            inventario_id = noc.inventario_id
            deposito_id = noc.deposito_id
            cirugia_id = noc.cirugia_id
            InventarioDescarga.objects.create(
                cantidad = cantidad_rebajar,
                deposito_id = deposito_id,
                inventario_id = inventario_id,
                usuario_id = request.user.id,
                tipodescarga_id = 8,
                cirugia_id = cirugia_id,
                nota = "Cirugias / Hospitalizacion [Conciliacion Manual]"
            )
            ConsumoCirugia.objects.filter(conciliada=False,cirugia_id = cirugia_id).update(
                conciliada = True
            )
            

    return redirect('index' )

def prefactura_pdf_xml2pdf(request, cirugia_id):
    # Aquí obtienes tu objeto presupuesto desde la base de datos
    #presupuesto = get_object_or_404(Presupuesto, id=presupuesto_id)
    cirugia = Cirugia.objects.filter(id=cirugia_id).first()

    if cirugia.congelar_moneda:
        cambio_calculo = cirugia.cambio_congelado
    else:
        cambio_calculo = CambioDiaBcv(datetime.now())

    totalabono = 0
    saldoactual=0
    totalabono_bs = 0
    saldoactual_bs =0
    cuentacobrar = CuentaxCobrar.objects.filter(cirugia_id=cirugia_id).first()
    if cuentacobrar:
        abonos = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id, montocobrar__lt = 0).aggregate(total_montocobrar=Sum('montocobrar'))
        totalabono = abonos['total_montocobrar'] or 0

        abonos_bs = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id, montocobrar_bs__lt = 0).aggregate(total_montocobrar=Sum('montocobrar_bs'))
        totalabono_bs = abonos_bs['total_montocobrar'] or 0

        saldo = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id).aggregate(total_montocobrar=Sum('montocobrar'))
        saldoactual = saldo['total_montocobrar'] or 0

    usuario_logueado = request.user.id
    objectos_detalle = []
    DetallePrefactura.objects.filter(cirugia_id = cirugia_id).delete()
    detallecirugia =  DetallePresupuesto.objects.filter(presupuesto_id=cirugia.presupuesto_id, cantidad__gte = 0).order_by('detalle__posicion')
    for detalle in detallecirugia:
        medico_participante = None
        medico = NotaQuirurgica.objects.filter(cirugia_id = cirugia_id, participante_id = detalle.detalle_id ).first()
        if medico:
            medico_participante = medico.medico_id

        if detalle.precio_usado == 0:
            montodescuento = (detalle.precio * (detalle.detalle.pagarmedico/100))
            precio_nuevo =  (detalle.precio - montodescuento)
            cantidad_usada = detalle.cantidad
        else:
            montodescuento = (detalle.precio_usado * (detalle.detalle.pagarmedico/100))
            precio_nuevo =  (detalle.precio_usado - montodescuento)
            cantidad_usada = detalle.detalle.cantidad_usada

        if montodescuento > 0:
            objectos_detalle.append(DetallePrefactura(cantidad_usada = 1 ,precio_usado = precio_nuevo,
                                            detalle_id=79 , tx =detalle.tx,
                                            fecha_creacion  = detalle.fecha_cambio ,convenio_id  =detalle.convenio_id ,
                                            grupo_id =12, plantilla_id =detalle.plantilla_id ,unidad_id  = 1,
                                            usuario_id = usuario_logueado, cirugia_id = cirugia_id,
                                            precio_congelado_cirugia = (precio_nuevo * cambio_calculo)
                                            ))


        objectos_detalle.append(DetallePrefactura(cantidad_usada = cantidad_usada  ,precio_usado = precio_nuevo,
                                            detalle_id=detalle.detalle_id , tx =detalle.tx,
                                            fecha_creacion  = detalle.fecha_cambio ,convenio_id  =detalle.convenio_id ,
                                            grupo_id =detalle.grupo_id, plantilla_id =detalle.plantilla_id ,unidad_id  = 1,
                                            usuario_id = usuario_logueado, cirugia_id = cirugia_id,
                                            precio_congelado_cirugia = (precio_nuevo * cambio_calculo),
                                            medico_id = medico_participante
                                            ))

            
    
    DetallePrefactura.objects.bulk_create(objectos_detalle)
    detallecirugia =  DetallePrefactura.objects.filter(cirugia_id=cirugia_id, cantidad_usada__gte = 0).order_by('detalle__posicion')
    subtotal_usd=0
    subtotal_bs=0
    detalle_agrupado = defaultdict(lambda: {'items': [], 'subtotal': 0, 'subtotalbs': 0})
    for detalle in detallecirugia:
        detalle_agrupado[detalle.grupo_id]['items'].append(detalle)
        detalle_agrupado[detalle.grupo_id]['subtotal'] += detalle.precio_usado   # Sumar el subtotal
        detalle_agrupado[detalle.grupo_id]['subtotalbs'] += detalle.precio_congelado_cirugia   # Sumar el subtotal
        subtotal_usd += detalle.precio_usado
        subtotal_bs += detalle.precio_congelado_cirugia

    # Obtener los nombres de los grupos
    grupo_ids = detalle_agrupado.keys()
    grupos = {grupo.id: grupo.nombre for grupo in GrupoBaremo.objects.filter(id__in=grupo_ids)}
    saldoactual_bs = (saldoactual * cambio_calculo)

    # Convertir el defaultdict a una lista para pasar a la plantilla
    detalle_agrupado_lista = [{'grupo_id': key, 'grupo_nombre': grupos[key], 'items': value['items'], 'subtotal': value['subtotal'], 'subtotalbs': value['subtotalbs']} for key, value in detalle_agrupado.items()]
        # Contexto para la plantilla
    context = {
            'cirugia': cirugia,
            'fecha_hoy': datetime.now(),
            'tasa_calculo': cambio_calculo,
            'subtotal_usd':subtotal_usd,
            'subtotal_bs':subtotal_bs,
            'totalabono' : totalabono,
            'totalabono_bs':totalabono_bs,
            'saldoactual' : saldoactual,
            'saldoactual_bs':saldoactual_bs,
            'detalle_agrupado': detalle_agrupado_lista  # Cambia 'detallecirugia' por 'detalle_agrupado'
        }
    
    # Renderiza tu plantilla HTML
    html_string = render_to_string('pre_factura.html', context)
    #html_string = render_to_string(self.template_name, context)
    html_string = html_string.replace('/static/', request.build_absolute_uri('/static/'))
    
    html = HTML(string=html_string)
    pdf = html.write_pdf()  # Genera el PDF en memoria
    nombre_archivo = f"prefactura_{cirugia_id}.pdf"
   
    # Crea la respuesta HTTP con el PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename='+nombre_archivo
    return response
       


@add_group_name_to_context    
class orden_de_compra(TemplateView): 
    template_name = 'orden_de_compra.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 

        return context


@add_group_name_to_context    
class editar_producto_inventario(UserPassesTestMixin, TemplateView): 
    template_name = 'editar_producto_inventario.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Inventario') | Q(name='Traslados') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        producto_id = self.kwargs['producto_id']
        prodinv = Inventario.objects.filter(id=producto_id).first()
        trasladosPpal = self.request.user.groups.filter(Q(name='Traslados')).exists()
        opciones = Inventario.COMPUESTO_CHOICES
        vencidos = InventarioHistoria.objects.filter(inventario_id = producto_id ).order_by('fecha_vencimiento')
        categorias = CategoriaInventario.objects.all()
        laboratorios = LaboratorioMedicina.objects.all()
        presentacion = PresentacionMedicina.objects.all()
        unidadcompra = UnidadCompra.objects.all().order_by('nombre')
        depositouso = DepositoUso.objects.filter(inventario_id=producto_id, inventario__producto_activo =True).order_by('deposito__nombre')
        tipodescarga = TipoDescarga.objects.all().order_by('nombre')
        if trasladosPpal:
            depositos = Deposito.objects.filter(id__in = [1,2]).order_by('nombre')
        else:
            depositos = Deposito.objects.all().order_by('nombre')
            
        montoincremento = MontoIncremento.objects.all().first()
        salida_total = InventarioDescarga.objects.filter(inventario_id=producto_id, deposito_id__isnull = False)
        total_cantidad = salida_total.aggregate(total=Sum('cantidad'))['total']
        cantidad_total_producto = depositouso.aggregate(total=Sum('cantidad_deposito'))['total']
        
        

        # Si no hay resultados, total_cantidad será None, así que puedes manejarlo si es necesario
        if cantidad_total_producto is None:
            cantidad_total_producto = 0  # O cualquier otro valor que desees asignar
        
        if total_cantidad is None:
            total_cantidad = 0  # O cualquier otro valor que desees asignar
        
        
        cambioInventario = self.request.user.groups.filter(Q(name='CambiarInventario')).exists()
        habilitarInventario = self.request.user.groups.filter(Q(name='HabilitarInventario')).exists()
        
        
        cantidad_total_producto_und = cantidad_total_producto 
        existencia_out = cantidad_total_producto_und - total_cantidad
        existencia = existencia_out 
        fecha_hoy = datetime.now().date()

        context['habilitarInventario'] = habilitarInventario
        context['montoincremento'] = montoincremento.porcentaje/100
        context['existencia_out'] = existencia_out
        context['cambioInventario'] = cambioInventario
        context['trasladosPpal'] = trasladosPpal
        context['total_cantidad'] = total_cantidad
        context['laboratorios'] = laboratorios
        context['presentacion'] = presentacion
        context['tipodescarga'] = tipodescarga
        context['unidadcompra'] = unidadcompra
        context['depositouso'] = depositouso
        context['existencia'] = existencia
        context['categorias'] = categorias
        context['fecha_hoy'] = fecha_hoy
        context['depositos'] = depositos
        context['opciones'] = opciones
        context['vencidos'] = vencidos
        context['prodinv'] = prodinv

        return context
    
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        producto_id = self.kwargs['producto_id']
        ventaUpdate = self.request.POST.get('ventaUpdate').replace(',','.')
        costoUpdate = self.request.POST.get('costoUpdate').replace(',','.')
        pivaUpdate = self.request.POST.get('pivaUpdate').replace(',','.')
        datalistnombre = self.request.POST.get('datalistnombre')
        nombreComercialUpdate = self.request.POST.get('nombreComercialUpdate')
        #loteUpdate = self.request.POST.get('loteUpdate')
        compuesto = self.request.POST.get('namecompuesto')
        #conversion = self.request.POST.get('conversion').replace(',','.')
        fechaelaboraUpdate = self.request.POST.get('fechaelaboraUpdate')
        fechavenceUpdate = self.request.POST.get('fechavenceUpdate')
        categoriaUpdate = self.request.POST.get('categoriaUpdate')
        #laboratorioUpdate = self.request.POST.get('laboratorioUpdate')
        presentacion_entradaUpdate = self.request.POST.get('presentacion_entradaUpdate')
        #presentacion_salidaUpdate = self.request.POST.get('presentacion_salidaUpdate')
        #unidad_compra = self.request.POST.get('unidad_compra')
        cantidad_minima = self.request.POST.get('cantidad_minima')
        cantidad_critica = self.request.POST.get('cantidad_critica')
        producto_activo = request.POST.get("desactivado")
        producto_reusable = request.POST.get("reusable")

        nombre_categoria = CategoriaInventario.objects.filter(id = categoriaUpdate ).first()
        cod3 = nombre_categoria.nombre[:3]
        
        if producto_activo == None:
            producto_activo = False
        else:
            producto_activo = True

        if producto_reusable == None:
            producto_reusable = False
        else:
            producto_reusable = True
               

        if not costoUpdate:
            costoUpdate = 0

        if ventaUpdate:
            # Obtén el objeto de Inventario
            inventario = Inventario.objects.get(id=producto_id)
            codigo_numerico = inventario.codigo[3:]
            nuevo_codigo = cod3 + codigo_numerico
            inventario.codigo = nuevo_codigo
            # Actualiza los campos necesarios
            inventario.costo = costoUpdate
            inventario.venta = ventaUpdate
            inventario.piva = pivaUpdate
            inventario.categoria_id = categoriaUpdate
            inventario.nombre = datalistnombre
            inventario.nombre_comercial = nombreComercialUpdate
            #inventario.laboratorio_id = laboratorioUpdate
            inventario.presentacion_id = presentacion_entradaUpdate
            #inventario.presentacion_salida_id = presentacion_salidaUpdate
            #inventario.lote = loteUpdate
            #inventario.unidadcompra_id = unidad_compra
            inventario.fecha_elaboracion = fechaelaboraUpdate
            inventario.fecha_vencimiento = fechavenceUpdate
            inventario.cantidad_min = cantidad_minima
            inventario.cantidad_cri = cantidad_critica
            inventario.usuario_id = self.request.user.id
            inventario.compuesto = compuesto
            inventario.producto_activo = producto_activo
            inventario.reusable = producto_reusable
            # Guarda el objeto, lo que actualizará fecha_act
            inventario.save()
                    
        
        return redirect('listado_producto_inventario')


@add_group_name_to_context    
class create_producto_inventario(UserPassesTestMixin, TemplateView): 
    template_name = 'create_producto_inventario.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Inventario') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        categorias = CategoriaInventario.objects.all()
        laboratorios = LaboratorioMedicina.objects.all()
        presentacion = PresentacionMedicina.objects.all()
        unidadcompra = UnidadCompra.objects.all().order_by('nombre')
        tipodescarga = TipoDescarga.objects.all().order_by('nombre')
        depositos = Deposito.objects.all().order_by('nombre')
        montoincremento = MontoIncremento.objects.all().first()
        productos = Inventario.objects.filter(producto_activo = True).order_by('nombre')
        
        # Calcular existencia
        fecha_hoy = datetime.now()

        context['montoincremento'] = montoincremento.porcentaje/100
        context['laboratorios'] = laboratorios
        context['presentacion'] = presentacion
        context['tipodescarga'] = tipodescarga
        context['unidadcompra'] = unidadcompra
        context['unidadcompra'] = unidadcompra
        context['categorias'] = categorias
        context['fecha_hoy'] = fecha_hoy
        context['depositos'] = depositos
        context['productos'] = productos
        


        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        ventaUpdate = self.request.POST.get('ventaUpdate').replace(',','.')
        costoUpdate = self.request.POST.get('costoUpdate').replace(',','.')
        pivaNew = self.request.POST.get('pivaNew').replace(',','.')
        nombreUpdate = self.request.POST.get('nombreUpdate')
        nombreComercialUpdate = self.request.POST.get('nombreComercialUpdate')
        loteUpdate = self.request.POST.get('loteUpdate')
        conversion = self.request.POST.get('conversion').replace(',','.')
        fechaelaboraUpdate = self.request.POST.get('fechaelaboraUpdate')
        fechavenceUpdate = self.request.POST.get('fechavenceUpdate')
        
        categoriaNew = self.request.POST.get('categoriaNew')
        laboratorioUpdate = self.request.POST.get('laboratorioUpdate')
        presentacion_entradaUpdate = self.request.POST.get('presentacion_entradaUpdate')
        presentacion_salidaUpdate = self.request.POST.get('presentacion_salidaUpdate')
        unidad_compra = self.request.POST.get('unidad_compra')
        cantidad_minima = self.request.POST.get('cantidad_minima')
        cantidad_critica = self.request.POST.get('cantidad_critica')

        nomcategoria = CategoriaInventario.objects.filter(id=categoriaNew).first()
        cod='XXX'
        if nomcategoria:
            cod = nomcategoria.nombre[:3]
            cod = cod.upper()

        max_id = Inventario.objects.aggregate(Max('id'))['id__max']
        consecutivo_codigo = max_id + 1
        
        inventario = Inventario.objects.create(
            codigo = cod + str(consecutivo_codigo).zfill(10),
            categoria_id = categoriaNew,
            laboratorio_id = laboratorioUpdate,
            presentacion_id = presentacion_entradaUpdate,
            presentacion_salida_id = presentacion_salidaUpdate,
            nombre = nombreUpdate,
            nombre_comercial = nombreComercialUpdate,
            lote = loteUpdate,
            usuario_id = self.request.user.id,
            fecha_elaboracion = fechaelaboraUpdate,
            fecha_vencimiento = fechavenceUpdate,
            unidadcompra_id = unidad_compra,
            venta = ventaUpdate,
            costo = costoUpdate,
            piva = pivaNew,
            unidad_conversion = conversion,
            cantidad_min = cantidad_minima,
            cantidad_cri = cantidad_critica

        )

        inventario.save()
        inventario_id = inventario.id
        depositouso = DepositoUso.objects.filter(inventario_id__isnull=True).order_by('deposito_id')
        for i in range(1, len(depositouso) + 1):
            id_deposito = request.POST.get(f'iddepositotransito_{i}')
            cantidad_deposito = request.POST.get(f'cantidaddeposito_{i}').replace(',','.')
            
            if id_deposito :
                DepositoUso.objects.create(
                    inventario_id = inventario_id,
                    deposito_id = id_deposito,
                    cantidad_deposito = cantidad_deposito,
                    usuario_id = self.request.user.id,

                )
                # Aquí puedes guardar los datos en tu modelo
                #DepositoUso.objects.create(deposito_id=id_deposito, cantidad=cantidad_deposito)

        return redirect('listado_producto_inventario')

def DepositoUpdate(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idDepositouso = datos['idDepositouso']
        newCantidad = datos['newCantidad'].replace(',','.')
        depositouso = DepositoUso.objects.get(id=idDepositouso)
        depositouso.cantidad_deposito = newCantidad

        depositouso.save()
    return JsonResponse({'success': True, 'message': 'Data received', })

def refresh_tableDepositoUso(request):
    idProducto = request.GET.get('idProducto')

    depositouso = DepositoUso.objects.filter(inventario_id=idProducto, inventario__producto_activo =True).order_by('deposito__nombre')

    return render(request, 'tabla_deposito_uso.html', { 'depositouso':depositouso}) 

def refresh_materia_prima(request):
    idProducto = request.GET.get('idProducto')
    if idProducto:
        materiaprima = MateriaPrimaInventario.objects.filter(producto_terminado_id=idProducto).order_by('producto_terminado__nombre')
        total_subtotal = materiaprima.aggregate(total=Coalesce(Sum('subtotal_precio_dl'), 0, output_field=DecimalField()))['total']
    else:
        materiaprima = []
        total_subtotal = 0


    montoincremento = MontoIncremento.objects.all().first()


    # Renderiza el template a una cadena HTML
    html = render_to_string('tabla_productos_terminados.html', {
        'materiaprima': materiaprima,
        'total_subtotal': total_subtotal
    })
    
    # Devuelve JSON con el HTML y el total
    return JsonResponse({
        'html': html,
        'total_subtotal': float(total_subtotal),  # Convierte a float para compatibilidad con JSON
        'montoincremento': float(montoincremento.porcentaje/100)
    })

def refresh_tableDepositoUsoDownload(request):
    idInventario = request.GET.get('idInventario')

    depositouso = DepositoUso.objects.filter(inventario_id=idInventario,cantidad_deposito__gt = 0, inventario__producto_activo =True ).order_by('deposito__nombre')

    return render(request, 'tabla_deposito_uso_download.html', { 'depositouso':depositouso}) 


def agregarUnidadCompra(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nomunidadcompra = datos['nomunidadcompra']

        unidadnew = UnidadCompra.objects.filter(nombre = nomunidadcompra).first()
        if not unidadnew:
            UnidadCompra.objects.create(
                nombre = nomunidadcompra
            )

    return JsonResponse({'success': True, 'message': 'Data received', })




@add_group_name_to_context    
class movimiento_producto(TemplateView): 
    template_name = 'movimiento_inventario.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        producto_id = self.kwargs['producto_id']
        producto = Inventario.objects.filter(id = producto_id).first()
        context['producto_id'] = producto_id
        context['producto'] = producto
        return context
    
    
def list_movimiento_producto(request): 
    inventario_id = request.GET.get('inventario_id')
    #producto = Inventario.objects.filter(id=producto_id).first()
    #productos = InventarioDescarga.objects.filter(inventario_id=producto_id).order_by('-fecha_act')
    productos = list(InventarioDescarga.objects.filter(inventario_id = inventario_id ).order_by('-id').values('id', 'cirugia_id' , 'fecha_act' , 'cantidad', 'nota', 'tipodescarga__nombre', 'deposito', 'deposito__nombre', 'depositoentrada', 'depositoentrada__nombre', 'usuario__username','cantidad_traslado'))
    data={'productos':productos}
    return JsonResponse(data)


def list_factura_producto(request): 
    inventario_id = request.GET.get('inventario_id')
    #facturascompra = FacturaProveedor.objects.filter(tipo__in = ['FC','FI']).order_by('-id')
    facturas = list(FacturaProveedor.objects.filter(tipo__in = ['FC','FI']).order_by('-id').values('id', 'fecha_entrega' , 'proveedor_compra__nombre' , 'notaentrega__numerodocumento', 'numerodocumento', 'numerocontrol', 'concepto__nombre', 'tipomoneda__nombre', 'tipodocumento__nombre', 'porcentaje_retencion_islr','proveedor_compra__porcentaje_retencion', 'proveedor_compra__rif','comprobante_id', 'comprobante__comprobante', 'proveedor_compra_id', 'tipodocumento_id' ))
    data={'productos':facturas}
    return JsonResponse(data)
    

def descargar_inventario(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        iddepositouso = datos['iddepositouso']
        cantidadDescargar = datos['cantidadDescargar']
        cantidadDescargar = float(cantidadDescargar)
        tipoDescarga = datos['tipoDescarga']
        nota = datos['nota']
        depositoentrada = datos['depositoentrada']
        factorTraslado = datos['unidadejecuciontraslado']
       
       
        if depositoentrada == '0':
            depositoentrada = None


        depositodescargar = DepositoUso.objects.filter(id=iddepositouso).first()
        cantidadTraslado = 0

        if depositodescargar:
            inventario_id = depositodescargar.inventario_id
            deposito_id = depositodescargar.deposito_id
            unidad_conversion = Decimal(depositodescargar.inventario.unidad_conversion)
            cantidadDescargar = Decimal(cantidadDescargar)
            factor = 1
            if factorTraslado == '2':
                factor = cantidadDescargar
            else:
                factor = cantidadDescargar

            DepositoUso.objects.filter(id=iddepositouso, inventario_id=inventario_id).update(

                cantidad_deposito = F('cantidad_deposito')-(factor)
            )
            
            if depositoentrada is not None:
                DepositoUso.objects.filter(deposito_id=depositoentrada, inventario_id=inventario_id).update(
                    cantidad_deposito = F('cantidad_deposito')+(factor)
                )

            
            if tipoDescarga == '5':
                cantidadTraslado = cantidadDescargar
                cantidadDescargar = 0


            InventarioDescarga.objects.create(
                cantidad = cantidadDescargar,
                cantidad_traslado = cantidadTraslado,
                nota = nota,
                deposito_id = deposito_id ,
                inventario_id = inventario_id ,
                tipodescarga_id = tipoDescarga,
                usuario_id = request.user.id,
                depositoentrada_id = depositoentrada
            )

            

        return JsonResponse({'mensaje': 'CAMBIO DE TIPO DOCUMENTO FACTURA GUARDADO correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al TIPO DOCUMENTO EN  FACTURA'})


def dt_serverside_inventario(request):
    context = {}
    dt = request.GET 
    draw = int(dt.get("draw"))
    start = int(dt.get("start"))
    length = int(dt.get("length"))
    search = dt.get("search[value]")
    
    registros = Inventario.objects.filter(producto_activo = True).values_list('id','codigo' ,'nombre','presentacion_salida__nombre','categoria__nombre','unidad_conversion','piva','costo', 'venta' ,'laboratorio__nombre','nombre_comercial','fecha_vencimiento','cantidad_min','cantidad_cri').order_by("nombre")
    
    if search:
        registros = registros.filter(
            Q(codigo__icontains=search) |
            Q(nombre__icontains=search) |
            Q(nombre_comercial__icontains=search) |
            Q(categoria__nombre__icontains=search) 
        )
        
    recordsTotal = registros.count()
    recordsFiltered = recordsTotal
    
    context["draw"] = draw
    context["recordsTotal"] = recordsTotal
    context["recordsFiltered"] = recordsFiltered
    
    reg = registros[start:start + length]
    paginator = Paginator(reg, length)
    
    try:
        obj = paginator.page(draw).object_list
    except PageNotAnInteger:
        obj = paginator.page(draw).object_list
    except EmptyPage:
        obj = paginator.page(paginator.num_pages).object_list
        
 
    datos = [
        {
            "id" :d[0],
            "codigo" :d[1],
            "nombre" : d[2],
            "presentacion" : d[3],
            "cantidad_min" : d[12],
            "cantidad_cri" : d[13],
            "categoria" : d[4],
            "existencia" : round(Inventario.objects.get(id=d[0]).existencia, 2) ,
            "existencia_und": round(Inventario.objects.get(id=d[0]).existencia_und, 2) ,
            "unidad_conversion" : d[5],
            "piva" : d[6],
            "costo" : d[7],
            "monto_venta": round(Inventario.objects.get(id=d[0]).monto_venta, 2) ,
            "laboratorio" : d[9],
            "nombre_comercial" : d[10],
            "fecha_vencimiento" : d[11],
           
            "id" : d[0]
        } for d in obj
    ]


    context["datos"] = datos
    return JsonResponse(context,safe=False)


@add_group_name_to_context    
class pre_factura(TemplateView):
    template_name='pre_factura.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['cirugia_id']
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        #numero_factura = NumeracionFactura.objects.all().last()
        numero_factura = NumeracionFactura.objects.filter(cirugia__isnull = True).order_by('-numero_factura').first()
        id_factura_nueva = numero_factura.id
        new_invoice_number = numero_factura.numero_factura
        control_number = numero_factura.numero_control

        if cirugia.congelar_moneda:
            cambio_calculo = cirugia.cambio_congelado
        else:
            cambio_calculo = CambioDiaBcv(datetime.now())


        totalabono = 0
        saldoactual=0
        totalabono_bs = 0
        saldoactual_bs =0
        cuentacobrar = CuentaxCobrar.objects.filter(cirugia_id=cirugia_id).first()
        if cuentacobrar:
            abonos = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id, montocobrar__lt = 0).aggregate(total_montocobrar=Sum('montocobrar'))
            totalabono = abonos['total_montocobrar'] or 0

            abonos_bs = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id, montocobrar_bs__lt = 0).aggregate(total_montocobrar=Sum('montocobrar_bs'))
            totalabono_bs = abonos_bs['total_montocobrar'] or 0

            saldo = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id).aggregate(total_montocobrar=Sum('montocobrar'))
            saldoactual = saldo['total_montocobrar'] or 0
            
            
        objectos_detalle = []
        DetallePrefactura.objects.filter(factura_id = id_factura_nueva).delete()
        detallecirugia =  DetallePresupuesto.objects.filter(presupuesto_id=cirugia.presupuesto_id).order_by('detalle__posicion')
        for detalle in detallecirugia:
            if detalle.grupo_id == 7:
                grupo_factura = detalle.grupo_id
            else:
                grupo_factura = 8
                
                
            medico_participante = None
            medico = NotaQuirurgica.objects.filter(cirugia_id = cirugia_id, participante_id = detalle.detalle_id ).first()
            if medico:
                medico_participante = medico.medico_id


            if detalle.precio_usado == 0:
                montodescuento = (detalle.precio * (detalle.detalle.pagarmedico/100))
                precio_nuevo =  (detalle.precio - montodescuento)
                cantidad_usa = detalle.cantidad
            else:
                montodescuento = (detalle.precio_usado * (detalle.detalle.pagarmedico/100))
                precio_nuevo =  (detalle.precio_usado - montodescuento)
                cantidad_usa = detalle.cantidad_usada
           


            objectos_detalle.append(DetallePrefactura(cantidad_usada = cantidad_usa ,precio_usado = precio_nuevo,
                                                detalle_id=detalle.detalle_id , tx =detalle.tx,
                                                convenio_id  = detalle.convenio_id ,
                                                grupo_id = detalle.grupo_id, plantilla_id =detalle.plantilla_id ,unidad_id  = 1,
                                                usuario_id = self.request.user.id, 
                                                precio_congelado_cirugia = (precio_nuevo * cambio_calculo),
                                                medico_id = medico_participante,
                                                detallepresupuesto_id = detalle.id,
                                                grupo_factura = grupo_factura,
                                                factura_id = id_factura_nueva,
                                                cirugia_id = cirugia_id
                                                
                                                ))

                
        
        DetallePrefactura.objects.bulk_create(objectos_detalle)
        detallecirugia =  DetallePrefactura.objects.filter(factura_id = id_factura_nueva).order_by('detalle__posicion')

        detalle_agrupado = defaultdict(lambda: {'items': [], 'subtotal': 0, 'subtotalbs': 0})
        subtotal_usd = 0
        subtotal_bs = 0
        for detalle in detallecirugia:
            detalle_agrupado[detalle.grupo_factura]['items'].append(detalle)
            detalle_agrupado[detalle.grupo_factura]['subtotal'] += detalle.precio_usado   # Sumar el subtotal
            detalle_agrupado[detalle.grupo_factura]['subtotalbs'] += detalle.precio_congelado_cirugia   # Sumar el subtotal
            subtotal_usd += detalle.precio_usado
            subtotal_bs += detalle.precio_congelado_cirugia

        # Obtener los nombres de los grupos
        grupo_ids = detalle_agrupado.keys()
        grupos = {grupo.id: grupo.nombre for grupo in GrupoBaremo.objects.filter(id__in=grupo_ids)}
        saldoactual_bs = (saldoactual * cambio_calculo)
        # Convertir el defaultdict a una lista para pasar a la plantilla
        detalle_agrupado_lista = [{'grupo_id': key, 'grupo_nombre': grupos[key], 'items': value['items'], 'subtotal': value['subtotal'], 'subtotalbs': value['subtotalbs']} for key, value in detalle_agrupado.items()]
            # Contexto para la plantilla
        context = {
                'cirugia': cirugia,
                'tasa_calculo': cambio_calculo,
                'fecha_hoy': datetime.now(),
                'subtotal_usd' : subtotal_usd,
                'subtotal_bs':subtotal_bs,
                'totalabono' : totalabono,
                'totalabono_bs':totalabono_bs,
                'saldoactual' : saldoactual,
                'saldoactual_bs':saldoactual_bs,
                'detalle_agrupado': detalle_agrupado_lista  ,
                'new_invoice_number' : new_invoice_number,
                'control_number' : control_number
            }
        return context


def crear_banco_local(request):
    administrador = request.user.groups.filter(Q(name='SuperAdministracion')).exists()
    if administrador:
        if request.method == 'POST':
            form = BancoLocalForm(request.POST)
            if form.is_valid():
                # Obtener el número de cuenta ingresado
                form.save(user=request.user)
                    
                return redirect('crear_banco_local')  # Cambia esto por la vista a la que deseas redirigir
        else:
            bancos = BancoLocal.objects.all().order_by('nombrecuenta')
            form = BancoLocalForm()
        return render(request, 'bancolocalnew.html', {'form': form, 'bancos':bancos})
    else:
        return render(request, 'home.html')

@add_group_name_to_context   
class create_presentacion(UserPassesTestMixin,TemplateView):
    model = PresentacionMedicina
    template_name = 'create_presentacion.html'
    success_url = reverse_lazy('index')
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Inventario') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        presentacion = PresentacionMedicina.objects.all().order_by('-id')

        context['presentacion']=presentacion
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        inventario = Inventario.objects.filter(producto_activo = True)
        nombrenew = self.request.POST.get('nombrenew')
        if nombrenew:
            presentacion=PresentacionMedicina.objects.filter(nombre=nombrenew).first()
            if presentacion:
                pass
            else:
                PresentacionMedicina.objects.create(
                    nombre = nombrenew
                )
        

        return redirect('create_presentacion')

def cambiar_nombre_api(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nombre_aplicacion = 'appcc58'
        idCambiar = datos['idCambiar']
        newValue = datos['newValue']
        tableName =  datos['tableName']
        Modelo = apps.get_model(nombre_aplicacion,tableName)
        Modelo.objects.filter(id=idCambiar).update(
            nombre = newValue.upper()
        )
        

        return JsonResponse({'mensaje': 'Datos eliminados correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al eliminar datos'})

@add_group_name_to_context   
class create_labs(UserPassesTestMixin,TemplateView):
    model = LaboratorioMedicina
    template_name = 'create_labs.html'
    success_url = reverse_lazy('index')
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Inventario') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        laboratorio = LaboratorioMedicina.objects.all().order_by('-id')

        context['laboratorio']=laboratorio
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        nombrenew = self.request.POST.get('nombrenew')
        if nombrenew:
            laboratorio=LaboratorioMedicina.objects.filter(nombre=nombrenew).first()
            if laboratorio:
                pass
            else:
                LaboratorioMedicina.objects.create(
                    nombre = nombrenew.upper()
                )
        

        return redirect('create_labs')


def aplicar_precarga_cirugia(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nCant = datos['nCant']
        idDepositoUso = datos['idDepositoUso']
        idCirugia = datos['idCirugia']
        depositouso = DepositoUso.objects.filter(id=idDepositoUso).first()

        if depositouso:
            precio_costo_unitario = precio_costo_producto_inventario(depositouso.inventario_id)
            consumocirugia = ConsumoCirugia.objects.create(
                cantidad_uso = nCant,
                precio_unitario = depositouso.inventario.monto_venta,
                cirugia_id = idCirugia,
                inventario_id = depositouso.inventario.id,
                consumo_id = 5,
                cantidad_real_usada = nCant,
                farmacia = False,
                solicitante_id = request.user.id,
                entregado_id = request.user.id,
                nota = 'PreCarga de productos en Admision',
                usuario_id = request.user.id,
                conciliada = True,
                hora = datetime.now(),
                hora_uso = datetime.now(),
                venta = nCant * depositouso.inventario.monto_venta,
                deposito_id = depositouso.deposito.id,
                precio_costo_unitario = precio_costo_unitario

            )
            consumocirugia.save()
            consumo_id = consumocirugia.id 

            DetalleConsumoCirugia.objects.create(
                    consumocirugia_id=consumo_id,
                    precio_unitario = nCant * depositouso.inventario.monto_venta,
                    cantidad_uso = nCant,
                    hora = datetime.now(),
                    inventario_id = depositouso.inventario_id
            )
            
            InventarioDescarga.objects.create(
                cantidad = nCant,
                nota = 'PreCarga de productos en Admision',
                deposito_id = depositouso.deposito.id,
                inventario_id = depositouso.inventario.id,
                usuario_id = request.user.id,
                tipodescarga_id = 6,
                cirugia_id = idCirugia,
                consumocirugia_id = consumo_id
            )
        
        return JsonResponse({'mensaje': 'CANTIDAD REAL GUARDADOS EN CONSUMO correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al GUARDAR CANTIDAD REAL EN CONSUMO datos'})
    
def aplicar_precarga_cirugia_obligatoria(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idCirugia = datos['idCirugia']
        operacionAplicar = datos['operacionAplicar']
        if operacionAplicar == 'C':
            deposito_precarga = Deposito.objects.filter(precarga = True).first()
            productos_kit_precarga = Inventario.objects.filter(kit_id = 14, producto_activo = True)
            if productos_kit_precarga:
                for producto in productos_kit_precarga:
                    disponibilidad_deposito = DepositoUso.objects.filter(inventario_id = producto.id, deposito_id = deposito_precarga.id ).first()
                    if disponibilidad_deposito:
                        if producto.cantidad_kit <= disponibilidad_deposito.existenciaUnd:
                            cantidad_obligatoria = producto.cantidad_kit
                            notaPrecarga = 'PreCarga Obligatoria '
                            advertencia = False
                        else:
                            cantidad_obligatoria = disponibilidad_deposito.existenciaUnd
                            notaPrecarga = 'Se Asigna esta cantidad por falta de disponibilidad en deposito :'+str(disponibilidad_deposito.deposito)
                            advertencia = True
                        
                        if cantidad_obligatoria > 0:   
                            precio_costo_unitario = precio_costo_producto_inventario(producto.id) 
                            consumocirugia = ConsumoCirugia.objects.create(
                                cantidad_uso = cantidad_obligatoria,
                                precio_unitario = producto.venta_kit,
                                cirugia_id = idCirugia,
                                inventario_id = producto.id,
                                consumo_id = 5,
                                cantidad_real_usada = cantidad_obligatoria,
                                farmacia = False,
                                solicitante_id = request.user.id,
                                entregado_id = request.user.id,
                                nota = notaPrecarga,
                                usuario_id = request.user.id,
                                conciliada = True,
                                hora = datetime.now(),
                                hora_uso = datetime.now(),
                                venta =  producto.venta_kit,
                                deposito_id = deposito_precarga.id,
                                obligatoria =  True,
                                advertencia = advertencia,
                                precio_costo_unitario = precio_costo_unitario
                                )
                            
                            InventarioDescarga.objects.create(
                                cantidad = cantidad_obligatoria,
                                nota = notaPrecarga,
                                deposito_id = deposito_precarga.id,
                                inventario_id = producto.id,
                                usuario_id = request.user.id,
                                tipodescarga_id = 6,
                                cirugia_id = idCirugia,
                                consumocirugia_id = consumocirugia.id
                            )
                        
                        
        else:
            Cirugia.objects.filter(id = idCirugia ).update(
                precarga = True,
                usuario = request.user.id
            )
            ConsumoCirugia.objects.filter(cirugia_id = idCirugia, consumo_id = 5 ).delete()
                            
        
        return JsonResponse({'mensaje': 'CANTIDAD REAL GUARDADOS EN CONSUMO correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al GUARDAR CANTIDAD REAL EN CONSUMO datos'})



def obtener_consumoPrecarga(request):
    id_cirugia = request.GET.get('idCirugia')
    consumo_precarga = []
    deposito_precarga = Deposito.objects.filter(precarga=True).first()
    #disponible_deposito = DepositoUso.objects.filter(deposito_id=deposito_precarga.id).order_by('inventario__nombre')
    #disponible_deposito = DepositoUso.objects.filter(deposito_id = deposito_precarga.id, cantidad_deposito__gt = 0)
    hay_precargaobligatoria = ConsumoCirugia.objects.filter(cirugia_id=id_cirugia, consumo_id = 5).count()
    if deposito_precarga:
        consumo_precarga = ConsumoCirugia.objects.filter(cirugia_id=id_cirugia, consumo_id = 5)
        
    
    html = render_to_string('my_tabla_precarga_admision.html', {
        'consumo_precarga': consumo_precarga,
        'hay_precargaobligatoria': hay_precargaobligatoria,
       
       
    })
    return JsonResponse({'html': html}) 
    
        
    #return render(request, 'my_tabla_precarga_admision.html', {'consumo_precarga': consumo_precarga, 'hay_precargaobligatoria':hay_precargaobligatoria, 'disponible_deposito':disponible_deposito})
    
    
def obtener_disponible_precarga(request):
    id_cirugia = request.GET.get('idCirugia')
    deposito_precarga = Deposito.objects.filter(precarga=True).first()
    disponible_deposito = DepositoUso.objects.filter(deposito_id = deposito_precarga.id, cantidad_deposito__gt = 0, inventario__producto_activo =True)
        
    
    html = render_to_string('my_tabla_disponible_precarga.html', {
        'disponible_deposito': disponible_deposito,
    })
    return JsonResponse({'html': html}) 

def eliminar_Precarga(request):
    idConsumoprecarga = request.GET.get('idConsumoprecarga')
    if idConsumoprecarga:
        ConsumoCirugia.objects.filter(id=idConsumoprecarga).delete()

    return JsonResponse({'mensaje': 'Datos eliminado en consumo precarga correctamente'})


def rebajarPrecargaDeposito(request):
    datos = json.loads(request.body)
    idCirugia = datos['idCirugia']
    #deposito_precarga = Deposito.objects.filter(precarga=True).first()
    
    """ if deposito_precarga:
        rebajarconsumo = ConsumoCirugia.objects.filter(deposito_id = deposito_precarga.id, cirugia_id = idCirugia, obligatoria = False )
        if rebajarconsumo:
            for rebajar in rebajarconsumo:
                InventarioDescarga.objects.create(
                    cantidad = rebajar.cantidad_real_usada,
                    nota = 'Asignado en Precarga Medicinas',
                    deposito_id  = deposito_precarga.id,
                    inventario_id = rebajar.inventario.id,
                    tipodescarga_id = 6,
                    cirugia_id = idCirugia,
                    usuario_id = request.user.id) """

    Cirugia.objects.filter(id=idCirugia).update(
        precarga = 0,
        usuario_id = request.user.id
        )


    return JsonResponse({'mensaje': 'Datos rebajados de inventario precarga correctamente'})

def resfresh_tabla_inventario(request):
    idDeposito = request.GET.get('idDeposito')
    depositos = Deposito.objects.all().order_by('nombre')

    inventariodeposito = DepositoUso.objects.filter(deposito_id=idDeposito, cantidad_deposito__gt = 0, inventario__producto_activo =True).order_by('inventario__nombre')
    
        
    return render(request, 'tabla_inventario_kits.html', {'inventariodeposito': inventariodeposito, 'depositos':depositos})



def guardar_descargaInventario(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        valores = data.get('rowData', [])
        
        for item in valores:
            id_deposito = item.get('id_deposito')  # Captura el ID del depósito
            deposito_afectado = DepositoUso.objects.filter(id=id_deposito).first()
            motivoretiro_id = item.get('motivoretiro')
            entregar_id = item.get('entregar_a')
            nota = item.get('nota')
            codigodescarga = item.get('codigodescarga')
            #inventario_id = item.get('inventario_id')
            cantidad_a_descargar = item.get('cantidad_a_descargar').replace(',','.')
            #cantidad_deposito = item.get('cantidad_deposito').replace(',','.')
            if float(cantidad_a_descargar) > 0:
                InventarioDescarga.objects.create(
                        descargamanual = codigodescarga,
                        tipodescarga_id = motivoretiro_id,
                        usuario_id = request.user.id,
                        inventario_id = deposito_afectado.inventario_id,
                        deposito_id = deposito_afectado.deposito.id,
                        nota = nota, 
                        cantidad = cantidad_a_descargar,
                        persona_id = entregar_id
                        ) 
                
            
        
        return JsonResponse({'mensaje': 'Datos guardados exitosamente!'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def refresh_table_descarga_ajuste(request):
    codigodescarga = request.GET.get('codigodescarga')
    descargainventario = InventarioDescarga.objects.filter(descargamanual=codigodescarga, cirugia_id__isnull=True)
   
    return render(request, 'tabla_descarga.html', {
                                                    'descargainventario':descargainventario 
                                                  })


def eliminarDescargaAjuste(request):
    idDescarga = request.GET.get('idDescarga')
    codigo = request.GET.get('codigo')
    InventarioDescarga.objects.filter(id=idDescarga).delete()
    descargainventario = InventarioDescarga.objects.filter(descargamanual=codigo, cirugia_id__isnull=True)
   
    return render(request, 'tabla_descarga.html', {
                                                    'descargainventario':descargainventario 
                                                  })



@add_group_name_to_context    
class listado_salida_productos(TemplateView): 
    template_name = 'listado_salida_productos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        print('ini', datetime.now())
        fecha_hoy = datetime.now()
        descargados = InventarioDescarga.objects.filter(depositoentrada__isnull = True).exclude(tipodescarga_id=5).order_by('-id')
        productos_solicitados = InventarioSolicitud.objects.filter(pendiente=True)
        if productos_solicitados:
            productos_solicitados = True
        else:
            productos_solicitados = False


        print('fin', datetime.now())
        context['fecha_hoy'] = fecha_hoy
        context['descargados'] = descargados
        context['productos_solicitados'] = productos_solicitados
        return context

@add_group_name_to_context    
class pdf_comprobante_inventario(TemplateView): 
    template_name = 'pdf_comprobante_inventario.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        codigodescarga = self.kwargs['codigodescarga']
        #cod_descarga = InventarioDescarga.objects.filter(id=descarga_id).first()
        documento = InventarioDescarga.objects.filter(descargamanual=codigodescarga).first()
        descargas = InventarioDescarga.objects.filter(descargamanual=codigodescarga)
        fecha_actual = datetime.now()
       
        context['descargas'] = descargas
        context['documento'] = documento
        context['fecha_actual'] = fecha_actual
        return context


@add_group_name_to_context    
class requisicion_inventario(TemplateView): 
    template_name = 'requisicion_inventario.html'
   
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        motivos=TipoDescarga.objects.filter(solicitud=True).order_by('nombre')
        inventariodeposito = DepositoUso.objects.filter(deposito_id__in = [4,7,8], cantidad_deposito__gt = 0, inventario__producto_activo =True)
        #Inventario.objects.all().order_by('nombre')
        solicitudpendiente = InventarioSolicitud.objects.filter(pendiente=True, solicitante_id = 1)

        context['motivos']=motivos
        context['inventariodeposito']=inventariodeposito
        context['solicitudpendiente']=solicitudpendiente
        return context

def agregarSolicituditem(request):
    itemIdInventario = request.GET.get('itemId')
    cantidad_solicitada = request.GET.get('cantidad')
    solicitante  = request.GET.get('nsolicitante')
    productosolicitar = Inventario.objects.filter(id=itemIdInventario, producto_activo=True).first()
    if productosolicitar:
        InventarioSolicitud.objects.create(
            cantidad = cantidad_solicitada,
            producto_id = productosolicitar.id,
            usuario_id = request.user.id,
            solicitante_id = solicitante
        )

    solicitudpendiente = InventarioSolicitud.objects.filter(pendiente=True, solicitante_id = solicitante)
   
    return render(request, 'tabla_solicitud.html', {
                                                    'solicitudpendiente':solicitudpendiente 
                                                  })


def eliminarSolicituditem(request):
    itemIdsolicitud = request.GET.get('itemId')
    InventarioSolicitud.objects.filter(id=itemIdsolicitud).delete()

    solicitudpendiente = InventarioSolicitud.objects.filter(pendiente=True)
   
    return render(request, 'tabla_solicitud.html', {
                                                    'solicitudpendiente':solicitudpendiente 
                                                  })


@add_group_name_to_context    
class procesar_solicitud_farmacia( UserPassesTestMixin, TemplateView): 
    template_name = 'procesar_solicitud_farmacia.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Inventario') | Q(name='Traslados')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
   
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        traslado = self.request.user.groups.filter(Q(name='Traslados')).exists()
        solicitudpendiente = InventarioSolicitud.objects.filter(pendiente=True).order_by('solicitante__nombre')
        if traslado:
            deposito_origen = Deposito.objects.filter(id = 4).order_by('nombre')
        else:
            deposito_origen = Deposito.objects.all().exclude(id=1).order_by('nombre')
        
        
        tipodescarga = TipoDescarga.objects.all().order_by('nombre')

        deposito_destino = 'FARMACIA'


        context['deposito_origen']=deposito_origen
        context['tipodescarga']=tipodescarga
        context['deposito_destino']=deposito_destino
        context['solicitudpendiente']=solicitudpendiente
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        for item in request.POST.getlist('item_id'):
            cantidad_despachar = request.POST.get(f'cantidad_pedida_{item}')
            datos_solicitud = InventarioSolicitud.objects.filter(id=item,pendiente=True).first()
            if datos_solicitud:
                deposito_descarga_id = datos_solicitud.depositoorigen_id
                deposito_solicitante_id = datos_solicitud.solicitante_id
                #cantidad = datos_solicitud.cantidad
                inventario_id = datos_solicitud.producto_id
                existencia = datos_solicitud.existenciaorigen
                cantidad = Decimal(cantidad_despachar.replace(',','.'))
                existencia = Decimal(existencia)
                inventario = Inventario.objects.filter(id=inventario_id).first()
                if cantidad <= existencia:
                    InventarioSolicitud.objects.filter(id=item,pendiente=True, solicitante_id = deposito_solicitante_id).update(
                        pendiente = False,
                        usuario_id = request.user.id
                    )
                    DepositoUso.objects.filter(deposito_id=deposito_descarga_id, inventario_id=inventario_id).update(
                        cantidad_deposito = F('cantidad_deposito')-(cantidad/inventario.unidad_conversion)
                    )
                    
                    DepositoUso.objects.filter(deposito_id=deposito_solicitante_id, inventario_id=inventario_id).update(
                          cantidad_deposito = F('cantidad_deposito')+(cantidad/inventario.unidad_conversion)
                        )
                    
                    InventarioDescarga.objects.create(
                        cantidad_traslado = cantidad,
                        nota = 'Solicitud de Reposicion Farmacia',
                        deposito_id = deposito_descarga_id ,
                        inventario_id = inventario_id ,
                        tipodescarga_id = 5,
                        usuario_id = request.user.id,
                        depositoentrada_id = deposito_solicitante_id
                    )


        return redirect('listado_producto_inventario') 


def colocaExistenciaDeposito(request):
    idDeposito = request.GET.get('idDeposito')
    idSolicitud = request.GET.get('idSolicitud')
    solicitud=InventarioSolicitud.objects.filter(id=idSolicitud).first()
    if solicitud:
        if idDeposito != '':
            productodisponibilidad = DepositoUso.objects.filter(deposito_id=idDeposito,inventario_id=solicitud.producto_id).first()
            cantidad_disponible_deposito = productodisponibilidad.existenciaUnd
            InventarioSolicitud.objects.filter(id=idSolicitud).update(
                depositoorigen_id=idDeposito,
                existenciaorigen=cantidad_disponible_deposito
            )

    solicitudpendiente = InventarioSolicitud.objects.filter(pendiente=True)
    deposito_origen = Deposito.objects.all().exclude(id=1).order_by('nombre')

    return render(request, 'procesar_solicitud_farmacia.html', {'solicitudpendiente':solicitudpendiente, 'deposito_origen':deposito_origen})

    

        
def filtra_fecha_salida(request):
    fecha_desde = request.GET.get('desde')
    fecha_hasta = request.GET.get('hasta')
    fecha_desde = timezone.datetime.strptime(fecha_desde, '%Y-%m-%d')
    fecha_hasta = timezone.datetime.strptime(fecha_hasta, '%Y-%m-%d') + timezone.timedelta(days=1) - timezone.timedelta(seconds=1)
    descargados = InventarioDescarga.objects.filter(fecha_act__range=(fecha_desde, fecha_hasta)).exclude(tipodescarga_id=5)

    return render(request, 'tabla_salida_productos.html', {
                                                    'descargados':descargados 
                                                  })

@add_group_name_to_context   
class create_tipo_descarga(UserPassesTestMixin,TemplateView):
    model = TipoDescarga
    template_name = 'create_tipo_descarga.html'
    success_url = reverse_lazy('index')
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Inventario') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        descargas = TipoDescarga.objects.all().order_by('nombre')

        context['descargas']=descargas
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        nombredescarga = self.request.POST.get('nombredescarga')
        descripciondescarga = self.request.POST.get('descripciondescarga')
        if nombredescarga:
            descargas = TipoDescarga.objects.filter(nombre=nombredescarga).first()
            if not descargas:
                descarganew = TipoDescarga.objects.create(
                    nombre=nombredescarga,
                    descripcion=descripciondescarga
                )
                descarganew.save()

        descargas = TipoDescarga.objects.all().order_by('nombre')
        context['descargas']=descargas
        return redirect('create_tipo_descarga' )

@add_group_name_to_context   
class create_categoria(UserPassesTestMixin,TemplateView):
    model = CategoriaInventario
    template_name = 'create_categoria.html'
    success_url = reverse_lazy('index')
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Inventario') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categorias = CategoriaInventario.objects.all().order_by('nombre')

        context['categorias']=categorias
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        nombrecategoria = self.request.POST.get('nombrecategoria')
        if nombrecategoria:
            categorias = CategoriaInventario.objects.filter(nombre=nombrecategoria).first()
            if not categorias:
                categorianew = CategoriaInventario.objects.create(
                    nombre=nombrecategoria,
                )
                categorianew.save()

        categorias = CategoriaInventario.objects.all().order_by('nombre')
        context['categorias']=categorias
        return redirect('create_categoria' )

@add_group_name_to_context   
class create_unidad_compra(UserPassesTestMixin,TemplateView):
    model = UnidadCompra
    template_name = 'create_unidad_compra.html'
    success_url = reverse_lazy('index')
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Inventario') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unidad_compras = UnidadCompra.objects.all().order_by('nombre')

        context['unidad_compras']=unidad_compras
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        nombreunidad = self.request.POST.get('nombreunidad')
        if nombreunidad:
            unidad_compras = UnidadCompra.objects.filter(nombre=nombreunidad).first()
            if not unidad_compras:
                unidadnew = UnidadCompra.objects.create(
                    nombre=nombreunidad,
                )
                unidadnew.save()

        unidad_compras = UnidadCompra.objects.all().order_by('nombre')
        context['unidad_compras']=unidad_compras
        return redirect('create_unidad_compra' )


@add_group_name_to_context   
class listado_existencia(TemplateView):
    model = DepositoUso
    template_name = 'listado_existencia.html'
    success_url = reverse_lazy('index')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        existenciadepositos = DepositoUso.objects.filter(cantidad_deposito__gt = 0).select_related('inventario').order_by('inventario__nombre')
        context['existenciadepositos']=existenciadepositos
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
       
        return redirect('listado_existencia' )

@add_group_name_to_context    
class cargar_cantidades_nota_entrega(TemplateView):
    model = NotaEntregaCompra
    template_name = 'cargar_cantidades_nota_entrega.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nota_id = self.kwargs['nota_id']
        notaentrega = NotaEntregaCompra.objects.filter(id=nota_id, cantidad_inventario_actualizado=False).first()
        detallenotaentrega = DetalleNotaEntrega.objects.filter(notaentrega_id = nota_id).annotate(
            total_unidades_entrada=ExpressionWrapper(
                F('cantidad') * F('unidad_conversion'),
                output_field=DecimalField()
            )
        )

        context['notaentrega'] = notaentrega
        context['detallenotaentrega'] = detallenotaentrega
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        nota_id = self.kwargs['nota_id']

        productonota = NotaEntregaCompra.objects.filter(id=nota_id).first()
        productos_carga_cantidad = DetalleNotaEntrega.objects.filter(notaentrega_id = nota_id, notaentrega__cantidad_inventario_actualizado=False )
        if productos_carga_cantidad:
            for producto in productos_carga_cantidad:
                precio_unitario_producto = Decimal(producto.costo_dl) / Decimal(producto.unidad_conversion)
                producto_actualizar = Inventario.objects.filter(id=producto.inventario_id).first()
                if producto_actualizar:
                    if producto_actualizar.costo  > precio_unitario_producto:
                        nuevo_costo = producto_actualizar.costo 
                    else:
                        nuevo_costo = precio_unitario_producto
                
                    
                actualizacion = {
                    'proveedor_id': productonota.proveedor_compra_id,
                    'presentacion_salida_id': producto.presentacion_salida_id,
                    'unidadcompra_id': producto.unidadcompra_id,
                    'laboratorio_id': producto.laboratorio_id,
                    'lote': producto.lote,
                    'piva': producto.piva,
                    'costo': nuevo_costo,
                    'clasificacion': producto.clasificacion_id,
                    'usuario_id' : self.request.user.id
                }
                if producto.venta_dl > 0:
                    actualizacion['venta'] = (producto.venta_dl/producto.unidad_conversion)+( (producto.venta_dl/producto.unidad_conversion) * (producto.piva/100))

                Inventario.objects.filter(id=producto.inventario_id).update(**actualizacion)

                InventarioHistoria.objects.create(
                    inventario_id = producto.inventario_id,
                    costo = producto.costo_dl,
                    venta = producto.venta_dl,
                    tasa = productonota.tasaaplicable,
                    unidadcompra_id = producto.unidadcompra_id,
                    presentacion_salida_id = producto.presentacion_salida_id,
                    notaentrega_id = nota_id,
                    usuario_id = self.request.user.id,
                    lote = producto.lote,
                    factor = producto.unidad_conversion,
                    laboratorio_id = producto.laboratorio_id,
                    cantidad = producto.cantidad,
                    fecha_vencimiento = producto.fechavencimiento,

                )
                menor_fecha_vencimiento_producto = InventarioHistoria.objects.filter(inventario_id = producto.inventario_id ).order_by('fecha_vencimiento').first()
                if menor_fecha_vencimiento_producto:
                    Inventario.objects.filter(id=producto.inventario_id ).update(
                        fecha_vencimiento = menor_fecha_vencimiento_producto.fecha_vencimiento
                    )
                    

                DepositoUso.objects.filter(deposito_id=producto.deposito_id,inventario_id=producto.inventario_id).update(
                    cantidad_deposito = F('cantidad_deposito') + Decimal(producto.cantidad * producto.unidad_conversion)
                )
                InventarioDescarga.objects.create(
                    cantidad = Decimal(producto.cantidad) * Decimal(producto.unidad_conversion),
                    depositoentrada_id = producto.deposito_id,
                    inventario_id = producto.inventario_id,
                    usuario_id = self.request.user.id,
                    tipodescarga_id = 4,
                )

        
            NotaEntregaCompra.objects.filter(id=nota_id).update(
                cantidad_inventario_actualizado = True
            )

        return redirect('entregas_transito' )


def upload_photo(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data['image']
        cedula = data['cedula']
        format, imgstr = image_data.split(';base64,') 
        ext = format.split('/')[-1]  # Obtiene la extensión de la imagen
        image = ContentFile(base64.b64decode(imgstr), name=f'{cedula}.{ext}')
        # Guarda la imagen en el modelo
        # Define la ruta donde se guardará la imagen
        image_path = os.path.join(settings.BASE_DIR, 'photos',  f'{cedula}.{ext}')
        # Crea el directorio si no existe
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        # Guarda la imagen en el directorio estático
        with open(image_path, 'wb') as f:
            f.write(image.read())

        imagenexiste = ImagenPhoto.objects.filter(cedula = cedula).first()

        if imagenexiste:
            ImagenPhoto.objects.filter(cedula = cedula).update(
                image=image_path,
            )
        else:
            photo = ImagenPhoto(image=image_path, cedula = cedula)
            photo.save()
        
        return JsonResponse({'message': 'Foto guardada exitosamente'}, status=201)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def upload_photo_profile(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data['image']
        cedula = data['cedula']
        format, imgstr = image_data.split(';base64,') 
        ext = format.split('/')[-1]  # Obtiene la extensión de la imagen
        image = ContentFile(base64.b64decode(imgstr), name=f'{cedula}.{ext}')
        # Guarda la imagen en el modelo
        # Define la ruta donde se guardará la imagen
        image_path = os.path.join(settings.BASE_DIR, 'photos',  f'{cedula}.{ext}')
        # Crea el directorio si no existe
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        # Guarda la imagen en el directorio estático
        with open(image_path, 'wb') as f:
            f.write(image.read())

        imagenexiste = Paciente.objects.filter(id = cedula).first()

        if imagenexiste:
            Paciente.objects.filter(id = cedula).update(
                fotoperfil=image_path,
            )
        else:
            photo = Paciente(fotoperfil=image_path, id = cedula)
            photo.save()
        
        return JsonResponse({'message': 'Foto guardada exitosamente'}, status=201)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def upload_photo_medical(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data['image']
        cedula = data['cedula']
        format, imgstr = image_data.split(';base64,') 
        ext = format.split('/')[-1]  # Obtiene la extensión de la imagen
        image = ContentFile(base64.b64decode(imgstr), name=f'{cedula}.{ext}')
        # Guarda la imagen en el modelo
        # Define la ruta donde se guardará la imagen
        image_path = os.path.join(settings.BASE_DIR, 'photos',  f'{cedula}.{ext}')
        # Crea el directorio si no existe
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        # Guarda la imagen en el directorio estático
        with open(image_path, 'wb') as f:
            f.write(image.read())

        imagenexiste = Paciente.objects.filter(id = cedula).first()

        if imagenexiste:
            Medico.objects.filter(id = cedula).update(
                fotoperfil=image_path,
            )
        else:
            photo = Medico(fotoperfil=image_path, id = cedula)
            photo.save()
        
        return JsonResponse({'message': 'Foto guardada exitosamente'}, status=201)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def upload_photo_cirugia(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data['image']
        cedula = data['cedula']
        numero_foto = ImagenCirugia.objects.filter(cirugia_id = cedula).count()
        format, imgstr = image_data.split(';base64,') 
        ext = format.split('/')[-1]  # Obtiene la extensión de la imagen
        cirugia_id = cedula
        numero_foto += 1
        cedula = cedula + '_' + str(numero_foto)
        image = ContentFile(base64.b64decode(imgstr), name=f'{cedula}.{ext}')
        # Guarda la imagen en el modelo
        # Define la ruta donde se guardará la imagen
        image_path = os.path.join(settings.BASE_DIR, 'photos',  f'{cedula}.{ext}')
        # Crea el directorio si no existe
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        
        # Guarda la imagen en el directorio estático
        with open(image_path, 'wb') as f:
            f.write(image.read())

        photo = ImagenCirugia(imagen=image_path, cirugia_id = cirugia_id, descripcion = 'Imagen # '+str(numero_foto), usuario_id = request.user.id)
        photo.save()
        
        return JsonResponse({'message': 'Foto guardada exitosamente'}, status=201)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@add_group_name_to_context    
class conversion_nota_a_factura_multiple(TemplateView):
    model = NotaEntregaCompra
    template_name = 'conversion_nota_a_factura_multiple.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nota_id = self.kwargs['nota_id']
        notaentrega = NotaEntregaCompra.objects.filter(id=nota_id, marca=True).first()
        por_retencion_iva = notaentrega.proveedor_compra.porcentaje_retencion
        notatotales = NotaEntregaCompra.objects.filter(marca=True)
        total_costo_bs = total_costo_dl = porcentaje_descuento = monto_descuento_bs = monto_descuento_dl = total_exento_neto_bs = total_exento_neto_dl = total_base_imponible_neto_bs = total_base_imponible_neto_dl = total_iva_neto_bs = total_iva_dl = total_operacion_bs = total_operacion_dl = 0
        for total in notatotales:
            total_costo_bs += total.total_costo_bs_multiple + total.total_iva_bs_multiple
            total_costo_dl += total.total_costo_dl
            porcentaje_descuento += total.porcentaje_descuento
            monto_descuento_bs += total.monto_descuento_bs
            monto_descuento_dl += total.monto_descuento_dl
            total_exento_neto_bs += total.total_exento_bs_multiple
            total_exento_neto_dl += total.total_exento_neto_dl
            total_base_imponible_neto_bs += total.total_base_imponible_bs_multiple
            total_base_imponible_neto_dl += total.total_base_imponible_neto_dl
            total_iva_neto_bs += total.total_iva_bs_multiple
            total_iva_dl += total.total_iva_dl
            total_operacion_dl += total.total_operacion_dl
        
        total_monto_retencion_iva_bs = total_iva_neto_bs * (por_retencion_iva/100)
        total_monto_retencion_iva_dl = total_iva_dl * (por_retencion_iva/100)
        monto_retencion_islr_bs = (total_exento_neto_bs + total_base_imponible_neto_bs) *  (notaentrega.porcentaje_retencion_islr/100)
        monto_retencion_islr_dl = (total_exento_neto_dl + total_base_imponible_neto_dl) *  (notaentrega.porcentaje_retencion_islr/100)

        total_operacion_bs = total_base_imponible_neto_bs + total_exento_neto_bs + total_iva_neto_bs +( total_monto_retencion_iva_bs*-1) + (monto_retencion_islr_bs*-1)
            

        detallenotaentrega = DetalleNotaEntrega.objects.filter(marca = True, notaentrega__proveedor_compra_id = notaentrega.proveedor_compra_id)
        conceptos = Retencion.objects.filter(activo=True).order_by('nombre')
        context['total_costo_bs'] = total_costo_bs
        context['total_costo_dl'] = total_costo_dl
        context['porcentaje_descuento'] = porcentaje_descuento
        context['monto_descuento_bs'] = monto_descuento_bs
        context['monto_descuento_dl'] = monto_descuento_dl
        context['total_exento_neto_bs'] = total_exento_neto_bs
        context['total_exento_neto_dl'] = total_exento_neto_dl
        context['porcentaje_retencion_islr'] = notaentrega.porcentaje_retencion_islr
        context['monto_retencion_islr_bs'] = monto_retencion_islr_bs * -1
        context['monto_retencion_islr_dl'] = monto_retencion_islr_dl * -1

        context['total_base_imponible_neto_bs'] = total_base_imponible_neto_bs
        context['total_base_imponible_neto_dl'] = total_base_imponible_neto_dl
        context['total_iva_neto_bs'] = total_iva_neto_bs
        context['total_iva_dl'] = total_iva_dl
        context['total_operacion_bs'] = total_operacion_bs
        context['total_operacion_dl'] = total_operacion_dl
        context['total_monto_retencion_iva_bs'] = total_monto_retencion_iva_bs * -1
        context['total_monto_retencion_iva_dl'] = total_monto_retencion_iva_dl * -1
        context['por_retencion_iva'] = por_retencion_iva
        context['conceptos'] = conceptos
        context['notaentrega'] = notaentrega
        context['detallenotaentrega'] = detallenotaentrega
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        nota_id = self.kwargs['nota_id']
        fecha_entrega =  self.request.POST.get('fechadocumento')
        nrofactura =  self.request.POST.get('nrofactura')
        nrocontrol =  self.request.POST.get('nrocontrol')
        numero_nota = self.request.POST.get('numeronota')
        tasa_nueva_factura = self.request.POST.get('tasacambiofactura')
        name_proveedor = self.request.POST.get('name_proveedor')
        conceptoretencion =  self.request.POST.get('conceptoretencion')
        #monto_descuento_bs =  self.request.POST.get('monto_descuento_bs').replace(',','.')
        
        #monto_descuento_bs = Decimal(monto_descuento_bs)
        monto_descuento_bs = 0

        tasa_nueva_factura = float(str(tasa_nueva_factura).replace(',','.'))

        notaentrega = NotaEntregaCompra.objects.filter(proveedor_compra_id = name_proveedor, marca = True).first()
        detallenotaentrega = DetalleNotaEntrega.objects.filter(notaentrega__proveedor_compra_id = name_proveedor, marca = True, factura = True, convertido_a_factura = False )
        
        existe_factura = FacturaProveedor.objects.filter(numerodocumento = nrofactura.strip(), proveedor_compra_id = name_proveedor).exists()
        if not existe_factura:
            existe_factura = FacturaProveedor.objects.filter(numerocontrol = nrocontrol.strip(), proveedor_compra_id = name_proveedor).exists()


        if existe_factura:
            messages.error(request, 'ERROR: ESTA FACTURA YA EXISTE EN LOS REGISTROS CON EL MISMO PROVEEDOR, NO PUEDE GENERARSE UNA NUEVA FACTURA CON EL MISMO NUMERO Y MISMO PROVEEDOR')
            return redirect('conversion_nota_a_factura_multiple', nota_id = nota_id )  

        porcentaje_retencion_islr = 0
        if conceptoretencion:
            rentencion = Retencion.objects.filter(id=conceptoretencion).first()
            if rentencion:
                rif = notaentrega.proveedor_compra.rif[0]
                if rif == 'J' or rif == 'G':
                    porcentaje_retencion_islr = rentencion.juridica
                else:
                    porcentaje_retencion_islr = rentencion.natural
            
        notas_ids = detallenotaentrega.values_list('notaentrega_id', flat=True).distinct()
        
        if notas_ids:    
            factura = FacturaProveedor.objects.create(
                fecha_entrega = fecha_entrega,
                numerodocumento = nrofactura.strip() ,
                numerocontrol = nrocontrol.strip(),
                cambio_congelado = tasa_nueva_factura,
                concepto_id = conceptoretencion,
                fecha_cambio = fecha_entrega,
                tipodocumento_id = 1,
                tipomoneda_id = 2,
                proveedor_compra_id = name_proveedor,
                tipo = 'FI',
                usuario_id = self.request.user.id,
                porcentaje_retencion_islr = porcentaje_retencion_islr
            ) 

            
            for nota in detallenotaentrega:
                DetalleFacturaProveedor.objects.create(
                    detallenotaentrega_id = nota.id,
                    factura_id = factura.id,
                    cambio_bcv = tasa_nueva_factura,
                    subtotal_bs = nota.cantidad * nota.costo_bs,
                    subtotal_dl = float(nota.cantidad * nota.costo_bs)/float(tasa_nueva_factura),
                    porc_iva = nota.piva
                )
                """ nota.factura = True
                nota.convertido_a_factura = True
                nota.usuario_id = self.request.user.id
                nota.save() """
                DetalleNotaEntrega.objects.filter(id = nota.id).update(factura = True, convertido_a_factura = True, usuario_id = self.request.user.id)

            for nt in notas_ids:
                cantidad_total_detallenotaentrega = DetalleNotaEntrega.objects.filter(notaentrega_id=nt, notaentrega__proveedor_compra_id = name_proveedor, marca = True).count()
                cantidad_convertida_detallenotaentrega = DetalleNotaEntrega.objects.filter(notaentrega_id=nt,notaentrega__proveedor_compra_id = name_proveedor, marca = True, factura = True, convertido_a_factura = True ).count()
                if cantidad_convertida_detallenotaentrega == cantidad_total_detallenotaentrega:
                    conversion_total = True
                else:
                    conversion_total = False

                if cantidad_convertida_detallenotaentrega == 0:
                    convertida_factura = False
                else:
                    convertida_factura = True

       
                NotaEntregaCompra.objects.filter(id=nt, proveedor_compra_id = name_proveedor,marca = True).update(
                    convertida_factura = convertida_factura,
                    convertida_factura_total = conversion_total,
                    usuario_id = self.request.user.id,
                    marca = False
                )

        return redirect('entregas_transito' )
        #return redirect('conversion_nota_a_factura_multiple', nota_id = nota_id )  

@add_group_name_to_context    
class conversion_nota_a_factura(TemplateView):
    model = NotaEntregaCompra
    template_name = 'conversion_nota_a_factura.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nota_id = self.kwargs['nota_id']
        notaentrega = NotaEntregaCompra.objects.filter(id=nota_id, marca=True).first()
        notatotales = NotaEntregaCompra.objects.filter(marca=True)
        total_costo_bs = total_costo_dl = porcentaje_descuento = monto_descuento_bs = monto_descuento_dl = total_exento_neto_bs = total_exento_neto_dl = total_base_imponible_neto_bs = total_base_imponible_neto_dl = total_iva_neto_bs = total_iva_dl = total_operacion_bs = total_operacion_dl = 0
        for total in notatotales:
            total_costo_bs += total.total_costo_bs
            total_costo_dl += total.total_costo_dl
            porcentaje_descuento += total.porcentaje_descuento
            monto_descuento_bs += total.monto_descuento_bs
            monto_descuento_dl += total.monto_descuento_dl
            total_exento_neto_bs += total.total_exento_neto_bs
            total_exento_neto_dl += total.total_exento_neto_dl
            total_base_imponible_neto_bs += total.total_base_imponible_neto_bs
            total_base_imponible_neto_dl += total.total_base_imponible_neto_dl
            total_iva_neto_bs += total.total_iva_neto_bs
            total_iva_dl += total.total_iva_dl
            total_operacion_bs += total.total_operacion_bs
            total_operacion_dl += total.total_operacion_dl
            
            
        detallenotaentrega = DetalleNotaEntrega.objects.filter(marca = True, notaentrega__proveedor_compra_id = notaentrega.proveedor_compra_id, convertido_a_factura = False)
        conceptos = Retencion.objects.filter(activo=True).order_by('nombre')
        
        context['total_costo_bs'] = total_costo_bs
        context['total_costo_dl'] = total_costo_dl
        context['porcentaje_descuento'] = porcentaje_descuento
        context['monto_descuento_bs'] = monto_descuento_bs
        context['monto_descuento_dl'] = monto_descuento_dl
        context['total_exento_neto_bs'] = total_exento_neto_bs
        context['total_exento_neto_dl'] = total_exento_neto_dl
        context['total_base_imponible_neto_bs'] = total_base_imponible_neto_bs
        context['total_base_imponible_neto_dl'] = total_base_imponible_neto_dl
        context['total_iva_neto_bs'] = total_iva_neto_bs
        context['total_iva_dl'] = total_iva_dl
        context['total_operacion_bs'] = total_operacion_bs
        context['total_operacion_dl'] = total_operacion_dl
        
        context['conceptos'] = conceptos
        context['notaentrega'] = notaentrega
        context['detallenotaentrega'] = detallenotaentrega
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        nota_id = self.kwargs['nota_id']
        fecha_entrega =  self.request.POST.get('fechadocumento')
        nrofactura =  self.request.POST.get('nrofactura')
        nrocontrol =  self.request.POST.get('nrocontrol')
        numero_nota = self.request.POST.get('numeronota')
        name_proveedor = self.request.POST.get('name_proveedor')
        conceptoretencion =  self.request.POST.get('conceptoretencion')
        monto_descuento_bs =  self.request.POST.get('monto_descuento_bs').replace(',','.')
        monto_descuento_bs = Decimal(monto_descuento_bs)

        #notaentrega = NotaEntregaCompra.objects.filter(id = nota_id, marca = True).first()
        notaentrega = NotaEntregaCompra.objects.filter(proveedor_compra_id = name_proveedor, marca = True).first()
        
        #detallenotaentrega = DetalleNotaEntrega.objects.filter(notaentrega__proveedor_compra_id = name_proveedor, marca = True, factura = True, convertido_a_factura = False )
        detallenotaentrega = DetalleNotaEntrega.objects.filter(marca = True, notaentrega__proveedor_compra_id = notaentrega.proveedor_compra_id, convertido_a_factura = False)

        existe_factura = FacturaProveedor.objects.filter(numerodocumento = nrofactura.strip(), proveedor_compra_id = notaentrega.proveedor_compra_id).exists()
        if existe_factura:
            messages.error(request, 'ERROR: ESTA FACTURA YA EXISTE EN LOS REGISTROS CON EL MISMO PROVEEDOR, NO PUEDE GENERARSE UNA NUEVA FACTURA CON EL MISMO NUMERO Y MISMO PROVEEDOR')
            return redirect('conversion_nota_a_factura', nota_id = nota_id )  
            
        
        porcentaje_retencion_islr = 0
        if conceptoretencion:
            rentencion = Retencion.objects.filter(id=conceptoretencion).first()
            if rentencion:
                rif = notaentrega.proveedor_compra.rif[0]
                print('rif', rif)
                if rif == 'J' or rif == 'G':
                    porcentaje_retencion_islr = rentencion.juridica
                else:
                    porcentaje_retencion_islr = rentencion.natural
            
        factura = FacturaProveedor.objects.create(
            fecha_entrega = fecha_entrega,
            numerodocumento = nrofactura.strip() ,
            numerocontrol = nrocontrol.strip(),
            cambio_congelado = notaentrega.tasaaplicable,
            concepto_id = conceptoretencion,
            tipodocumento_id = 1,
            tipomoneda_id = 2,
            proveedor_compra_id = notaentrega.proveedor_compra_id,
            notaentrega_id = notaentrega.id,
            tipo = 'FI',
            usuario_id = self.request.user.id,
            monto_descuento_bs = monto_descuento_bs,
            porcentaje_descuento = notaentrega.porcentaje_descuento,
            porcentaje_retencion_islr = porcentaje_retencion_islr
        )

        factura.save()

        for nota in detallenotaentrega:
            DetalleFacturaProveedor.objects.create(
                detallenotaentrega_id = nota.id,
                factura_id = factura.id,
                cambio_bcv = nota.cambioaplicado,
                subtotal_bs = nota.cantidad * nota.costo_bs,
                subtotal_dl = (nota.cantidad * nota.costo_bs)/nota.cambioaplicado,
                porc_iva = nota.piva
            )

            NotaEntregaCompra.objects.filter(id = nota.notaentrega_id).update(
                convertida_factura = True,
                convertida_factura_total = True,
                marca = False
            ) 

            DetalleNotaEntrega.objects.filter(id = nota.id).update(
                factura = True,
                convertido_a_factura = True
            )

        return redirect('entregas_transito' )


@add_group_name_to_context    
class listado_requisicion_material(TemplateView): 
    template_name = 'listado_requisicion_material.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        productos_solicitados = InventarioSolicitud.objects.all().order_by('-fecha_solicitud')
       
        context['productos_solicitados'] = productos_solicitados
        return context

@add_group_name_to_context    
class factura_compra_pagar(TemplateView): 
    template_name='factura_compra_pagar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        factura_id = self.kwargs['pk']
        facturascompra = FacturaProveedor.objects.filter(id=factura_id).first()
        notas_credito = FacturaProveedor.objects.filter(proveedor_compra_id = facturascompra.proveedor_compra_id, tipodocumento_id = 3, estatus = 'PEN'  )
        notas_credito_cantidad = FacturaProveedor.objects.filter(proveedor_compra_id = facturascompra.proveedor_compra_id, tipodocumento_id = 3, estatus = 'PEN' ).count()
        cuentas = BancoLocal.objects.filter(activo = True).order_by('nombrecuenta')
        cuentaproveedor = FormaPagoProveedor.objects.filter(proveedor_id = facturascompra.proveedor_compra_id, activo = True )
        detallefactura = DetalleFacturaProveedor.objects.filter(factura_id=factura_id)
        notaentrega = NotaEntregaCompra.objects.filter(id=facturascompra.notaentrega_id).first()
        abonos = AbonoCuentaPagar.objects.filter(
            Q(factura_id=factura_id) |
            Q(
                id__in=Subquery(
                    TransaccionFacturaMultiple.objects.filter(
                        factura_id=factura_id
                    ).values('abono_id')
                )
            )
        )
        forma_pago_cadena= ''
        ultimo_abono = AbonoCuentaPagar.objects.filter(factura_id = factura_id).order_by('-id')
        ultima_fecha = AbonoCuentaPagar.objects.filter(factura_id = factura_id).order_by('-fecha_pago').first()
        if ultima_fecha:
            ultima_fecha_pago = ultima_fecha.fecha_pago
        else:
            detalle_pagado_multiple_factura = ''
            forma_pago_multiple_factura = TransaccionFacturaMultiple.objects.filter(factura_id = factura_id )
            if forma_pago_multiple_factura:
                i = 0
                for forma_p in forma_pago_multiple_factura:
                    if i == 0:
                        conector = ''
                    else:
                        conector = ' + '
                    
                    cadena = forma_p.transaccion.mediomoneda
                    forma_pago_cadena += str(conector) +str(cadena)
                    if forma_p.transaccion.mediomoneda.moneda_id == 1:
                        monto_pagado = forma_p.transaccion.monto_dolar * -1 
                        signo_moneda = "$"
                    else:
                        monto_pagado = forma_p.transaccion.monto * -1
                        signo_moneda = "Bs"

                    detalle_pagado_multiple_factura += (conector)+str(monto_pagado)+str(signo_moneda)+':'+str(forma_p.transaccion.descripcion.strip())
                    i+=1


                
            ultima_fecha = TransaccionFacturaMultiple.objects.filter(factura_id = factura_id ).order_by('-transaccion_id').first()
            if ultima_fecha:
                ultima_fecha_pago = ultima_fecha.transaccion.fechatransaccion
            else:
                ultima_fecha_pago = ''

        formas_pagos = detalle_pagado = ''
        i = 0
        for ultimo in ultimo_abono:
            if i == 0:
                conector = ''
            else:
                conector = ' + '
            
            if ultimo.origen_pago:
                if ultimo.origen_pago.moneda_id == 1:
                    signo_moneda = ' $ '
                    monto_pagado = ultimo.montopago
                else:
                    signo_moneda = ' Bs '
                    monto_pagado = ultimo.montopago_bs
            else:
                signo_moneda = ' NC '
                monto_pagado = ultimo.montopago_bs

            if ultimo.destino_pago:
                fp_resume = ultimo.destino_pago.formapago
            else:
                fp_resume = "Nota Credito"


            formas_pagos += (conector)+str(fp_resume) 
            detalle_pagado += (conector)+str(monto_pagado)+str(signo_moneda)+':'+str(ultimo.descripcion.strip())

            i += 1
            #forma_pagada = ultimo.destino_pago.formapago

        if len(detalle_pagado.strip()) == 0:
            detalle_pagado = detalle_pagado_multiple_factura + str(' :[Multiples facturas]')

        if len(formas_pagos.strip()) == 0:
            formas_pagos = forma_pago_cadena

        resultado = " + ".join(dict.fromkeys(p.strip() for p in formas_pagos.split("+")))

        factura_pago_multiple = TransaccionFacturaMultiple.objects.filter(factura_id = factura_id ).exists()

        total_pagado_dl = AbonoCuentaPagar.total_montopago_dl(factura_id)
        total_pagado_bs = AbonoCuentaPagar.total_montopago_bs(factura_id)
        tasa_dia = CambioDiaBcv(facturascompra.fecha_entrega)
        fecha_hoy = facturascompra.fecha_entrega
        total_baseimponible_bs = facturascompra.total_baseimponible_bs + facturascompra.total_exento_bs
        total_baseimponible_dl = float(total_baseimponible_bs) / float(facturascompra.cambio_congelado
)
        saldo_actual =   float(facturascompra.total_operacion_bs - total_pagado_bs) + facturascompra.monto_igtf
        saldo_actual_dl = float(saldo_actual) / float(tasa_dia)
        if saldo_actual_dl < 0.01:
            saldo_actual_dl = 0

        if saldo_actual < 0.01 and factura_pago_multiple:
            saldo_actual = 0 

        if facturascompra.actualizada == False :
            for detalle in detallefactura:
                detallenota = DetalleNotaEntrega.objects.filter(id=detalle.detallenotaentrega_id).first()
                if detallenota:
                    DetalleFacturaProveedor.objects.filter(id=detalle.id).update(
                        cantidad = detallenota.cantidad,
                        precio_bs = detallenota.costo_bs,
                        precio_dl = detallenota.costo_dl,
                        subtotal_bs = detallenota.cantidad * detallenota.costo_bs,
                        subtotal_dl = (detallenota.cantidad * detallenota.costo_bs) / detallenota.cambioaplicado,
                        
                    )
                
            
            
            detallefactura = DetalleFacturaProveedor.objects.filter(factura_id=factura_id)
            FacturaProveedor.objects.filter(id=factura_id).update(
                actualizada = True
            )
        
        rif = facturascompra.proveedor_compra.rif
        
        if rif[0] == 'J' or rif[0] == 'G':
            porcentaje_retencion = facturascompra.concepto.juridica
        else:
            porcentaje_retencion = facturascompra.concepto.natural

        
        monto_total_dolares_factura = facturascompra.monto_iva_dl + facturascompra.total_baseimponible_dl + facturascompra.total_exento_dl
        
        context['abonos'] = abonos
        context['cuentas'] = cuentas
        context['tasa_dia'] = tasa_dia
        context['fecha_hoy'] = fecha_hoy
        context['notaentrega'] = notaentrega
        context['formas_pagos'] = resultado.strip()
        context['notas_credito'] = notas_credito
        context['detalle_pagado'] = detalle_pagado.strip()
        context['ultima_fecha_pago'] = ultima_fecha_pago
        context['porcentaje_retencion'] = porcentaje_retencion
        context['saldo_actual'] = saldo_actual
        context['saldo_actual_dl'] = saldo_actual_dl
        context['facturascompra'] = facturascompra
        context['detallefactura'] = detallefactura
        context['cuentaproveedor'] = cuentaproveedor
        context['total_pagado_dl'] = total_pagado_dl
        context['total_pagado_bs'] = total_pagado_bs
        context['total_baseimponible_bs'] = total_baseimponible_bs
        context['total_baseimponible_dl'] = total_baseimponible_dl
        context['notas_credito_cantidad'] = notas_credito_cantidad
        context['monto_total_dolares_factura'] = monto_total_dolares_factura


        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        factura_id = self.kwargs['pk']
        facturascompra = FacturaProveedor.objects.filter(id=factura_id).first()
        idOrigenFondos =  self.request.POST.get('idOrigenFondos')
        idDestinoFondos =  self.request.POST.get('idDestinoFondos')
        idmontopagar =  self.request.POST.get('idmontopagar')
        idmontopagarusd =  self.request.POST.get('idmontopagarusd')
        idreferenciapago =  self.request.POST.get('idreferenciapago')
        idnotapago =  self.request.POST.get('idnotapago')
        tasacambio =  self.request.POST.get('tasacambio')
        fecha_pago =  self.request.POST.get('fecha-pago')
        # Leer checkbox
        igtf = request.POST.get('igtf') 
        if igtf:
            igtf_valor = True
        else:
            igtf_valor = False

        if facturascompra and igtf_valor:
            FacturaProveedor.objects.filter(id=factura_id).update(
                igtf = igtf_valor,
                usuario_id = self.request.user.id
            )


        tasacambio = tasacambio.replace(',','.')
        idmontopagar = idmontopagar.replace(',','.')
        monedadepago = FormaPagoProveedor.objects.filter(id=idDestinoFondos).first()
        tasa_dia = CambioDiaBcv(datetime.now())
        
        #1-dolares 2-bolivares en moneda

        transaccion = Transaccion.objects.create(
            monto =  Decimal(idmontopagar) * -1,
            monto_dolar = Decimal(idmontopagarusd) * -1,
            fechatransaccion = fecha_pago,
            descripcion = 'Pago factura ' + str(facturascompra.numerodocumento) + ' - BENEFICIARIO:'+ str(facturascompra.proveedor_compra)  ,
            referencia = idreferenciapago,
            bancolocal_id = idOrigenFondos,
            banco_id = idDestinoFondos,
            usuario_id = self.request.user.id,
            nota = idnotapago,
            tasa_bcv = Decimal(tasacambio),
            cuentapagar_id = factura_id,
            mediomoneda_id = monedadepago.formapago_id,
            fechatasa = fecha_pago

        )

        idTransaccion = transaccion.id

        abono_factura = AbonoCuentaPagar.objects.create(
            montopago = idmontopagarusd,
            montopago_bs = idmontopagar,
            descripcion = idnotapago,
            tasa_bcv = tasacambio,
            destino_pago_id = idDestinoFondos,
            origen_pago_id = idOrigenFondos,
            factura_id = factura_id,
            usuario_id = self.request.user.id,
            referencia = idreferenciapago,
            transaccion_id = idTransaccion,
            fecha_pago = fecha_pago,
            igtf = igtf_valor

        )


        total_pagado_bs = AbonoCuentaPagar.total_montopago_bs(factura_id)
        total_nota_credito = (float(facturascompra.total_operacion_bs) + float(facturascompra.monto_igtf) ) - float(total_pagado_bs)
        if total_nota_credito < -0.01:
            nota_credito_nueva = FacturaProveedor.objects.create(
                tipodocumento_id = 3,
                fecha_entrega = fecha_pago,
                numerodocumento = facturascompra.numerodocumento + str('-nc'),
                numerocontrol = facturascompra.numerocontrol + str('-nc'),
                fecha_cambio =  fecha_pago,
                concepto_id = facturascompra.concepto_id,
                tipomoneda_id = facturascompra.tipomoneda_id,
                cambio_congelado = facturascompra.cambio_congelado,
                congelar_moneda = facturascompra.congelar_moneda,
                proveedor_compra_id = facturascompra.proveedor_compra_id,
                tipo='FC',
                usuario_id = self.request.user.id,
                estatus = 'PEN',
                abono_id = abono_factura.id
            )
            DetalleFacturaProveedor.objects.create(
                cantidad = 1,
                precio_unitario = (Decimal(total_nota_credito) / Decimal(tasa_dia)) * -1,
                descripcion = 'Nota de credito generada automaticamente por: '+str(self.request.user.username),
                factura_id = nota_credito_nueva.id,
                precio_bs = Decimal(total_nota_credito) * -1,
                subtotal = Decimal(total_nota_credito) * -1,
                subtotal_bs = Decimal(total_nota_credito) * -1,
                subtotal_dl = (Decimal(total_nota_credito) / Decimal(tasa_dia)) * -1,
                precio_dl = (Decimal(total_nota_credito) / Decimal(tasa_dia)) * -1,
                cambio_bcv =  Decimal(tasa_dia),
                usuario_id = self.request.user.id,

            )

            AbonoCuentaPagar.objects.filter(id = abono_factura.id).update(
                nota_credito_generada = nota_credito_nueva.id
            )


            print('generar nota de credito', total_nota_credito)
        
        return redirect('factura_compra_pagar', pk = factura_id )
    
    
@add_group_name_to_context    
class factura_compra_modificar(TemplateView): 
    template_name='factura_compra_modificar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        factura_id = self.kwargs['pk']
        facturascompra = FacturaProveedor.objects.filter(id=factura_id).first()
        cuentas = BancoLocal.objects.filter(activo = True).order_by('nombrecuenta')
        cuentaproveedor = FormaPagoProveedor.objects.filter(proveedor_id = facturascompra.proveedor_compra_id, activo = True )
        detallefactura = DetalleFacturaProveedor.objects.filter(factura_id=factura_id)
        notaentrega = NotaEntregaCompra.objects.filter(id=facturascompra.notaentrega_id).first()

        abonos = AbonoCuentaPagar.objects.filter(
            Q(factura_id=factura_id) |
            Q(
                id__in=Subquery(
                    TransaccionFacturaMultiple.objects.filter(
                        factura_id=factura_id
                    ).values('abono_id')
                )
            )
        )
        total_pagado_dl = AbonoCuentaPagar.total_montopago_dl(factura_id)
        total_pagado_bs = AbonoCuentaPagar.total_montopago_bs(factura_id)
        tasa_dia = CambioDiaBcv(datetime.now())
        factura_pago_multiple = TransaccionFacturaMultiple.objects.filter(factura_id = factura_id ).exists()
        saldo_actual =   facturascompra.total_operacion_bs - total_pagado_bs
        if saldo_actual < 0 and factura_pago_multiple:
            saldo_actual = 0
            
        if facturascompra.actualizada == False :
            for detalle in detallefactura:
                detallenota = DetalleNotaEntrega.objects.filter(id=detalle.detallenotaentrega_id).first()
                if detallenota:
                    DetalleFacturaProveedor.objects.filter(id=detalle.id).update(
                        cantidad = detallenota.cantidad,
                        precio_bs = detallenota.costo_bs,
                        precio_dl = detallenota.costo_dl,
                        subtotal_bs = detallenota.cantidad * detallenota.costo_bs,
                        subtotal_dl = (detallenota.cantidad * detallenota.costo_bs) / detallenota.cambioaplicado,
                        
                    )
                
            
            
            detallefactura = DetalleFacturaProveedor.objects.filter(factura_id=factura_id)
            FacturaProveedor.objects.filter(id=factura_id).update(
                actualizada = True
            )
        
        rif = facturascompra.proveedor_compra.rif
        
        if facturascompra.concepto:
            if rif[0] == 'J' or rif[0] == 'G':
                porcentaje_retencion = facturascompra.concepto.juridica
            else:
                porcentaje_retencion = facturascompra.concepto.natural
        else:
            porcentaje_retencion = 0
                
        
        conceptos = Retencion.objects.filter(activo=True).order_by('nombre')
        proveedores = Proveedor.objects.filter(activo = True).order_by('nombre')
        centrocosto = CentroCostoFacturaCompra.objects.all().order_by('nombre')

        context['abonos'] = abonos
        context['cuentas'] = cuentas
        context['tasa_dia'] = tasa_dia
        context['conceptos'] = conceptos
        context['notaentrega'] = notaentrega
        context['centrocosto'] = centrocosto
        context['proveedores'] = proveedores
        context['porcentaje_retencion'] = porcentaje_retencion
        context['saldo_actual'] = saldo_actual
        context['facturascompra'] = facturascompra
        context['detallefactura'] = detallefactura
        context['cuentaproveedor'] = cuentaproveedor
        context['total_pagado_dl'] = total_pagado_dl
        context['total_pagado_bs'] = total_pagado_bs
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        factura_id = self.kwargs['pk']
        facturascompra = FacturaProveedor.objects.filter(id=factura_id).first()
        idOrigenFondos =  self.request.POST.get('idOrigenFondos')
        idDestinoFondos =  self.request.POST.get('idDestinoFondos')
        idmontopagar =  self.request.POST.get('idmontopagar')
        idmontopagarusd =  self.request.POST.get('idmontopagarusd')
        idreferenciapago =  self.request.POST.get('idreferenciapago')
        idnotapago =  self.request.POST.get('idnotapago')
        tasacambio =  self.request.POST.get('tasacambio')
        fecha_pago =  self.request.POST.get('fecha-pago')
        #centrocosto =  self.request.POST.get('centrocosto')
        tasacambio = tasacambio.replace(',','.')
        idmontopagar = idmontopagar.replace(',','.')
        monedadepago = FormaPagoProveedor.objects.filter(id=idDestinoFondos).first()
        
        
        #1-dolares 2-bolivares en moneda

        transaccion = Transaccion.objects.create(
            monto =  Decimal(idmontopagar) * -1,
            monto_dolar = Decimal(idmontopagarusd) * -1,
            fechatransaccion = fecha_pago,
            descripcion = 'Pago factura ' + str(facturascompra.numerodocumento) + ' - BENEFICIARIO:'+ str(facturascompra.proveedor_compra)  ,
            referencia = idreferenciapago,
            bancolocal_id = idOrigenFondos,
            banco_id = idDestinoFondos,
            usuario_id = self.request.user.id,
            nota = idnotapago,
            tasa_bcv = Decimal(tasacambio),
            cuentapagar_id = factura_id,
            mediomoneda_id = monedadepago.formapago_id,
            fechatasa = fecha_pago

        )

        idTransaccion = transaccion.id

        AbonoCuentaPagar.objects.create(
            montopago = idmontopagarusd,
            montopago_bs = idmontopagar,
            descripcion = idnotapago,
            tasa_bcv = tasacambio,
            destino_pago_id = idDestinoFondos,
            origen_pago_id = idOrigenFondos,
            factura_id = factura_id,
            usuario_id = self.request.user.id,
            referencia = idreferenciapago,
            transaccion_id = idTransaccion,
            fecha_pago = fecha_pago

        )
        
        return redirect('factura_compra_modificar', pk = factura_id )


def eliminar_abonoCuentaPagar(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idEliminarPago = datos['idEliminarPago']
        idfactura = datos['idfactura']
        abono = AbonoCuentaPagar.objects.filter(id=idEliminarPago).first()
        if abono:
            if abono.igtf:
                FacturaProveedor.objects.filter(id = idfactura).update(
                    igtf = False,
                    usuario_id = request.user.id,
                  )


            contiene_notas_generadas = AbonoCuentaPagar.objects.filter(factura_id = idfactura, nota_credito_generada__isnull = False).exists()
            if not contiene_notas_generadas:
                proceder = True
                FacturaProveedor.objects.filter(id = idfactura).update(
                    estatus = 'PEN',
                    usuario_id = request.user.id,
                  )

                FacturaProveedor.objects.filter(abono_id = abono.id).update(
                    estatus = 'PEN',
                    usuario_id = request.user.id
                )

            elif contiene_notas_generadas and abono.nota_credito_generada and abono.nota_credito :
                proceder = True
                FacturaProveedor.objects.filter(id = idfactura).update(
                    estatus = 'PEN',
                    usuario_id = request.user.id
                )

                FacturaProveedor.objects.filter(abono_id = abono.id).update(
                    estatus = 'PEN',
                    usuario_id = request.user.id
                )
            elif contiene_notas_generadas and abono.nota_credito_generada and not abono.nota_credito :
                proceder = True
                FacturaProveedor.objects.filter(id = abono.nota_credito_generada_id).delete()
                FacturaProveedor.objects.filter(id = idfactura).update(
                    estatus = 'PEN',
                    usuario_id = request.user.id
                )

                FacturaProveedor.objects.filter(abono_id = abono.id).update(
                    estatus = 'PEN',
                    usuario_id = request.user.id
                )
                
            else:
                proceder = False
                print('Tratando de borrar un abono donde hay una nota de credito generada')
           
        if proceder:
            AbonoCuentaPagar.objects.filter(id = idEliminarPago).delete()
            Transaccion.objects.filter(id=abono.transaccion_id).delete()
            return JsonResponse({'mensaje': 'ELIMINADO correctamente', 'id': idfactura})
        else:
            return JsonResponse({'mensaje': 'NO'})
    
    else:
        return JsonResponse({'mensaje': 'Error POST'})

@add_group_name_to_context    
class lista_proveedor_producto(TemplateView): 
    template_name = 'lista_proveedor_producto.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        producto_id = self.kwargs['producto_id']
        producto = Inventario.objects.filter(id=producto_id).first()
        productos_proveedor = InventarioHistoria.objects.filter(inventario_id=producto_id).order_by('notaentrega__proveedor_compra__nombre')

        context['producto'] = producto
        context['productos_proveedor'] = productos_proveedor
        return context
    
@add_group_name_to_context    
class lista_producto_proveedor(TemplateView): 
    template_name = 'lista_producto_proveedor.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        #producto_comprado = DetalleFacturaProveedor.objects.filter(detallenotaentrega_id__isnull = False )
        producto_comprado = DetalleFacturaProveedor.objects.filter(factura__tipo__in = ['FI','FC']).exclude(detallenotaentrega_id__isnull = True,inventario_id__isnull = True )
        context['producto_comprado'] = producto_comprado
        return context




@add_group_name_to_context    
class requisicion_enfermeras(TemplateView): 
    template_name = 'requisicion_enfermeras.html'
   
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        motivos=TipoDescarga.objects.filter(solicitud=True).order_by('nombre')
       
        descargas_subquery = InventarioDescarga.objects.filter(
            inventario=OuterRef('inventario_id'),
            deposito=OuterRef('deposito_id')
        ).exclude(
            tipodescarga_id=4
        ).values(
            'inventario'
        ).annotate(
            total=Sum('cantidad')
        ).values('total')
    

        incremento = MontoIncremento.objects.get(id=1).porcentaje / 100

        inventariodeposito = DepositoUso.objects.filter(
            deposito_id__in=[4,7,8],
            inventario__categoria_id__in=[1,2],
            inventario__producto_activo=True
        ).annotate(
            # 🔹 SUMA DE DESCARGAS (NO tipo 4)
            descarga_total=Coalesce(
                Subquery(descargas_subquery, output_field=DecimalField()),
                Value(0)
            ),

            # 🔹 MONTO VENTA (ya lo tenías)
            monto_venta=ExpressionWrapper(
                (
                    F('inventario__costo') *
                    (Value(1.0) + Value(incremento)) *
                    (Value(1.0) + (F('inventario__piva') / Value(100.0)))
                ),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        ).annotate(
            # 🔥 EXISTENCIA UND FINAL
            existenciaUnd=ExpressionWrapper(
                (
                    F('cantidad_deposito') * F('inventario__unidad_conversion')
                ) - F('descarga_total'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        ).filter(
            existenciaUnd__gt=0   # 🔥 AQUÍ
        ).values(
            'id',
            'inventario__id',
            'inventario__codigo',
            'inventario__nombre',
            'inventario__nombre_comercial',
            'inventario__presentacion_salida__nombre',
            'inventario__laboratorio__nombre',
            'deposito__nombre',
            'monto_venta',
            'existenciaUnd'
        )
        
        #Inventario.objects.all().order_by('nombre')
        solicitudpendiente = InventarioSolicitud.objects.filter(pendiente=True, solicitante_id = 2)
        context['motivos']=motivos
        context['inventariodeposito']=inventariodeposito
        context['solicitudpendiente']=solicitudpendiente
        return context



def dt_serverside_requisicion(request):
    context = {}
    
    dt = request.GET 
    
    draw = int(dt.get("draw"))
    start = int(dt.get("start"))
    length = int(dt.get("length"))
    search = dt.get("search[value]")
    
    #registros = Inventario.objects.all().values_list('id','codigo' ,'nombre','presentacion__nombre','categoria__nombre','unidad_conversion','piva','costo', 'venta' ,'laboratorio__nombre','nombre_comercial','fecha_vencimiento').order_by("nombre")
    registros = DepositoUso.objects.filter(deposito_id__in = [4,7,8], inventario__categoria_id__in = [1,2], inventario__producto_activo = True).values_list('id','inventario__codigo','inventario__categoria__nombre' ,'inventario__nombre' ,'inventario__nombre_comercial', 'inventario__presentacion__nombre','inventario__presentacion_salida__nombre','inventario__laboratorio__nombre', 'inventario__id','deposito__nombre','inventario__unidad_conversion','cantidad_consumida')
    
    if search:
        registros = registros.filter(
            Q(inventario__codigo__icontains=search) |
            Q(inventario__nombre__icontains=search) |
            Q(inventario__nombre_comercial__icontains=search) |
            Q(deposito__nombre__icontains=search) 
        )
        
    recordsTotal = registros.count()
    recordsFiltered = recordsTotal
    
    context["draw"] = draw
    context["recordsTotal"] = recordsTotal
    context["recordsFiltered"] = recordsFiltered
    
    reg = registros[start:start + length]
    paginator = Paginator(reg, length)
    
    try:
        obj = paginator.page(draw).object_list
    except PageNotAnInteger:
        obj = paginator.page(draw).object_list
    except EmptyPage:
        obj = paginator.page(paginator.num_pages).object_list
        
 
    datos = [
        {
            "id" : d[0],
            "idInventario":d[8],
            "categoria":d[1],
            "inventario":d[3],
            "nombre_comercial":d[4],
            "presentacion":d[5],
            "presentacion_salida":d[6],
            "laboratorio" : d[7],
            "monto_venta": round(Inventario.objects.get(id=d[8]).monto_venta, 2) ,
            "existencia_und": round(Inventario.objects.get(id=d[8]).existencia_und, 2) ,
            "deposito" : d[9],
            "unidad_conversion": round(Inventario.objects.get(id=d[8]).unidad_conversion, 2) ,
            "cantidad_consumida" : d[11],
            "id" : d[0],
            
           
        } for d in obj
    ]

    context["datos"] = datos
    return JsonResponse(context,safe=False)

def actualizarDescuentoNotaentrega(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        baseimponible = datos['baseimponible']
        montoDescuento = datos['montoDescuento']
        
        idNota = datos['idNota']
        NotaEntregaCompra.objects.filter(id = idNota).update(
            monto_descuento_bs = montoDescuento,
            porcentaje_descuento = (Decimal(montoDescuento) / Decimal(baseimponible)) * 100
        )

        return JsonResponse({'mensaje': 'Bien'})

def change_TasaCambio(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idFactura = datos['idFactura']
        nuevoCambio = datos['nuevoCambio']
        fecha_new_cambio = datos['fecha_new_cambio']
        
        FacturaProveedor.objects.filter(id=idFactura).update(
            usuario_id = request.user.id,
            cambio_congelado = Decimal(nuevoCambio),
            fecha_entrega = fecha_new_cambio,
            fecha_cambio =  fecha_new_cambio

        )
        DetalleFacturaProveedor.objects.filter(factura_id=idFactura).update(
            cambio_bcv = Decimal(nuevoCambio),
            subtotal_bs = F('subtotal_dl')*Decimal(nuevoCambio)
        )
       
        return JsonResponse({'mensaje': 'CAMBIO', 'id': idFactura})
    else:
        return JsonResponse({'mensaje': 'Error POST'})
    
    
def dt_serverside_salidaproductos(request):
    context = {}
    formato_fecha = '%Y-%m-%d'
    print('inicial', datetime.now())
    fecha_inicial = request.GET.get('fecha_inicial')
    fecha_final = request.GET.get('fecha_final')
    
    
    fecha_inicial = datetime.strptime(fecha_inicial, formato_fecha)
    
    fecha_final = datetime.strptime(fecha_final, formato_fecha)
    
    fecha_final = fecha_final.replace(hour=23, minute=59, second=59)
    fecha_inicial = fecha_inicial.replace(hour=00, minute=00, second=00)
    
    dt = request.GET 
    
    draw = int(dt.get("draw"))
    start = int(dt.get("start"))
    length = int(dt.get("length"))
    search = dt.get("search[value]")
    
    registros = InventarioDescarga.objects.filter(fecha_act__range=(fecha_inicial, fecha_final), depositoentrada__isnull = True).exclude(tipodescarga_id = 5).values_list( 'id','fecha_act','inventario__codigo','inventario__nombre', 'inventario__nombre_comercial', 'inventario__presentacion__nombre','inventario__presentacion_salida__nombre','cantidad','deposito__nombre','cirugia_id','cirugia__paciente__nombre','tipodescarga__nombre','usuario__username','descargamanual','cirugia__paciente__apellido', 'atencion_inmediata__paciente__nombre','atencion_inmediata__paciente__apellido','atencion_inmediata__codigo').order_by('-id')
    
    if search:
        registros = registros.filter(
            Q(inventario__codigo__icontains=search) |
            Q(inventario__nombre__icontains=search) |
            Q(cirugia__id__icontains=search) |
            Q(inventario__nombre_comercial__icontains=search) |
            Q(tipodescarga__nombre__icontains=search) |
            Q(descargamanual__icontains=search)
        )
        
    recordsTotal = registros.count()
    recordsFiltered = recordsTotal
    
    context["draw"] = draw
    context["recordsTotal"] = recordsTotal
    context["recordsFiltered"] = recordsFiltered
    
    reg = registros[start:start + length]
    paginator = Paginator(reg, length)
    
    try:
        obj = paginator.page(draw).object_list
    except PageNotAnInteger:
        obj = paginator.page(draw).object_list
    except EmptyPage:
        obj = paginator.page(paginator.num_pages).object_list
        
 
    datos = [
        {
            "id":d[0],
            "fecha_act" : d[1],
            "codigo":d[2],
            "nombre":d[3],
            "nombre_comercial":d[4],
            "presentacion":d[5],
            "presentacion_salida" : d[6],
            "cantidad":d[7],
            "deposito":d[8],
            "cirugia_id":d[9],
            "paciente":d[10],
            "tipodescarga":d[11],
            "usuario":d[12],
            "descargamanual":d[13],
            "apellido":d[14],
            "nombre_ami":d[15],
            "apellido_ami":d[16],
            "codigo_ami":d[17],
            "id" : d[0],
            
           
        } for d in obj
    ]
    print('final', datetime.now())
    context["datos"] = datos
    return JsonResponse(context,safe=False)

def generar_siguiente_codigo_preingreso():
    ultimo = (PreIngreso.objects
        .annotate(num=Cast(Substr('codigo', 4), IntegerField()))
        .order_by('-num')
        .first()
    )

    if not ultimo:
        # Si no hay registros, comienza por AMI0001
        return 1

    numero = ultimo.num + 1
    return numero


def generar_siguiente_codigo():
    ultimo = (AtencionInmediata.objects
        .annotate(num=Cast(Substr('codigo', 4), IntegerField()))
        .order_by('-num')
        .first()
    )

    if not ultimo:
        # Si no hay registros, comienza por AMI0001
        return 1

    numero = ultimo.num + 1
    return numero

def generar_siguiente_codigo_cortesia():
    ultimo = (AtencionInmediataCortesia.objects
        .annotate(num=Cast(Substr('codigo', 4), IntegerField()))
        .order_by('-num')
        .first()
    )

    if not ultimo:
        # Si no hay registros, comienza por AMI0001
        return 1

    numero = ultimo.num + 1
    return numero


@add_group_name_to_context    
class AtencionInmediataView(UserPassesTestMixin,TemplateView):
    template_name='atencion_inmediata.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Enfermeria')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        AtencionInmediata.objects.filter(estatus_id = 9).delete()
        #Paciente.objects.filter(status = 'X').delete()
        habitaciones = Habitacion.objects.all().order_by('habitacion')
        kit = KitInventario.objects.all().order_by('nombre')
        personal_medico = Medico.objects.filter(grupo='M').exclude(tipopersonal_id = 9).order_by('nombre')
        depositos = Deposito.objects.all().order_by('nombre')
        baremo = Baremo.objects.filter(inactivar = False).order_by('detalle__posicion')
        tipo_procedimiento = TipoProcedimiento.objects.filter(id=5).first()
        #edad_paciente=calcular_edad(cirugia.paciente.fecha_nac)
        atencioncreada = AtencionInmediata.objects.create(
            usuario_id = self.request.user.id
        )
        atencion_id = atencioncreada.id
        nuevo_codigo = generar_siguiente_codigo()
        AtencionInmediata.objects.filter(id = atencion_id ).update(
            codigo = 'AMI'+str(nuevo_codigo).zfill(4)
        )
        fecha_hoy = datetime.now().date()
        hora_actual = datetime.now().time()
        medicosatencioninmediata = NotaQuirurgica.objects.filter(atencion_inmediata_id=atencion_id).order_by('medico__nombre')

        context['codigoatencion'] = 'AMI'+str(nuevo_codigo).zfill(4)
        context['kit'] = kit
        context['atencion_id'] = atencion_id
        context['personal_medico'] = personal_medico
        context['depositos'] = depositos
        context['baremo'] = baremo
        context['fecha_hoy'] = fecha_hoy
        context['hora_actual'] = hora_actual
        context['habitaciones'] = habitaciones
        context['tipo_procedimiento'] = tipo_procedimiento
        context['medicosatencioninmediata'] = medicosatencioninmediata
        
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        if 'guardar_atencion' in request.POST:
            cedula_atencion_inmediata =  self.request.POST.get('cedula_atencion_inmediata')
            nombrepaciente =  self.request.POST.get('nombrepaciente')
            apellidopaciente =  self.request.POST.get('apellidopaciente')
            fecha_nac_paciente =  self.request.POST.get('fecha_nac_paciente')
            fecha_atencion =  self.request.POST.get('fecha_atencion')
            motivo_atencion =  self.request.POST.get('motivo_atencion')
            medico_ppal_atencion =  self.request.POST.get('medico_ppal_atencion')
            habitacion_atencion =  self.request.POST.get('habitacion_atencion')
            idPaciente_name =  self.request.POST.get('idPaciente_name')
            idatencion_name =  self.request.POST.get('id-atencion-name')
            hora_ingreso =  self.request.POST.get('hora_ingreso')
            
            
            Paciente.objects.filter(id=idPaciente_name).update(
                cedula = cedula_atencion_inmediata,
                nombre = nombrepaciente,
                apellido = apellidopaciente,
                fecha_nac = fecha_nac_paciente,
                status = 'A'
            )
            
            AtencionInmediata.objects.filter(id = idatencion_name).update(
                fecha_procedimiento = fecha_atencion,
                motivo_atencion = motivo_atencion,
                estatus_id = 2,
                medico_ppal_id = medico_ppal_atencion,
                paciente_id = idPaciente_name,
                tipo_procedimiento_id = 5,
                usuario_id = self.request.user.id,
                habitacion_id = habitacion_atencion,
                hora_procedimiento = hora_ingreso
                
            )
            presupuesto = Presupuesto.objects.filter(atencion_inmediata_id = idatencion_name).first()
            if presupuesto:
                Presupuesto.objects.filter(atencion_inmediata_id = idatencion_name).update(
                    medico_ppal_id = medico_ppal_atencion,
                    estatus_id = 2,
                )
            else:
                presupuesto = Presupuesto.objects.create(
                    atencion_inmediata_id =  idatencion_name,
                    fecha_procedimiento  = datetime.now(),
                    hora_procedimiento = datetime.now().time(),
                    nombre_procedimiento = 'Atencion Medica Inmediata ',
                    medico_ppal_id = medico_ppal_atencion,
                    paciente_id = idPaciente_name,
                    tipo_procedimiento_id = 5,
                    usuario_id = request.user.id,
                    estatus_id = 2,
                    convenio_id = 1,
                    )  
            
            consumohospital = ConsumoCirugia.objects.filter(atencion_inmediata_id = idatencion_name)
            descargainventario = ConsumoCirugia.objects.filter(atencion_inmediata_id = idatencion_name, conciliada = False)
            if consumohospital: 
                monto_subtotal_farmacia = consumohospital.aggregate(subtotal_farmacia=Sum('venta'))['subtotal_farmacia']
                for descarga in descargainventario:
                    ConsumoCirugia.objects.filter(id = descarga.id).update(
                        conciliada = True
                    )
            else:
                monto_subtotal_farmacia = 0
            
            presupuesto = Presupuesto.objects.filter(atencion_inmediata_id = idatencion_name).first()
            
            if presupuesto:
                presupuestoatencioninmediata = DetallePresupuesto.objects.filter(presupuesto__atencion_inmediata_id = idatencion_name)
                monto_subtotal_baremo = presupuestoatencioninmediata.aggregate(total=Sum(F('precio')))['total']
                if not presupuestoatencioninmediata:
                    monto_subtotal_baremo = 0
                    
                total_subtotal = Decimal(monto_subtotal_farmacia) + Decimal(monto_subtotal_baremo)
                
                cuenta_por_cobrar = CuentaxCobrar.objects.create(
                        pagado = False,
                        atencion_inmediata_id = idatencion_name,
                        paciente_id = idPaciente_name,
                        presupuesto_id = presupuesto.id,
                        usuario_id = self.request.user.id
                    )
                    
                DetalleCuentaCobrar.objects.create(
                        cuentacobrar_id = cuenta_por_cobrar.id,
                        montocobrar = total_subtotal,
                        descripcion = 'Atencion Medica Inmediata:'+str(idatencion_name).zfill(4),
                    )
            
            
            
        return redirect('listado_atencion_inmediata')
    
    
def buscar_paciente_existe(request):
    #por aqui pasa atencion medica inmediata
    if request.method == 'POST':
        datos = json.loads(request.body)
        cedula = datos['cedula']
        paciente = Paciente.objects.filter(cedula=cedula).first()
        cirugias_anteriores = Cirugia.objects.filter(paciente__cedula = cedula).order_by('-fecha_act')
        amis_activas = AtencionInmediata.objects.filter(paciente__cedula = cedula, estatus_id__lt = 7).count()
        amis_cortesia_activas = AtencionInmediataCortesia.objects.filter(paciente__cedula = cedula, estatus_id__lt = 7).count()
        presupuestos = Presupuesto.objects.filter(paciente__cedula = cedula, estatus_id = 1)
        presupuesto_data = []
        if presupuestos:
            presupuesto_data = [
            {
                'id': presupuesto.id,
                'fecha_act': presupuesto.fecha_act,
                'nombre_procedimiento': presupuesto.nombre_procedimiento,  # Asumiendo que tienes un campo 'tipo' en el modelo Cirugia
                'tipo_procedimiento': presupuesto.tipo_procedimiento.nombre,
                # Agrega más campos según sea necesario
            }
            for presupuesto in presupuestos
            ]
            
            
        cirugias_activas = 0
        if cirugias_anteriores:
            cirugias_activas = Cirugia.objects.filter(paciente__cedula = cedula, estatus_id__in = [1,2,3,4,5,6,11] ).count()
                
            historial = 'True'
            cirugias_data = [
            {
                'id': cirugia.id,
                'fecha_act': cirugia.fecha_act,
                'nombre_procedimiento': cirugia.nombre_procedimiento,  # Asumiendo que tienes un campo 'tipo' en el modelo Cirugia
                'tipo_procedimiento': cirugia.tipo_procedimiento.nombre,
                # Agrega más campos según sea necesario
            }
            for cirugia in cirugias_anteriores
            ]
            
        else:
            historial = 'False'
            cirugias_data = []

        if paciente:
            nombre = paciente.nombre
            apellido = paciente.apellido
            fecha_nac = paciente.fecha_nac
            return JsonResponse({
                'mensaje': 'Paciente encontrado',
                'cedula': cedula,
                'nombre': nombre,
                'apellido': apellido,
                'fecha_nac': fecha_nac,
                'idPaciente': paciente.id,
                'historial': historial,
                'cirugias_anteriores': cirugias_data ,
                'cirugias_activas' : cirugias_activas,
                'presupuestos_activos' : presupuesto_data,
                'amis_activas':amis_activas,
                'amis_cortesia_activas' : amis_cortesia_activas
            })
        else:
            pacientenew = Paciente.objects.create(
                cedula = cedula,
                usuario_id = request.user.id,
                status = 'X'
            )
            
            return JsonResponse({
                'mensaje': 'Paciente no encontrado',
                'cedula': cedula,
                'nombre': '',
                'apellido': '',
                'fecha_nac': '',
                'idPaciente': pacientenew.id,
                'historial': historial,
                'cirugias_anteriores': cirugias_data,
                'amis_activas':amis_activas,
                'amis_cortesia_activas' : amis_cortesia_activas
            })
    else:
        return JsonResponse({'mensaje': 'Error al procesar la solicitud'}, status=400)
    
    
@add_group_name_to_context    
class IncrementoInventario(UserPassesTestMixin,TemplateView):
    template_name='update_percent_inventory.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incremento = MontoIncremento.objects.filter(id=1).first()

        context['incremento'] = incremento
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        porcentaje =  self.request.POST.get('porcentajeincremento')
        
        MontoIncremento.objects.filter(id=1).update(
            porcentaje = porcentaje.replace(',','.')
        )
        
        return redirect('index')
    
def eliminarPagoMedico(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idNotaQx = datos['idNotaQx']
        NotaQuirurgica.objects.filter(id=idNotaQx).update(
                    pagado = True,
                    pagoeliminado = True,
                    notaeliminacion = 'Pago eliminado por usuario:'+str(request.user.username),
                    usuario_id = request.user.id
                    )
    
        return JsonResponse({'mensaje': 'procesada la solicitud'}, status=200)
    
def eliminarTodosPagoMedico(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        medico_id = datos['medico_id']
        NotaQuirurgica.objects.filter(medico_id=medico_id).update(
                    pagado = True,
                    pagoeliminado = True,
                    notaeliminacion = 'Pago eliminado por usuario:'+str(request.user.username),
                    usuario_id = request.user.id
                    )
    
        return JsonResponse({'mensaje': 'procesada la solicitud'}, status=200)

def buscar_tasa_bcv(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nfechaCambio = datos['nfechaCambio']
        idFactura = datos['idFactura']
        
        tasa_tx = CambioBcv.objects.filter(fecha_cambio=nfechaCambio).first()
        tasa_del_dia = 0
        if tasa_tx:
            tasa_del_dia = tasa_tx.cambio
            FacturaProveedor.objects.filter(id=idFactura).update(
                cambio_congelado = tasa_del_dia,
                fecha_cambio = nfechaCambio,
                congelar_moneda = True
            )
            DetalleFacturaProveedor.objects.filter(factura_id = idFactura, cambio_bcv__gt = 0).update(
                congelar_moneda = True,
                cambio_bcv = tasa_del_dia,
                precio_bs = F('precio_unitario')*tasa_del_dia,
                gastos_bs = F('gastos')*tasa_del_dia,
                subtotal_bs = (F('precio_unitario')*F('cantidad'))*tasa_del_dia
                
            )
            DetalleFacturaProveedor.objects.filter(factura_id = idFactura, cambio_bcv = 0).update(
                congelar_moneda = True,
                precio_bs = F('precio_unitario')*tasa_del_dia,
                subtotal_bs = (F('precio_unitario')*F('cantidad'))*tasa_del_dia
                
            )
            
        return JsonResponse({
                'congelar_cambio': tasa_del_dia,
            })

def cambio_tasa_bcv_factura_medico(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nNuevocambio = datos['nNuevocambio']
        idFactura = datos['idFactura']
        tasa_del_dia = Decimal(nNuevocambio)
        FacturaProveedor.objects.filter(id=idFactura).update(
            cambio_congelado = Decimal(nNuevocambio),
            congelar_moneda = True,
            usuario_id = request.user.id
        )
        DetalleFacturaProveedor.objects.filter(factura_id = idFactura).update(
            congelar_moneda = True,
            cambio_bcv = tasa_del_dia,
            precio_bs = F('precio_unitario')*tasa_del_dia,
            gastos_bs = F('gastos')*tasa_del_dia,
            subtotal_bs = (F('precio_unitario')*F('cantidad'))*tasa_del_dia
            
        )
        DetalleFacturaProveedor.objects.filter(factura_id = idFactura, cambio_bcv = 0).update(
            congelar_moneda = True,
            precio_bs = F('precio_unitario')*tasa_del_dia,
            subtotal_bs = (F('precio_unitario')*F('cantidad'))*tasa_del_dia
            
        )
            
        return JsonResponse({
                'congelar_cambio': tasa_del_dia,
            })
        
def seleccionaPersonalMedico(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idMedico = datos['idMedico']
        idAtencion = datos['idAtencion']
        
        NotaQuirurgica.objects.create(
            medico_id = idMedico,
            atencion_inmediata_id = idAtencion,
            nota = 'Atencion Medica Inmediata usuario creador : '+str(request.user.username)
        )
        return JsonResponse({'mensaje': 'Creado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})
    
def refresh_table_atencion(request):
    idAtencion = request.GET.get('idAtencion')
    medicosatencioninmediata = NotaQuirurgica.objects.filter(atencion_inmediata_id = idAtencion).order_by('medico__nombre')
    atencion_inmediata = AtencionInmediata.objects.filter(id=idAtencion).first()
    
    return render(request, 'tabla_medico_atencion.html', {'medicosatencioninmediata': medicosatencioninmediata,'atencion_inmediata' : atencion_inmediata })  


def refresh_table_disponible_deposito(request):
    depositoId = request.GET.get('depositoId')
    deposito_seleccion = DepositoUso.objects.filter(deposito_id = depositoId, inventario__categoria_id__in=['1', '2'], inventario__producto_activo =True)
        
    return render(request, 'tabla_farmacia_atencion_inmediata.html', {'deposito_seleccion': deposito_seleccion, 'depositoId':depositoId})  


def agregar_a_consumo_cirugia(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        inventario_id = datos['inventario_id']
        cantidad_aplicar = datos['cantidad_aplicar']
        idAtencion = datos['idAtencion']
        depositoId = datos['depositoId']
        depositoubicacion = DepositoUso.objects.filter(inventario_id = inventario_id, deposito_id = depositoId).first()
        if depositoubicacion:
            if  Decimal(cantidad_aplicar) <= Decimal(depositoubicacion.existenciaUnd):
                producto = Inventario.objects.filter(id=inventario_id).first()
                precio_costo_unitario = precio_costo_producto_inventario(inventario_id)
                consumonuevo = ConsumoCirugia.objects.create(
                    atencion_inmediata_id = idAtencion,
                    cantidad_real_usada = cantidad_aplicar,
                    cantidad_uso = cantidad_aplicar,
                    venta = 0,
                    nota = 'ATENCION INMEDIATA',
                    inventario_id = inventario_id,
                    consumo_id = 6,
                    usuario_id = request.user.id,
                    hora_uso = datetime.now().time(),
                    precio_unitario = producto.monto_venta,
                    deposito_id = depositoId,
                    precio_costo_unitario = precio_costo_unitario
                )
                InventarioDescarga.objects.create(
                    cantidad = cantidad_aplicar,
                    nota = 'ATENCION INMEDIATA',
                    deposito_id = depositoId,
                    inventario_id = inventario_id,
                    usuario_id = request.user.id,
                    tipodescarga_id = 10,
                    atencion_inmediata_id = idAtencion,
                    persona_id = request.user.id,
                    consumocirugia_id = consumonuevo.id
                )
                
                return JsonResponse({'mensaje': 'Creado Consumo'})
            else:
                return JsonResponse({'mensaje': 'No dispone de cantidad en existencia'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8048 View.py'})

def agregar_a_consumo_cirugia_cortesia(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        inventario_id = datos['inventario_id']
        cantidad_aplicar = datos['cantidad_aplicar']
        idAtencion = datos['idAtencion']
        depositoId = datos['depositoId']
        depositoubicacion = DepositoUso.objects.filter(inventario_id = inventario_id, deposito_id = depositoId).first()
        if depositoubicacion:
            if  Decimal(cantidad_aplicar) <= Decimal(depositoubicacion.existenciaUnd):
                producto = Inventario.objects.filter(id=inventario_id).first()
                precio_costo_unitario = precio_costo_producto_inventario(inventario_id)
                consumonuevo = ConsumoCirugia.objects.create(
                    atencion_cortesia_id = idAtencion,
                    cantidad_real_usada = cantidad_aplicar,
                    cantidad_uso = cantidad_aplicar,
                    venta = 0,
                    nota = 'ATENCION CORTESIA',
                    inventario_id = inventario_id,
                    consumo_id = 12,
                    usuario_id = request.user.id,
                    hora_uso = datetime.now().time(),
                    precio_unitario = producto.monto_venta,
                    deposito_id = depositoId,
                    precio_costo_unitario = precio_costo_unitario
                )
                InventarioDescarga.objects.create(
                    cantidad = cantidad_aplicar,
                    nota = 'ATENCION CORTESIA',
                    deposito_id = depositoId,
                    inventario_id = inventario_id,
                    usuario_id = request.user.id,
                    tipodescarga_id = 10,
                    atencion_cortesia_id = idAtencion,
                    persona_id = request.user.id,
                    consumocirugia_id = consumonuevo.id
                )
                
                return JsonResponse({'mensaje': 'Creado Consumo'})
            else:
                return JsonResponse({'mensaje': 'No dispone de cantidad en existencia'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8048 View.py'})
    
    
def refresh_table_consumo_cirugia(request):
    idAtencion = request.GET.get('idAtencion')
    atencion_inmediata = AtencionInmediata.objects.filter(id=idAtencion).first()
    consumohospital = ConsumoCirugia.objects.filter(atencion_inmediata_id = idAtencion).order_by('-id')
    total_subtotal_farmacia = consumohospital.annotate(
        sub_total=F('cantidad_real_usada') * F('precio_unitario')
    ).aggregate(total=Sum('sub_total'))['total']
    
    html = render_to_string('tabla_consumo_farmacia_atencion.html', {
        'consumohospital': consumohospital,
        'total_subtotal_farmacia': total_subtotal_farmacia,
        'atencion_inmediata':atencion_inmediata
    })
    
    return JsonResponse({'html': html, 'total_subtotal_farmacia': total_subtotal_farmacia}) 


    
def refresh_table_consumo_cirugia_cortesia(request):
    idAtencion = request.GET.get('idAtencion')
    atencion_inmediata = AtencionInmediataCortesia.objects.filter(id=idAtencion).first()
    consumohospital = ConsumoCirugia.objects.filter(atencion_cortesia_id = idAtencion).order_by('-id')
    total_subtotal_farmacia = consumohospital.annotate(
        sub_total=F('cantidad_real_usada') * F('precio_costo_unitario')
    ).aggregate(total=Sum('sub_total'))['total']
    
    html = render_to_string('tabla_consumo_farmacia_atencion.html', {
        'consumohospital': consumohospital,
        'total_subtotal_farmacia': total_subtotal_farmacia,
        'atencion_inmediata':atencion_inmediata
    })
    
    return JsonResponse({'html': html, 'total_subtotal_farmacia': total_subtotal_farmacia}) 

def refresh_table_consumo_preingreso(request):
    idAtencion = request.GET.get('idAtencion')
    atencion_inmediata = PreIngreso.objects.filter(id=idAtencion).first()
    consumohospital = ConsumoCirugia.objects.filter(preingreso_id = idAtencion).order_by('-id')
    superUser = request.user.groups.filter(Q(name='SuperAdministracion')).exists()
    total_subtotal_farmacia = consumohospital.annotate(
        sub_total=F('cantidad_real_usada') * F('precio_unitario')
    ).aggregate(total=Sum('sub_total'))['total']
    
    html = render_to_string('tabla_consumo_farmacia_atencion.html', {
        'consumohospital': consumohospital,
        'total_subtotal_farmacia': total_subtotal_farmacia,
        'atencion_inmediata':atencion_inmediata,
        'superUser':superUser
    })
    
    return JsonResponse({'html': html, 'total_subtotal_farmacia': total_subtotal_farmacia}) 

def eliminar_consumo_cirugia_atencionmedica(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        consumo_id = datos['consumo_id']
        compuesto = ConsumoCirugia.objects.filter(id=consumo_id, conciliada=False).first()
        superUser = request.user.groups.filter(Q(name='SuperAdministracion')).exists()
        if superUser:
            consumoeliminar = ConsumoCirugia.objects.filter(id=consumo_id).first()
            if consumoeliminar:
                LogInventario.objects.create(
                    inventario_id = consumoeliminar.inventario_id,
                    cantidad = consumoeliminar.cantidad_real_usada,
                    usuario_id = request.user.id,
                    cirugia_id = consumoeliminar.cirugia_id,
                    nota = 'Eliminado en Atencion inmediata por super user :'+str(consumoeliminar.inventario)+str(consumoeliminar.inventario.codigo)+' de la cirugia: '+str(consumoeliminar.cirugia_id)+' / '+ str(consumoeliminar.cirugia)
                )
            
                ConsumoCirugia.objects.filter(id=consumo_id).delete()
        else:
            ConsumoCirugia.objects.filter(id=consumo_id, conciliada=False).delete()
        
        return JsonResponse({'mensaje': 'Eliminado Consumo'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8065 View.py'})
    

def eliminar_medico_atencionmedica(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idNotaQx = datos['idNotaQx']
        NotaQuirurgica.objects.filter(id=idNotaQx, pagado=False).delete()
        return JsonResponse({'mensaje': 'Eliminado Medico'})
    else:
        return JsonResponse({'mensaje': 'Error Creeliminarando 8077 View.py'})
    

def agregar_tratamiento_atencioninmediata(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        comentarios_tratamiento = datos['comentarios_tratamiento']
        idAtencion = datos['idAtencion']
        cantidad = datos['cantidad']

        Tratamiento.objects.create(
           atencion_inmediata_id =  idAtencion,
           tratamiento = comentarios_tratamiento,
           cantidad_uso = cantidad,
           usuario_id = request.user.id
        )        
        
        return JsonResponse({'mensaje': 'Agregado tratamiento Medico'})
    else:
        return JsonResponse({'mensaje': 'Error agregartratamiento 8091 View.py'})

def agregar_tratamiento_atencion_cortesia(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        comentarios_tratamiento = datos['comentarios_tratamiento']
        idAtencion = datos['idAtencion']
        cantidad = datos['cantidad']

        Tratamiento.objects.create(
           atencion_cortesia_id =  idAtencion,
           tratamiento = comentarios_tratamiento,
           cantidad_uso = cantidad,
           usuario_id = request.user.id
        )        
        
        return JsonResponse({'mensaje': 'Agregado tratamiento Medico'})
    else:
        return JsonResponse({'mensaje': 'Error agregartratamiento 8091 View.py'})
    
def agregar_tratamiento_preingreso(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        comentarios_tratamiento = datos['comentarios_tratamiento']
        idAtencion = datos['idAtencion']
        cantidad = datos['cantidad']

        Tratamiento.objects.create(
           preingreso_id =  idAtencion,
           tratamiento = comentarios_tratamiento,
           cantidad_uso = cantidad,
           usuario_id = request.user.id
        )        
        
        return JsonResponse({'mensaje': 'Agregado tratamiento Medico'})
    else:
        return JsonResponse({'mensaje': 'Error agregartratamiento 8091 View.py'})

    
def refresh_table_tratamiento_atencioninmediata(request):
    idAtencion = request.GET.get('idAtencion')
    tratamientos = Tratamiento.objects.filter(atencion_inmediata_id = idAtencion)
    atencion_inmediata = AtencionInmediata.objects.filter(id=idAtencion).first()
    return render(request, 'tabla_tratamiento_atencion.html', {'tratamientos': tratamientos, 'atencion_inmediata':atencion_inmediata})  

def refresh_table_tratamiento_atencion_cortesia(request):
    idAtencion = request.GET.get('idAtencion')
    tratamientos = Tratamiento.objects.filter(atencion_cortesia_id = idAtencion)
    atencion_inmediata = AtencionInmediataCortesia.objects.filter(id=idAtencion).first()
    return render(request, 'tabla_tratamiento_atencion.html', {'tratamientos': tratamientos, 'atencion_inmediata':atencion_inmediata})  

def refresh_table_tratamiento_preingreso(request):
    idAtencion = request.GET.get('idAtencion')
    tratamientos = Tratamiento.objects.filter(preingreso_id = idAtencion)
    atencion_inmediata = PreIngreso.objects.filter(id=idAtencion).first()
    return render(request, 'tabla_tratamiento_atencion.html', {'tratamientos': tratamientos, 'atencion_inmediata':atencion_inmediata})  




def eliminar_tratamiento_atencionmedica(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idTratamiento = datos['idTratamiento']
        Tratamiento.objects.filter(id=idTratamiento, cumplido = False).delete()
        
        return JsonResponse({'mensaje': 'Eliminado Tratamiento'})
    else:
        return JsonResponse({'mensaje': 'Error Tratamiento 8123 View.py'})
    

def agregar_presupuesto_atencioninmediata(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idBaremo = datos['idBaremo']
        idAtencion = datos['idAtencion']
        idMedico = datos['idMedico']
        idPaciente = datos['idPaciente']
        baremo = Baremo.objects.filter(id=idBaremo).first()
        if baremo:
            existe_presupuesto = Presupuesto.objects.filter(atencion_inmediata_id=idAtencion).first()
            if existe_presupuesto:
                presupuesto_id = existe_presupuesto.id
            else:
                presupuesto = Presupuesto.objects.create(
                    atencion_inmediata_id =  idAtencion,
                    fecha_procedimiento  = datetime.now(),
                    hora_procedimiento = datetime.now().time(),
                    nombre_procedimiento = 'Atencion Medica Inmediata ',
                    medico_ppal_id = idMedico,
                    paciente_id = idPaciente,
                    tipo_procedimiento_id = 5,
                    usuario_id = request.user.id,
                    estatus_id = 9,
                    convenio_id = 1,
                    )  
                presupuesto_id = presupuesto.id
                
                
            DetallePresupuesto.objects.create(
                cantidad = baremo.cantidad,
                precio = baremo.venta,
                notas = 'Atencion Medica Inmediata',
                convenio_id = 1,
                detalle_id = baremo.detalle_id,
                grupo_id = baremo.grupo_id,
                plantilla_id = baremo.plantilla_id,
                usuario_id = request.user.id,
                presupuesto_id = presupuesto_id
                )
            
                
        return JsonResponse({'mensaje': 'Agregado Baremo Presupuesto Medico'})
    else:
        return JsonResponse({'mensaje': 'Error agrega baremo xxxx View.py'})

def agregar_presupuesto_atencion_cortesia(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idBaremo = datos['idBaremo']
        idAtencion = datos['idAtencion']
        idMedico = datos['idMedico']
        idPaciente = datos['idPaciente']
        baremo = Baremo.objects.filter(id=idBaremo).first()
        if baremo:
            existe_presupuesto = Presupuesto.objects.filter(atencion_cortesia_id=idAtencion).first()
            if existe_presupuesto:
                presupuesto_id = existe_presupuesto.id
            else:
                presupuesto = Presupuesto.objects.create(
                    atencion_cortesia_id =  idAtencion,
                    fecha_procedimiento  = datetime.now(),
                    hora_procedimiento = datetime.now().time(),
                    nombre_procedimiento = 'Atencion Medica Cortesia : AMC',
                    medico_ppal_id = idMedico,
                    paciente_id = idPaciente,
                    tipo_procedimiento_id = 5,
                    usuario_id = request.user.id,
                    estatus_id = 9,
                    convenio_id = 1,
                    )  
                presupuesto_id = presupuesto.id
                
                
            DetallePresupuesto.objects.create(
                cantidad = baremo.cantidad,
                precio = baremo.costo,
                notas = 'Atencion Medica Cortesia',
                convenio_id = 1,
                detalle_id = baremo.detalle_id,
                grupo_id = baremo.grupo_id,
                plantilla_id = baremo.plantilla_id,
                usuario_id = request.user.id,
                presupuesto_id = presupuesto_id
                )
            
                
        return JsonResponse({'mensaje': 'Agregado Baremo Presupuesto Medico'})
    else:
        return JsonResponse({'mensaje': 'Error agrega baremo xxxx View.py'})
    
    
def agregar_presupuesto_preingreso(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idBaremo = datos['idBaremo']
        idAtencion = datos['idAtencion']
        idMedico = datos['idMedico']
        idPaciente = datos['idPaciente']
        baremo = Baremo.objects.filter(id=idBaremo).first()
        preingreso = PreIngreso.objects.filter(id=idAtencion).first()
        
        if baremo:
            existe_presupuesto = Presupuesto.objects.filter(id=preingreso.cirugia.presupuesto_id).first()
            if existe_presupuesto:
                presupuesto_id = existe_presupuesto.id
            else:
                presupuesto = Presupuesto.objects.create(
                    fecha_procedimiento  = datetime.now(),
                    hora_procedimiento = datetime.now().time(),
                    nombre_procedimiento = 'PREINGRESO : CPA'+str(idAtencion).zfill(4),
                    medico_ppal_id = idMedico,
                    paciente_id = idPaciente,
                    tipo_procedimiento_id = 6,
                    usuario_id = request.user.id,
                    estatus_id = 11,
                    convenio_id = baremo.convenio_id,
                    )  
                presupuesto_id = presupuesto.id
                
                
            detalle_presupuesto = DetallePresupuesto.objects.filter(presupuesto_id = presupuesto_id, detalle_id = baremo.detalle_id).first()
                
            if detalle_presupuesto:
                DetallePresupuesto.objects.filter(id = detalle_presupuesto.id).update(
                    preingreso_id = idAtencion,
                    usuario_id = request.user.id,
                    cantidad = baremo.cantidad,
                    precio = baremo.venta,
                )
            else:
                DetallePresupuesto.objects.create(
                    cantidad = baremo.cantidad,
                    precio = baremo.venta,
                    notas = 'PRE INGRESO',
                    convenio_id = baremo.convenio_id,
                    detalle_id = baremo.detalle_id,
                    grupo_id = baremo.grupo_id,
                    plantilla_id = baremo.plantilla_id,
                    usuario_id = request.user.id,
                    presupuesto_id = presupuesto_id,
                    preingreso_id = idAtencion,
                    montotope = baremo.topedia,
                    baremo_id = baremo.id
                    )
                
            
            baremo_vinculado = BaremoVinculado.objects.filter(detalle_principal_id = baremo.detalle_id)    
            if baremo_vinculado:
                for nuevo_vinculado in baremo_vinculado:
                    baremo_incluir = Baremo.objects.filter(detalle_id=nuevo_vinculado.detalle_baremo_id, inactivar = False).first()
                    if baremo_incluir:
                        detalle_presupuesto = DetallePresupuesto.objects.filter(presupuesto_id = presupuesto_id, detalle_id = baremo_incluir.detalle_id).first()
                        if detalle_presupuesto:
                            DetallePresupuesto.objects.filter(id = detalle_presupuesto.id).update(
                                preingreso_id = idAtencion,
                                usuario_id = request.user.id,
                                cantidad = baremo_incluir.cantidad,
                                precio = baremo_incluir.venta,
                            )
                        else:
                            DetallePresupuesto.objects.create(
                                cantidad = baremo_incluir.cantidad,
                                precio = baremo_incluir.venta,
                                notas = 'PRE INGRESO',
                                convenio_id = baremo_incluir.convenio_id,
                                detalle_id = baremo_incluir.detalle_id,
                                grupo_id = baremo_incluir.grupo_id,
                                plantilla_id = baremo_incluir.plantilla_id,
                                usuario_id = request.user.id,
                                presupuesto_id = presupuesto_id,
                                preingreso_id = idAtencion,
                                montotope = baremo_incluir.topedia,
                                baremo_id = baremo_incluir.id
                                )
                        
                
            
                
        return JsonResponse({'mensaje': 'Agregado Baremo Presupuesto Medico'})
    else:
        return JsonResponse({'mensaje': 'Error agrega baremo xxxx View.py'})
    

def refresh_table_baremo_atencioninmediata(request):
    atencion_inmediata_id = request.GET.get('atencion_inmediata_id')
    presupuestoatencioninmediata = DetallePresupuesto.objects.filter(presupuesto__atencion_inmediata_id = atencion_inmediata_id).exclude(
         Q(detalle_id=18) | Q(detalle_id=19) )
    
    atencion_inmediata = AtencionInmediata.objects.filter(id=atencion_inmediata_id).first()
    total_subtotal = presupuestoatencioninmediata.annotate(
        sub_total= F('precio')
    ).aggregate(total=Sum('sub_total'))['total']
    
    superUser = request.user.groups.filter(Q(name='SuperAdministracion')).exists()
    html = render_to_string('tabla_baremo_atencioninmediata.html', {
        'presupuestoatencioninmediata': presupuestoatencioninmediata,
        'total_subtotal': total_subtotal,
        'atencion_inmediata':atencion_inmediata,
        'superUser' : superUser
    })
    
    # Devolver un JSON con el HTML y el total
    return JsonResponse({'html': html, 'total_subtotal': total_subtotal }) 

def refresh_table_baremo_atencion_cortesia(request):
    atencion_inmediata_id = request.GET.get('atencion_inmediata_id')
    presupuestoatencioninmediata = DetallePresupuesto.objects.filter(presupuesto__atencion_cortesia_id = atencion_inmediata_id).exclude(
         Q(detalle_id=18) | Q(detalle_id=19) )
    
    atencion_inmediata = AtencionInmediataCortesia.objects.filter(id=atencion_inmediata_id).first()
    total_subtotal = presupuestoatencioninmediata.annotate(
        sub_total= F('precio')
    ).aggregate(total=Sum('sub_total'))['total']
    
    superUser = request.user.groups.filter(Q(name='SuperAdministracion')).exists()
    html = render_to_string('tabla_baremo_atencioninmediata.html', {
        'presupuestoatencioninmediata': presupuestoatencioninmediata,
        'total_subtotal': total_subtotal,
        'atencion_inmediata':atencion_inmediata,
        'superUser' : superUser
    })
    
    # Devolver un JSON con el HTML y el total
    return JsonResponse({'html': html, 'total_subtotal': total_subtotal }) 


def refresh_table_baremo_preingreso(request):
    atencion_inmediata_id = request.GET.get('atencion_inmediata_id')
    presupuestoatencioninmediata = DetallePresupuesto.objects.filter(preingreso_id = atencion_inmediata_id).exclude(
         Q(detalle_id=18) | Q(detalle_id=19) | Q(detalle_id=94))
    
    atencion_inmediata = PreIngreso.objects.filter(id=atencion_inmediata_id).first()
   
    total_subtotal = presupuestoatencioninmediata.annotate(
        sub_total=F('precio')
    ).aggregate(total=Sum('sub_total'))['total']
    
    superUser = request.user.groups.filter(Q(name='SuperAdministracion')).exists()
    html = render_to_string('tabla_baremo_atencioninmediata.html', {
        'presupuestoatencioninmediata': presupuestoatencioninmediata,
        'total_subtotal': total_subtotal,
        'atencion_inmediata':atencion_inmediata,
        'superUser' : superUser,
    })
    
    # Devolver un JSON con el HTML y el total
    return JsonResponse({'html': html, 'total_subtotal': total_subtotal }) 


def eliminar_detallebaremo_atencionmedica(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idDetallepresupuesto = datos['idDetallepresupuesto']
        detallepresupuesto = DetallePresupuesto.objects.filter(id=idDetallepresupuesto).first()
        if detallepresupuesto:
            presupuesto_id = detallepresupuesto.presupuesto_id
            if presupuesto_id:
                cirugia = Cirugia.objects.filter(presupuesto_id=presupuesto_id).first()
                if cirugia:
                    DetalleCirugia.objects.filter(lugar_consumo_id = 7, detalle_id = detallepresupuesto.detalle_id,cirugia_id = cirugia.id).delete()
                
        
                
        DetallePresupuesto.objects.filter(id=idDetallepresupuesto).delete()
        
        return JsonResponse({'mensaje': 'Eliminado baremo'})
    else:
        return JsonResponse({'mensaje': 'Error baremo 8187 View.py'})
    
def cambiar_precio_baremo(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idDetallepresupuesto = datos['idDetallepresupuesto']
        ncantidad = datos['ncantidad']
        vCampo = datos['vCampo']
        detalle =  DetallePresupuesto.objects.filter(id=idDetallepresupuesto).first()
        if vCampo == 'C':
            DetallePresupuesto.objects.filter(id=idDetallepresupuesto).update(
                cantidad = Decimal(ncantidad),
            )
        else:
            if detalle.cantidad == 0:
                newcantidad = 1
            else:
                newcantidad = detalle.cantidad
                
            DetallePresupuesto.objects.filter(id=idDetallepresupuesto).update(
                precio = Decimal(ncantidad)*newcantidad,
                cantidad = newcantidad
            )
        
        return JsonResponse({'mensaje': 'Precio Cambiado Baremo'})
    else:
        return JsonResponse({'mensaje': 'Error  8282 View.py'})
    
    
def actualizar_medico_detalle_presupuesto(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        medico_id = datos['medico_id']
        id_detalle = datos['id_detalle']
        DetallePresupuesto.objects.filter(id=id_detalle).update(
            medico_id = medico_id
        )
            
        return JsonResponse({'mensaje': 'actualizar medico'})
    else:
        return JsonResponse({'mensaje': 'Error  8229 View.py'})
    

def eliminar_no_concretados_atencion_inmediata(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        AtencionInmediata.objects.filter(estatus_id = 9).delete()
        #Paciente.objects.filter(status = 'X').delete()
        return JsonResponse({'mensaje': 'Eliminado no concretados'})
    else:
        return JsonResponse({'mensaje': 'Error  8302 View.py'})

def eliminar_no_concretados_atencion_cortesia(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        AtencionInmediataCortesia.objects.filter(estatus_id = 9).delete()
        #Paciente.objects.filter(status = 'X').delete()
        return JsonResponse({'mensaje': 'Eliminado no concretados'})
    else:
        return JsonResponse({'mensaje': 'Error  8302 View.py'})
    

def eliminar_no_concretados_preingreso(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        PreIngreso.objects.filter(estatus_id = 9).delete()
        #Paciente.objects.filter(status = 'X').delete()
        return JsonResponse({'mensaje': 'Eliminado no concretados'})
    else:
        return JsonResponse({'mensaje': 'Error  8302 View.py'})


    
@add_group_name_to_context    
class ListadoAtencionInmediata(TemplateView):
    template_name='listado_atencion_inmediata.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        AtencionInmediata.objects.filter(estatus_id = 9).delete()
        atencion_inmediata = AtencionInmediata.objects.filter(estatus_id__lte = 9).order_by('-fecha_act')

        context['atencion_inmediata']=atencion_inmediata
        return context
    
@add_group_name_to_context    
class ListadoPreingreso(TemplateView):
    template_name='listado_preingresos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        PreIngreso.objects.filter(estatus_id = 9).delete()
        preingresos = PreIngreso.objects.filter(estatus_id = 11).order_by('-id')

        context['preingresos']=preingresos
        return context
    
    
@add_group_name_to_context    
class AtencionInmediataUpdate(UserPassesTestMixin,TemplateView):
    template_name='atencion_inmediata_update.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Enfermeria')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_atencion = self.kwargs.get('atencion_id')
        habitaciones = Habitacion.objects.all().order_by('habitacion')
        personal_medico = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        depositos = Deposito.objects.all().order_by('nombre')
        baremo = Baremo.objects.filter(inactivar = False).order_by('detalle__posicion')
        tipo_procedimiento = TipoProcedimiento.objects.filter(id=5).first()
        atencion_inmediata = AtencionInmediata.objects.filter(id = id_atencion).first()
        medicostratante = DetallePresupuesto.objects.filter(presupuesto__atencion_inmediata_id = id_atencion, grupo_id = 7, medico__participaalta = True)
        consumohospital = ConsumoCirugia.objects.filter(atencion_inmediata_id = id_atencion)
        monto_subtotal_farmacia = consumohospital.aggregate(subtotal_farmacia=Sum(F('precio_unitario') * F('cantidad_real_usada')))['subtotal_farmacia']
        presupuestoatencioninmediata = DetallePresupuesto.objects.filter(presupuesto__atencion_inmediata_id = id_atencion ).exclude(
                                                                                                                            Q(detalle_id=18) | Q(detalle_id=19))
        monto_subtotal_baremo = presupuestoatencioninmediata.aggregate(total=Sum(F('precio')))['total']
        tratamientos = Tratamiento.objects.filter(atencion_inmediata_id = id_atencion)
        if not consumohospital:
            monto_subtotal_farmacia = 0
            
        if not presupuestoatencioninmediata:
            monto_subtotal_baremo =0
            
        total_subtotal = monto_subtotal_farmacia + monto_subtotal_baremo
        
        superUser = self.request.user.groups.filter(Q(name='SuperAdministracion')).exists()
        context['superUser'] = superUser
        context['personal_medico'] = personal_medico
        context['medicostratante'] = medicostratante
        context['depositos'] = depositos
        context['baremo'] = baremo
        context['habitaciones'] = habitaciones
        context['atencion_inmediata'] = atencion_inmediata
        context['tipo_procedimiento'] = tipo_procedimiento
        context['tratamientos'] = tratamientos
        context['consumohospital'] = consumohospital
        context['total_subtotal'] = total_subtotal
        context['monto_subtotal_farmacia'] = monto_subtotal_farmacia
        context['monto_subtotal_baremo'] = monto_subtotal_baremo
        
        context['presupuestoatencioninmediata'] = presupuestoatencioninmediata
        
        
        
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        id_atencion = self.kwargs.get('atencion_id')
        medicos_notaqx = DetallePresupuesto.objects.filter(presupuesto__atencion_inmediata_id = id_atencion, grupo_id = 7, medico__isnull = False)
        medico_ppal_atencion =  self.request.POST.get('medico_ppal_atencion')
        habitacion_atencion =  self.request.POST.get('habitacion_atencion')
        
        AtencionInmediata.objects.filter(id = id_atencion).update(
            medico_ppal_id = medico_ppal_atencion,
            usuario_id = self.request.user.id,
            habitacion_id = habitacion_atencion,
            
        )
        
        presupuesto = Presupuesto.objects.filter(atencion_inmediata_id = id_atencion).first()
        Presupuesto.objects.filter(atencion_inmediata_id = id_atencion).update(
            medico_ppal_id = medico_ppal_atencion,
            usuario_id = self.request.user.id,
        )
        
        consumohospital = ConsumoCirugia.objects.filter(atencion_inmediata_id = id_atencion)
        descargainventario  = ConsumoCirugia.objects.filter(atencion_inmediata_id = id_atencion, conciliada = False)
        if consumohospital: 
            monto_subtotal_farmacia = consumohospital.aggregate(subtotal_farmacia=Sum(F('precio_unitario') * F('cantidad_real_usada')))['subtotal_farmacia']
            for descarga in descargainventario:
                ConsumoCirugia.objects.filter(id = descarga.id).update(
                    conciliada = True
                )
        else:
            monto_subtotal_farmacia = 0
        
        presupuesto = Presupuesto.objects.filter(atencion_inmediata_id = id_atencion).first()
        monto_subtotal_baremo = 0
        
        if presupuesto:
            presupuestoatencioninmediata = DetallePresupuesto.objects.filter(presupuesto__atencion_inmediata_id = id_atencion).exclude(
                                                                                                                        Q(detalle_id=18) | Q(detalle_id=19))
            monto_subtotal_baremo = presupuestoatencioninmediata.aggregate(total=Sum(F('precio')))['total']
            if not presupuestoatencioninmediata:
                monto_subtotal_baremo = 0
                
                
        total_subtotal = Decimal(monto_subtotal_farmacia) + Decimal(monto_subtotal_baremo)
            
        cuentaxcobrar = CuentaxCobrar.objects.filter(atencion_inmediata_id = id_atencion).first()
        if cuentaxcobrar:  
            DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuentaxcobrar.id, montocobrar__gt = 0).update(
                montocobrar = total_subtotal,
                descripcion = '(AMI) Atencion Medica Inmediata',
                )
        
        
        
        if 'generar_alta_medica' in request.POST:
            fecha_salida = request.POST.get('fecha-egreso-datetime')
            condiciones_egreso = request.POST.get('condicion-egreso')
            diagnostico_egreso = request.POST.get('diag-egreso')
            diagnostico_ingreso = request.POST.get('diag-ingreso')
            tratamiento_recibido = request.POST.get('tratamiento-recibido')
            if medicos_notaqx:
                for pagomedico in medicos_notaqx:
                    NotaQuirurgica.objects.create(
                        nota='Pago por atencion medica inmediata',
                        fecha_elaboracion = datetime.now().date(),
                        atencion_inmediata_id = id_atencion,
                        medico_id = pagomedico.medico_id,
                        participante_id = pagomedico.detalle_id,
                        montopendiente = pagomedico.subtotal,
                    )
                    DetalleCirugia.objects.create(
                        cantidad = 1,
                        precio = pagomedico.subtotal,
                        notas = 'Pago medico atencion medica inmediata',
                        atencion_inmediata_id = id_atencion,
                        detalle_id = pagomedico.detalle_id,
                        grupo_id =  pagomedico.grupo_id,
                        plantilla_id = pagomedico.plantilla_id,
                        unidad_id = 1,
                        usuario_id = self.request.user.id,
                        ntqx = True,
                        facturable= True
                    )
                    
            AltaMedica.objects.create(
                fecha_salida = fecha_salida,
                condiciones_egreso = condiciones_egreso,
                diagnostico_egreso = diagnostico_egreso,
                medico_egreso_id=medico_ppal_atencion,
                diagnostico_ingreso=diagnostico_ingreso,
                tratamiento_recibido=tratamiento_recibido,
                atencion_inmediata_id = id_atencion,
                usuario_id = self.request.user.id
                )
            
            AtencionInmediata.objects.filter(id = id_atencion).update(
                usuario_id = self.request.user.id,
                estatus_id = 7
            )
            
            descargainventario  = ConsumoCirugia.objects.filter(atencion_inmediata_id = id_atencion, conciliada = False)
            for descarga in descargainventario:
                ConsumoCirugia.objects.filter(id = descarga.id).update(
                    conciliada = True
                )
            return redirect('atencion_inmediata_update', atencion_id = id_atencion )
            
        
            
        return redirect('listado_atencion_inmediata')

@add_group_name_to_context    
class AtencionCortesiaUpdate(UserPassesTestMixin,TemplateView):
    template_name='atencion_cortesia_update.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Enfermeria')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_atencion = self.kwargs.get('atencion_id')
        habitaciones = Habitacion.objects.all().order_by('habitacion')
        personal_medico = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        depositos = Deposito.objects.all().order_by('nombre')
        baremo = Baremo.objects.filter(inactivar = False).order_by('detalle__posicion')
        tipo_procedimiento = TipoProcedimiento.objects.filter(id=5).first()
        atencion_inmediata = AtencionInmediataCortesia.objects.filter(id = id_atencion).first()
        medicostratante = DetallePresupuesto.objects.filter(presupuesto__atencion_cortesia_id = id_atencion, grupo_id = 7, medico__participaalta = True)
        consumohospital = ConsumoCirugia.objects.filter(atencion_cortesia_id = id_atencion)
        monto_subtotal_farmacia = consumohospital.aggregate(subtotal_farmacia=Sum(F('precio_costo_unitario') * F('cantidad_real_usada')))['subtotal_farmacia']
        presupuestoatencioninmediata = DetallePresupuesto.objects.filter(presupuesto__atencion_cortesia_id = id_atencion ).exclude(
                                                                                                                            Q(detalle_id=18) | Q(detalle_id=19))
        monto_subtotal_baremo = presupuestoatencioninmediata.aggregate(total=Sum(F('precio')))['total']
        tratamientos = Tratamiento.objects.filter(atencion_cortesia_id = id_atencion)
        if not consumohospital:
            monto_subtotal_farmacia = 0
            
        if not presupuestoatencioninmediata:
            monto_subtotal_baremo =0
            
        total_subtotal = monto_subtotal_farmacia + monto_subtotal_baremo
        
        superUser = self.request.user.groups.filter(Q(name='SuperAdministracion')).exists()
        context['superUser'] = superUser
        context['personal_medico'] = personal_medico
        context['medicostratante'] = medicostratante
        context['depositos'] = depositos
        context['baremo'] = baremo
        context['habitaciones'] = habitaciones
        context['atencion_inmediata'] = atencion_inmediata
        context['tipo_procedimiento'] = tipo_procedimiento
        context['tratamientos'] = tratamientos
        context['consumohospital'] = consumohospital
        context['total_subtotal'] = total_subtotal
        context['monto_subtotal_farmacia'] = monto_subtotal_farmacia
        context['monto_subtotal_baremo'] = monto_subtotal_baremo
        
        context['presupuestoatencioninmediata'] = presupuestoatencioninmediata
        
        
        
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        id_atencion = self.kwargs.get('atencion_id')
        medicos_notaqx = DetallePresupuesto.objects.filter(presupuesto__atencion_cortesia_id = id_atencion, grupo_id = 7, medico__isnull = False)
        medico_ppal_atencion =  self.request.POST.get('medico_ppal_atencion')
        habitacion_atencion =  self.request.POST.get('habitacion_atencion')
        motivo_atencion =  self.request.POST.get('motivo_atencion')
        
        AtencionInmediataCortesia.objects.filter(id = id_atencion).update(
            medico_ppal_id = medico_ppal_atencion,
            usuario_id = self.request.user.id,
            habitacion_id = habitacion_atencion,
            motivo_atencion = motivo_atencion
            
        )
        
        presupuesto = Presupuesto.objects.filter(atencion_cortesia_id = id_atencion).first()
        Presupuesto.objects.filter(atencion_cortesia_id = id_atencion).update(
            medico_ppal_id = medico_ppal_atencion,
            usuario_id = self.request.user.id,
            nombre_procedimiento = motivo_atencion
        )
        
        consumohospital = ConsumoCirugia.objects.filter(atencion_cortesia_id = id_atencion)
        descargainventario  = ConsumoCirugia.objects.filter(atencion_cortesia_id = id_atencion, conciliada = False)
        if consumohospital: 
            monto_subtotal_farmacia = consumohospital.aggregate(subtotal_farmacia=Sum(F('precio_costo_unitario') * F('cantidad_real_usada')))['subtotal_farmacia']
            for descarga in descargainventario:
                ConsumoCirugia.objects.filter(id = descarga.id).update(
                    conciliada = True
                )
        else:
            monto_subtotal_farmacia = 0
        
        presupuesto = Presupuesto.objects.filter(atencion_cortesia_id = id_atencion).first()
        monto_subtotal_baremo = 0
        
        if presupuesto:
            presupuestoatencioninmediata = DetallePresupuesto.objects.filter(presupuesto__atencion_cortesia_id = id_atencion).exclude(
                                                                                                                        Q(detalle_id=18) | Q(detalle_id=19))
            monto_subtotal_baremo = presupuestoatencioninmediata.aggregate(total=Sum(F('precio')))['total']
            if not presupuestoatencioninmediata:
                monto_subtotal_baremo = 0
                
                
        total_subtotal = Decimal(monto_subtotal_farmacia) + Decimal(monto_subtotal_baremo)
            
        cuentaxcobrar = CuentaxCobrar.objects.filter(atencion_cortesia_id = id_atencion).first()
        if cuentaxcobrar:  
            DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuentaxcobrar.id).update(
                montocobrar = total_subtotal,
                descripcion = '(AMC) Atencion Medica Cortesia: AMC',
                )
        
        
        
        if 'generar_alta_medica' in request.POST:
            fecha_salida = request.POST.get('fecha-egreso-datetime')
            condiciones_egreso = request.POST.get('condicion-egreso')
            diagnostico_egreso = request.POST.get('diag-egreso')
            diagnostico_ingreso = request.POST.get('diag-ingreso')
            tratamiento_recibido = request.POST.get('tratamiento-recibido')
            if medicos_notaqx:
                for pagomedico in medicos_notaqx:
                    NotaQuirurgica.objects.create(
                        nota='Pago por atencion medica CORTESIA',
                        fecha_elaboracion = datetime.now().date(),
                        atencion_cortesia_id = id_atencion,
                        medico_id = pagomedico.medico_id,
                        participante_id = pagomedico.detalle_id,
                        montopendiente = pagomedico.subtotal,
                    )
                    DetalleCirugia.objects.create(
                        cantidad = 1,
                        precio = pagomedico.subtotal,
                        notas = 'Pago medico atencion medica inmediata',
                        atencion_cortesia_id = id_atencion,
                        detalle_id = pagomedico.detalle_id,
                        grupo_id =  pagomedico.grupo_id,
                        plantilla_id = pagomedico.plantilla_id,
                        unidad_id = 1,
                        usuario_id = self.request.user.id,
                        ntqx = True,
                        facturable= True
                    )
                    
            AltaMedica.objects.create(
                fecha_salida = fecha_salida,
                condiciones_egreso = condiciones_egreso,
                diagnostico_egreso = diagnostico_egreso,
                medico_egreso_id=medico_ppal_atencion,
                diagnostico_ingreso=diagnostico_ingreso,
                tratamiento_recibido=tratamiento_recibido,
                atencion_cortesia_id = id_atencion,
                usuario_id = self.request.user.id
                )
            
            AtencionInmediataCortesia.objects.filter(id = id_atencion).update(
                usuario_id = self.request.user.id,
                estatus_id = 7
            )
            
            descargainventario  = ConsumoCirugia.objects.filter(atencion_cortesia_id = id_atencion, conciliada = False)
            for descarga in descargainventario:
                ConsumoCirugia.objects.filter(id = descarga.id).update(
                    conciliada = True
                )
            return redirect('atencion_cortesia_update', atencion_id = id_atencion )
            
        
            
        return redirect('listado_atencion_cortesia')
    
def dt_serverside_farmacia_atencion(request):
    deposito_seleccionado = request.GET.get('deposito_seleccionado', None)
    context = {}
    dt = request.GET 
    
    draw = int(dt.get("draw"))
    start = int(dt.get("start"))
    length = int(dt.get("length"))
    search = dt.get("search[value]")
    
    #registros = Inventario.objects.all().values_list('id','codigo' ,'nombre','presentacion__nombre','categoria__nombre','unidad_conversion','piva','costo', 'venta' ,'laboratorio__nombre','nombre_comercial','fecha_vencimiento').order_by("nombre")
    registros = DepositoUso.objects.filter(deposito_id = deposito_seleccionado,cantidad_deposito__gt = 0, inventario__producto_activo =True ).values_list('id','inventario__codigo','inventario__categoria__nombre' ,'inventario__nombre' ,'inventario__nombre_comercial', 'inventario__presentacion__nombre','inventario__presentacion_salida__nombre', 'inventario__id','deposito__nombre','inventario__unidad_conversion','cantidad_consumida','inventario__compuesto')
    
    if search:
        registros = registros.filter(
            Q(id__icontains=search) |
            Q(inventario__nombre__icontains=search) |
            Q(inventario__nombre_comercial__icontains=search) |
            Q(inventario__id__icontains=search) 
        )
        
    recordsTotal = registros.count()
    recordsFiltered = recordsTotal
    
    context["draw"] = draw
    context["recordsTotal"] = recordsTotal
    context["recordsFiltered"] = recordsFiltered
    
    reg = registros[start:start + length]
    paginator = Paginator(reg, length)
    
    try:
        obj = paginator.page(draw).object_list
    except PageNotAnInteger:
        obj = paginator.page(draw).object_list
    except EmptyPage:
        obj = paginator.page(paginator.num_pages).object_list
        
 
    datos = [
        {
            "id" : d[0],
            "idInventario":d[7],
            "categoria":d[2],
            "inventario":d[3],
            "nombre_comercial":d[4],
            "presentacion":d[5],
            "presentacion_salida":d[6],
            "monto_venta": round(Inventario.objects.get(id=d[7]).monto_venta, 2) ,
            
            "existencia_und": round(DepositoUso.objects.filter(inventario_id=d[7], deposito_id=deposito_seleccionado, inventario__producto_activo =True).first().existenciaUnd, 2) if DepositoUso.objects.filter(inventario_id=d[7], deposito_id=deposito_seleccionado).exists() else 0,
            "deposito" : d[8],
            "unidad_conversion": round(Inventario.objects.get(id=d[7]).unidad_conversion, 2) ,
            "cantidad_consumida" : d[10],
            "compuesto" : d[11],
            "id" : d[0],
            
           
        } for d in obj
        if (
            DepositoUso.objects.filter(inventario_id=d[7], deposito_id=deposito_seleccionado).exists() and
            round(DepositoUso.objects.filter(inventario_id=d[7], deposito_id=deposito_seleccionado).first().existenciaUnd, 2) >= 0
        )
    ]

    context["datos"] = datos
    return JsonResponse(context,safe=False)


@add_group_name_to_context    
class pdfAltamedicaAtencionInmediata(TemplateView):
    template_name='pdfaltamedicainmediata.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        usuario_elabora = '('+ self.request.user.username + ') '+ self.request.user.first_name +' '+ self.request.user.last_name
        atencion_id = self.kwargs['pk']
        fecha_hoy = datetime.now()
        usuario_logueado = self.request.user.id
        user = User.objects.get(id=usuario_logueado)
        atencioninmediata = AtencionInmediata.objects.filter(id=atencion_id).first()
        altamedica = AltaMedica.objects.filter(atencion_inmediata_id =atencion_id ).first()
        edad_paciente=calcular_edad(atencioninmediata.paciente.fecha_nac)
        
        
        context['fecha_hoy']=fecha_hoy
        context['altamedica']=altamedica
        context['atencioninmediata']=atencioninmediata
        context['edad_paciente']=edad_paciente
        context['usuario_elabora']=usuario_elabora
        return context

@add_group_name_to_context    
class pdfAltamedicaAtencionCortesia(TemplateView):
    template_name='pdfaltamedicainmediata.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        usuario_elabora = '('+ self.request.user.username + ') '+ self.request.user.first_name +' '+ self.request.user.last_name
        atencion_id = self.kwargs['pk']
        fecha_hoy = datetime.now()
        usuario_logueado = self.request.user.id
        user = User.objects.get(id=usuario_logueado)
        atencioninmediata = AtencionInmediataCortesia.objects.filter(id=atencion_id).first()
        altamedica = AltaMedica.objects.filter(atencion_cortesia_id = atencion_id ).first()
        edad_paciente=calcular_edad(atencioninmediata.paciente.fecha_nac)
        
        
        context['fecha_hoy']=fecha_hoy
        context['altamedica']=altamedica
        context['atencioninmediata']=atencioninmediata
        context['edad_paciente']=edad_paciente
        context['usuario_elabora']=usuario_elabora
        return context
    
    
@add_group_name_to_context    
class listadoConsumoAtencionInmediata(TemplateView): 
    
    template_name='listado_consumo_atencion_inmediata.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atencion_inmediata_id = self.kwargs['pk']
        atencion_inmediata = AtencionInmediata.objects.filter(id=atencion_inmediata_id).first()
        consumos = ConsumoCirugia.objects.filter(atencion_inmediata_id = atencion_inmediata_id).order_by('inventario__nombre')
        
        context['consumo'] = consumos
        context['atencion_inmediata'] = atencion_inmediata
        return context

@add_group_name_to_context    
class listadoConsumoAtencionCortesia(TemplateView): 
    
    template_name='listado_consumo_atencion_cortesia.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atencion_inmediata_id = self.kwargs['pk']
        atencion_inmediata = AtencionInmediataCortesia.objects.filter(id=atencion_inmediata_id).first()
        consumos = ConsumoCirugia.objects.filter(atencion_cortesia_id = atencion_inmediata_id).order_by('inventario__nombre')
        
        context['consumo'] = consumos
        context['atencion_inmediata'] = atencion_inmediata
        return context
    
def change_precio_usd_factura(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idDetallefactura = datos['idDetallefactura']
        montoNew = datos['montoNew']
        
        detalle = DetalleFacturaProveedor.objects.filter(id=idDetallefactura).first()
        DetalleFacturaProveedor.objects.filter(id=idDetallefactura).update(
            precio_bs = Decimal(montoNew),
            subtotal_bs = Decimal(montoNew) * F('cantidad'),
            precio_dl = Decimal(montoNew) / F('cambio_bcv'),
            subtotal_dl = F('subtotal_bs')/F('cambio_bcv'),
            
        )
        
        FacturaProveedor.objects.filter(id = detalle.factura_id).update(
            usuario_id = request.user.id
        )
       
        return JsonResponse({'mensaje': 'PRECIO', 'id': idDetallefactura})
    else:
        return JsonResponse({'mensaje': 'Error POST'})

def change_porcentaje_iva_factura(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idDetallefactura = datos['idDetallefactura']
        montoNew = datos['montoNew']
        
        detalle = DetalleFacturaProveedor.objects.filter(id=idDetallefactura).first()
        DetalleFacturaProveedor.objects.filter(id=idDetallefactura).update(
            porc_iva = montoNew,
            usuario_id = request.user.id
            
        )
        
        FacturaProveedor.objects.filter(id = detalle.factura_id).update(
            usuario_id = request.user.id
        )
       
        return JsonResponse({'mensaje': 'PRECIO', 'id': idDetallefactura})
    else:
        return JsonResponse({'mensaje': 'Error POST'})
    
def change_descuento_bs_factura(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idDetallefactura = datos['idDetallefactura']
        montoNew = datos['montoNew']
        
        detalle = DetalleFacturaProveedor.objects.filter(id=idDetallefactura).first()
        DetalleFacturaProveedor.objects.filter(id=idDetallefactura).update(
            monto_descuento_bs = montoNew
        )
        
        FacturaProveedor.objects.filter(id = detalle.factura_id).update(
            usuario_id = request.user.id
        )
       
        return JsonResponse({'mensaje': 'PRECIO', 'id': idDetallefactura})
    else:
        return JsonResponse({'mensaje': 'Error POST'})
    
def cambiar_cantidad_conciliacion(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        consumo_id = datos['consumo_id']
        cantidad_real_usada = datos['cantidad_real_usada']
        ConsumoCirugia.objects.filter(id=consumo_id, conciliada=False).update(
            cantidad_real_usada = cantidad_real_usada,
            usuario_id = request.user.id
        )
        return JsonResponse({'mensaje': 'cambiado Consumo'})
    else:
        return JsonResponse({'mensaje': 'No dispone de cantidad en existencia'})
    
@add_group_name_to_context    
class CorteCuentaAtencionInmediata(UserPassesTestMixin,TemplateView):
    template_name='corte_cuenta_atencion_inmediata.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atencion_id = self.kwargs['atencion_id']
        atencion_inmediata = AtencionInmediata.objects.filter(id=atencion_id).first()
        total_consumo_farmacia = total_consumo_mmq = 0
        consumos = ConsumoCirugia.objects.filter(atencion_inmediata_id = atencion_id)
        tasa_actual = CambioDiaBcv(datetime.now())
        
        for consumo in consumos:
            if consumo.inventario.categoria_id == 1 :
                total_consumo_farmacia = total_consumo_farmacia + (consumo.precio_unitario * consumo.cantidad_uso)
            
            if consumo.inventario.categoria_id == 2:
                total_consumo_mmq = total_consumo_mmq + (consumo.precio_unitario * consumo.cantidad_uso)
            
        
        detallepresupuesto = []
        medicos = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        fecha_actual = datetime.now().date()
        presupuesto = Presupuesto.objects.filter(atencion_inmediata_id=atencion_id).first()
        if presupuesto:
            detallepresupuesto = DetallePresupuesto.objects.filter(presupuesto_id=presupuesto.id, detalle_id = 19).first()
            detallepresupuesto_mmq = DetallePresupuesto.objects.filter(presupuesto_id=presupuesto.id, detalle_id = 18).first()
            if detallepresupuesto:
                if total_consumo_farmacia > 0:
                    DetallePresupuesto.objects.filter(presupuesto__atencion_inmediata_id=atencion_id, detalle_id = 19).update(
                        cantidad = 1,
                        precio = total_consumo_farmacia,
                        usuario_id = self.request.user.id,
                    )
                    
              
            else:
                if total_consumo_farmacia > 0:
                    DetallePresupuesto.objects.create(
                        presupuesto_id = presupuesto.id,
                        cantidad = 1,
                        precio = total_consumo_farmacia,
                        notas = 'Atencion Medica Inmediata',
                        fecha_cambio = datetime.now().date(),
                        convenio_id = 1,
                        detalle_id = 19,
                        grupo_id = 8,
                        plantilla_id = 1,
                        usuario_id = self.request.user.id,
                    )
                    
            if detallepresupuesto_mmq:
                if total_consumo_mmq > 0:
                    DetallePresupuesto.objects.filter(presupuesto__atencion_inmediata_id=atencion_id, detalle_id = 18).update(
                        cantidad = 1,
                        precio = total_consumo_mmq,
                        usuario_id = self.request.user.id,
                    )
                    
              
            else:
                if total_consumo_mmq > 0:
                    DetallePresupuesto.objects.create(
                        presupuesto_id = presupuesto.id,
                        cantidad = 1,
                        precio = total_consumo_mmq,
                        notas = 'Atencion Medica Inmediata',
                        fecha_cambio = datetime.now().date(),
                        convenio_id = 1,
                        detalle_id = 18,
                        grupo_id = 8,
                        plantilla_id = 1,
                        usuario_id = self.request.user.id,
                    )
                
                
            
            monto_total_pagar_dl = presupuesto.total_monto_precio
            detallepresupuesto = DetallePresupuesto.objects.filter(presupuesto_id=presupuesto.id).annotate(
                                                                subtotal_bs=ExpressionWrapper(
                                                                    F('precio') * tasa_actual,
                                                                    output_field=FloatField()
                                                                )
                                                            ).order_by('detalle__posicion')
            
            cuentacobrar = CuentaxCobrar.objects.filter(atencion_inmediata_id = atencion_id, presupuesto_id = presupuesto.id).first()
            if cuentacobrar:
                DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuentacobrar.id, montocobrar__gte = 0).update(
                    montocobrar = monto_total_pagar_dl
                    
                )
        
        context['medicos'] = medicos 
        context['fecha_actual'] = fecha_actual  
        context['detallepresupuesto'] = detallepresupuesto  
        context['atencion_inmediata'] = atencion_inmediata  
        return context

@add_group_name_to_context    
class CorteCuentaAtencionCortesia(UserPassesTestMixin,TemplateView):
    template_name='corte_cuenta_atencion_inmediata.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atencion_id = self.kwargs['atencion_id']
        atencion_inmediata = AtencionInmediataCortesia.objects.filter(id=atencion_id).first()
        total_consumo_farmacia = total_consumo_mmq = 0
        consumos = ConsumoCirugia.objects.filter(atencion_cortesia_id = atencion_id)
        tasa_actual = CambioDiaBcv(datetime.now())
        
        for consumo in consumos:
            if consumo.inventario.categoria_id == 1 :
                total_consumo_farmacia = total_consumo_farmacia + (consumo.precio_costo_unitario * consumo.cantidad_uso)
            
            if consumo.inventario.categoria_id == 2:
                total_consumo_mmq = total_consumo_mmq + (consumo.precio_costo_unitario * consumo.cantidad_uso)
            
        
        detallepresupuesto = []
        medicos = Medico.objects.filter(grupo = 'M').exclude(tipopersonal_id = 9).order_by('nombre')
        fecha_actual = datetime.now().date()
        presupuesto = Presupuesto.objects.filter(atencion_cortesia_id=atencion_id).first()
        if presupuesto:
            detallepresupuesto = DetallePresupuesto.objects.filter(presupuesto_id=presupuesto.id, detalle_id = 19).first()
            detallepresupuesto_mmq = DetallePresupuesto.objects.filter(presupuesto_id=presupuesto.id, detalle_id = 18).first()
            if detallepresupuesto:
                if total_consumo_farmacia > 0:
                    DetallePresupuesto.objects.filter(presupuesto__atencion_cortesia_id=atencion_id, detalle_id = 19).update(
                        cantidad = 1,
                        precio = total_consumo_farmacia,
                        usuario_id = self.request.user.id,
                    )
                    
              
            else:
                if total_consumo_farmacia > 0:
                    DetallePresupuesto.objects.create(
                        presupuesto_id = presupuesto.id,
                        cantidad = 1,
                        precio = total_consumo_farmacia,
                        notas = 'Atencion Medica CORTESIA',
                        fecha_cambio = datetime.now().date(),
                        convenio_id = 1,
                        detalle_id = 19,
                        grupo_id = 8,
                        plantilla_id = 1,
                        usuario_id = self.request.user.id,
                    )
                    
            if detallepresupuesto_mmq:
                if total_consumo_mmq > 0:
                    DetallePresupuesto.objects.filter(presupuesto__atencion_cortesia_id=atencion_id, detalle_id = 18).update(
                        cantidad = 1,
                        precio = total_consumo_mmq,
                        usuario_id = self.request.user.id,
                    )
                    
              
            else:
                if total_consumo_mmq > 0:
                    DetallePresupuesto.objects.create(
                        presupuesto_id = presupuesto.id,
                        cantidad = 1,
                        precio = total_consumo_mmq,
                        notas = 'Atencion Medica CORTESIA',
                        fecha_cambio = datetime.now().date(),
                        convenio_id = 1,
                        detalle_id = 18,
                        grupo_id = 8,
                        plantilla_id = 1,
                        usuario_id = self.request.user.id,
                    )
                
                
            
            monto_total_pagar_dl = presupuesto.total_monto_precio
            detallepresupuesto = DetallePresupuesto.objects.filter(presupuesto_id=presupuesto.id).annotate(
                                                                subtotal_bs=ExpressionWrapper(
                                                                    F('precio') * tasa_actual,
                                                                    output_field=FloatField()
                                                                )
                                                            ).order_by('detalle__posicion')
            
            cuentacobrar = CuentaxCobrar.objects.filter(atencion_cortesia_id = atencion_id, presupuesto_id = presupuesto.id).first()
            if cuentacobrar:
                DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuentacobrar.id, montocobrar__gte = 0).update(
                    montocobrar = monto_total_pagar_dl
                    
                )
        
        context['medicos'] = medicos 
        context['fecha_actual'] = fecha_actual  
        context['tipo_atencion'] = 'AC' 
        context['detallepresupuesto'] = detallepresupuesto  
        context['atencion_inmediata'] = atencion_inmediata  
        return context
    
    
@add_group_name_to_context    
class ListadoSeguroAtencionInmediata(View): 
    template_name = 'listado_seguro_paciente.html'
    
    def get_context_data(self, atencion_id):
        atencion = AtencionInmediata.objects.filter(id=atencion_id).first()
        total_items = ConsumoCirugia.objects.filter(atencion_inmediata_id = atencion_id).count()
        tasa_bcv_calculo = CambioDiaBcv(datetime.now())
        total_usd = 0
        total_general_costo = 0
        consumos = ConsumoCirugia.objects.filter(atencion_inmediata_id=atencion_id).order_by('inventario__nombre')
        for consumo in consumos:
            monto_venta = round(consumo.inventario.monto_venta,2)  # Asegúrate de que 'inventario' es el campo de relación
            subtotal = Decimal(consumo.cantidad_real_usada) * Decimal(monto_venta)
            subcosto = consumo.precio_costo_unitario
            total_usd = Decimal(total_usd) + Decimal(subtotal)
            consumo.subtotal = subtotal  # Puedes agregarlo como un atributo temporal
            consumo.subtotal_bs = Decimal(subtotal) * Decimal(tasa_bcv_calculo) # Puedes agregarlo como un atributo temporal
            consumo.costo = subcosto
            consumo.subtcosto = Decimal(subcosto)*Decimal(consumo.cantidad_real_usada)
            total_general_costo += Decimal(subcosto)*Decimal(consumo.cantidad_real_usada)
        
        
        total_general_bs = total_usd * tasa_bcv_calculo
        total_general_usd = total_usd
        fecha_hoy = datetime.now()
        user = self.request.user 
        verCostos = self.request.user.groups.filter(Q(name='VerCostos')).exists()

        return {
            'cirugia': atencion,
            'user': user,
            'tasa_bcv_calculo': tasa_bcv_calculo,
            'total_items': total_items,
            'total_general_bs': total_general_bs,
            'total_general_usd': total_general_usd,
            'total_general_costo':total_general_costo,
            'consumos': consumos,
            'fecha_hoy': fecha_hoy,
            'verCostos': verCostos
        }

    def get(self, request, **kwargs):
        # Aquí puedes manejar la lógica de la vista si es necesario
        atencion_id = self.kwargs['atencion_id']
        context = self.get_context_data(atencion_id)
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        atencion_id = self.kwargs['atencion_id']
        context = self.get_context_data(atencion_id)

        html_string = render_to_string(self.template_name, context)
        html_string = html_string.replace('/static/', request.build_absolute_uri('/static/'))

        html = HTML(string=html_string)
        pdf = html.write_pdf()  # Genera el PDF en memoria
        nombre_archivo = f"consumo_historia_{atencion_id}.pdf"
        # Crea la respuesta HTTP con el PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename='+nombre_archivo
        return response

@add_group_name_to_context    
class ListadoSeguroAtencionCortesia(View): 
    template_name = 'listado_seguro_paciente.html'
    
    def get_context_data(self, atencion_id):
        atencion = AtencionInmediataCortesia.objects.filter(id=atencion_id).first()
        total_items = ConsumoCirugia.objects.filter(atencion_cortesia_id = atencion_id).count()
        tasa_bcv_calculo = CambioDiaBcv(datetime.now())
        total_usd = 0
        total_general_costo = 0
        consumos = ConsumoCirugia.objects.filter(atencion_cortesia_id=atencion_id).order_by('inventario__nombre')
        for consumo in consumos:
            monto_venta = consumo.precio_costo_unitario  # Asegúrate de que 'inventario' es el campo de relación
            subtotal = consumo.precio_costo_unitario * consumo.cantidad_real_usada
            consumo.precio_unitario = 0
            subcosto = consumo.precio_costo_unitario
            total_usd = Decimal(total_usd) + Decimal(subtotal)
            consumo.subtotal = 0  # Puedes agregarlo como un atributo temporal
            consumo.subtotal_bs = Decimal(subtotal) * Decimal(tasa_bcv_calculo) # Puedes agregarlo como un atributo temporal
            consumo.costo = subcosto
            consumo.subtcosto = Decimal(subcosto)*Decimal(consumo.cantidad_real_usada)
            total_general_costo += Decimal(subcosto)*Decimal(consumo.cantidad_real_usada)
        
        
        total_general_bs = total_usd * tasa_bcv_calculo
        total_general_usd = total_usd
        fecha_hoy = datetime.now()
        user = self.request.user 
        verCostos = self.request.user.groups.filter(Q(name='VerCostos')).exists()

        return {
            'cirugia': atencion,
            'user': user,
            'tasa_bcv_calculo': tasa_bcv_calculo,
            'total_items': total_items,
            'total_general_bs': total_general_bs,
            'total_general_usd': total_general_usd,
            'total_general_costo':total_general_costo,
            'consumos': consumos,
            'fecha_hoy': fecha_hoy,
            'verCostos': verCostos
        }

    def get(self, request, **kwargs):
        # Aquí puedes manejar la lógica de la vista si es necesario
        atencion_id = self.kwargs['atencion_id']
        context = self.get_context_data(atencion_id)
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        atencion_id = self.kwargs['atencion_id']
        context = self.get_context_data(atencion_id)

        html_string = render_to_string(self.template_name, context)
        html_string = html_string.replace('/static/', request.build_absolute_uri('/static/'))

        html = HTML(string=html_string)
        pdf = html.write_pdf()  # Genera el PDF en memoria
        nombre_archivo = f"consumo_historia_{atencion_id}.pdf"
        # Crea la respuesta HTTP con el PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename='+nombre_archivo
        return response
    
    
    
@add_group_name_to_context    
class pdfCorteCuentaAtencionInmediata(TemplateView):
    template_name='pdf_cortecuenta_atencion_inmediata.html'
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atencion_id = self.kwargs['pk']
        atencion_inmediata = AtencionInmediata.objects.filter(id=atencion_id).first()
        responsable = Responsable.objects.filter(id=atencion_inmediata.paciente.responsable_id).first()
        #detallepresupuesto = DetalleCirugia.objects.filter(cirugia_id=cirugia.id, precio__gt = 0 ).order_by('detalle__posicion')
        detallepresupuesto = DetallePresupuesto.objects.filter(presupuesto__atencion_inmediata_id = atencion_id).order_by('detalle__posicion')
            
        fecha_actual = datetime.now()
        valor_bolivar_dia=CambioDiaBcv(fecha_actual)
       
        context['detallepresupuesto'] = detallepresupuesto
        context['valor_bolivar_dia'] = valor_bolivar_dia
        context['fecha_actual'] = fecha_actual
        context['responsable'] = responsable
        context['atencion_inmediata'] = atencion_inmediata
        return context

@add_group_name_to_context    
class pdfCorteCuentaAtencionInmediataCortesia(TemplateView):
    template_name='pdf_cortecuenta_atencion_inmediata.html'
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atencion_id = self.kwargs['pk']
        atencion_inmediata = AtencionInmediataCortesia.objects.filter(id=atencion_id).first()
        responsable = Responsable.objects.filter(id=atencion_inmediata.paciente.responsable_id).first()
        #detallepresupuesto = DetalleCirugia.objects.filter(cirugia_id=cirugia.id, precio__gt = 0 ).order_by('detalle__posicion')
        detallepresupuesto = DetallePresupuesto.objects.filter(presupuesto__atencion_cortesia_id = atencion_id).order_by('detalle__posicion')
            
        fecha_actual = datetime.now()
        valor_bolivar_dia=CambioDiaBcv(fecha_actual)
       
        context['detallepresupuesto'] = detallepresupuesto
        context['valor_bolivar_dia'] = valor_bolivar_dia
        context['fecha_actual'] = fecha_actual
        context['responsable'] = responsable
        context['atencion_inmediata'] = atencion_inmediata
        return context





@add_group_name_to_context    
class ListadoCirugiaUci(TemplateView):
    template_name='listado_cirugia_uci.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugias = Cirugia.objects.filter(estatus_id__in = [10,7], uci = True  ).order_by('-id').annotate(
            tratamientos_no_cumplidos=Count('tratamiento', filter=Q(tratamiento__cumplido=False))
        )

        quirofanos = Quirofano.objects.all().order_by('NQx')
        disponible_deposito = []
        deposito_precarga = []

        deposito_precarga = Deposito.objects.filter(precarga=True).first()
        if deposito_precarga:
            disponible_deposito = DepositoUso.objects.filter(deposito_id = deposito_precarga.id, cantidad_deposito__gt = 0, inventario__producto_activo =True)

        context['cirugias']=cirugias
        context['quirofanos']=quirofanos
        context['deposito_precarga']=deposito_precarga
        context['disponible_deposito']=disponible_deposito

        return context
    
def is_in_group_admin(user):
    return user.groups.filter(Q(name='Administradores') | Q(name='Administracion')).exists()

def is_in_group_admision(user):
    return user.groups.filter(Q(name='Administradores') | Q(name='Administracion') | Q(name='Admision')).exists()

def handle_error(request):
    return JsonResponse({'mensaje': 'UnautorizedUser'})

@login_required
@user_passes_test(is_in_group_admin, login_url='handle_error')
def change_uci(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idCirugia = datos['idCirugia']
        Cirugia.objects.filter(id=idCirugia).update(
            estatus_id = 10,
            usuario_id = request.user.id,
            uci = True
        )
        cirugia = Cirugia.objects.filter(id=idCirugia).first()
        baremos = Baremo.objects.filter(convenio_id = 1, grupo_id = 13, inactivar = False)
        for baremo in baremos:
            detalle_consumo_uci = DetalleCirugia.objects.filter(cirugia_id = idCirugia, detalle_id = baremo.detalle_id, lugar_consumo_id = 7).first()
            if not detalle_consumo_uci:
                DetalleCirugia.objects.create(cantidad = baremo.cantidad, precio = baremo.venta,convenio_id = baremo.convenio_id,detalle_id = baremo.detalle_id,grupo_id = baremo.grupo_id,
                    plantilla_id = baremo.plantilla_id,unidad_id = baremo.unidad_id,usuario_id = request.user.id,facturable = True,montotope = baremo.topedia,lugar_consumo_id = 7,cirugia_id = idCirugia,
                    ntqx = baremo.ntqx)
                    
                    
            detalle_consumo_uci_presupuesto = DetallePresupuesto.objects.filter(presupuesto_id = cirugia.presupuesto_id, detalle_id = baremo.detalle_id, lugar_consumo_id = 7).first()
            if not detalle_consumo_uci_presupuesto:
                DetallePresupuesto.objects.create(cantidad = baremo.cantidad,precio = 0,cantidad_usada = baremo.cantidad,precio_usado = baremo.venta,convenio_id = baremo.convenio_id,detalle_id = baremo.detalle_id, grupo_id = baremo.grupo_id,plantilla_id = baremo.plantilla_id,unidad_id = baremo.unidad_id, usuario_id = request.user.id,montotope = baremo.topedia,
                    lugar_consumo_id = 7,presupuesto_id = cirugia.presupuesto_id, alertaexcedente = True, ntqx = baremo.ntqx)
                
            if baremo.ntqx:
                notaqx = NotaQuirurgica.objects.filter(cirugia_id = idCirugia, participante_id = baremo.detalle_id, lugar_consumo_id = 7 )
                if not notaqx:
                    NotaQuirurgica.objects.create(
                        nota='UCI',fecha_elaboracion = datetime.now().date(), cirugia_id = idCirugia, participante_id = baremo.detalle_id, quirofano_id = cirugia.quirofano_id, incluir=True, 
                        lugar_consumo_id = 7, usuario_id = request.user.id ) 
                        
        return JsonResponse({'mensaje': 'Cambio de estatus'})
    else:
        return JsonResponse({'mensaje': 'Error POST'})
    
@add_group_name_to_context    
class Atencion_Uci(UserPassesTestMixin,TemplateView):
    template_name='atencion_uci.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Enfermeria') | Q(name='Farmacia')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs.get('cirugia_id')
        habitaciones = Habitacion.objects.all().order_by('habitacion')
        personal_medico = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        depositos = Deposito.objects.filter(id__in = [1,2,3,5]).order_by('nombre')
        baremo = Baremo.objects.filter(plantilla_id=2, inactivar = False).order_by('detalle__posicion')
        cirugia = Cirugia.objects.filter(id = cirugia_id).first()
        try:
            habitacion_actual = CirugiaHabitacion.objects.filter(cirugia_id=cirugia_id).latest('fecha_asignacion')
        except ObjectDoesNotExist:
            habitacion_actual = None  # O maneja el caso donde no hay coincidencias
        
        medicostratante = DetallePresupuesto.objects.filter(presupuesto_id = cirugia.presupuesto_id, grupo_id = 7, medico__participaalta = True)
        
        consumohospital = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, consumo_id = 7)
        monto_subtotal_farmacia = consumohospital.aggregate(subtotal_farmacia=Sum(F('precio_unitario') * F('cantidad_real_usada')))['subtotal_farmacia']
        
        presupuestoatencioninmediata = DetallePresupuesto.objects.filter(presupuesto_id = cirugia.presupuesto_id, lugar_consumo_id = 7 ).exclude(
                                                                                                                            Q(detalle_id=18) | Q(detalle_id=19) | Q(detalle_id=85) )
        monto_subtotal_baremo = presupuestoatencioninmediata.aggregate(total=Sum(F('precio_usado') * F('cantidad_usada')))['total']
        tratamientos = Tratamiento.objects.filter(cirugia_id = cirugia_id, lugar_consumo=7)
        if not consumohospital:
            monto_subtotal_farmacia = 0
            
        if not presupuestoatencioninmediata:
            monto_subtotal_baremo =0
            
        total_subtotal = monto_subtotal_farmacia + monto_subtotal_baremo
        
        context['personal_medico'] = personal_medico
        context['medicostratante'] = medicostratante
        context['depositos'] = depositos
        context['baremo'] = baremo
        context['habitaciones'] = habitaciones
        context['habitacion_actual'] = habitacion_actual
        context['cirugia'] = cirugia
        context['tratamientos'] = tratamientos
        context['consumohospital'] = consumohospital
        context['total_subtotal'] = total_subtotal
        context['monto_subtotal_farmacia'] = monto_subtotal_farmacia
        context['monto_subtotal_baremo'] = monto_subtotal_baremo
        context['presupuestoatencioninmediata'] = presupuestoatencioninmediata
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        cirugia_id = self.kwargs.get('cirugia_id')
        habitacion_atencion =  self.request.POST.get('habitacion_atencion')
        consumouci = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, consumo_id = 7, conciliada = False)
        cirugia_actualizar = Cirugia.objects.filter(id=cirugia_id).first()
        Cirugia.objects.filter(id=cirugia_id).update(
            usuario_id = self.request.user.id
        )
        for consumo in consumouci:
            ConsumoCirugia.objects.filter(id = consumo.id).update(
                conciliada = True
            )
        
        habitacion = CirugiaHabitacion.objects.filter(cirugia_id = cirugia_id, habitacion_id = habitacion_atencion ).first()
        if not habitacion:
            CirugiaHabitacion.objects.create(
                cirugia_id = cirugia_id,
                habitacion_id = habitacion_atencion,
                fecha_asignacion = datetime.now(),
                status = 'O'
            )
        Tratamiento.objects.filter(cirugia_id=cirugia_id,lugar_consumo_id = 7).update(
            cumplido =True,
            medico_aplicante_id = self.request.user.id,
        )
        
        ##crear el item si no existe en detalle de la cirugia
        
        if 'cambiar_hospitalizacion' in request.POST:
            fecha_salida = request.POST.get('fecha-egreso-datetime')
            condiciones_egreso = request.POST.get('condicion-egreso')
            diagnostico_egreso = request.POST.get('diag-egreso')
            diagnostico_ingreso = request.POST.get('diag-ingreso')
            tratamiento_recibido = request.POST.get('tratamiento-recibido')
            medico_ppal_atencion = request.POST.get('medico_ppal_atencion')
            
            TrasladoUci.objects.create(
                fecha_salida = fecha_salida,
                condiciones_egreso = condiciones_egreso,
                diagnostico_egreso = diagnostico_egreso,
                medico_egreso_id=medico_ppal_atencion,
                diagnostico_ingreso=diagnostico_ingreso,
                tratamiento_recibido=tratamiento_recibido,
                cirugia_id = cirugia_id
                )
            
            Cirugia.objects.filter(id=cirugia_id).update(
                estatus_id = 6
            )
            
            Presupuesto.objects.filter(id=cirugia_actualizar.presupuesto_id).update(
                estatus_id = 6
            )
            
            

        return redirect('listado_cirugia_uci')
    
    
def agregar_a_consumo_cirugia_uci(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        inventario_id = datos['inventario_id']
        cantidad_aplicar = datos['cantidad_aplicar']
        idCirugia = datos['idCirugia']
        depositoId = datos['depositoId']
        depositoubicacion = DepositoUso.objects.filter(inventario_id = inventario_id, deposito_id = depositoId).first()
        if depositoubicacion:
            if  Decimal(cantidad_aplicar) <= Decimal(depositoubicacion.existenciaUnd):
                producto = Inventario.objects.filter(id=inventario_id).first()
                precio_costo_unitario = precio_costo_producto_inventario(inventario_id)
                consumonuevo = ConsumoCirugia.objects.create(
                    cirugia_id = idCirugia,
                    cantidad_real_usada = cantidad_aplicar,
                    cantidad_uso = cantidad_aplicar,
                    venta = Decimal(cantidad_aplicar) * Decimal(producto.monto_venta),
                    inventario_id = inventario_id,
                    consumo_id = 7,
                    usuario_id = request.user.id,
                    hora_uso = datetime.now().time(),
                    hora = datetime.now().time(),
                    precio_unitario = producto.monto_venta,
                    deposito_id = depositoId,
                    nota = 'UCI',
                    precio_costo_unitario = precio_costo_unitario
                )
                
                InventarioDescarga.objects.create(
                    cantidad = cantidad_aplicar,
                    nota = 'UCI',
                    deposito_id = depositoId,
                    inventario_id = inventario_id,
                    usuario_id = request.user.id,
                    tipodescarga_id = 11,
                    cirugia_id = idCirugia,
                    persona_id = request.user.id,
                    consumocirugia_id = consumonuevo.id
                )
                
                return JsonResponse({'mensaje': 'Creado Consumo'})
            else:
                return JsonResponse({'mensaje': 'No dispone de cantidad en existencia'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8048 View.py'})
    
    
def refresh_table_consumo_cirugia_uci(request):
    idCirugia = request.GET.get('idCirugia')
    consumohospital = ConsumoCirugia.objects.filter(cirugia_id = idCirugia, consumo_id = 7).order_by('-id')
    total_subtotal_farmacia = consumohospital.annotate(
        sub_total=F('cantidad_real_usada') * F('precio_unitario')
    ).aggregate(total=Sum('sub_total'))['total']
    
    html = render_to_string('tabla_consumo_farmacia_atencion.html', {
        'consumohospital': consumohospital,
        'total_subtotal_farmacia': total_subtotal_farmacia,
    })
    
    return JsonResponse({'html': html, 'total_subtotal_farmacia': total_subtotal_farmacia}) 
    



def agregar_presupuesto_uci(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idBaremo = datos['idBaremo']
        idCirugia = datos['idCirugia']
        idMedico = datos['idMedico']
        idPaciente = datos['idPaciente']
        baremo = Baremo.objects.filter(id=idBaremo).first()
        if baremo:
            #existe_presupuesto = Presupuesto.objects.filter(atencion_inmediata_id=idCirugia).first()
            cirugia_update = Cirugia.objects.filter(id=idCirugia).first()
            if cirugia_update:
                presupuesto_id = cirugia_update.presupuesto_id
                
                detallepresupuesto = DetallePresupuesto.objects.create(
                    cantidad = baremo.cantidad,
                    cantidad_usada = baremo.cantidad,
                    precio_usado = baremo.venta,
                    notas = 'Agregado en UCI',
                    convenio_id = 1,
                    detalle_id = baremo.detalle_id,
                    grupo_id = baremo.grupo_id,
                    plantilla_id = baremo.plantilla_id,
                    usuario_id = request.user.id,
                    unidad_id = baremo.unidad_id,
                    presupuesto_id = presupuesto_id,
                    lugar_consumo_id = 7,
                    ntqx = baremo.ntqx,
                    )
                DetalleCirugia.objects.create(
                    cantidad = baremo.cantidad,
                    precio = baremo.venta,
                    notas = 'Agregado en UCI',
                    fecha_cambio = datetime.now().date(),
                    convenio_id = 1,
                    detalle_id = baremo.detalle_id,
                    grupo_id = baremo.grupo_id,
                    plantilla_id = baremo.plantilla_id,
                    usuario_id = request.user.id,
                    unidad_id = baremo.unidad_id,
                    facturable = True,
                    manual = 1,
                    cirugia_id = idCirugia,
                    lugar_consumo_id = 7,
                    ntqx = baremo.ntqx,
                )
                if baremo.ntqx and baremo.grupo_id == 7:
                    notaqx = NotaQuirurgica.objects.create(
                        nota = 'Agregado en UCI',
                        fecha_elaboracion = datetime.now().date(),
                        cirugia_id = idCirugia,
                        participante_id = baremo.detalle_id,
                        incluir = True,
                        montopendiente = baremo.cantidad * baremo.venta,
                        lugar_consumo_id = 7,
                        detallepresupuesto_id = detallepresupuesto.id
                    )
                
            
                
        return JsonResponse({'mensaje': 'Agregado Baremo Presupuesto Medico'})
    else:
        return JsonResponse({'mensaje': 'Error agrega baremo xxxx View.py'})
    
    
def refresh_table_baremo_uci(request):
    cirugia_id = request.GET.get('idCirugia')
    cirugia = Cirugia.objects.filter(id=cirugia_id).first()
    presupuestoatencioninmediata = DetallePresupuesto.objects.filter(presupuesto_id = cirugia.presupuesto_id, lugar_consumo_id = 7).exclude(
         Q(detalle_id=18) | Q(detalle_id=19) | Q(detalle_id=85) )
    
    total_subtotal = presupuestoatencioninmediata.annotate(
        sub_total=F('cantidad_usada') * F('precio_usado')
    ).aggregate(total=Sum('sub_total'))['total']
    
    html = render_to_string('tabla_baremo_uci.html', {
        'presupuestoatencioninmediata': presupuestoatencioninmediata,
        'total_subtotal': total_subtotal,
    })
    
    # Devolver un JSON con el HTML y el total
    return JsonResponse({'html': html, 'total_subtotal': total_subtotal}) 

def cambiar_precio_baremo_uci(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idDetallepresupuesto = datos['idDetallepresupuesto']
        ncantidad = datos['ncantidad']
        vCampo = datos['vCampo']
        cirugia_id = datos['cirugia_id']
        cirugia=Cirugia.objects.filter(id=cirugia_id).first()
        detalle =  DetallePresupuesto.objects.filter(id=idDetallepresupuesto).first()
            
        if vCampo == 'C':
            DetallePresupuesto.objects.filter(id=idDetallepresupuesto).update(
                cantidad = Decimal(ncantidad),
                cantidad_usada = Decimal(ncantidad),
                usuario_id = request.user.id
            )
            DetalleCirugia.objects.filter(cirugia_id = cirugia_id, detalle_id = detalle.detalle_id, lugar_consumo_id = 7).update(
                cantidad = Decimal(ncantidad),
                usuario_id = request.user.id
            )
            if detalle.ntqx:
                NotaQuirurgica.objects.filter(cirugia_id = cirugia_id, lugar_consumo_id = 7, participante_id = detalle.detalle_id).update(
                    montopendiente = Decimal(ncantidad) * detalle.precio_usado,
                )
            
        else:
            if detalle.cantidad_usada == 0:
                newcantidad = 1
            else:
                newcantidad = detalle.cantidad
                
            DetallePresupuesto.objects.filter(id=idDetallepresupuesto).update(
                precio_usado = Decimal(ncantidad),
                cantidad = newcantidad,
                cantidad_usada = newcantidad,
                usuario_id = request.user.id
            )
            DetalleCirugia.objects.filter(cirugia_id = cirugia_id, detalle_id = detalle.detalle_id, lugar_consumo_id = 7).update(
                precio = Decimal(ncantidad),
                usuario_id = request.user.id,
                cantidad = newcantidad
            )
            if detalle.ntqx:
                NotaQuirurgica.objects.filter(cirugia_id = cirugia_id, lugar_consumo_id = 7, participante_id = detalle.detalle_id).update(
                    montopendiente = newcantidad * Decimal(ncantidad),
                )
            
        
        return JsonResponse({'mensaje': 'Precio Cambiado Baremo'})
    else:
        return JsonResponse({'mensaje': 'Error  8282 View.py'})
    
def actualizar_medico_detalle_presupuesto_uci(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        medico_id = datos['medico_id']
        id_detalle = datos['id_detalle']
        idCirugia = datos['idCirugia']
        cirugia = Cirugia.objects.filter(id = idCirugia).first()
        presupuesto = DetallePresupuesto.objects.filter(id = id_detalle).first()
        DetallePresupuesto.objects.filter(id=id_detalle).update(
            medico_id = medico_id,
            usuario_id = request.user.id,
            
        )
        DetalleCirugia.objects.filter(cirugia_id = idCirugia, detalle_id = presupuesto.detalle_id, lugar_consumo_id = 7, ).update(
            medico_id = medico_id,
            usuario_id = request.user.id,
                
        )
        if presupuesto.ntqx:
            NotaQuirurgica.objects.filter(cirugia_id = idCirugia, lugar_consumo_id = 7, participante_id = presupuesto.detalle_id).update(
                    medico_id = medico_id,
                    incluir = True,
                )
        
            
        return JsonResponse({'mensaje': 'actualizar medico'})
    else:
        return JsonResponse({'mensaje': 'Error  8229 View.py'})
    
def agregar_tratamiento_uci(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        comentarios_tratamiento = datos['comentarios_tratamiento']
        idCirugia = datos['idCirugia']
        cantidad = datos['cantidad']

        Tratamiento.objects.create(
           cirugia_id =  idCirugia,
           tratamiento = comentarios_tratamiento,
           cantidad_uso = cantidad,
           lugar_consumo_id = 7,
           medico_aplicante_id = request.user.id,
           medico_orden_id = request.user.id,
           
        )        
        
        return JsonResponse({'mensaje': 'Agregado tratamiento Medico'})
    else:
        return JsonResponse({'mensaje': 'Error agregartratamiento 8091 View.py'})
    
def refresh_table_tratamiento_uci(request):
    idCirugia = request.GET.get('idCirugia')
    tratamientos = Tratamiento.objects.filter(cirugia_id = idCirugia, lugar_consumo_id = 7)
    return render(request, 'tabla_tratamiento_atencion.html', {'tratamientos': tratamientos})  

def actualizar_piva_notaentrega(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nuevo_piva = datos['nuevo_piva']
        id_detallenotaentrega = datos['id_detallenotaentrega']
        DetalleNotaEntrega.objects.filter(id=id_detallenotaentrega).update(
            piva = nuevo_piva,
            usuario_id = request.user.id
        )
        
        return JsonResponse({'mensaje': 'Bien'})
    
def actualizar_precio_unitario_notaentrega(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nuevo_precio_unitario = datos['nuevo_precio_unitario']
        id_detallenotaentrega = datos['id_detallenotaentrega']
        DetalleNotaEntrega.objects.filter(id=id_detallenotaentrega).update(
            costo_bs = Decimal(nuevo_precio_unitario),
            costo_dl = Decimal(nuevo_precio_unitario) / F('cambioaplicado'),
            usuario_id = request.user.id
        )
        return JsonResponse({'mensaje': 'Bien'})

def actualizar_marca_a_factura(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        marcado = datos['marcado']
        producto_id = datos['producto_id']

        DetalleNotaEntrega.objects.filter(id=producto_id).update(
            factura = marcado,
            usuario_id = request.user.id
        )
        return JsonResponse({'mensaje': 'Bien'})

def actualizar_retencion_islr_ne(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        porcentaje = datos['porcentaje']
        id_notaentrega = datos['id_notaentrega']
        id_concepto = datos['id_concepto']
        porcentaje =  porcentaje.replace(',','.')

        NotaEntregaCompra.objects.filter(id=id_notaentrega).update(
            porcentaje_retencion_islr = Decimal(porcentaje),
            usuario_id = request.user.id,
            concepto = id_concepto
        )
        return JsonResponse({'mensaje': 'Bien'})
    

def agregar_a_consumo_cirugia_farmacia(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        inventario_id = datos['inventario_id']
        cantidad_aplicar = datos['cantidad_aplicar']
        idCirugia = datos['idCirugia']
        depositoId = datos['depositoId']
        depositoubicacion = DepositoUso.objects.filter(inventario_id = inventario_id, deposito_id = depositoId).first()
        if depositoubicacion:
            if  Decimal(cantidad_aplicar) <= Decimal(depositoubicacion.existenciaUnd):
                producto = Inventario.objects.filter(id=inventario_id).first()
                if producto.compuesto == '2':
                    compuesto = 2
                    cantidad_compuesto = cantidad_aplicar
                    lugar_consumo = 10                    
                else:
                    compuesto = 1
                    cantidad_compuesto = 0
                    lugar_consumo = 1
                    
                    
                total_venta = Decimal(cantidad_aplicar) * Decimal(producto.monto_venta)
                consumoexiste = ConsumoCirugia.objects.filter(cirugia_id = idCirugia, consumo_id = 1, inventario_id = inventario_id, compuesto = compuesto, conciliada=False).first()
                if consumoexiste:
                    ConsumoCirugia.objects.filter(cirugia_id = idCirugia, consumo_id = 1, inventario_id = inventario_id, compuesto = compuesto).update(
                        cantidad_uso = F('cantidad_uso') + cantidad_aplicar,
                        #cantidad_real_usada = F('cantidad_real_usada') + cantidad_aplicar,
                        usuario_id = request.user.id,
                        hora_uso = datetime.now().time(),
                    )
                    InventarioDescarga.objects.filter(consumocirugia_id = consumoexiste.id).update(
                        cantidad = F('cantidad') + cantidad_aplicar,
                        usuario_id = request.user.id,
                    )
                    consumocirugia_id = consumoexiste.id
                    
                else:
                    precio_costo_unitario = precio_costo_producto_inventario(inventario_id)
                    consumonuevo = ConsumoCirugia.objects.create(
                        cirugia_id = idCirugia,
                        cantidad_real_usada = cantidad_compuesto,
                        cantidad_uso = cantidad_aplicar,
                        venta = total_venta,
                        inventario_id = inventario_id,
                        farmacia = True,
                        consumo_id = lugar_consumo,
                        usuario_id = request.user.id,
                        hora_uso = datetime.now().time(),
                        precio_unitario = producto.monto_venta,
                        deposito_id = depositoId,
                        nota = 'ASIGNADO EN FARMACIA',
                        compuesto = compuesto,
                        precio_costo_unitario = precio_costo_unitario
                    )
                    
                    InventarioDescarga.objects.create(
                        cantidad = cantidad_aplicar,
                        nota = 'ASIGNADO EN FARMACIA',
                        deposito_id = depositoId,
                        inventario_id = inventario_id,
                        usuario_id = request.user.id,
                        tipodescarga_id = 6,
                        cirugia_id = idCirugia,
                        persona_id = request.user.id,
                        consumocirugia_id = consumonuevo.id
                    )
                    
                    if compuesto == 2:
                        InventarioCompuesto.objects.create(
                            consumo_id = consumonuevo.id,
                            usuario_id = request.user.id,
                        )
                        
                    consumocirugia_id = consumonuevo.id
                 
                        
                ######## detalle de consumo en cirugia
                DetalleConsumoCirugia.objects.create(
                        cantidad_uso = cantidad_aplicar,
                        precio_unitario = producto.monto_venta,
                        hora = datetime.now().time(),
                        consumocirugia_id = consumocirugia_id,
                        inventario_id = inventario_id,
                        usuario_cirugia_id = request.user.id,
                        usuario_farmacia_id = request.user.id,
                        nota = 'Asignacion Farmacia'
                        
                    )
                   
                
                return JsonResponse({'mensaje': 'Creado Consumo'})
            else:
                return JsonResponse({'mensaje': 'SINCANTIDAD'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8048 View.py'})
    
    
def dt_serverside_farmacia_altamedica(request):
    context = {}
    dt = request.GET 
    
    draw = int(dt.get("draw"))
    start = int(dt.get("start"))
    length = int(dt.get("length"))
    search = dt.get("search[value]")
    
    #registros = Inventario.objects.all().values_list('id','codigo' ,'nombre','presentacion__nombre','categoria__nombre','unidad_conversion','piva','costo', 'venta' ,'laboratorio__nombre','nombre_comercial','fecha_vencimiento').order_by("nombre")
    registros = DepositoUso.objects.filter(deposito_id__in = [1,2], inventario__producto_activo =True).values_list('id','inventario__codigo','inventario__categoria__nombre' ,'inventario__nombre' ,'inventario__nombre_comercial', 'inventario__presentacion__nombre','inventario__presentacion_salida__nombre', 'inventario__id','deposito__nombre','inventario__unidad_conversion','cantidad_consumida','deposito_id').order_by('inventario_id','deposito_id')
    
    if search:
        registros = registros.filter(
            Q(inventario__codigo__icontains=search) |
            Q(inventario__nombre__icontains=search) |
            Q(inventario__nombre_comercial__icontains=search) |
            Q(inventario__id__icontains=search) 
        )
        
    recordsTotal = registros.count()
    recordsFiltered = recordsTotal
    
    context["draw"] = draw
    context["recordsTotal"] = recordsTotal
    context["recordsFiltered"] = recordsFiltered
    
    reg = registros[start:start + length]
    paginator = Paginator(reg, length)
    
    try:
        obj = paginator.page(draw).object_list
    except PageNotAnInteger:
        obj = paginator.page(draw).object_list
    except EmptyPage:
        obj = paginator.page(paginator.num_pages).object_list
        
 
    datos = [
        {
            "id" : d[0],
            "idInventario":d[7],
            "codigo":d[1],
            "inventario":d[3],
            "nombre_comercial":d[4],
            "presentacion":d[5],
            "presentacion_salida":d[6],
            "monto_venta": round(Inventario.objects.get(id=d[7]).monto_venta, 2) ,
            "existencia_und": round(DepositoUso.objects.filter(inventario_id=d[7], deposito_id  = d[11], inventario__producto_activo =True).first().existenciaUnd, 2) if DepositoUso.objects.filter(inventario_id=d[7], deposito_id = d[11]).exists() else 0,
            "deposito" : d[8],
            "unidad_conversion": round(Inventario.objects.get(id=d[7]).unidad_conversion, 2) ,
            "cantidad_consumida" : d[10],
            "id" : d[0],
            
           
        } for d in obj
        if (
            DepositoUso.objects.filter(inventario_id=d[7], deposito_id = d[11]).exists() and
            round(DepositoUso.objects.filter(inventario_id=d[7], deposito_id = d[11]).first().existenciaUnd, 2) > 0
        )
    ]

    context["datos"] = datos
    return JsonResponse(context,safe=False)


def refresh_table_disponible_altamedica(request):
    deposito_seleccion = DepositoUso.objects.filter(deposito_id__in = [1,2]).order_by('inventario_id','deposito_id')
    
    return render(request, 'tabla_farmacia_alta_medica.html', {'deposito_seleccion': deposito_seleccion})  


def agregar_a_consumo_alta_medica(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        inventario_id = datos['inventario_id']
        cantidad_aplicar = datos['cantidad_aplicar']
        idCirugia = datos['idCirugia']
        depositoId = datos['depositoId']
        tipo_procedimiento_id = datos['tipo_procedimiento_id']
        depositouso = DepositoUso.objects.filter(id = depositoId).first()
        if depositouso:
            consumo_id = depositouso.deposito_id
            producto = Inventario.objects.filter(id=inventario_id).first()
            precio_costo_unitario = precio_costo_producto_inventario(inventario_id)
            if int(tipo_procedimiento_id) == 5:
                consumonuevo = ConsumoCirugia.objects.create(
                    atencion_inmediata_id = idCirugia,
                    cantidad_real_usada = cantidad_aplicar,
                    cantidad_uso = cantidad_aplicar,
                    venta = cantidad_aplicar * producto.monto_venta,
                    inventario_id = inventario_id,
                    consumo_id = 6,
                    usuario_id = request.user.id,
                    hora_uso = datetime.now().time(),
                    precio_unitario = producto.monto_venta,
                    deposito_id = depositouso.deposito_id,
                    nota = 'Agregado en Alta Medica',
                    hora = datetime.now().time(),
                    conciliada = True,
                    advertencia = True,
                    precio_costo_unitario = precio_costo_unitario
                )
                InventarioDescarga.objects.create(
                    cantidad = cantidad_aplicar,
                    nota = 'Descargado en Alta Medica',
                    deposito_id = depositouso.deposito_id,
                    inventario_id = inventario_id,
                    usuario_id = request.user.id,
                    tipodescarga_id = 15,
                    atencion_inmediata_id = idCirugia,
                    persona_id = request.user.id,
                    consumocirugia_id = consumonuevo.id
                )
                
            else:
                consumonuevo = ConsumoCirugia.objects.create(
                    cirugia_id = idCirugia,
                    cantidad_real_usada = cantidad_aplicar,
                    cantidad_uso = cantidad_aplicar,
                    venta = cantidad_aplicar * producto.monto_venta,
                    inventario_id = inventario_id,
                    consumo_id = consumo_id,
                    usuario_id = request.user.id,
                    hora_uso = datetime.now().time(),
                    precio_unitario = producto.monto_venta,
                    deposito_id = depositouso.deposito_id,
                    nota = 'Agregado en Alta Medica',
                    hora = datetime.now().time(),
                    conciliada = True,
                    advertencia = True,
                    precio_costo_unitario = precio_costo_unitario
                )
            
                InventarioDescarga.objects.create(
                    cantidad = cantidad_aplicar,
                    nota = 'Descargado en Alta Medica',
                    deposito_id = depositouso.deposito_id,
                    inventario_id = inventario_id,
                    usuario_id = request.user.id,
                    tipodescarga_id = 15,
                    cirugia_id = idCirugia,
                    persona_id = request.user.id,
                    consumocirugia_id = consumonuevo.id
                )
        
        return JsonResponse({'mensaje': 'Creado Consumo'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8048 View.py'})
    
    
def eliminar_consumo_altamedica(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        consumo_id = datos['consumo_id']
        consumoeliminar = ConsumoCirugia.objects.filter(id=consumo_id).first()
        if consumoeliminar:
            LogInventario.objects.create(
                inventario_id = consumoeliminar.inventario_id,
                cantidad = consumoeliminar.cantidad_real_usada,
                usuario_id = request.user.id,
                cirugia_id = consumoeliminar.cirugia_id,
                nota = 'Eliminado en Alta Medica producto :'+str(consumoeliminar.inventario)+str(consumoeliminar.inventario.codigo)+' de la cirugia: '+str(consumoeliminar.cirugia_id)+' / '+ str(consumoeliminar.cirugia)
            )
            
        
        ConsumoCirugia.objects.filter(id=consumo_id).delete()
        
        
        return JsonResponse({'mensaje': 'Eliminado Consumo'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8065 View.py'})
    
    
def cambio_cantidad_consumo(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        consumo_id = datos['idconsumocirugia']
        new_cantidad = datos['new_cantidad']
        existeconsumo = ConsumoCirugia.objects.filter(id=consumo_id).first()
        if existeconsumo:
            deposito_usado = existeconsumo.deposito_id
            cantidad_anterior = existeconsumo.cantidad_real_usada
            disponibilidad_deposito = DepositoUso.objects.filter(inventario_id = existeconsumo.inventario_id, deposito_id = deposito_usado).first()
            
            if not disponibilidad_deposito:
                disponible = 0
            else:
                disponible = disponibilidad_deposito.existenciaUnd
                
            new_cantidad = float(new_cantidad)
            cantidad_anterior = float(cantidad_anterior)
            cantidad_diferencial = new_cantidad - cantidad_anterior
            if cantidad_diferencial > 0:
                if disponible < cantidad_diferencial:
                    return JsonResponse({'mensaje': 'DISPONIBILIDAD'})
                    
                
            ConsumoCirugia.objects.filter(id = consumo_id).update(
                    cantidad_real_usada = new_cantidad,
                    cantidad_uso =  new_cantidad,
                    venta = (new_cantidad) * F('precio_unitario') ,
                    usuario_id = request.user.id,
                    nota = 'Cantidad Modificada en consumo por: '+str(request.user.username)
                )
            
            InventarioDescarga.objects.filter(consumocirugia_id = existeconsumo.id).update(
                cantidad = new_cantidad,
                usuario_id = request.user.id,
                nota = 'Cantidad Modificada en consumo por: '+str(request.user.username)
                )
            
                
            LogInventario.objects.create(
                inventario_id = existeconsumo.inventario_id,
                cantidad = new_cantidad,
                usuario_id = request.user.id,
                cirugia_id = existeconsumo.cirugia_id,
                nota = 'Cantidad modificada :'+str(existeconsumo.inventario)+str(existeconsumo.inventario.codigo)+' de la cirugia: '+str(existeconsumo.cirugia_id)+' / '+ str(existeconsumo.cirugia)+' / Cantidad anterior:'+str(cantidad_anterior)
            )
            
            
        return JsonResponse({'mensaje': 'Consumo Modificado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8065 View.py'})
    
    
def cambio_precio_unico_consumo(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        consumo_id = datos['idconsumocirugia']
        nuevo_precio = datos['nuevo_precio']
        
        ConsumoCirugia.objects.filter(id = consumo_id).update(
                precio_unitario = nuevo_precio,
                venta = F('cantidad_real_usada') * nuevo_precio ,
                usuario_id = request.user.id,
                nota = 'Precio Modificado en consumo por: '+str(request.user.username),
            )
            
        LogEliminacion.objects.create(
            usuario_id = request.user.id,
            descripcion = ' Modificacion de precio unitario , nuevo precio:'+str(nuevo_precio)
        )
            
            
        return JsonResponse({'mensaje': 'Consumo Modificado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8065 View.py'})
    
    
def actualizar_cuentas_pagomedico(request):
    medico_id = request.GET.get('medico_id')
    pagomedico = PagoMedico.objects.filter(medico_id = medico_id)  # Obtén los datos que necesites
    html = render_to_string('select_dinamico_pagomedico.html', {'pagomedico': pagomedico})
    
    return JsonResponse({'html': html})

def agregar_medio_pago_medico(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        aliasdepago = datos['aliasdepago']
        id_formadepago = datos['id_formadepago']
        cuentabancaria = datos['cuentabancaria']
        id_bancodestino = datos['id_bancodestino']
        id_moneda = datos['id_moneda']
        id_correodestinopago = datos['id_correodestinopago']
        cedula_pagomovil = datos['cedula_pagomovil']
        telefono_pagomovil = datos['telefono_pagomovil']
        medico_id_pago = datos['medico_id_pago']

        pagoexiste = PagoMedico.objects.filter(
            numerocuenta = cuentabancaria, 
            formapago_id = id_formadepago, 
            medico_id = medico_id_pago,
            moneda_id = id_moneda
            )

        if pagoexiste:
            return JsonResponse({'mensaje': 'YAEXISTE'})
        else:
            PagoMedico.objects.create(
                nombre = aliasdepago,
                numerocuenta = cuentabancaria,
                numeropago = telefono_pagomovil,
                correo = id_correodestinopago,
                formapago_id = id_formadepago,
                medico_id = medico_id_pago,
                cedulapago = cedula_pagomovil,
                bancopago_id = id_bancodestino,
                moneda_id = id_moneda,
                usuario_id = request.user.id
            )
            return JsonResponse({'mensaje': 'actualizar medico'})
    else:
        return JsonResponse({'mensaje': 'Error  8229 View.py'})
    
    
@add_group_name_to_context    
class pre_factura_update(UserPassesTestMixin, TemplateView):
    template_name='pre_factura_update.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='SuperAdministracion')  
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['cirugia_id']
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        
        numero_factura = NumeracionFactura.objects.filter(cirugia__isnull = True).order_by('-numero_factura').first()
        id_factura_nueva = numero_factura.id
        new_invoice_number = numero_factura.numero_factura
        control_number = numero_factura.numero_control

        if cirugia.congelar_moneda:
            cambio_calculo = cirugia.cambio_congelado
        else:
            cambio_calculo = CambioDiaBcv(datetime.now())


        totalabono = 0
        saldoactual=0
        totalabono_bs = 0
        saldoactual_bs =0
        cuentacobrar = CuentaxCobrar.objects.filter(cirugia_id=cirugia_id).first()
        if cuentacobrar:
            abonos = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id, montocobrar__lt = 0).aggregate(total_montocobrar=Sum('montocobrar'))
            totalabono = abonos['total_montocobrar'] or 0

            abonos_bs = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id, montocobrar_bs__lt = 0).aggregate(total_montocobrar=Sum('montocobrar_bs'))
            totalabono_bs = abonos_bs['total_montocobrar'] or 0

            saldo = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id).aggregate(total_montocobrar=Sum('montocobrar'))
            saldoactual = saldo['total_montocobrar'] or 0
            
        usuario_logueado = self.request.user.id
        objectos_detalle = []
        DetallePrefactura.objects.filter(factura_id = id_factura_nueva).delete()
        detallecirugia =  DetallePresupuesto.objects.filter(presupuesto_id=cirugia.presupuesto_id).order_by('detalle__posicion')
        for detalle in detallecirugia:
            if detalle.grupo_id == 7:
                grupo_factura = detalle.grupo_id
            else:
                grupo_factura = 8
                    
            medico_participante = None
            medico = NotaQuirurgica.objects.filter(cirugia_id = cirugia_id, participante_id = detalle.detalle_id ).first()
            if medico:
                medico_participante = medico.medico_id

            montodescuento = (detalle.precio_usado * (detalle.detalle.pagarmedico/100))
            precio_nuevo =  (detalle.precio_usado - montodescuento)
           

            objectos_detalle.append(DetallePrefactura(cantidad_usada = detalle.cantidad_usada ,precio_usado = precio_nuevo,
                                                detalle_id=detalle.detalle_id , tx =detalle.tx,
                                                convenio_id  = detalle.convenio_id ,
                                                grupo_id = detalle.grupo_id, plantilla_id =detalle.plantilla_id ,unidad_id  = 1,
                                                usuario_id = self.request.user.id, 
                                                precio_congelado_cirugia = (precio_nuevo * cambio_calculo),
                                                medico_id = medico_participante,
                                                detallepresupuesto_id = detalle.id,
                                                grupo_factura = grupo_factura,
                                                factura_id = id_factura_nueva
                                                ))

                
        
        DetallePrefactura.objects.bulk_create(objectos_detalle)
        detallecirugia =  DetallePrefactura.objects.filter(factura_id = id_factura_nueva).order_by('detalle__posicion')

        detalle_agrupado = defaultdict(lambda: {'items': [], 'subtotal': 0, 'subtotalbs': 0})
        subtotal_usd = 0
        subtotal_bs = 0
        for detalle in detallecirugia:
            detalle_agrupado[detalle.grupo_factura]['items'].append(detalle)
            detalle_agrupado[detalle.grupo_factura]['subtotal'] += detalle.precio_usado   # Sumar el subtotal
            detalle_agrupado[detalle.grupo_factura]['subtotalbs'] += detalle.precio_congelado_cirugia   # Sumar el subtotal
            subtotal_usd += detalle.precio_usado
            subtotal_bs += detalle.precio_congelado_cirugia

        # Obtener los nombres de los grupos
        grupo_ids = detalle_agrupado.keys()
        grupos = {grupo.id: grupo.nombre for grupo in GrupoBaremo.objects.filter(id__in=grupo_ids)}
        saldoactual_bs = (saldoactual * cambio_calculo)
        # Convertir el defaultdict a una lista para pasar a la plantilla
        detalle_agrupado_lista = [{'grupo_id': key, 'grupo_nombre': grupos[key], 'items': value['items'], 'subtotal': value['subtotal'], 'subtotalbs': value['subtotalbs']} for key, value in detalle_agrupado.items()]
            # Contexto para la plantilla
        context = {
                'cirugia': cirugia,
                'tasa_calculo': cambio_calculo,
                'fecha_hoy': datetime.now(),
                'subtotal_usd' : subtotal_usd,
                'subtotal_bs':subtotal_bs,
                'totalabono' : totalabono,
                'totalabono_bs':totalabono_bs,
                'saldoactual' : saldoactual,
                'saldoactual_bs':saldoactual_bs,
                'detalle_agrupado': detalle_agrupado_lista,
                'new_invoice_number' : new_invoice_number,
                'control_number' : control_number,
                'prefactura_id' : id_factura_nueva
            }
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        cirugia_id = self.kwargs.get('cirugia_id')
        fecha_factura =  self.request.POST.get('fecha_factura_final')
        numero_factura = NumeracionFactura.objects.filter(cirugia__isnull = True).order_by('-numero_factura').first()
        id_factura_nueva = numero_factura.id
        nuevafactura = NumeracionFactura.objects.filter(id = id_factura_nueva ).update(
            cirugia_id = cirugia_id,
            usuario_id = self.request.user.id,
            fecha_factura = fecha_factura
        )
        prefactura_id =  id_factura_nueva
        nuevo_numero_factura_disponible = numero_factura.numero_factura + 1
        nuevo_numero_control_disponible = numero_factura.numero_control + 1
        NumeracionFactura.objects.create(
            numero_factura = nuevo_numero_factura_disponible,
            numero_control = nuevo_numero_control_disponible,
            usuario_id = self.request.user.id
        )
       
       
        return redirect('factura_resumen', prefactura_id = prefactura_id)
    
    
def cambiar_precios_factor(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        checkboxes = data.get('checkboxes', [])
        idpresupuesto = data.get('idpresupuesto')
        factor_aumento = data.get('factor_aumento')
        # Guardar cada detalle en la base de datos
        for detalle_id in checkboxes:
            numeros = re.findall(r'\d+', detalle_id)
            detallepresupuesto = DetallePresupuesto.objects.filter(presupuesto_id = idpresupuesto, grupo_id = int(numeros[0]))
            for detalle in detallepresupuesto:
                monto_original = detalle.precio_usado
                nuevo_precio = (float(detalle.precio_usado) * factor_aumento)+float(detalle.precio_usado)
                DetallePresupuesto.objects.filter(id=detalle.id).update(
                    precio_usado = nuevo_precio,
                    usuario_id = request.user.id,
                    factor = factor_aumento
                )
                LogDetallePresupuesto.objects.create(
                    detalle = detalle.detalle.nombre,
                    usuario_id =  request.user.id,
                    presupuesto_id = detalle.presupuesto_id,
                    nota = 'Modificado en Modificar Prefactura',
                    factor = factor_aumento ,
                    monto_original = monto_original
                )
           
                       
        return JsonResponse({'success': True, 'mensaje': 'detalles guardados.'})
    else:
        return JsonResponse({'error': True, 'mensaje': 'error detalles guardados.'})

def cambiar_precios_factor_undo(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        idpresupuesto = data.get('idpresupuesto')
        
        DetallePresupuesto.objects.filter(presupuesto_id = idpresupuesto).update(
            precio_usado = F('precio_usado') / (F('factor')+1),
            factor = 0,
            usuario_id =  request.user.id,
        )
        
        LogDetallePresupuesto.objects.create(
                    detalle = 'Reverso del monto',
                    usuario_id =  request.user.id,
                    presupuesto_id = idpresupuesto,
                    nota = 'Reverso del factor en Modificar Prefactura',
                    factor = 0 ,
                    monto_original = 0
                )
        
    
    return JsonResponse({'success': True, 'mensaje': 'detalles guardados.'})

def cambiar_tx_cambio_cirugia(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cirugia_id = data.get('cirugia_id')
        cambio_nuevo = data.get('cambio_nuevo')
        if cambio_nuevo > 0:
            Cirugia.objects.filter(id=cirugia_id).update(
                congelar_moneda = True,
                cambio_congelado = cambio_nuevo,
                usuario_id = request.user.id
            )
            LogEliminacion.objects.create(
            descripcion = 'Cambio de tasa de cobro de cirugia '+str(cirugia_id)+' por nueva tasa de :'+str(cambio_nuevo),
            usuario_id = request.user.id
        )

        
        
    
    return JsonResponse({'success': True, 'mensaje': 'cambio hechos.'})


@add_group_name_to_context    
class factura_resumen(TemplateView):
    template_name='factura_resumen.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prefactura_id = self.kwargs['prefactura_id']
        numero_factura = NumeracionFactura.objects.filter(id=prefactura_id).first()
        if numero_factura:
           cirugia_id =  numero_factura.cirugia_id

        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        
        if cirugia.paciente.responsable and cirugia.paciente.responsable.cedula != '':
            nombre_factura = cirugia.paciente.responsable.nombre + ' ' +cirugia.paciente.responsable.apellido
            cedula_factura = cirugia.paciente.responsable.cedula
            telefono_factura = cirugia.paciente.responsable.telefono1
            direccion_factura = cirugia.paciente.responsable.direccion
        else:
            nombre_factura = cirugia.paciente.nombre +' '+ cirugia.paciente.apellido
            cedula_factura = cirugia.paciente.cedula
            telefono_factura = cirugia.paciente.telefono1
            direccion_factura = cirugia.paciente.direccion
            
        
        new_invoice_number = numero_factura.numero_factura
        factura_legal = str(new_invoice_number).zfill(7)
        if cirugia.congelar_moneda:
            cambio_calculo = cirugia.cambio_congelado
        else:
            cambio_calculo = CambioDiaBcv(datetime.now())
        
        detallecirugia =  DetallePrefactura.objects.filter(factura_id = prefactura_id).order_by('detalle__posicion')

        detalle_agrupado = defaultdict(lambda: {'items': [], 'subtotal': 0, 'subtotalbs': 0})
        subtotal_usd = 0
        subtotal_bs = 0
        total_general_bs = 0
        for detalle in detallecirugia:
            detalle_agrupado[detalle.grupo_factura]['items'].append(detalle)
            detalle_agrupado[detalle.grupo_factura]['subtotal'] += detalle.precio_usado   # Sumar el subtotal
            detalle_agrupado[detalle.grupo_factura]['subtotalbs'] += detalle.precio_congelado_cirugia   # Sumar el subtotal
            subtotal_usd += detalle.precio_usado
            subtotal_bs += detalle.precio_congelado_cirugia
            total_general_bs += detalle.precio_congelado_cirugia

        # Obtener los nombres de los grupos
        grupo_ids = detalle_agrupado.keys()
        grupos = {grupo.id: grupo.nombre for grupo in GrupoBaremo.objects.filter(id__in=grupo_ids)}
        # Convertir el defaultdict a una lista para pasar a la plantilla
        detalle_agrupado_lista = [{'grupo_id': key, 'grupo_nombre': grupos[key], 'items': value['items'], 'subtotal': value['subtotal'], 'subtotalbs': value['subtotalbs']} for key, value in detalle_agrupado.items()]
            # Contexto para la plantilla
        context = {
                'cirugia': cirugia,
                'tasa_calculo': cambio_calculo,
                'fecha_hoy': datetime.now(),
                'subtotal_usd' : subtotal_usd,
                'subtotal_bs':subtotal_bs,
                'total_general_bs':total_general_bs,
                'detalle_agrupado': detalle_agrupado_lista,
                'new_invoice_number' : factura_legal,
                'nombre_factura' : nombre_factura,
                'cedula_factura': cedula_factura,
                'telefono_factura' : telefono_factura,
                'direccion_factura' : direccion_factura
            }
        return context
    
    
def factura_pdf_xml2pdf(request, cirugia_id):
    # Aquí obtienes tu objeto presupuesto desde la base de datos
    #presupuesto = get_object_or_404(Presupuesto, id=presupuesto_id)
    cirugia = Cirugia.objects.filter(id=cirugia_id).first()

    if cirugia.congelar_moneda:
        cambio_calculo = cirugia.cambio_congelado
    else:
        cambio_calculo = CambioDiaBcv(datetime.now())

    totalabono = 0
    saldoactual=0
    totalabono_bs = 0
    saldoactual_bs =0
    cuentacobrar = CuentaxCobrar.objects.filter(cirugia_id=cirugia_id).first()
    if cuentacobrar:
        abonos = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id, montocobrar__lt = 0).aggregate(total_montocobrar=Sum('montocobrar'))
        totalabono = abonos['total_montocobrar'] or 0

        abonos_bs = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id, montocobrar_bs__lt = 0).aggregate(total_montocobrar=Sum('montocobrar_bs'))
        totalabono_bs = abonos_bs['total_montocobrar'] or 0

        saldo = DetalleCuentaCobrar.objects.filter(cuentacobrar_id=cuentacobrar.id).aggregate(total_montocobrar=Sum('montocobrar'))
        saldoactual = saldo['total_montocobrar'] or 0

    usuario_logueado = request.user.id
    objectos_detalle = []
    DetallePrefactura.objects.filter(presupuesto_id=cirugia.presupuesto_id).delete()
    detallecirugia =  DetallePresupuesto.objects.filter(presupuesto_id=cirugia.presupuesto_id, cantidad__gte = 0).order_by('detalle__posicion')
    for detalle in detallecirugia:
        medico_participante = None
        medico = NotaQuirurgica.objects.filter(cirugia_id = cirugia_id, participante_id = detalle.detalle_id ).first()
        if medico:
            medico_participante = medico.medico_id

        montodescuento = (detalle.precio_usado * (detalle.detalle.pagarmedico/100))
        precio_nuevo =  (detalle.precio_usado - montodescuento)
        if montodescuento > 0:
            objectos_detalle.append(DetallePrefactura(presupuesto_id=cirugia.presupuesto_id ,cantidad_usada = 1 ,precio_usado = precio_nuevo,
                                            detalle_id=79 , tx =detalle.tx,
                                            fecha_cambio  = detalle.fecha_cambio ,convenio_id  =detalle.convenio_id ,
                                            grupo_id =12, plantilla_id =detalle.plantilla_id ,unidad_id  = 1,
                                            usuario_id = usuario_logueado, cirugia_id = cirugia_id,
                                            precio_congelado_cirugia = (precio_nuevo * cambio_calculo)
                                            ))


        objectos_detalle.append(DetallePrefactura(presupuesto_id=cirugia.presupuesto_id ,cantidad_usada = detalle.cantidad_usada ,precio_usado = precio_nuevo,
                                            detalle_id=detalle.detalle_id , tx =detalle.tx,
                                            fecha_cambio  = detalle.fecha_cambio ,convenio_id  =detalle.convenio_id ,
                                            grupo_id =detalle.grupo_id, plantilla_id =detalle.plantilla_id ,unidad_id  = 1,
                                            usuario_id = usuario_logueado, cirugia_id = cirugia_id,
                                            precio_congelado_cirugia = (precio_nuevo * cambio_calculo),
                                            medico_id = medico_participante
                                            ))

            
    
    DetallePrefactura.objects.bulk_create(objectos_detalle)
    detallecirugia =  DetallePrefactura.objects.filter(cirugia_id=cirugia_id, cantidad_usada__gte = 0).order_by('detalle__posicion')
    subtotal_usd=0
    subtotal_bs=0
    total_general_bs = 0
    detalle_agrupado = defaultdict(lambda: {'items': [], 'subtotal': 0, 'subtotalbs': 0})
    for detalle in detallecirugia:
        detalle_agrupado[detalle.grupo_id]['items'].append(detalle)
        detalle_agrupado[detalle.grupo_id]['subtotal'] += detalle.precio_usado   # Sumar el subtotal
        detalle_agrupado[detalle.grupo_id]['subtotalbs'] += detalle.precio_congelado_cirugia   # Sumar el subtotal
        subtotal_usd += detalle.precio_usado
        subtotal_bs += detalle.precio_congelado_cirugia
        total_general_bs += detalle.precio_congelado_cirugia

    # Obtener los nombres de los grupos
    grupo_ids = detalle_agrupado.keys()
    grupos = {grupo.id: grupo.nombre for grupo in GrupoBaremo.objects.filter(id__in=grupo_ids)}
    saldoactual_bs = (saldoactual * cambio_calculo)

    # Convertir el defaultdict a una lista para pasar a la plantilla
    detalle_agrupado_lista = [{'grupo_id': key, 'grupo_nombre': grupos[key], 'items': value['items'], 'subtotal': value['subtotal'], 'subtotalbs': value['subtotalbs']} for key, value in detalle_agrupado.items()]
        # Contexto para la plantilla
    context = {
            'cirugia': cirugia,
            'fecha_hoy': datetime.now(),
            'tasa_calculo': cambio_calculo,
            'subtotal_usd':subtotal_usd,
            'subtotal_bs':subtotal_bs,
            'totalabono' : totalabono,
            'totalabono_bs':totalabono_bs,
            'saldoactual' : saldoactual,
            'saldoactual_bs':saldoactual_bs,
            'total_general_bs':total_general_bs,
            'detalle_agrupado': detalle_agrupado_lista  # Cambia 'detallecirugia' por 'detalle_agrupado'
        }
    
    # Renderiza tu plantilla HTML
    html_string = render_to_string('factura_resumen.html', context)
    #html_string = render_to_string(self.template_name, context)
    html_string = html_string.replace('/static/', request.build_absolute_uri('/static/'))
    
    html = HTML(string=html_string)
    pdf = html.write_pdf()  # Genera el PDF en memoria
    nombre_archivo = f"factura_{cirugia_id}.pdf"
   
    # Crea la respuesta HTTP con el PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename='+nombre_archivo
    return response

@add_group_name_to_context    
class PreingresoNew(UserPassesTestMixin,TemplateView):
    template_name='preingreso_new.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Enfermeria')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        PreIngreso.objects.filter(estatus_id = 9).delete()
        #Paciente.objects.filter(status = 'X').delete()
        habitaciones = Habitacion.objects.all().order_by('habitacion')
        kit = KitInventario.objects.all().order_by('nombre')
        personal_medico = Medico.objects.filter(grupo='M').exclude(tipopersonal_id = 9).order_by('nombre')
        depositos = Deposito.objects.all().order_by('nombre')
        baremo = Baremo.objects.filter(inactivar = False).order_by('detalle__posicion')
        tipo_procedimiento = TipoProcedimiento.objects.all().order_by('nombre')
        #edad_paciente=calcular_edad(cirugia.paciente.fecha_nac)
        preingreso = PreIngreso.objects.create(
            usuario_id = self.request.user.id
        )
        preingreso_id = preingreso.id
        nuevo_codigo_preingreso = generar_siguiente_codigo_preingreso()
        PreIngreso.objects.filter(id = preingreso_id ).update(
            codigo = 'CPA'+str(nuevo_codigo_preingreso).zfill(4)
        )
        fecha_hoy = datetime.now().date()
        hora_actual = datetime.now().time()
        medicospreingreso = NotaQuirurgica.objects.filter(preingreso_id=preingreso_id).order_by('medico__nombre')

        context['codigoatencion'] = 'CPA'+str(nuevo_codigo_preingreso).zfill(4)
        context['kit'] = kit
        context['preingreso_id'] = preingreso_id
        context['personal_medico'] = personal_medico
        context['depositos'] = depositos
        context['baremo'] = baremo
        context['fecha_hoy'] = fecha_hoy
        context['hora_actual'] = hora_actual
        context['habitaciones'] = habitaciones
        context['tipo_procedimiento'] = tipo_procedimiento
        context['medicospreingreso'] = medicospreingreso
        
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        if 'guardar_atencion' in request.POST:
            cedula_atencion_inmediata =  self.request.POST.get('cedula_atencion_inmediata')
            nombrepaciente =  self.request.POST.get('nombrepaciente')
            apellidopaciente =  self.request.POST.get('apellidopaciente')
            tipoprocedimiento =  self.request.POST.get('tipoprocedimiento')
            fecha_nac_paciente =  self.request.POST.get('fecha_nac_paciente')
            fecha_atencion =  self.request.POST.get('fecha_atencion')
            motivo_atencion =  self.request.POST.get('motivo_atencion')
            medico_ppal_atencion =  self.request.POST.get('medico_ppal_atencion')
            habitacion_atencion =  self.request.POST.get('habitacion_atencion')
            idPaciente_name =  self.request.POST.get('idPaciente_name')
            idatencion_name =  self.request.POST.get('id-atencion-name')
            hora_ingreso =  self.request.POST.get('hora_ingreso')
            presupuesto_vinculado = self.request.POST.get('name_presupuesto_vinculado')
            
            Paciente.objects.filter(id=idPaciente_name).update(
                cedula = cedula_atencion_inmediata,
                nombre = nombrepaciente,
                apellido = apellidopaciente,
                fecha_nac = fecha_nac_paciente,
                status = 'A'
            )
            
            presupuesto_vinculado = int(presupuesto_vinculado)
            
            presupuesto = Presupuesto.objects.filter(id = presupuesto_vinculado).first()

            #presupuesto = Presupuesto.objects.filter(paciente_id = idPaciente_name, estatus_id = 1).order_by('-fecha_act').first()
                
            if presupuesto:
                Presupuesto.objects.filter(id=presupuesto.id).update(
                    medico_ppal_id = medico_ppal_atencion,
                    estatus_id = 11,
                    usuario_id = request.user.id,
                )
            else:
                presupuesto = Presupuesto.objects.create(
                    fecha_procedimiento  = datetime.now(),
                    hora_procedimiento = datetime.now().time(),
                    nombre_procedimiento = motivo_atencion,
                    medico_ppal_id = medico_ppal_atencion,
                    paciente_id = idPaciente_name,
                    tipo_procedimiento_id = tipoprocedimiento,
                    usuario_id = request.user.id,
                    estatus_id = 11,
                    convenio_id = 1,
                    nota = 'creado en preingreso'
                    ) 
                #INCLUYE SOLO EL MMQ DE PREINGRESO DE LA PLANTILLA ESPECIAL
                baremo_incluir = Baremo.objects.filter(detalle__preingreso = True).first()
                if baremo_incluir:
                    DetallePresupuesto.objects.create(
                                cantidad = baremo_incluir.cantidad,
                                precio = baremo_incluir.venta,
                                convenio_id = baremo_incluir.convenio_id,
                                detalle_id = baremo_incluir.detalle_id,
                                grupo_id = baremo_incluir.grupo_id,
                                plantilla_id = baremo_incluir.plantilla_id,
                                unidad_id = baremo_incluir.unidad_id,
                                presupuesto_id = presupuesto.id,
                                ntqx = baremo_incluir.ntqx,
                                usuario_id = request.user.id,
                                preingreso_id = idatencion_name
                            )
                #FIN SOLO EL MMQ DE PREINGRESO DE LA PLANTILLA ESPECIAL
                
                baremo_incluir = Baremo.objects.filter(plantilla_id = 1).exclude(detalle_id__in = [32,33])
                if baremo_incluir:
                    for incluir in baremo_incluir:
                        if incluir.detalle.preingreso:
                            preingreso_id = idatencion_name
                            monto_venta = incluir.venta
                        else:
                            preingreso_id = None
                            monto_venta = 0
                            
                            
                        detallepresupuesto = DetallePresupuesto.objects.create(
                            cantidad = incluir.cantidad,
                            precio = monto_venta,
                            convenio_id = incluir.convenio_id,
                            detalle_id = incluir.detalle_id,
                            grupo_id = incluir.grupo_id,
                            plantilla_id = incluir.plantilla_id,
                            unidad_id = incluir.unidad_id,
                            presupuesto_id = presupuesto.id,
                            ntqx = incluir.ntqx,
                            usuario_id = request.user.id,
                            preingreso_id = preingreso_id
                        )
                        
                
            presupuesto_id = presupuesto.id
            cirugia = Cirugia.objects.create(
                fecha_procedimiento = fecha_atencion,
                hora_procedimiento = hora_ingreso,
                nombre_procedimiento = motivo_atencion,
                medico_ppal_id = medico_ppal_atencion,
                paciente_id = idPaciente_name,
                tipo_procedimiento_id = 6,
                usuario_id = self.request.user.id,
                presupuesto_id = presupuesto_id,
                convenio_id = 1,
                estatus_id = 11,
                ultimo_estatus = 11,
                fecha_creacion = datetime.now()
            )
            
            PreIngreso.objects.filter(id = idatencion_name).update(
                estatus_id = 11,
                usuario_id = self.request.user.id,
                cirugia_id = cirugia.id,
                habitacion_id = habitacion_atencion,
                nombre_procedimiento = motivo_atencion
                
            )
            
                            
            
            
            presupuesto = Presupuesto.objects.filter(id = presupuesto_id).first()
            
            if presupuesto:
                
                monto_subtotal_baremo = presupuesto.total_monto_precio
                
                """ presupuestoatencioninmediata = DetallePresupuesto.objects.filter(presupuesto_id = presupuesto_id)
                monto_subtotal_baremo = presupuestoatencioninmediata.aggregate(total=Sum(F('precio') * F('cantidad')))['total']
                if not presupuestoatencioninmediata:
                    monto_subtotal_baremo = 0 """
                    
                    
                cuenta_por_cobrar = CuentaxCobrar.objects.filter(presupuesto_id = presupuesto_id).first()
                if cuenta_por_cobrar:
                    CuentaxCobrar.objects.filter(presupuesto_id = presupuesto_id).update(
                            pagado = False,
                            cirugia_id = cirugia.id,
                            paciente_id = idPaciente_name,
                            presupuesto_id = presupuesto.id,
                            usuario_id = self.request.user.id
                        )
                    detalle_existe = DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuenta_por_cobrar.id, montocobrar__gte = 0).first()
                    if detalle_existe:
                        DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuenta_por_cobrar.id, montocobrar__gte = 0).update(
                            montocobrar = monto_subtotal_baremo,
                            descripcion = 'PreIngreso No.:'+str(idatencion_name).zfill(4)+' de cirugia No.: '+str(cirugia.id).zfill(6) ,
                        )
                    else:
                        DetalleCuentaCobrar.objects.create(
                            cuentacobrar_id = cuenta_por_cobrar.id,
                            montocobrar = monto_subtotal_baremo,
                            descripcion = 'PreIngreso No.:'+str(idatencion_name).zfill(4)+' de cirugia No.: '+str(cirugia.id).zfill(6) ,
                        )
                    
                else:
                    cuenta_por_cobrar = CuentaxCobrar.objects.create(
                            pagado = False,
                            cirugia_id = cirugia.id,
                            paciente_id = idPaciente_name,
                            presupuesto_id = presupuesto.id,
                            usuario_id = self.request.user.id
                        )
                    
                    DetalleCuentaCobrar.objects.create(
                            cuentacobrar_id = cuenta_por_cobrar.id,
                            montocobrar = monto_subtotal_baremo,
                            descripcion = 'PreIngreso No.:'+str(idatencion_name).zfill(4)+' de cirugia No.: '+str(cirugia.id).zfill(6) ,
                        )
            
        return redirect('listado_preingresos')
    
def revisar_existe_compuesto_consumo(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idproducto = datos['idproducto']
        idcirugia = datos['idcirugia']
        lugar_consumo = datos['lugar_consumo']
        consumo = ConsumoCirugia.objects.filter(cirugia_id = idcirugia, compuesto = 2, inventario_id = idproducto, consumo_id = lugar_consumo).exists()
            
        return JsonResponse({'consumo': consumo})
    
        
    return JsonResponse({'consumo': consumo})

def buscar_pagador_notacredito(request):
    vcedulapagador = request.GET.get('vcedulapagador')
    # Query your database to retrieve the corresponding date
    nombre = telefono = direccion = ''
    cantidad_existe_notacredito = 0
    pagador_id = 0
    total_saldo = 0
    existepagador = PagadorUnico.objects.filter(cedula = vcedulapagador).first()
    if not existepagador:
        existepagador = Medico.objects.filter(cedula = vcedulapagador).first()
        if existepagador:
            telefono = existepagador.telefono1
            nombre = existepagador.nombre
            direccion = existepagador.direccion
        else:
            existepagador = Paciente.objects.filter(cedula = vcedulapagador).first()
            if existepagador:
                telefono = existepagador.telefono1
                nombre = existepagador.nombre + ' '+ existepagador.apellido
                direccion = existepagador.direccion 
            
            
    else:
        pagador_id = existepagador.id
        nombre = existepagador.nombre
        direccion = existepagador.direccion
        telefono = existepagador.telefono
        existe_notacredito = NotaCreditoCtaCobrar.objects.filter(pagador_id = existepagador.id, aplicada=False)
        cantidad_existe_notacredito = NotaCreditoCtaCobrar.objects.filter(pagador_id = existepagador.id, aplicada=False).count()
        if existe_notacredito:
            total_saldo = existe_notacredito.aggregate(total=Sum('saldo'))['total']
            
   
    return JsonResponse({'nombre': nombre, 'telefono':telefono, 'direccion':direccion, 'pagador_id':pagador_id, 'total_saldo':total_saldo, 'cantidad_existe_notacredito':cantidad_existe_notacredito})

def detalle_cuentacobrar_notacredito(request):
    if request.method == 'POST':
        tasa_hoy = CambioDiaBcv(datetime.now())
        datos = json.loads(request.body)
        cuentacobrar_id = datos['cuentacobrar_id']
        total_saldo = datos['total_saldo']
        vcedulapagador = datos['vcedulapagador']
        saldo_deudor = datos['saldo_deudor']
        saldo_deudor = float(saldo_deudor)
        total_saldo = float(total_saldo)
        
        tasa_hoy = float(tasa_hoy)
        existepagador = PagadorUnico.objects.filter(cedula = vcedulapagador).first()
        existe_notacredito = NotaCreditoCtaCobrar.objects.filter(pagador_id = existepagador.id, aplicada=False).order_by('saldo')
        notacredito_id = NotaCreditoCtaCobrar.objects.filter(pagador_id = existepagador.id, aplicada=False).first()
        if notacredito_id:
            id_notacredito = notacredito_id.id
            transaccion_vinculada = Transaccion.objects.filter(notacredito = id_notacredito).first()
            if transaccion_vinculada:
                transaccion_vinculada_id = transaccion_vinculada.id
            else:
                transaccion_vinculada_id = None
                
            pagador_de_nota_credito = Pagador.objects.filter(notacredito_origen_id = id_notacredito).first()
            if pagador_de_nota_credito:
                pagador_de_nota_credito_id = pagador_de_nota_credito.id
            else:
                pagador_de_nota_credito_id = None
                
        else:
            id_notacredito = 0
            transaccion_vinculada_id = None
            pagador_de_nota_credito_id = None
            
            
        numero_historias = ''
        for cirugia in existe_notacredito:
            if cirugia.detallecuentaxcobrar:
                numero_historias = numero_historias + '# '+ str(cirugia.detallecuentaxcobrar.cuentacobrar.cirugia_id)
            else:
                numero_historias = cirugia.descripcion + ' ID: '+str(cirugia.id)+ ' Nota Creada por:'+str(cirugia.usuario)
        
        nuevo_saldo = 0
        
        if saldo_deudor < total_saldo:
            monto_pago = saldo_deudor
            nuevo_saldo = total_saldo - saldo_deudor
            for nota in existe_notacredito:
                NotaCreditoCtaCobrar.objects.filter(id=nota.id).update(
                        aplicada = True,
                        usuario_id = request.user.id,
                        cuentaxcobrar_aplicada_id = cuentacobrar_id,
                    )
                if nota.saldo > saldo_deudor:
                    nuevo_detalle = DetalleCuentaCobrar.objects.create(
                        montocobrar = nuevo_saldo * -1.00,
                        descripcion = 'Nota de Credito AutoGenerada: '+numero_historias,
                        cuentacobrar_id = cuentacobrar_id,
                        montocobrar_bs = (nuevo_saldo * tasa_hoy)*-1.00,
                        tasa_bcv = tasa_hoy,
                        notacredito = True,
                        notacredito_manual_id = nota.id,
                        transaccion_id = transaccion_vinculada_id
                    ) 
                    NotaCreditoCtaCobrar.objects.create(
                        saldo = nuevo_saldo,
                        detallecuentaxcobrar_id = nuevo_detalle.id,
                        usuario_id = request.user.id,
                        pagador_id = existepagador.id,
                        descripcion = "NOTA CREDITO GENERADA POR SALDO RESTANTE DE LA NOTA DE CREDITO DE: "+str(total_saldo)+" NC ORIGEN: "+str(nota.id),
                        fechatasa = datetime.now(),
                        saldo_bs = (nuevo_saldo * tasa_hoy)*-1.00,
                        fecha_pago = datetime.now(),
                        tasa = tasa_hoy,
                        autogenerada = True
                        
                    )
                    
                
        else:
            monto_pago = total_saldo
            NotaCreditoCtaCobrar.objects.filter(pagador_id = existepagador.id, aplicada=False).update(
                        aplicada = True,
                        usuario_id = request.user.id,
                        cuentaxcobrar_aplicada_id = cuentacobrar_id,
                    )
            
            
        nuevo_detalle = DetalleCuentaCobrar.objects.create(
            montocobrar = monto_pago * -1.00,
            descripcion = 'PAGO CON Nota de Credito de cirugias: '+numero_historias,
            cuentacobrar_id = cuentacobrar_id,
            montocobrar_bs = (monto_pago * tasa_hoy)*-1.00,
            tasa_bcv = tasa_hoy,
            notacredito = True,
            notacredito_manual_id = id_notacredito,
            transaccion_id = transaccion_vinculada_id
        ) 
        if pagador_de_nota_credito_id:
            Pagador.objects.filter(id = pagador_de_nota_credito_id ).update(
                detallecuentaxcobrar_id = nuevo_detalle.id 
            )
        
      
        return JsonResponse({'mensaje': 'Creado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})


@add_group_name_to_context    
class notas_credito_cuentacobrar(UserPassesTestMixin, TemplateView): 
    
    template_name='notas_credito_cuentacobrar.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # inicio de borrado luego de correrlo
        
        notascredito = NotaCreditoCtaCobrar.objects.all().order_by('pagador_id')
        total_monto_credito = sum(nc.saldo for nc in notascredito)  # Sumar los saldos
        eliminarNota = self.request.user.groups.filter(Q(name='EliminarNC')).exists()
        
        context['notascredito'] = notascredito
        context['eliminarNota'] = eliminarNota
        context['total_monto_credito'] = total_monto_credito
        
        return context
    
def transaccion_moneda(request):
    transaccion = Transaccion.objects.all()
    context=[]
    for tr in transaccion:
        cuenta_destino = ''
        cuenta_origen = ''
        nombre_proveedor = ''
        if tr.monto < 0:
            movimiento='Debito'
            cuenta_origen = tr.bancolocal.nombrecuenta
            
            if tr.banco:
                cuenta_destino = tr.banco.nombre
                
            nombre_proveedor = tr.pagomedico.medico.nombre
            monto_bolivares = tr.monto * -1
            monto_dolares = tr.monto_dolar * -1
                
        else:
            monto_bolivares = tr.monto
            monto_dolares = tr.monto_dolar
            if tr.cuentacobrar.cirugia:
                nombre_proveedor = 'CIRUGIA'
            else:
                 if tr.cuentacobrar.atencion_inmediata:
                     nombre_proveedor = 'ATENCION INMEDIATA'
                 else:
                     nombre_proveedor = 'PRESUPUESTO'
            
            movimiento='Credito'
            cuenta_destino = tr.bancolocal.nombrecuenta
            if tr.banco:
                cuenta_origen = tr.banco.nombre
            
            
        
        if tr.mediomoneda.moneda_id == 1:
            monto_unico = monto_dolares
            monto_bolivares = 0
        else:
            monto_unico = monto_bolivares
            monto_dolares = 0
        
        monto_solo_dolar = tr.monto_dolar 
        if tr.monto_dolar < 0:
            monto_solo_dolar = tr.monto_dolar * -1
         
        DebitoCredito.objects.create(
             transaccion_id = tr.id,
             cuenta_origen = cuenta_origen,
             cuenta_destino = cuenta_destino,
             medico_proveedor = nombre_proveedor,
             monto_bolivares = monto_bolivares,
             monto_dolar = monto_dolares,
             tasa_bcv = tr.tasa_bcv,
             movimiento = movimiento,
             fechatransaccion = tr.fecha_act,
             descripcion = tr.descripcion,
             referencia = tr.referencia,
             usuario = tr.usuario.username,
             formapago = tr.mediomoneda.nombre,
             moneda = tr.mediomoneda.moneda.nombre,
             monto_unico = monto_unico,
             dolares =  monto_solo_dolar
         )       
    return context

def agregar_a_consumo_preanestesia(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        inventario_id = datos['inventario_id']
        cantidad_aplicar = datos['cantidad_aplicar']
        idAtencion = datos['idAtencion']
        depositoId = datos['depositoId']
        cirugiaId = datos['cirugiaId']
        depositoubicacion = DepositoUso.objects.filter(inventario_id = inventario_id, deposito_id = depositoId).first()
        if depositoubicacion:
            if  Decimal(cantidad_aplicar) <= Decimal(depositoubicacion.existenciaUnd):
                producto = Inventario.objects.filter(id=inventario_id).first()
                precio_costo_unitario = precio_costo_producto_inventario(inventario_id)
                consumonuevo = ConsumoCirugia.objects.create(
                    preingreso_id = idAtencion,
                    cantidad_real_usada = cantidad_aplicar,
                    cantidad_uso = cantidad_aplicar,
                    venta = 0,
                    nota = 'PRE-INGRESO CONSULTA PREANESTESIA',
                    inventario_id = inventario_id,
                    consumo_id = 8,
                    usuario_id = request.user.id,
                    hora_uso = datetime.now().time(),
                    precio_unitario = producto.monto_venta,
                    deposito_id = depositoId,
                    cirugia_id = cirugiaId,
                    precio_costo_unitario = precio_costo_unitario
                )
                InventarioDescarga.objects.create(
                    cantidad = cantidad_aplicar,
                    nota = 'PRE-INGRESO CONSULTA PREANESTESIA',
                    deposito_id = depositoId,
                    inventario_id = inventario_id,
                    usuario_id = request.user.id,
                    tipodescarga_id = 18,
                    preingreso_id = idAtencion,
                    persona_id = request.user.id,
                    consumocirugia_id = consumonuevo.id,
                    cirugia_id = cirugiaId
                )
                
                return JsonResponse({'mensaje': 'Creado Consumo'})
            else:
                return JsonResponse({'mensaje': 'No dispone de cantidad en existencia'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8048 View.py'})
    
    
@add_group_name_to_context    
class PreingresoUpdate(UserPassesTestMixin,TemplateView):
    template_name='preingreso_update.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Enfermeria')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_atencion = self.kwargs.get('preingreso_id')
        habitaciones = Habitacion.objects.all().order_by('habitacion')
        personal_medico = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        depositos = Deposito.objects.all().order_by('nombre')
        baremo = Baremo.objects.filter(inactivar = False).order_by('detalle__posicion')
        tipo_procedimiento = TipoProcedimiento.objects.filter(id=6).first()
        atencion_inmediata = PreIngreso.objects.filter(id = id_atencion).first()
        cirugia = Cirugia.objects.filter(id = atencion_inmediata.cirugia_id ).first()
        medicostratante = DetallePresupuesto.objects.filter(presupuesto_id = cirugia.presupuesto_id, grupo_id = 7, medico__participaalta = True)
        consumohospital = ConsumoCirugia.objects.filter(preingreso_id=id_atencion, consumo_id = 8)
        monto_subtotal_farmacia = consumohospital.aggregate(subtotal_farmacia=Sum(F('precio_unitario') * F('cantidad_real_usada')))['subtotal_farmacia']
        presupuesto = Presupuesto.objects.filter(id = cirugia.presupuesto_id).first()
        if presupuesto:
            monto_subtotal_baremo = presupuesto.total_monto_precio
        else:
            monto_subtotal_baremo = 0
            
        presupuestoatencioninmediata = DetallePresupuesto.objects.filter(presupuesto_id = cirugia.presupuesto_id, preingreso_id = id_atencion).exclude(detalle_id=94)
        """ monto_subtotal_baremo = presupuestoatencioninmediata.aggregate(total=Sum(F('precio') * F('cantidad')))['total'] """
        tratamientos = Tratamiento.objects.filter(preingreso_id = id_atencion)
        detallesubbaremocirugia = DetalleSubBaremoConsumo.objects.filter(cirugia_id = cirugia.id).exists()

        destino_farmacos_mmq = DetallePresupuesto.objects.filter(presupuesto_id = cirugia.presupuesto_id, preingreso_id = id_atencion, montotope__gt = 0 )
        if destino_farmacos_mmq:
            muestra_seleccion = 'true'
        else:
            muestra_seleccion = 'false'
            
        if not consumohospital:
            monto_subtotal_farmacia = 0
            
        """ if not presupuestoatencioninmediata:
            monto_subtotal_baremo =0 """
            
        total_subtotal = monto_subtotal_farmacia + monto_subtotal_baremo
        
        superUser = self.request.user.groups.filter(Q(name='SuperAdministracion')).exists()
        enfermeria = self.request.user.groups.filter(Q(name='Enfermeria')).exists()
        detallesubbaremocirugia = DetalleSubBaremoConsumo.objects.filter(cirugia_id = cirugia.id).order_by('subbaremo__nombre_subbaremo')
        
        context['superUser'] = superUser
        context['enfermeria'] = enfermeria
        context['cirugia'] = cirugia
        context['personal_medico'] = personal_medico
        context['medicostratante'] = medicostratante
        context['depositos'] = depositos
        context['baremo'] = baremo
        context['habitaciones'] = habitaciones
        context['atencion_inmediata'] = atencion_inmediata
        context['muestra_seleccion'] = muestra_seleccion
        context['tipo_procedimiento'] = tipo_procedimiento
        context['tratamientos'] = tratamientos
        context['consumohospital'] = consumohospital
        context['total_subtotal'] = total_subtotal
        context['destino_farmacos_mmq'] = destino_farmacos_mmq
        context['monto_subtotal_farmacia'] = monto_subtotal_farmacia
        context['monto_subtotal_baremo'] = monto_subtotal_baremo
        context['detallesubbaremocirugia'] = detallesubbaremocirugia
        context['presupuestoatencioninmediata'] = presupuestoatencioninmediata
        
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        preingreso_id = self.kwargs.get('preingreso_id')
        preingreso = PreIngreso.objects.filter(id=preingreso_id).first()
        cirugia_id = preingreso.cirugia_id
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        medicos_notaqx = DetallePresupuesto.objects.filter(presupuesto_id = cirugia.presupuesto_id, grupo_id = 7, medico__isnull = False)
        medico_ppal_atencion =  self.request.POST.get('medico_ppal_atencion')
        nombre_procedimiento =  self.request.POST.get('nombre_procedimiento')
        nombre_diagnostico =  self.request.POST.get('nombre_diagnostico')
        habitacion_atencion =  self.request.POST.get('habitacion_atencion')
        
        Cirugia.objects.filter(id=cirugia_id).update(
            medico_ppal_id = medico_ppal_atencion,
            usuario_id = self.request.user.id,
            nombre_procedimiento = nombre_procedimiento,
            diagnostico = nombre_diagnostico
        )
        
        PreIngreso.objects.filter(cirugia_id = cirugia_id).update(
            usuario_id = self.request.user.id,
            habitacion_id = habitacion_atencion,
            
            
        )
        
        presupuesto = Presupuesto.objects.filter(id = cirugia.presupuesto_id).first()
        Presupuesto.objects.filter(id = presupuesto.id).update(
            medico_ppal_id = medico_ppal_atencion,
            usuario_id = self.request.user.id,
        )
        
        consumohospital = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, consumo_id = 8 )
        descargainventario  = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, consumo_id = 8, conciliada = False)
        if consumohospital: 
            monto_subtotal_farmacia = consumohospital.aggregate(subtotal_farmacia=Sum(F('precio_unitario') * F('cantidad_real_usada')))['subtotal_farmacia']
            for descarga in descargainventario:
                ConsumoCirugia.objects.filter(id = descarga.id).update(
                    conciliada = True,
                    usuario_id = self.request.user.id
                )
        else:
            monto_subtotal_farmacia = 0
        
        
        monto_subtotal_baremo = 0
        
        if presupuesto:
            presupuestoatencioninmediata = DetallePresupuesto.objects.filter(presupuesto_id =  cirugia.presupuesto_id)
            monto_subtotal_baremo = presupuesto.total_monto_precio
            if not presupuestoatencioninmediata:
                monto_subtotal_baremo = 0
                
                
        total_subtotal = Decimal(monto_subtotal_baremo)
            
        cuentaxcobrar = CuentaxCobrar.objects.filter(cirugia_id = cirugia_id).first()
        if cuentaxcobrar:  
            DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuentaxcobrar.id, montocobrar__gte = 0).update(
                    montocobrar = total_subtotal,
                    descripcion = '(Monto a Cobrar por:) Preingreso HISTORIA..: '+str(cirugia_id).zfill(6),
                    )
        
        
        return redirect('listado_preingresos')
    
@add_group_name_to_context    
class fotos_cirugia(UserPassesTestMixin,TemplateView):
    template_name='foto.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Enfermeria')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    
def modificar_baremo(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idBaremo = datos['idBaremo']
        tipo = datos['tipo']
        monto = datos['monto']
        monto = float(monto.replace(',','.'))
        if tipo == 'V':
            Baremo.objects.filter(id=idBaremo).update(
                venta = monto,
                usuario_id = request.user.id
            )
        if tipo == 'T':
             Baremo.objects.filter(id=idBaremo).update(
                topedia = monto,
                usuario_id = request.user.id
            )
        if tipo == 'C':
             Baremo.objects.filter(id=idBaremo).update(
                costo = monto,
                usuario_id = request.user.id
            )


        
        return JsonResponse({'mensaje': 'Datos guardados correctamente en moficicacion de corte de cuenta'})
    else:
        return JsonResponse({'mensaje': 'Error al guardar en modificacion de corte de cuenta'})
    
@add_group_name_to_context    
class CorteCuentaPreingreso(UserPassesTestMixin,TemplateView):
    template_name='corte_cuenta_preingreso.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atencion_id = self.kwargs['atencion_id']
        atencion_inmediata = PreIngreso.objects.filter(id=atencion_id).first()
        total_consumo_farmacia = total_consumo_mmq = 0
        consumos = ConsumoCirugia.objects.filter(cirugia_id = atencion_inmediata.cirugia_id, consumo_id = 8)
        subbaremitos = DetalleSubBaremoConsumo.objects.filter(cirugia_id = atencion_inmediata.cirugia_id)
        
        tasa_actual = CambioDiaBcv(datetime.now())
        for consumo in consumos:
            #if consumo.inventario.categoria_id == 1 or consumo.inventario.categoria_id == 2 :
            total_consumo_farmacia = total_consumo_farmacia + (consumo.precio_unitario * consumo.cantidad_uso)
        
        
        detallepresupuesto = []
        medicos = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        fecha_actual = datetime.now().date()
        presupuesto = Presupuesto.objects.filter(id=atencion_inmediata.cirugia.presupuesto_id).first()
        if presupuesto:
            monto_tope = monto_excedente = precio_baremo = 0
            baremo = Baremo.objects.filter(convenio_id=1, plantilla_id = 2, detalle_id=94).first()
            if baremo:
                monto_tope = baremo.topedia
                precio_baremo = baremo.venta
                
            if total_consumo_farmacia > monto_tope:
                monto_excedente = total_consumo_farmacia - monto_tope
                
            detallepresupuesto = DetallePresupuesto.objects.filter(presupuesto_id=presupuesto.id, detalle_id = 94).first()
            if detallepresupuesto:
                if total_consumo_farmacia > 0:
                    DetallePresupuesto.objects.filter(presupuesto_id=presupuesto.id, detalle_id = 94).update(
                        cantidad = 1,
                        precio = precio_baremo+monto_excedente ,
                        cantidad_usada = 1,
                        precio_usado = precio_baremo+monto_excedente ,
                        usuario_id = self.request.user.id,
                    )
                    
            
            consumo_detalle_presupuesto =  DetallePresupuesto.objects.filter(presupuesto_id=presupuesto.id, montotope__gt = 0, preingreso__isnull = False, alertaexcedente = True)   
            for monto_consumo in consumo_detalle_presupuesto:
                if monto_consumo.total_consumo_preingreso > monto_consumo.montotope:
                    DetallePresupuesto.objects.filter(id = monto_consumo.id).update(
                        excedente = (monto_consumo.total_consumo_preingreso - monto_consumo.montotope),
                        usuario_id = self.request.user.id
                    )
                    
        
            detallepresupuesto = DetallePresupuesto.objects.filter(presupuesto_id=presupuesto.id, preingreso__isnull = False).annotate(
                                                                subtotal_bs=ExpressionWrapper(
                                                                    F('precio') * tasa_actual,
                                                                    output_field=FloatField()
                                                                )
                                                            ).order_by('detalle__posicion')
            
            total_cobrar = 0
            for subtotal in detallepresupuesto:
                total_cobrar += (subtotal.subtotal)
                
            cuentacobrar = CuentaxCobrar.objects.filter(presupuesto_id = presupuesto.id).first()
            if cuentacobrar:
                DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuentacobrar.id, montocobrar__gte = 0).update(
                    montocobrar = total_cobrar
                )
            
        
        context['medicos'] = medicos 
        context['subbaremitos'] = subbaremitos 
        context['fecha_actual'] = fecha_actual  
        context['detallepresupuesto'] = detallepresupuesto  
        context['atencion_inmediata'] = atencion_inmediata  
        return context
    
    
@add_group_name_to_context    
class AdmisionPreingreso(TemplateView):
    template_name='admision.html'
    
    def get(self, request, *args, **kwargs):
        paciente_id = self.kwargs['paciente_id']
        paciente = Paciente.objects.filter(id=paciente_id).first()
        
        if paciente:
            cirugia = Cirugia.objects.filter(paciente_id=paciente.id).first()
            if cirugia:
                if cirugia.estatus_id in [2,3,4,5,6,9,10]:
                    messages.error(request, 'EXISTE UNA ADMISION ACTUAL CON ESE PACIENTE Y LA HISTORIA ES :'+str(cirugia.id)+' ESTATUS ACTUAL: '+str(cirugia.estatus)+'/ NOTA: NO PUEDE ADMITIR NUEVAMENTE ANTES DE EJECUTAR EL ALTA DEL PACIENTE')
                    return redirect('pacientes')
        
        # Si no hay redireccionamiento, llama al método get_context_data
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id = self.kwargs['paciente_id']
        paciente = Paciente.objects.filter(id=paciente_id).first()
        
        edad_paciente=calcular_edad(paciente.fecha_nac)
        presupuestos = Presupuesto.objects.filter(estatus_id=11, paciente_id = paciente_id).order_by('-fecha_act')
        
        responsable = Responsable.objects.filter(id=paciente.responsable_id).first()
        if responsable:
            context['responsable'] = responsable
            
        
        cambio_hoy = CambioDiaBcv(datetime.now())
        fecha_hoy = datetime.now()
        medicos = Medico.objects.all().exclude(tipopersonal_id = 9).order_by('nombre')
        imagen_paciente = ImagenPhoto.objects.filter(cedula = paciente.cedula ).first()
        if imagen_paciente:
            pass
        else:
            imagen_paciente = ImagenPhoto.objects.filter(cedula = 'VU58Image' ).first()

        
        context['edad_paciente'] = edad_paciente
        context['imagen_paciente'] = imagen_paciente
        context['paciente'] = paciente
        context['cambio_hoy'] = cambio_hoy
        context['fecha_hoy'] = fecha_hoy
        context['presupuestos'] = presupuestos
        context['medicos'] = medicos
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        paciente_id = self.kwargs['paciente_id']
        user_id = self.request.user.id
        id_presupuesto_seleccionado = request.POST.get('seleccion')
        if not id_presupuesto_seleccionado:
            messages.warning(request, 'Debe seleccionar el presupuesto para proceder a la admision del paciente')
            return redirect('admision' , paciente_id = paciente_id ) 
        
        cambio_congelado = request.POST.get('monto_cambio_congelado')
        fecha_congelado = request.POST.get('fecha_cambio_congelado')
        medico_id = request.POST.get('medico')
        persona_contacto = request.POST.get('persona_contacto')
        if medico_id == "None":
            medico_id = None
        else:
            medico = Medico.objects.filter(id=medico_id).first()

        
        telefono_contacto = request.POST.get('telefono_contacto')
        registros_presupuesto = Presupuesto.objects.filter(id=id_presupuesto_seleccionado).first()
        responsable = Responsable.objects.filter(id=registros_presupuesto.paciente.responsable_id).first()
        if registros_presupuesto.congelar_moneda:
            Presupuesto.objects.filter(id=id_presupuesto_seleccionado).update(
                cambio_congelado = cambio_congelado.replace(',','.'),
                fecha_cambio = fecha_congelado
            )
            registros_presupuesto = Presupuesto.objects.filter(id=id_presupuesto_seleccionado).first()
            
            
        informe_med_ingreso = orden_ingreso = carta_compromiso = tramite_administrativo = examen_preoperatorio = evaluacion_cardio = evaluacion_preanestesica = False
        
        
        if 'informe_med_ingreso' in request.POST:
            informe_med_ingreso = True
            
        if 'orden_ingreso' in request.POST:
            orden_ingreso = True
            
        if 'carta_compromiso' in request.POST:
            carta_compromiso = True
            
        if 'tramite_administrativo' in request.POST:
            tramite_administrativo = True
            
        if 'examen_preoperatorio' in request.POST:
            examen_preoperatorio = True
            
        if 'evaluacion_cardio' in request.POST:
            evaluacion_cardio = True
            
        if 'evaluacion_preanestesica' in request.POST:
            evaluacion_preanestesica = True
            
        boton_presionado = request.POST.get('btn_aceptar')
        if boton_presionado == 'aceptar':
            objectos_detalle = []
            cirugia_creada = Cirugia.objects.filter(paciente_id = registros_presupuesto.paciente.id, estatus_id = 11).first()
            idHistoria = cirugia_creada.id
            if cirugia_creada:
                if registros_presupuesto.congelar_moneda:
                    Cirugia.objects.filter(id = cirugia_creada.id).update(
                        congelar_moneda =  True,
                        cambio_congelado = cambio_congelado.replace(',','.'),
                        fecha_cambio = fecha_congelado
                        
                    )
                    
                
                registros_detalle_presupuesto = DetallePresupuesto.objects.filter(presupuesto_id=cirugia_creada.presupuesto_id)
                for detalle in registros_detalle_presupuesto:
                    if detalle.ntqx:
                        facturable = False
                    else:
                        facturable = True
                    
                    objectos_detalle.append(DetalleCirugia(cirugia_id=idHistoria ,cantidad =detalle.cantidad ,precio = detalle.precio,
                                                    detalle_id=detalle.detalle_id ,notas =detalle.notas  , tx =detalle.tx,
                                                    fecha_cambio  =detalle.fecha_cambio ,convenio_id  =detalle.convenio_id ,
                                                    grupo_id =detalle.grupo_id, plantilla_id =detalle.plantilla_id ,unidad_id  = 1, 
                                                    usuario_id  = self.request.user.id, ntqx = detalle.ntqx, facturable=facturable,
                                                    
                                                    ))
                
                
            DetalleCirugia.objects.bulk_create(objectos_detalle)
            Presupuesto.objects.filter(id=id_presupuesto_seleccionado).update(
                estatus_id=2,
                usuario_id = self.request.user.id
                )
            Cirugia.objects.filter(id=idHistoria).update(
                estatus_id=2,
                usuario_id = self.request.user.id
                )
            PreIngreso.objects.filter(cirugia_id=idHistoria).update(
                estatus_id=2,
                usuario_id = self.request.user.id
                )
            
            RequisitoIngreso.objects.create(
                cirugia_id = idHistoria,
                informe_med_ingreso = informe_med_ingreso,
                orden_ingreso = orden_ingreso,
                carta_compromiso = carta_compromiso,
                tramite_administrativo = tramite_administrativo,
                examen_preoperatorio = examen_preoperatorio,
                evaluacion_cardio = evaluacion_cardio,
                evaluacion_preanestesica = evaluacion_preanestesica
            )
            
            CuentaxCobrar.objects.filter(presupuesto_id = id_presupuesto_seleccionado).update(
                cirugia_id = idHistoria,
                usuario_id = self.request.user.id,
            )

            return redirect('lista_cirugia') 
        else:
            imagen_paciente = ImagenPhoto.objects.filter(cedula = registros_presupuesto.paciente.cedula).first()
            if imagen_paciente:
                pass
            else:
                imagen_paciente = ImagenPhoto.objects.filter(cedula = 'VU58Image' ).first()
            
            if registros_presupuesto:
                edad_paciente=calcular_edad(registros_presupuesto.paciente.fecha_nac)
                context['telefono_contacto'] = telefono_contacto
                context['persona_contacto'] = persona_contacto
                context['registros_presupuesto'] = registros_presupuesto
                context['edad_paciente'] = edad_paciente
                context['responsable'] = responsable
                context['informe_med_ingreso'] = informe_med_ingreso
                context['orden_ingreso'] = orden_ingreso
                context['carta_compromiso'] = carta_compromiso
                context['tramite_administrativo'] = tramite_administrativo
                context['examen_preoperatorio'] = examen_preoperatorio
                context['evaluacion_cardio'] = evaluacion_cardio
                context['evaluacion_preanestesica'] = evaluacion_preanestesica
                context['medico'] = medico
                context['imagen_paciente'] = imagen_paciente

                if boton_presionado == 'imprimirconsentimiento':
                    fecha_hoy = datetime.now()
                    context['fecha_hoy'] = fecha_hoy
                    context['registros_presupuesto'] = registros_presupuesto
                    return render(request, 'consentimiento.html', context)
                else:
                    return render(request, 'hc1.html', context)
            else:
                return render(request, 'hc1.html')
            
            
def buscar_existe_nota_entrega(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nroDocumento = datos['nroDocumento']
        idProveedor = datos['idProveedor']
        existe = 'false'  
        convertida = NotaEntregaCompra.objects.filter(
            Q(numerodocumento = nroDocumento) & Q(proveedor_compra_id = idProveedor) , Q(cantidad_inventario_actualizado = True) | Q(convertida_factura = True)
        ).first()
       
        #convertida = NotaEntregaCompra.objects.filter(numerodocumento = nroDocumento, proveedor_compra_id = idProveedor,cantidad_inventario_actualizado = True).exclude(convertida_factura__isnull = ).first()
        if convertida:
            existe = 'true'  
        
        data = {'existe' : existe}
        return JsonResponse(data)
    else:
        return JsonResponse({'mensaje': 'Error al GUARDAR Nota de entrega'})

def buscar_existe_factura_inventario(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nroDocumento = datos['nroDocumento']
        idProveedor = datos['idProveedor']
        nroControl = datos['nroControl']
        existe = 'false'  
        convertida = FacturaProveedor.objects.filter(numerodocumento=nroDocumento.strip() ,proveedor_compra_id = idProveedor).exclude(tipo = 'XX').first()
        if not convertida:
            FacturaProveedor.objects.filter(numerocontrol=nroControl.strip() ,proveedor_compra_id = idProveedor).exclude(tipo = 'XX').first()
       
        if convertida:
            existe = 'true'  
        
        data = {'existe' : existe}
        return JsonResponse(data)
    else:
        return JsonResponse({'mensaje': 'Error al GUARDAR Nota de entrega'})
    
    
    
def cambiar_detalle_cortecuenta(request):
    idDetallePresupuestoDelete = request.GET.get('idDetallePresupuestoDelete')
    idDetallePresupuestoDelete = int(idDetallePresupuestoDelete)
    presupuesto=DetallePresupuesto.objects.filter(id=idDetallePresupuestoDelete).first()
    
    presupuesto_id = presupuesto.presupuesto_id
    ambos_hospitalizacion = DetallePresupuesto.objects.filter(presupuesto_id = presupuesto_id, detalle_id__in = [32,33]).count()
    if ambos_hospitalizacion == 2:
        return JsonResponse({'mensaje': 'unautorized'})

    detalle_id = presupuesto.detalle_id
    cirugia = Cirugia.objects.filter(presupuesto_id = presupuesto_id ).first()
    if detalle_id == 32:
        nuevo_detalle = 33
    else:
        nuevo_detalle = 32
    
    precio_nuevo = cantidad_nueva = monto_tope = precio_adicional = 0
    baremo = Baremo.objects.filter(detalle_id = nuevo_detalle, convenio_id = 1).first()
    if baremo and presupuesto and cirugia:
        precio_nuevo = baremo.venta
        cantidad_nueva = baremo.cantidad
        precio_adicional = precio_nuevo
        monto_tope = baremo.topedia
        DetallePresupuesto.objects.create(cantidad=cantidad_nueva,cantidad_usada = cantidad_nueva, precio_usado = precio_nuevo ,precio=0, convenio_id=baremo.convenio_id, detalle_id=nuevo_detalle, grupo_id=baremo.grupo_id, 
                                          plantilla_id=baremo.plantilla_id,presupuesto_id= presupuesto_id,ntqx = baremo.ntqx, usuario_id=request.user.id, unidad_id=baremo.unidad_id,montotope=monto_tope, ) 
        
        DetalleCirugia.objects.create(cantidad=cantidad_nueva,  precio=precio_nuevo, convenio_id=baremo.convenio_id, detalle_id=nuevo_detalle, grupo_id=baremo.grupo_id,montotope=monto_tope, 
                                          plantilla_id=baremo.plantilla_id,cirugia_id=cirugia.id,ntqx = baremo.ntqx, usuario_id=request.user.id, unidad_id=baremo.unidad_id ) 
        
   
    DetallePresupuesto.objects.filter(id=idDetallePresupuestoDelete).update(
        precio_usado = 0,
        cantidad_usada = 0
    )
    if cirugia:
        precio = DetalleCirugia.objects.filter(cirugia_id=cirugia.id, detalle_id = detalle_id ).first()
        if precio:
            precio_menos = precio.precio
        else:
            precio_menos = 0
        
        DetalleCirugia.objects.filter(cirugia_id=cirugia.id, detalle_id = detalle_id ).delete()
        idCirugia = cirugia.id
        LogEliminacion.objects.create(
            descripcion = 'Cambio de item hospitalizacion y ambulatorio en corte de cuenta cirugia: '+str(idCirugia)+ ' paciente:'+str(cirugia.paciente),
            usuario_id = request.user.id
        )      
        ####
        cuentacobrar = CuentaxCobrar.objects.filter(cirugia_id = idCirugia).first()
        saldo_cuenta = 0
        if cuentacobrar:
            monto_cirugia = DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuentacobrar.id, montocobrar__gt = 0).first()
            if monto_cirugia is None:
                monto_total = 0
            else:
                monto_total = (monto_cirugia.montocobrar + Decimal(precio_adicional)) - Decimal(precio_menos)
                DetalleCuentaCobrar.objects.filter(cuentacobrar_id = cuentacobrar.id, montocobrar__gt = 0).update(
                  montocobrar = (F('montocobrar') + Decimal(precio_adicional))   -  Decimal(precio_menos)
                )
                
                
            total_pagado = DetalleCuentaCobrar.objects.filter(
                                        cuentacobrar_id=cuentacobrar.id,
                                        montocobrar__lt=0
                                    ).aggregate(total=Sum('montocobrar'))['total']
            
                                    # Si no hay resultados, total_pagado será None, así que puedes manejarlo si es necesario
            if total_pagado is None:
                total_pagado = 0
            
            
            
            saldo_cuenta = monto_total + total_pagado
                
            
            if cirugia.estatus_id == 8 and saldo_cuenta > 0:
                Cirugia.objects.filter(id=idCirugia).update(
                    estatus_id = 7,
                    usuario_id = request.user.id
                )
            else:
                if cirugia.estatus_id == 7 and saldo_cuenta <= 0:
                    Cirugia.objects.filter(id=idCirugia).update(
                        estatus_id = 8,
                        usuario_id = request.user.id,
                    )
                else:
                    Cirugia.objects.filter(id=idCirugia).update(
                        usuario_id = request.user.id,
                    )
                    
        ###

    return JsonResponse({'mensaje': 'Datos eliminado en corte cuenta correctamente'})
        
        
def detalle_cuentacobrar_eliminar(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        id_detallectacobrar = datos['id_detallectacobrar']
        detalle_ctacobrar = DetalleCuentaCobrar.objects.filter(id=id_detallectacobrar).first()
        if detalle_ctacobrar:
            id_nota_credito = detalle_ctacobrar.notacredito_manual_id
            cuentaxcobrar_id = detalle_ctacobrar.cuentacobrar_id
            transaccion_id = detalle_ctacobrar.transaccion_id
            monto_bs = detalle_ctacobrar.montocobrar
            monto_dl = detalle_ctacobrar.montocobrar_bs
            ami_id = detalle_ctacobrar.cuentacobrar.atencion_inmediata_id
            cirugia_id = detalle_ctacobrar.cuentacobrar.cirugia_id
            preingreso_id = detalle_ctacobrar.cuentacobrar.preingreso_id
            presupuesto_id = detalle_ctacobrar.cuentacobrar.presupuesto_id
            usuario_id = request.user.id
            LogCuentaCobrar.objects.create(
                monto_bs = monto_bs,
                monto_dl = monto_dl,
                ami_id = ami_id,
                cirugia_id = cirugia_id,
                preingreso_id = preingreso_id,
                presupuesto_id = presupuesto_id,
                usuario_id = usuario_id
            )
            NotaCreditoCtaCobrar.objects.filter(id = id_nota_credito).update(
                aplicada = False,
                cuentaxcobrar_aplicada_id = None,
                usuario_id = request.user.id,
                
            )
            transaccion_eliminar = Transaccion.objects.filter(id=transaccion_id).first()
            if transaccion_eliminar:
                NotaCreditoCtaCobrar.objects.filter(id = transaccion_eliminar.notacredito).delete()
                
            Transaccion.objects.filter(id=transaccion_id).delete()
            DetalleCuentaCobrar.objects.filter(id=id_detallectacobrar).delete()
            
            

                        
        return JsonResponse({'mensaje': 'Eliminado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})
    
def refresh_table_baremo_eliminar(request):
    id_eliminar = request.GET.get('id_eliminar')
    detalle = Baremo.objects.filter(id=id_eliminar).first()
    if detalle:
        cirugiaeliminar = DetalleCirugia.objects.filter(detalle_id = detalle.detalle_id).order_by('-cirugia__id')
        cantidad = DetalleCirugia.objects.filter(detalle_id = detalle.detalle_id).count()
        
        
        
    
    html = render_to_string('tabla_baremo_eliminar.html', {
        'cirugiaeliminar': cirugiaeliminar,
    })
    
    # Devolver un JSON con el HTML y el total
    return JsonResponse({'html': html }) 

def eliminar_item_baremo(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idbaremo = datos['idbaremo']
        baremo = Baremo.objects.filter(id=idbaremo).first()
        if baremo:
            detalle_eliminar = baremo.detalle_id
            LogEliminacion.objects.create(
                descripcion = 'Eliminacion de item de baremo :'+str(detalle_eliminar)+' - '+str(baremo.detalle.nombre),
                usuario_id = request.user.id
            )
            DetalleCirugia.objects.filter(detalle_id = detalle_eliminar).delete()
            DetallePresupuesto.objects.filter(detalle_id = detalle_eliminar).delete()
            Baremo.objects.filter(id=idbaremo).delete()
            
        return JsonResponse({'mensaje': 'Creado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})
    
def activar_detalle_item_baremo(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        id_baremo = datos['id_baremo']
        activar = datos['activar']
        baremo = Baremo.objects.filter(id=id_baremo).first()
        if baremo:
            DetalleBaremo.objects.filter(id=baremo.detalle_id).update(
            activar_subbaremo =  activar,
            )
            
        LogEliminacion.objects.create(
                descripcion = 'Activacion de detalle de subbaremos '+str(baremo.detalle_id)+' '+str(baremo.detalle),
                usuario_id = request.user.id
            )
           
            
        return JsonResponse({'mensaje': 'Creado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})
    
    
def item_relacionados_presupuesto_eliminar(request):
    presupuesto_id = request.GET.get('presupuesto_id')
    presupuesto = Presupuesto.objects.filter(id=presupuesto_id).first()
    cirugia = Cirugia.objects.filter(presupuesto_id = presupuesto_id).first()
    transacciones = []
    cuenta_pagar = []
    cuenta_cobrar = []
    consumo = []
    if cirugia:
        numero_historia = cirugia.id
        cuenta_cobrar = CuentaxCobrar.objects.filter(cirugia_id = cirugia.id)
        if not cuenta_cobrar:
            cuenta_cobrar = CuentaxCobrar.objects.filter(atencion_inmediata_id = presupuesto.atencion_inmediata_id)
            
            
        cuenta_pagar = DetalleFacturaProveedor.objects.filter(cirugia_id = cirugia.id)
        if cuenta_cobrar:
            cuenta_cobrar_ids = cuenta_cobrar.values_list('id', flat=True)
            transacciones = Transaccion.objects.filter(cuentacobrar_id__in=cuenta_cobrar_ids )
            
            
        consumo = ConsumoCirugia.objects.filter(cirugia_id = cirugia.id)
    else:
        numero_historia = ''
        if presupuesto.atencion_inmediata:
            consumo = ConsumoCirugia.objects.filter(atencion_inmediata_id = presupuesto.atencion_inmediata_id)
            numero_historia = 'AMI'+str(presupuesto.atencion_inmediata_id).zfill(4)
        
            
    
    html = render_to_string('tabla_relacion_eliminar.html', {
        'cirugia': numero_historia,
        'cuenta_cobrar' : cuenta_cobrar,
        'transacciones' : transacciones,
        'cuenta_pagar' : cuenta_pagar,
        'consumo' : consumo,
    })
    
    # Devolver un JSON con el HTML y el total
    return JsonResponse({'html': html }) 


def cambio_medico(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idCirugia=datos['idCirugia']
        id_medico=datos['id_medico']
            
        Cirugia.objects.filter(id = idCirugia ).update(
            medico_ppal_id = id_medico,
            usuario_id = request.user.id
        )
        return JsonResponse({'mensaje': 'Tratamiento hospital guardado con éxito'})
    
    
    return JsonResponse({'mensaje': 'Error al guardar Tratamiento hospital'})

def cambio_procedimiento_diagnostico(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        idCirugia=datos['idCirugia']
        id_procedimiento=datos['id_procedimiento']
        nombre_procedimiento=datos['nombre_procedimiento']
        nombre_diagnostico=datos['nombre_diagnostico']
            
        Cirugia.objects.filter(id = idCirugia ).update(
            nombre_procedimiento = nombre_procedimiento,
            diagnostico = nombre_diagnostico,
            tipo_procedimiento_id = id_procedimiento,
            usuario_id = request.user.id
        )
        return JsonResponse({'mensaje': 'Tratamiento hospital guardado con éxito'})
    
    
    return JsonResponse({'mensaje': 'Error al guardar Tratamiento hospital'})

@add_group_name_to_context    
class retencion_cuentacobrar(UserPassesTestMixin, TemplateView): 
    
    template_name='retencion_cuentacobrar.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # inicio de borrado luego de correrlo
        
        retenciones = DetalleCuentaCobrar.objects.filter(retencion_id__isnull = False ).order_by('-id')
        total_monto_credito = sum(nc.montocobrar_bs for nc in retenciones)  # Sumar los saldos
        
        context['retenciones'] = retenciones
        context['total_monto_credito'] = total_monto_credito
        
        return context
    
@add_group_name_to_context    
class agregar_nota_credito(UserPassesTestMixin, TemplateView): 
    
    template_name='agregar_nota_credito.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Administracion') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        presupuestos = Presupuesto.objects.filter(estatus_id = 1).order_by('id')
        formapago = FormaPago.objects.all().order_by('nombre')
        bancos = Banco.objects.all().order_by('nombre')
        # inicio de borrado luego de correrlo
        tasa_hoy = CambioDiaBcv(datetime.now())
        bancolocal = BancoLocal.objects.filter(activo = True).order_by('nombrecuenta')
        tasa_hoy = truncate_to_decimals(tasa_hoy, 2)
        fecha_hoy = datetime.now().date()
        
        context['bancos'] = bancos
        context['tasa_hoy'] = tasa_hoy
        context['formapago'] = formapago
        context['fecha_hoy'] = fecha_hoy
        context['bancolocal'] = bancolocal
        context['presupuestos'] = presupuestos
        return context
    
    
def obtener_notascredito(request):
    pagador_id = request.GET.get('pagador_id')
    notascreditocliente = NotaCreditoCtaCobrar.objects.filter(pagador_id=pagador_id).order_by('-fecha_act')
    total_saldo = notascreditocliente.aggregate(
        total=Coalesce(Sum('saldo'), Value(0, output_field=DecimalField()))
        )['total']
    
    html = render_to_string('lista_nota_credito_cliente.html', {
        'notascreditocliente': notascreditocliente,
        'total_saldo':total_saldo,
       
    })
    return JsonResponse({'html': html}) 


def buscar_monedas_notacredito(request):
    formapago = request.GET.get('formapago')
    recepcion_fondos = request.GET.get('recepcion_fondos')
    # Query your database to retrieve the corresponding date
    moneda_fp = FormaPago.objects.filter(id = formapago).first()
    moneda_recepcion_fondos = BancoLocal.objects.filter(id=recepcion_fondos).first()  
    if moneda_fp.moneda_id == moneda_recepcion_fondos.moneda_id:
        monedaIgual = 'true'
    else:
        monedaIgual = 'false'
   
    return JsonResponse({'monedaIgual': monedaIgual})


def aplicar_nota_credito(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        monto_dolares = datos['monto_dolares']
        monto_bolivares = datos['monto_bolivares']
        tasatx = datos['tasatx']
        formapago = datos['formapago']
        recepcion_fondos = datos['recepcion_fondos']
        cedulapagador = datos['cedulapagador']
        nombrepagador = datos['nombrepagador']
        telefonopagador = datos['telefonopagador']
        direccionpagador = datos['direccionpagador']
        desnotacredito = datos['desnotacredito']
        presupuesto_referencia = datos['presupuesto_referencia']
        bancos_origen_fondos = datos['bancos_origen_fondos']
        referencia_pago = datos['referencia_pago']
        fecha_pago = datos['fecha_pago']
        forma_de_pago = FormaPago.objects.filter(id=formapago).first()
        tasatx = tasatx.replace(',','.')
        nombre_banco_origen = ''
        if bancos_origen_fondos:
            origen_fondos = Banco.objects.filter(id=bancos_origen_fondos).first()
            if origen_fondos:
                nombre_banco_origen = origen_fondos.nombre
                
            
        banco_receptor = BancoLocal.objects.filter(id=recepcion_fondos).first()
        if banco_receptor:
            nombre_banco_receptor = banco_receptor.nombrecuenta,
            tipo_moneda = banco_receptor.moneda_id
        else:
            nombre_banco_receptor = 'No hay banco receptor revisar'
            tipo_moneda = 0
        
       
            
        pagador = PagadorUnico.objects.filter(cedula = cedulapagador).first()       
        if pagador:
            pagadorunico_id = pagador.id
            PagadorUnico.objects.filter(id=pagador.id).update(
                nombre = nombrepagador,
                direccion = direccionpagador,
                telefono = telefonopagador
            )
        else:
            pagadorunico = PagadorUnico.objects.create(
                cedula = cedulapagador,
                nombre = nombrepagador,
                direccion = direccionpagador,
                telefono = telefonopagador
            )
            pagadorunico_id = pagadorunico.id
        
        
        
        nota_de_credito = NotaCreditoCtaCobrar.objects.create(
            pagador_id = pagadorunico_id,
            saldo = monto_dolares,
            usuario_id = request.user.id,
            presupuesto_referencia_id = presupuesto_referencia,
            descripcion = desnotacredito,
            tasa = tasatx,
            saldo_bs = monto_bolivares,
            fecha_pago = fecha_pago
            
        )
        
        Pagador.objects.create(
            cedula = cedulapagador,
            nombre = nombrepagador,
            direccion = direccionpagador,
            telefono = telefonopagador,
            notacredito_origen_id = nota_de_credito.id
        )
        
        transaccion_realizada = Transaccion.objects.create(
            monto = monto_bolivares,
            monto_dolar = monto_dolares,
            fechatransaccion = datetime.now(),
            descripcion = desnotacredito,
            referencia = referencia_pago,
            bancolocal_id = recepcion_fondos,
            usuario_id = request.user.id,
            nota = desnotacredito + ' al presupuesto no.: '+ str(presupuesto_referencia),
            tasa_bcv = tasatx,
            mediomoneda_id = formapago,
            notacredito = nota_de_credito.id
        )
        if tipo_moneda == 1:
            nom_moneda = 'Dolares'
            monto_dl = monto_dolares
            monto_bs = 0
        
        if tipo_moneda == 2:
            monto_dl = 0
            monto_bs = monto_bolivares
            nom_moneda = 'Bolivares'
        
        DebitoCredito.objects.create(
            cuenta_origen = nombre_banco_origen,
            cuenta_destino = nombre_banco_receptor,
            medico_proveedor = 'NC / ANTICIPO',
            monto_bolivares = monto_bs,
            monto_dolar = monto_dl,
            tasa_bcv = tasatx,
            movimiento = 'Credito',
            descripcion = desnotacredito,
            referencia = referencia_pago,
            usuario = request.user.username,
            formapago = forma_de_pago.nombre,
            moneda = nom_moneda,
            monto_unico = monto_dolares,
            dolares = monto_dolares,
            transaccion_id = transaccion_realizada.id,
            motivo = desnotacredito,
            notacredito_id = nota_de_credito.id
            
        )
        
        
        return JsonResponse({'mensaje': 'CANTIDAD REAL GUARDADOS EN CONSUMO correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error al GUARDAR CANTIDAD REAL EN CONSUMO datos'})
    
def eliminar_nota_credito(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        id_notacredito = datos['id_notacredito']
        notadecredito = NotaCreditoCtaCobrar.objects.filter(id = id_notacredito).first()
        
        NotaCreditoCtaCobrar.objects.filter(id = id_notacredito).delete()     
        Transaccion.objects.filter(notacredito = id_notacredito).delete()
        
        LogEliminacion.objects.create(
            descripcion = 'Eliminacion de nota de credito de: '+str(notadecredito.saldo),
            usuario_id = request.user.id
        )
        
    return JsonResponse({'mensaje': 'Error al GUARDAR CANTIDAD REAL EN CONSUMO datos'})

@add_group_name_to_context    
class pdf_recibo_nota_credito(TemplateView): 
    template_name='pdf_recibo_nota_credito.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notacredito_id = self.kwargs['pk']
        nombre_paciente = nombre_procedimiento = ''
        notacredito = NotaCreditoCtaCobrar.objects.filter(id=notacredito_id).first()
        if notacredito.presupuesto_referencia:
            nombre_paciente = notacredito.presupuesto_referencia.paciente
            nombre_procedimiento = notacredito.presupuesto_referencia.nombre_procedimiento
            
            
        transaccion = Transaccion.objects.filter(notacredito = notacredito.id).first()
        if not transaccion:
            transaccion = Transaccion.objects.filter(id = notacredito.detallecuentaxcobrar.transaccion_id).first()
            if transaccion.cuentacobrar.cirugia:
                nombre_paciente = transaccion.cuentacobrar.cirugia.paciente
                nombre_procedimiento = transaccion.cuentacobrar.cirugia.nombre_procedimiento
            else:
                nombre_paciente = transaccion.cuentacobrar.atencion_inmediata.paciente
                nombre_procedimiento = transaccion.cuentacobrar.atencion_inmediata.motivo_atencion
        
        fecha_hoy = datetime.now()
        context['fecha_hoy'] = fecha_hoy
        context['notacredito'] = notacredito
        context['transaccion'] = transaccion
        context['nombre_paciente'] = nombre_paciente
        context['nombre_procedimiento'] = nombre_procedimiento
       
        return context
    
    
@add_group_name_to_context    
class consolidado_cxc(UserPassesTestMixin, TemplateView): 
    template_name='consolidado_cxc.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='ConsolidadoCxC')  
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        pagadores = Pagador.objects.filter(detallecuentaxcobrar_id__isnull = False).order_by('cedula')
        # Agrupar por nombre_pagador
        agrupados_pagador = defaultdict(lambda: {'pagado': 0})
        for item in pagadores:
            nombre_pagador = item.cedula.strip() + ' # ' +item.nombre.strip()
            agrupados_pagador[nombre_pagador]['pagado'] += (item.detallecuentaxcobrar.montocobrar * -1)
            
        # Convertir el defaultdict a una lista de diccionarios
        datos_agrupados_pagador = [
            {'nombre_pagador': nombre, 'pagado': datos['pagado'] }
            for nombre, datos in agrupados_pagador.items()
        ]
        
        # Ordenar por total_monto de mayor a menor
        datos_agrupados_pagador = sorted(datos_agrupados_pagador, key=lambda x: x['pagado'], reverse=True)
        
        #NOTAS DE CREDITO
        nota_credito = NotaCreditoCtaCobrar.objects.filter(aplicada = False).order_by('pagador')
        # Agrupar por nombre_pagador
        agrupados_pagador_nc = defaultdict(lambda: {'pendiente': 0})
        total_nc = 0
        for item in nota_credito:
            nombre_pagador_nc = item.pagador.cedula.strip() + ' # ' +item.pagador.nombre.strip()
            agrupados_pagador_nc[nombre_pagador_nc]['pendiente'] += (item.saldo)
            total_nc += (item.saldo)
            
        datos_agrupados_nc = [
            {'nombre_pagador_nc': nombre, 'pendiente': datos['pendiente'] }
            for nombre, datos in agrupados_pagador_nc.items()
        ]
        
        #FIN NOTAS DE CREDITO
        
        #Cirugias Pendiente de Cobro con saldo mayor a 0
        hoy = datetime.now().date()
        montos = {
            '30_dias': 0,
            '60_dias': 0,
            '90_dias': 0,
            '120_dias': 0,
        }
        
        #Fin Cirugias Pendiente de Cobro con saldo mayor a 0
        
        
        cirugia = CuentaxCobrar.objects.filter(cirugia_id__isnull = False).order_by('cirugia__nombre_procedimiento')
        # Agrupar por nombre_procedimiento
        agrupados = defaultdict(lambda: {'total_monto': 0, 'cantidad': 0, 'dias':0, 'horasqx':0})
        for item in cirugia:
            nombre_procedimiento = item.cirugia.nombre_procedimiento.strip()
            agrupados[nombre_procedimiento]['total_monto'] += item.total_monto
            agrupados[nombre_procedimiento]['cantidad'] += 1  # O usa item.cantidad si tienes esa propiedad
            agrupados[nombre_procedimiento]['dias'] += item.cirugia.dias_hospitalizacion
            agrupados[nombre_procedimiento]['horasqx'] += item.cirugia.horas_qx
            
            
        # Convertir el defaultdict a una lista de diccionarios
        datos_agrupados = [
            {'nombre_procedimiento': nombre, 'total_monto': datos['total_monto'], 'cantidad': datos['cantidad'], 'dias': datos['dias'],'horasqx': datos['horasqx'] }
            for nombre, datos in agrupados.items()
        ]
        
        # Ordenar por total_monto de mayor a menor
        #datos_agrupados = sorted(datos_agrupados, key=lambda x: x['total_monto'], reverse=True)
        monto_pagado_cirugia = 0
        monto_total_cirugia = 0
        suma_total_cobrado = 0
        monto_pendiente = 0

        cuentas_por_cobrar_vigentes = CuentaxCobrar.objects.all().exclude(atencion_inmediata__isnull = True, cirugia__isnull = True)
        cantidad_cirugias = cantidad_amis = total_pagado_cirugias = total_pagado_amis = total_vendido_cirugias = total_vendido_amis = 0
        for cuenta in cuentas_por_cobrar_vigentes:
            monto_total_cirugia += cuenta.total_monto
            if (cuenta.total_monto_pagado * -1) > cuenta.total_monto:
                monto_pagado_cirugia = cuenta.total_monto
            else:
                monto_pagado_cirugia = (cuenta.total_monto_pagado * -1)
                
                
            if cuenta.cirugia:
                dias_pendientes = (hoy - cuenta.cirugia.fecha_procedimiento).days
                cantidad_cirugias += 1
                total_pagado_cirugias += monto_pagado_cirugia
                total_vendido_cirugias += cuenta.total_monto
            else:
                cantidad_amis += 1
                total_pagado_amis += monto_pagado_cirugia
                total_vendido_amis += cuenta.total_monto
                dias_pendientes = (hoy - cuenta.atencion_inmediata.fecha_procedimiento).days
                
                
            
                
            suma_total_cobrado += monto_pagado_cirugia
            monto_pendiente = cuenta.total_monto - monto_pagado_cirugia
            if dias_pendientes <= 30:
                montos['30_dias'] += monto_pendiente
            elif dias_pendientes <= 60:
                montos['60_dias'] += monto_pendiente
            elif dias_pendientes <= 90:
                montos['90_dias'] += monto_pendiente
            elif dias_pendientes > 90:
                montos['120_dias'] += monto_pendiente
                
        
   
        total_montocobrar_usd = DetalleCuentaCobrar.objects.filter(
                                montocobrar__lt=0,
                                transaccion__mediomoneda__moneda_id=1
                            ).aggregate(
                                total=Coalesce(Sum('montocobrar', output_field=DecimalField()), Decimal('0.00'))
                            )['total']
                            
        total_montocobrar_bs = DetalleCuentaCobrar.objects.filter(
                                montocobrar_bs__lt=0,
                                transaccion__mediomoneda__moneda_id=2
                            ).aggregate(
                                total=Coalesce(Sum('montocobrar_bs', output_field=DecimalField()), Decimal('0.00'))
                            )['total']
                            
        # RUTINA DEL GRAFICO DE COBRADO BRUTO X MES
        class DateFormat(Func):
            function = 'DATE_FORMAT'
            template = "%(function)s(%(expressions)s)"
            output_field = CharField()
        
        detalles = (
            DetalleCuentaCobrar.objects
            .filter(
                montocobrar__lt=0,
                fecha_act__isnull=False,
                cuentacobrar__isnull=False
            )
            .annotate(ym=DateFormat(F('fecha_act'), Value('%m-%Y')))
            .values('ym')
            .annotate(total_pagado=Sum('montocobrar'))
            .order_by('ym')
        )

        fechas = []
        montos_pagados = []

        for detalle in detalles:
            fechas.append(detalle['ym'])  # ya viene "YYYY-MM"
            montos_pagados.append(float(detalle['total_pagado']*-1))
            #print(fechas[-1], montos_pagados[-1])
            
       
         # FIN DE RUTINA DEL GRAFICO COBRO X MES
         
         # RUTINA DEL GRAFICO DE COBRADO POR BANCO
        
        detalles = (
            DetalleCuentaCobrar.objects
            .filter(
                montocobrar__lt=0,
                fecha_act__isnull=False,
                cuentacobrar__isnull=False,
                destino_pago__isnull=False,
            )
            .values('destino_pago__alias', 'destino_pago__moneda_id')
            .annotate(
                total_pagado=Sum(
                    Case(
                        When(destino_pago__moneda_id=1, then=F('montocobrar')),
                        When(destino_pago__moneda_id=2, then=F('montocobrar_bs')),
                        default=0,
                        output_field=DecimalField()
                    )
                )
            )
            .order_by('destino_pago__alias')
        )

        destinos = []
        montos_pagados_destino = []
        montos_pagados_destino = []
        monedas = []  

        for detalle in detalles:
            destinos.append(detalle['destino_pago__alias'])
            montos_pagados_destino.append(float(detalle['total_pagado'] * -1))
            monedas.append(detalle['destino_pago__moneda_id'])
      
       
         # FIN DE RUTINA DEL GRAFICO COBRO X BANCO
         
        context['fechas'] = fechas
        context['montos_pagados'] = montos_pagados 
        context['destinos'] = destinos
        context['montos_pagados_destino'] = montos_pagados_destino 
        context['monedas'] = monedas
        context['montos'] = montos
        context['total_nc'] = total_nc
        context['total_montocobrar_usd'] = total_montocobrar_usd*(-1)
        context['total_montocobrar_bs'] = total_montocobrar_bs*(-1)
        context['cirugia'] = datos_agrupados
        context['pagador_frecuente'] = datos_agrupados_pagador
        context['nota_credito_pendiente'] = datos_agrupados_nc
        context['suma_total_cobranza'] = monto_total_cirugia
        context['suma_total_cobrado'] = suma_total_cobrado 
        context['total_por_cobrar'] = monto_total_cirugia - suma_total_cobrado
        
        context['total_pagado_cirugias'] = total_pagado_cirugias 
        context['total_pagado_amis'] = total_pagado_amis 
        
        context['total_vendido_cirugias'] = total_vendido_cirugias 
        context['total_vendido_amis'] = total_vendido_amis
        
        context['cantidad_cirugias'] = cantidad_cirugias 
        context['cantidad_amis'] = cantidad_amis
        
        return context
    
    
def agregar_detalle_item_baremito(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        id_cirugia = datos['id_cirugia']
        id_detalle = datos['id_detalle']
        nombre_baremito = datos['nombre_baremito']
        id_detallepresupuesto = datos['id_detallepresupuesto']
        
        
        nombre_existe = NombreSubBaremo.objects.filter(nombre = nombre_baremito).first()
        if nombre_existe:
            id_nombre_baremito = nombre_existe.id
        else:
            nombre_nuevo = NombreSubBaremo.objects.create(
                nombre = nombre_baremito
            )
            id_nombre_baremito = nombre_nuevo.id

        
        subbaremo_existe = SubBaremo.objects.filter(nombre_subbaremo_id = id_nombre_baremito, detalle_id = id_detalle).first()
        if subbaremo_existe:
            subbaremo_id = subbaremo_existe.id
        else:
            subbaremo_nuevo = SubBaremo.objects.create(
                nombre_subbaremo_id = id_nombre_baremito,
                usuario_id = request.user.id,
                detalle_id = id_detalle
            )
            subbaremo_id = subbaremo_nuevo.id
        
        DetalleSubBaremoConsumo.objects.create(
            cirugia_id = id_cirugia,
            subbaremo_id = subbaremo_id,
            cantidad = 1,
            usuario_id = request.user.id,
            detalle_id = id_detalle,
            detalle_presupuesto_id = id_detallepresupuesto
            )
        
            
        LogEliminacion.objects.create(
                descripcion = 'Agregacion de nuevo baremito '+str(id_detalle)+' '+str(nombre_baremito),
                usuario_id = request.user.id
            )
           
            
        return JsonResponse({'mensaje': 'Creado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})
    
    
def refresh_table_baremitos(request):
    id_cirugia = request.GET.get('id_cirugia')
    id_detalle = request.GET.get('id_detalle')
    modo = request.GET.get('modo')
    detalle_presupuesto = request.GET.get('detalle_presupuesto')
    detallesubbaremocirugia = DetalleSubBaremoConsumo.objects.filter(cirugia_id = id_cirugia, detalle_id = id_detalle).order_by('subbaremo__nombre_subbaremo')
    
    if not detallesubbaremocirugia and modo == 'N':
        pasarTodosBaremito(id_cirugia, id_detalle, request.user.id, detalle_presupuesto )
        detallesubbaremocirugia = DetalleSubBaremoConsumo.objects.filter(cirugia_id = id_cirugia, detalle_id = id_detalle).order_by('subbaremo__nombre_subbaremo')
    
    html = render_to_string('tabla_detalle_baremitos.html', {
        'detallesubbaremocirugia': detallesubbaremocirugia,
    })
    
    # Devolver un JSON con el HTML y el total
    return JsonResponse({'html': html }) 

def eliminar_detalle_item_baremito(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        id_baremito_consumo = datos['id_baremito_consumo']
        subdetalle_eliminar = DetalleSubBaremoConsumo.objects.filter(id=id_baremito_consumo).first()
        if subdetalle_eliminar:        
            LogEliminacion.objects.create(
                    descripcion = 'Eliminacion de SubBaremito '+str(subdetalle_eliminar.subbaremo_id)+' '+str(subdetalle_eliminar.subbaremo),
                    usuario_id = request.user.id
                )
            DetalleSubBaremoConsumo.objects.filter(id=id_baremito_consumo).delete()
            
        return JsonResponse({'mensaje': 'Eliminado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})
    
def refresh_select_baremo_preingreso(request):
    atencion_inmediata_id = request.GET.get('atencionInmediataId')
    
    #atencion_inmediata = PreIngreso.objects.filter(id=atencion_inmediata_id).first()
    destino_farmacos_mmq = DetallePresupuesto.objects.filter(preingreso_id=atencion_inmediata_id, montotope__gt=0)
    if destino_farmacos_mmq:
        muestra_seleccion = 'true'
    else:
        muestra_seleccion = 'false'
    
       
    return render(request, 'select_baremitos_destino_farmaco.html', {'destino_farmacos_mmq': destino_farmacos_mmq, 'muestra_seleccion':muestra_seleccion })  

def agregar_a_consumo_preanestesia_con_detallepresupuesto_en_consumo(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        inventario_id = datos['inventario_id']
        cantidad_aplicar = datos['cantidad_aplicar']
        idAtencion = datos['idAtencion']
        depositoId = datos['depositoId']
        cirugiaId = datos['cirugiaId']
        id_select_destino = datos['id_select_destino']
        depositoubicacion = DepositoUso.objects.filter(inventario_id = inventario_id, deposito_id = depositoId).first()
        if depositoubicacion:
            if  Decimal(cantidad_aplicar) <= Decimal(depositoubicacion.existenciaUnd):
                producto = Inventario.objects.filter(id=inventario_id).first()
                precio_costo_unitario = precio_costo_producto_inventario(inventario_id)
                consumonuevo = ConsumoCirugia.objects.create(
                    preingreso_id = idAtencion,
                    cantidad_real_usada = cantidad_aplicar,
                    cantidad_uso = cantidad_aplicar,
                    venta = 0,
                    nota = 'PRE-INGRESO CONSULTA PREANESTESIA',
                    inventario_id = inventario_id,
                    consumo_id = 8,
                    usuario_id = request.user.id,
                    hora_uso = datetime.now().time(),
                    precio_unitario = producto.monto_venta,
                    deposito_id = depositoId,
                    cirugia_id = cirugiaId,
                    detalle_presupuesto_id = id_select_destino,
                    precio_costo_unitario  = precio_costo_unitario 
                )
                InventarioDescarga.objects.create(
                    cantidad = cantidad_aplicar,
                    nota = 'PRE-INGRESO CONSULTA PREANESTESIA',
                    deposito_id = depositoId,
                    inventario_id = inventario_id,
                    usuario_id = request.user.id,
                    tipodescarga_id = 18,
                    preingreso_id = idAtencion,
                    persona_id = request.user.id,
                    consumocirugia_id = consumonuevo.id,
                    cirugia_id = cirugiaId
                )
                
                return JsonResponse({'mensaje': 'Creado Consumo'})
            else:
                return JsonResponse({'mensaje': 'No dispone de cantidad en existencia'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8048 View.py'})
    
def buscar_tasa_bcv_nc(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nfechaCambio = datos['nfechaCambio']
        
        tasa_tx = CambioBcv.objects.filter(fecha_cambio=nfechaCambio).first()
        tasa_del_dia = 0
        if tasa_tx:
            monto_cambio_congelado = truncate_to_decimals(tasa_tx.cambio, 2)
            tasa_del_dia = monto_cambio_congelado
            
    return JsonResponse({
                'congelar_cambio': tasa_del_dia,
            })
    

def buscar_tasa_bcv_cxp(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nfechaCambio = datos['nfechaCambio']
        
        tasa_tx = CambioBcv.objects.filter(fecha_cambio=nfechaCambio).first()
        tasa_del_dia = 0
        if tasa_tx:
            monto_cambio_congelado = tasa_tx.cambio
            tasa_del_dia = monto_cambio_congelado
            
    return JsonResponse({
                'congelar_cambio': tasa_del_dia,
            })
    
    
def pasar_medico_a_servicio(request):
    id_detalle_presupuesto = request.GET.get('id_detalle_presupuesto')
    id_cirugia = request.GET.get('id_cirugia')
    new_servicio_baremo = request.GET.get('new_servicio_baremo')
    cirugia = Cirugia.objects.filter(id = id_cirugia).first()
    if cirugia:
        LogEliminacion.objects.create(
            descripcion = 'Cambio de medico a servicio en corte de cuenta de la cirugia:'+str(id_cirugia),
            usuario_id = request.user.id
        )
        
        detalle_quitar = DetallePresupuesto.objects.filter(id=id_detalle_presupuesto).first()
        detalle_quitar_cirugia = DetalleCirugia.objects.filter(cirugia_id = cirugia.id, detalle_id = detalle_quitar.detalle_id ).first()
        if detalle_quitar_cirugia.pagado:
            return JsonResponse({'precio': 0, 'pagado':1})
        
        if detalle_quitar:
            precio_agregar = detalle_quitar.precio_usado
            print('a variar:',precio_agregar )
            baremo_new = Baremo.objects.filter(id = new_servicio_baremo ).first()
            if baremo_new:
                detalle_nuevo = DetallePresupuesto.objects.filter(grupo_id = baremo_new.grupo_id, detalle_id = baremo_new.detalle_id, presupuesto_id = cirugia.presupuesto_id).first()
                detalle_nuevo_cirugia = DetalleCirugia.objects.filter(grupo_id = baremo_new.grupo_id, detalle_id = baremo_new.detalle_id, cirugia_id = cirugia.id).first()
                if detalle_nuevo:
                    DetallePresupuesto.objects.filter(id = detalle_nuevo.id).update(
                        #precio = F('precio')+precio_agregar,
                        precio_usado =  F('precio_usado')+precio_agregar,
                        usuario_id = request.user.id
                    )
                    detalle_nuevo_presupuesto_id = detalle_nuevo.id
                else:
                    detalle_nuevo_presupuesto = DetallePresupuesto.objects.create(
                        cantidad = detalle_quitar.cantidad,
                        precio = 0,
                        notas = 'Traslado de servicio',
                        fecha_cambio = detalle_quitar.fecha_cambio,
                        tx = detalle_quitar.tx,
                        convenio_id = baremo_new.convenio_id,
                        detalle_id = baremo_new.detalle_id,
                        grupo_id = baremo_new.grupo_id,
                        plantilla_id = baremo_new.plantilla_id,
                        unidad_id = baremo_new.unidad_id,
                        usuario_id = request.user.id,
                        presupuesto_id = cirugia.presupuesto_id,
                        cantidad_usada =  baremo_new.cantidad,
                        precio_usado =  precio_agregar,
                        montotope = baremo_new.topedia,
                        baremo_id = baremo_new.id,
                    )
                    detalle_nuevo_presupuesto_id = detalle_nuevo_presupuesto.id
                    
                if detalle_nuevo_cirugia:
                    DetalleCirugia.objects.filter(id = detalle_nuevo_cirugia.id).update(
                        precio = F('precio')+precio_agregar,
                        usuario_id = request.user.id,
                        manual = True
                    )
                else:
                    DetalleCirugia.objects.create(
                        cantidad = detalle_quitar.cantidad,
                        precio = precio_agregar,
                        notas = 'Traslado de servicio',
                        fecha_cambio = detalle_quitar.fecha_cambio,
                        tx = detalle_quitar.tx,
                        convenio_id = baremo_new.convenio_id,
                        detalle_id = baremo_new.detalle_id,
                        grupo_id = baremo_new.grupo_id,
                        plantilla_id = baremo_new.plantilla_id,
                        unidad_id = baremo_new.unidad_id,
                        usuario_id = request.user.id,
                        cirugia_id = cirugia.id,
                        montotope = baremo_new.topedia,
                        facturable = True,
                        manual = True
                    )
                
                NotaQuirurgica.objects.filter(participante_id = detalle_quitar_cirugia.detalle_id, cirugia_id = cirugia.id).update(
                    detallepresupuesto_id = detalle_nuevo_presupuesto_id,
                    pagoeliminado = True,
                    pagado = True,
                    usuario_id = request.user.id
                )
                
                #DetallePresupuesto.objects.filter(id=detalle_quitar.id).delete()
                DetallePresupuesto.objects.filter(id=detalle_quitar.id).update(
                    precio_usado = 0,
                    cantidad_usada = 0,
                    usuario_id = request.user.id
                )
                DetalleCirugia.objects.filter(id=detalle_quitar_cirugia.id).delete()
                    
                
    return JsonResponse({'precio': 0, 'pagado':0})


def refresh_table_cirugia_pendiente(request):
    dias = int(request.GET.get('parametro1', 0))
    hoy = timezone.now().date()
    # Subquery para calcular el total a cobrar
    total_cobrar_subquery = DetalleCuentaCobrar.objects.filter(
                cuentacobrar_id=OuterRef('pk')
            ).values('cuentacobrar_id').annotate(total=Sum('montocobrar')).values('total')
    # Filtrar cuentas por cobrar vigentes y calcular total_cobrar_monto
    cuentas_por_cobrar_vigentes = CuentaxCobrar.objects.annotate(
                total_cobrar_monto_pendiente=Subquery(total_cobrar_subquery)
            ).exclude(
                atencion_inmediata__isnull=True, cirugia__isnull=True
            ).filter(total_cobrar_monto_pendiente__gt=0)
    # Clasificar cuentas por días pendientes
    ids_filtrados = []
    for cuenta in cuentas_por_cobrar_vigentes:
        if cuenta.cirugia:
            dias_pendientes = (hoy - cuenta.cirugia.fecha_procedimiento).days
        else:
            dias_pendientes = (hoy - cuenta.atencion_inmediata.fecha_procedimiento).days
        if (dias == 30 and dias_pendientes <= 30) or \
           (dias == 60 and 30 < dias_pendientes <= 60) or \
           (dias == 90 and 60 < dias_pendientes <= 90) or \
           (dias == 120 and dias_pendientes > 90):
            ids_filtrados.append(cuenta.id)
    # Cargar las cuentas filtradas
    cuentas_por_cobrar_vigentes = CuentaxCobrar.objects.filter(id__in=ids_filtrados)
 
    
    html = render_to_string('cirugias_cxc.html', {
        'cuentas_por_cobrar_vigentes': cuentas_por_cobrar_vigentes,
    })
    
    return JsonResponse({'html': html, 'total': 0}) 

def refresh_table_cirugia_pagador_frecuente(request):
    cedula = request.GET.get('parametro1', '')
    
    cuentas_por_cobrar_pagador_frecuente = Pagador.objects.filter(cedula = cedula, detallecuentaxcobrar__isnull = False )
    
    html = render_to_string('cirugias_cxc_pagador_frecuente.html', {
        'cuentas_por_cobrar_pagador_frecuente': cuentas_por_cobrar_pagador_frecuente,
    })
    
    return JsonResponse({'html': html, 'total': 0}) 


def refresh_table_cirugia_pagador_notacredito(request):
    cedula = request.GET.get('parametro1', '')
    notascreditocliente = NotaCreditoCtaCobrar.objects.filter(pagador__cedula = cedula )
    html = render_to_string('lista_nota_credito_cliente.html', {
        'notascreditocliente': notascreditocliente,
    })
    
    return JsonResponse({'html': html, 'total': 0}) 

def refresh_table_cirugia_pagador_notacredito_seleccion(request):
    cedula = request.GET.get('parametro1', '')
    notascreditocliente = NotaCreditoCtaCobrar.objects.filter(pagador__cedula = cedula, aplicada = False )
    html = render_to_string('notacredito_pendiente_seleccion.html', {
        'notascreditocliente': notascreditocliente,
    })
    
    return JsonResponse({'html': html, 'total': 0}) 

def procesar_ncr_seleccionada(request):
    if request.method == "POST":
        data = json.loads(request.body)
        seleccionados = data.get("datos", [])

        # Aquí puedes procesar los seleccionados
        # Ejemplo: recorrerlos e imprimir en consola
        total_monto_aplicar = 0
        notas_credito_id = ''
        pagador_id = None
        # Ordenar de mayor a menor por saldo
        seleccionados_ordenados = sorted(seleccionados, key=lambda x: x['saldo'], reverse=True)
        tasa_hoy = CambioDiaBcv(datetime.now())
        
        for fila in seleccionados_ordenados:
            cuentacobrar_id = fila["cuentacobrar_id"]
            notacredito_aplicar = NotaCreditoCtaCobrar.objects.filter(id = fila["id"]).first()
            cedula_pagador = ''
            if notacredito_aplicar:
                cedula_pagador = notacredito_aplicar.pagador.cedula
                pagador_id = notacredito_aplicar.pagador_id
                notas_credito_id = notas_credito_id + str(fila["id"]) + '/'
                monto_nota_credito = notacredito_aplicar.saldo
                
                NotaCreditoCtaCobrar.objects.filter(id=notacredito_aplicar.id).update(
                            usuario_id = request.user.id,
                            cuentaxcobrar_aplicada_id = cuentacobrar_id, 
                            aplicada = True,
                        )
                
                transaccion = Transaccion.objects.filter(notacredito = notacredito_aplicar.id).first()
                transaccion_id = None
                if transaccion:
                    transaccion_id = transaccion.id
                    
                deuda_pendiente = CuentaxCobrar.objects.filter(id= fila["cuentacobrar_id"]).first()
                if deuda_pendiente.cirugia:
                    numero_historia =  deuda_pendiente.cirugia_id
                else:
                    numero_historia = deuda_pendiente.atencion_inmediata.codigo
                    
                
                monto_a_acreditar = deuda_pendiente.total_cobrar_monto - monto_nota_credito
                nueva_nc = 0
                if monto_a_acreditar < 0:
                    nueva_nc = float(monto_a_acreditar) * -1.00
                    monto_a_acreditar = (deuda_pendiente.total_cobrar_monto)
                else:
                    if monto_a_acreditar >= 0:
                        monto_a_acreditar = (monto_nota_credito)
                        
                        
                detalle_nuevo = DetalleCuentaCobrar.objects.create(
                    montocobrar = float(monto_a_acreditar) * -1.00 ,
                    descripcion = 'PAGO CON NOTA DE CREDITO No.: '+str(notacredito_aplicar.id) + ' de monto: '+str(monto_nota_credito) + ' a cirugia/AMI :'+ str(numero_historia),
                    cuentacobrar_id = cuentacobrar_id,
                    montocobrar_bs = (float(monto_a_acreditar) * float(tasa_hoy))*-1.00,
                    tasa_bcv = tasa_hoy,
                    notacredito = True,
                    transaccion_id  = transaccion_id
                )
                
                Pagador.objects.filter(cedula=cedula_pagador, notacredito_origen_id = notacredito_aplicar.id ).update(
                    detallecuentaxcobrar_id = detalle_nuevo.id
                )
                
                
                if nueva_nc > 0 :
                    detalle_nuevo_nc = DetalleCuentaCobrar.objects.create(
                        montocobrar = float(nueva_nc) * -1.00 ,
                        descripcion = 'NOTA CREDITO A FAVOR DE PAGADOR: No. Cirugia/AMI :'+ str(numero_historia),
                        cuentacobrar_id = cuentacobrar_id,
                        montocobrar_bs = (float(nueva_nc) * float(tasa_hoy))*-1.00,
                        tasa_bcv = tasa_hoy,
                        notacredito = True,
                        transaccion_id = transaccion_id
                        ) 
                    NotaCreditoCtaCobrar.objects.create(
                            saldo = nueva_nc,
                            aplicada = False,
                            detallecuentaxcobrar_id = detalle_nuevo_nc.id, 
                            usuario_id = request.user.id,
                            pagador_id = pagador_id,
                            descripcion = 'Auto Generada por saldo al aplicar las notas de credito: cirugia/AMI'+str(numero_historia),
                            fechatasa = datetime.now().date(),
                            saldo_bs = nueva_nc * float(tasa_hoy),
                            tasa = tasa_hoy,
                            fecha_pago = datetime.now(),
                            autogenerada = True,
                        )
                    Pagador.objects.filter(cedula=cedula_pagador, notacredito_origen_id = notacredito_aplicar.id ).update(
                        detallecuentaxcobrar_id = detalle_nuevo_nc.id
                    )
                
            
        
        # Devolver respuesta al frontend
        return JsonResponse({"status": "ok", "procesados": len(seleccionados)})

    return JsonResponse({"status": "error", "msg": "Método no permitido"}, status=405)



def grafico_barras(request):
    # Obtener la suma del total_monto_pagado por fecha
    #fecha_limite = timezone.now().date() - timedelta(days=30)
    #detalles = DetalleCuentaCobrar.objects.filter(fecha_act__gte=fecha_limite, montocobrar__lt = 0).annotate(total_pagado=Sum('montocobrar')).order_by('fecha_act')
    
    
    
    class DateFormat(Func):
        function = 'DATE_FORMAT'
        template = "%(function)s(%(expressions)s)"
        output_field = CharField()
    
    detalles = (
        DetalleCuentaCobrar.objects
        .filter(
            montocobrar__lt=0,
            fecha_act__isnull=False
        )
        .annotate(ym=DateFormat(F('fecha_act'), Value('%m-%Y')))
        .values('ym')
        .annotate(total_pagado=Sum('montocobrar'))
        .order_by('ym')
    )

    fechas = []
    montos_pagados = []

    for detalle in detalles:
        fechas.append(detalle['ym'])  # ya viene "YYYY-MM"
        montos_pagados.append(float(detalle['total_pagado']*-1))
        print(fechas[-1], montos_pagados[-1])
        
     
    context = {
        'fechas': fechas,
        'montos_pagados': montos_pagados,
    }
    
    return render(request, 'grafico_barras.html', context)


""" def normalizar(texto):
    texto = str(texto).lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto = re.sub(r'\b(de|para|con|talla|el|la|los|las)\b', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

# Función para verificar si hay al menos una palabra en común
def tiene_palabra_comun(texto1, texto2):
    palabras1 = set(texto1.split())
    palabras2 = set(texto2.split())
    return len(palabras1 & palabras2) > 0

def buscar_coincidencias(request):
    path_anterior = 'C:/Sistema Antiguo U58 BD/hoja_anterior.xlsx'
    path_actual = 'C:/Sistema Antiguo U58 BD/hoja_actual.xlsx'

    hoja_anterior = pd.read_excel(path_anterior)
    hoja_actual = pd.read_excel(path_actual)

    resultados = []
    UMBRAL = 70  # porcentaje mínimo de similitud aceptada

    for _, row in hoja_anterior.iterrows():
        desc_anterior = normalizar(row["descripcion"])
        codigo_anterior = row["codigo"]

        opciones = []
        for _, r2 in hoja_actual.iterrows():
            opciones.append((r2["codigo"], normalizar(r2["descripcion"])))
            if pd.notna(r2["descripcion_comercial"]):
                opciones.append((r2["codigo"], normalizar(r2["descripcion_comercial"])))

        mejor_match = process.extractOne(
            desc_anterior,
            [op[1] for op in opciones],
            scorer=fuzz.token_sort_ratio
        )

        if mejor_match:
            mejor_desc = mejor_match[0]
            score = mejor_match[1]
            codigo_match = next(c for c, d in opciones if d == mejor_desc)

            # Validar por score o por palabra en común
            if score >= UMBRAL or tiene_palabra_comun(desc_anterior, mejor_desc):
                resultados.append({
                    "codigo_anterior": codigo_anterior,
                    "codigo_actual": codigo_match,
                    "descripcion_anterior": row["descripcion"],  # original
                    "descripcion_actual": mejor_desc,
                    "coincidencia": score
                })
            else:
                resultados.append({
                    "codigo_anterior": codigo_anterior,
                    "codigo_actual": None,
                    "descripcion_anterior": row["descripcion"],
                    "descripcion_actual": "SIN COINCIDENCIA",
                    "coincidencia": 0
                })
        else:
            resultados.append({
                "codigo_anterior": codigo_anterior,
                "codigo_actual": None,
                "descripcion_anterior": row["descripcion"],
                "descripcion_actual": "SIN COINCIDENCIA",
                "coincidencia": 0
            })

    df_resultado = pd.DataFrame(resultados)
    output_path = 'C:/Sistema Antiguo U58 BD/resultados.xlsx'
    df_resultado.to_excel(output_path, index=False)

    return HttpResponse(f"Reporte generado en: {output_path}", status=200) """
    
def desactivar_medio_pago_proveedor(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        id_mediopago = datos['id_mediopago']
        FormaPagoProveedor.objects.filter(id = id_mediopago).update(
            activo = False,
            usuario_id = request.user.id
        )
            
        return JsonResponse({'mensaje': 'Creado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})
    
@add_group_name_to_context    
class recibo_pago_proveedor(TemplateView): 
    template_name='recibo_pago_proveedor.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        abono_id = self.kwargs['pk']
        abono = AbonoCuentaPagar.objects.filter(id = abono_id).first()
        pagomultiplefactura = TransaccionFacturaMultiple.objects.filter(abono_id = abono_id )
        context['abono'] = abono
        context['pagomultiplefactura'] = pagomultiplefactura
        
        
        return context
    
@add_group_name_to_context    
class estado_cuenta_compra(TemplateView): 
    template_name='estado_cuenta_compra.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        factura_id = self.kwargs['pk']
        factura = FacturaProveedor.objects.filter(id = factura_id).first()
        #abonos = AbonoCuentaPagar.objects.filter(factura_id = factura_id)
        abonos = AbonoCuentaPagar.objects.filter(
            Q(factura_id=factura_id) |
            Q(
                id__in=Subquery(
                    TransaccionFacturaMultiple.objects.filter(
                        factura_id=factura_id
                    ).values('abono_id')
                )
            )
        )

        total_pagado_dl = AbonoCuentaPagar.total_montopago_dl(factura_id)
        total_pagado_bs = AbonoCuentaPagar.total_montopago_bs(factura_id)


        abonos_total = AbonoCuentaPagar.objects.filter(Q(factura_id=factura_id) |
            Q(
                id__in=Subquery(
                    TransaccionFacturaMultiple.objects.filter(
                        factura_id=factura_id
                    ).values('abono_id')
                )
            )).aggregate(total=Sum('montopago_bs'))['total'] or 0
        
        abonos_ids = abonos.values_list('transaccion_id', flat=True)

        pago_factura_multiple = TransaccionFacturaMultiple.objects.filter(factura_id = factura_id ).exists()
        pagomultiplefactura = (
            TransaccionFacturaMultiple.objects
            .filter(transaccion_id__in=abonos_ids)
            .values('factura_id', 'factura__fecha_entrega', 'factura__numerodocumento', 'factura__numerocontrol')
            .distinct()
            .order_by('factura_id')
        )
        
        saldo_actual = (factura.total_operacion_bs - abonos_total)
        if saldo_actual < 0 and pago_factura_multiple:
            saldo_actual = 0 

        context['abonos'] = abonos
        context['factura'] = factura
        context['abonos_total'] = abonos_total
        context['saldo_actual'] = saldo_actual
        context['pagomultiplefactura'] = pagomultiplefactura
        
        return context
    
    
def cambiar_nombre_tipo_proveedor(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        id_tipoproveedor = datos['id_tipoproveedor']
        nombrenuevo = datos['nombrenuevo']
        TipoProveedor.objects.filter(id=id_tipoproveedor).update(
            descripcion = nombrenuevo
        )
   
        
        return JsonResponse({'mensaje': 'Creado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})
    

@add_group_name_to_context   
class link_baremo( UserPassesTestMixin,TemplateView):
    template_name = 'link_baremos.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='SuperAdministracion')  
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        detalles = DetalleBaremo.objects.all().order_by('nombre')

        context['baremos'] = detalles
        return context

    """ def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        habitacion = self.request.POST.get('habitacion')
        descripcion = self.request.POST.get('descripcion')
        if habitacion:
            habitaciones = Habitacion.objects.filter(habitacion=habitacion).first()
            if not habitaciones:
                Habitacion.objects.create(
                    habitacion=habitacion,
                    nota=descripcion
                )

        habitaciones = Habitacion.objects.all().order_by('habitacion')
        context['habitaciones']=habitaciones
        return redirect('create_rooms' ) """
    
def vincular_baremo(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        detalle_vincular = datos['detalle_vincular']
        baremo_principal = datos['baremo_principal']
        baremo = BaremoVinculado.objects.filter(detalle_principal_id = baremo_principal, detalle_baremo_id = detalle_vincular ).first()
        if not baremo:
            BaremoVinculado.objects.create(
                detalle_principal_id = baremo_principal,
                detalle_baremo_id = detalle_vincular,
                usuario_id = request.user.id
            )
            
            
        return JsonResponse({'mensaje': 'Creado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})
    
def refresh_table_vinculados(request):
    baremo_principal_id = request.GET.get('baremo_principal_id')
    vinculados = BaremoVinculado.objects.filter(detalle_principal_id = baremo_principal_id )
    
    html = render_to_string('tabla_baremo_vinculado.html', {
        'vinculados': vinculados,
    })
    
    # Devolver un JSON con el HTML y el total
    return JsonResponse({'html': html }) 

def eliminar_vinculo_baremo(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        detalle_vincular = datos['detalle_vincular']
        BaremoVinculado.objects.filter(id = detalle_vincular).delete()
            
        return JsonResponse({'mensaje': 'Creado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})
    

def buscar_elemento_vinculado(request):
    detalle_id = request.GET.get('detalle_id')
    vinculados = BaremoVinculado.objects.filter(detalle_principal_id = detalle_id )
    if vinculados:
        vinculado = 1
        vinculados_ids = vinculados.values_list('detalle_baremo_id', flat=True)
        relacionados = Baremo.objects.filter(detalle_id__in=vinculados_ids)
        datos = list(relacionados.values('id', 'detalle_id','detalle__nombre', 'convenio_id', 'convenio__nombre', 'venta','unidad__nombre', 'grupo_id', 'ntqx', 'xcantidad' ))
    else:
        vinculado = 0
        datos = []
    
    
    # Devolver un JSON con el HTML y el total
    return JsonResponse({'vinculado': vinculado, 'datos':datos })    
    
def inactivar_detalle_item_baremo(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        baremo_id = datos['baremo_id']
        inactivar = datos['inactivar']
        baremo = Baremo.objects.filter(id=baremo_id).first()
        Baremo.objects.filter(id=baremo_id).update(
            inactivar =  inactivar,
            )
            
        LogEliminacion.objects.create(
                descripcion = 'Inactivacion de detalle de Baremo '+str(baremo.detalle_id)+' '+str(baremo.detalle),
                usuario_id = request.user.id
            )
           
            
        return JsonResponse({'mensaje': 'Creado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})



def cambiar_estatus_cirugia_manual(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        cirugia_id = datos['cirugia_id']
        nuevo_estatus = datos['nuevo_estatus']
         
        cirugia = Cirugia.objects.filter(id = cirugia_id ).first()
        if cirugia:
            buscar_alta_medica = AltaMedica.objects.filter(cirugia_id = cirugia_id).first()
            if nuevo_estatus == 7 and not buscar_alta_medica:
                return JsonResponse({'mensaje': 'SIN-ALTA'})
            
            presupuesto_id = cirugia.presupuesto_id
            Cirugia.objects.filter(id=cirugia_id).update(
                estatus_id = nuevo_estatus,
                usuario_id = request.user.id
            )
            
            Presupuesto.objects.filter(id = presupuesto_id).update(
                estatus_id = nuevo_estatus,
                usuario_id = request.user.id
            )
        
            LogEliminacion.objects.create(
                    descripcion = 'Cambio de estatus a la cirugia: '+str(cirugia_id)+' estatus anterior:'+str(cirugia.estatus)+ ' nuevo estatus:'+str(nuevo_estatus),
                    usuario_id = request.user.id
                )
           
            
        return JsonResponse({'mensaje': 'Creado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})
    
def cambio_proveedor_factura(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        notaentrega_id = datos['notaentrega_id']
        facturacompra_id = datos['facturacompra_id']
        nuevoproveedor_id = datos['nuevoproveedor_id']
        proveedor_actual_id = datos['proveedor_actual_id']

        if notaentrega_id != 'None':
            NotaEntregaCompra.objects.filter(id = notaentrega_id, proveedor_compra_id = proveedor_actual_id ).update(
                proveedor_compra_id = nuevoproveedor_id,
                usuario_id = request.user.id
            )
        FacturaProveedor.objects.filter(id = facturacompra_id, proveedor_compra_id = proveedor_actual_id).update(
            proveedor_compra_id = nuevoproveedor_id,
            usuario_id = request.user.id
        )
        LogEliminacion.objects.create(
            descripcion = " Cambio de proveedor en factura id proveedor anterior :"+str(proveedor_actual_id)+' por nuevo proveedor: '+str(nuevoproveedor_id),
            usuario_id = request.user.id
        )
        
            
    return JsonResponse({
                'congelar_cambio': 0,
            })
    
def cambio_retencion_factura(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nueva_retencion_id = datos['nueva_retencion_id']
        sustraendo = 0
        if nueva_retencion_id == '':
            nueva_retencion_id = None
            
        facturacompra_id = datos['facturacompra_id']
        if nueva_retencion_id:
            nueva_retencion = Retencion.objects.filter(id = nueva_retencion_id).first()
        else:
            nueva_retencion = None
            
        factura = FacturaProveedor.objects.filter(id = facturacompra_id).first()
        if nueva_retencion:
            if factura:
                tipo_persona = factura.proveedor_compra.rif[0]
                if tipo_persona == 'J' or tipo_persona == 'G':
                    porcentaje = nueva_retencion.juridica
                    sustraendo = nueva_retencion.sustraendojuridica
                else:
                    porcentaje = nueva_retencion.natural
                    sustraendo = nueva_retencion.sustraendonatural
                    
        else:
            porcentaje = sustraendo = 0     
                
        
            
        FacturaProveedor.objects.filter(id = facturacompra_id).update(
            porcentaje_retencion_islr = porcentaje,
            sustraendo_bs = sustraendo,
            usuario_id = request.user.id,
            concepto_id = nueva_retencion_id
        )
        LogEliminacion.objects.create(
            descripcion = " Cambio de concepto de retencion a la factura id"+str(facturacompra_id),
            usuario_id = request.user.id
        )
        
            
    return JsonResponse({
                'congelar_cambio': 0,
            })
    
    
@add_group_name_to_context   
class numeracion_factura( UserPassesTestMixin,TemplateView):
    template_name = 'numeracion_factura.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='CambioNumeracionFactura')  
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        facturas_emitidas = NumeracionFactura.objects.filter(cirugia__isnull = False).order_by('-fecha_factura')
        proximo_numero_factura = NumeracionFactura.objects.filter(cirugia__isnull = True).order_by('-numero_factura').first()
        context['facturas_emitidas'] = facturas_emitidas
        context['proximo_numero_factura'] = proximo_numero_factura.numero_factura
        
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        nuevo_numero = request.POST.get('nuevo_numeroFactura')
        NumeracionFactura.objects.filter(cirugia__isnull = True).update(
           numero_factura = nuevo_numero,
           numero_control = nuevo_numero,
           usuario_id = self.request.user.id
        )
        
        LogEliminacion.objects.create(
            descripcion = 'Cambio de numeracion de proximafactura a: '+str(nuevo_numero),
            usuario_id = self.request.user.id
        )
        return redirect('numeracion_factura')
    
    
    
def verificar_fecha_factura_valida(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        fecha_factura_str = datos['fecha_factura']
        # Convertir la fecha de string a objeto date
        fecha_factura = parse_date(fecha_factura_str)
        if not fecha_factura:
            return JsonResponse({'mensaje': 'fecha_invalida'}, status=400)
        
        # Verificar si existe alguna fecha mayor a fecha_factura
        existe_fecha_mayor = NumeracionFactura.objects.filter(fecha_factura__gt=fecha_factura).exists()
        if existe_fecha_mayor:
            return JsonResponse({'mensaje': 'fecha_invalida'})
        else:
            return JsonResponse({'mensaje': 'fecha valida'})
    else:
        return JsonResponse({'mensaje': 'Método no permitido'}, status=405)
    
    
def cambio_seleccion_consumo_cirugia(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        consumo_id = datos['consumo_id']
        seleccion = datos['seleccion']
        consumocirugia = ConsumoCirugia.objects.filter(id = consumo_id).first()
        ConsumoCirugia.objects.filter(id=consumo_id).update(
            seleccionado = seleccion
        )        
        cantidad_seleccionada = ConsumoCirugia.objects.filter(cirugia_id = consumocirugia.cirugia_id, seleccionado = True).count()
        return JsonResponse({'cantidad': cantidad_seleccionada})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})
    
    

def cambiar_consumo_nuevo_baremo(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nuevo_baremo = datos['nuevo_baremo']
        cirugia_id = datos['cirugia_id']
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        nuevo_lugar_consumo_id = 11
        consumo_cambiar = ConsumoCirugia.objects.filter(cirugia_id = cirugia_id, seleccionado = True)
        detalle = Baremo.objects.filter(id = nuevo_baremo).first()
        if detalle:
            detalle_id = detalle.detalle_id
            total_general_consumo = 0
            for consumo in consumo_cambiar:
                total_general_consumo += consumo.venta
                ConsumoCirugia.objects.filter(id = consumo.id).update(
                    consumo_id = nuevo_lugar_consumo_id,
                    nota = ' Consumo cambiado de lugar de consumo',
                    usuario_id = request.user.id,
                    baremo_cobro_id = detalle_id
                )
                LogEliminacion.objects.create(
                    descripcion = 'Consumo Cambiado de lugar de consumo en la opcion de consumo ' +str(consumo.inventario),
                    usuario_id = request.user.id
                    )
            #buscar detalle_id o crear el baremo y presupesto en detalle
            if total_general_consumo > 0:
                detalle_nuevo = DetallePresupuesto.objects.filter(presupuesto_id = cirugia.presupuesto_id, detalle_id = detalle_id).first()
                if detalle_nuevo:
                    DetallePresupuesto.objects.filter(id=detalle_nuevo.id).update(
                        precio = total_general_consumo,
                        precio_usado = total_general_consumo
                    )
                else:
                    DetallePresupuesto.objects.create(
                        presupuesto_id = cirugia.presupuesto_id,
                        cantidad = 1,
                        precio = total_general_consumo,
                        notas = ' Creado automaticamente por cambio en consumo de baremo facturacion',
                        fecha_cambio = datetime.now().date(),
                        convenio_id = detalle.convenio_id,
                        detalle_id = detalle_id,
                        grupo_id = detalle.grupo_id,
                        plantilla_id = detalle.plantilla_id,
                        unidad_id = detalle.unidad_id,
                        usuario_id = request.user.id,
                        ntqx = detalle.ntqx,
                        cantidad_usada = 1,
                        precio_usado = total_general_consumo,
                        lugar_consumo_id = nuevo_lugar_consumo_id
                        
                    )

            
            
        print('id_detalle',detalle_id )
        
        return JsonResponse({'cantidad': '0'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})
    
    
def extraer_retencion_iva(request):
    proveedor_id = request.GET.get('proveedor_id')
    
    proveedor = Proveedor.objects.filter(id = proveedor_id).first()
    porcentaje_retener = proveedor.porcentaje_retencion
    

    
    # Devolver un JSON con el HTML y el total
    return JsonResponse({'porcentaje_retener': porcentaje_retener }) 


@add_group_name_to_context    
class listado_inventario_contable(TemplateView): 
    template_name = 'listado_inventario_contable.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        #productos = Inventario.objects.all().order_by('nombre')
        #context['productos'] = productos
        hoy = date.today()
        fecha_inicio_inventario = hoy.replace(day=1)
        fecha_tope_inventario = hoy
        categorias = CategoriaInventario.objects.all().order_by('nombre')
        context['categorias'] = categorias
        context['fecha_inicio_inventario'] = fecha_inicio_inventario
        context['fecha_tope_inventario'] = fecha_tope_inventario
        return context


def refrescar_tabla_inventario_contable(request): 
    fecha_tope_str = request.GET.get('fecha_tope')
    fecha_inicio_str = request.GET.get('fecha_inicio')
    categoria_id = request.GET.get('categoria_filtro')
    
    #fecha_tope_date = date.fromisoformat(fecha_tope_str)  # Convierte "2025-06-25" a date(2025, 6, 25)
    fecha_tope_date = datetime.strptime(fecha_tope_str, "%d/%m/%Y").date()
    fecha_fin = datetime(
                    year=fecha_tope_date.year,
                    month=fecha_tope_date.month,
                    day=fecha_tope_date.day,
                    hour=23,
                    minute=59,
                    second=59,
                    microsecond=999999
                )

    #fecha_inicio_date = date.fromisoformat(fecha_inicio_str)  # Convierte "2025-06-25" a date(2025, 6, 25)
    fecha_inicio_date = datetime.strptime(fecha_inicio_str, "%d/%m/%Y").date()
    fecha_inicio = datetime(
                    year=fecha_inicio_date.year,
                    month=fecha_inicio_date.month,
                    day=fecha_inicio_date.day,
                    hour=0,
                    minute=0,
                    second=0
                )

    subquery_descarga = InventarioDescarga.objects.filter(
        inventario_id=OuterRef('pk'),
        fecha_act__isnull=False,  # Opcional: excluye nulos si no quieres incluirlos en la suma
        fecha_act__gte = fecha_inicio,
        fecha_act__lte = fecha_fin,
        reciclado = False
            ).exclude(tipodescarga_id = 4
            ).values('inventario_id').annotate(
                suma=Coalesce(
                    Sum('cantidad', output_field=DecimalField()),  # Suma como Decimal (primer arg posicional)
                    Decimal('0.00'),  # Valor por defecto (segundo arg posicional)
                    output_field=DecimalField()  # Kwarg correcto: fuerza tipo de salida (sin coma extra)
                )
            ).values('suma')[:1]  # Devuelve solo la suma por inventario_id

    subquery_entrada = DepositoUso.objects.filter(
         inventario_id=OuterRef('pk')
     ).values('inventario_id').annotate(
         suma=Coalesce(
            Sum('cantidad_deposito', output_field=DecimalField()),  # Suma como Decimal
            Decimal('0.00')  # Valor por defecto como Decimal (compatible)
        , output_field=DecimalField())  # Opcional: fuerza el tipo en Coalesce
    ).values('suma')[:1]

    subquery_salida_reciclado = ReutilizacionInventario.objects.filter(
         inventario_id=OuterRef('pk')
     ).values('inventario_id').annotate(
         suma=Coalesce(
            Sum('cantidad', output_field=DecimalField()),  # Suma como Decimal
            Decimal('0.00')  # Valor por defecto como Decimal (compatible)
        , output_field=DecimalField())  # Opcional: fuerza el tipo en Coalesce
    ).values('suma')[:1]
    

    subquery_entrada_nota_entrega = InventarioDescarga.objects.filter(
        inventario_id=OuterRef('pk'),
        tipodescarga_id=4,
        reciclado = False,
        fecha_act__lte = fecha_fin,
        fecha_act__gte = fecha_inicio
        ).values('inventario_id').annotate(
            suma=Coalesce(
                Sum('cantidad', output_field=DecimalField()),  # Suma como Decimal
                Decimal('0.00')  # Valor por defecto como Decimal (compatible)
            , output_field=DecimalField())  # Opcional: fuerza el tipo en Coalesce
        ).values('suma')[:1]


    if categoria_id:
        productos = Inventario.objects.filter(
            producto_activo=True,
            categoria_id = categoria_id
        ).annotate(
                total_descarga=(Subquery(subquery_descarga)/F('unidad_conversion')),
                total_entrada=(Subquery(subquery_entrada)),
                total_entrada_nota_entrega=(Subquery(subquery_entrada_nota_entrega))
            # Similar para total_usada con DepositoUso
        ).order_by('nombre').values(
            'nombre', 'nombre_comercial', 'codigo', 'total_descarga', 'total_entrada', 'total_entrada_nota_entrega','unidad_conversion', 'costo', 'piva', 'unidadcompra__nombre', 'presentacion_salida__nombre'
        )

    else:
        productos = Inventario.objects.filter(
            producto_activo=True
        ).annotate(
                total_descarga=Coalesce(Subquery(subquery_descarga), Decimal('0.00')),
                total_entrada=Coalesce(Subquery(subquery_entrada), Decimal('0.00')),
                total_entrada_nota_entrega=Coalesce(Subquery(subquery_entrada_nota_entrega), Decimal('0.00')),
                total_reciclado = Coalesce(Subquery(subquery_salida_reciclado), Decimal('0.00')),
             # Similar para total_usada con DepositoUso
        ).order_by('nombre').values(
            'nombre', 'nombre_comercial', 'codigo', 'total_descarga', 'total_entrada', 'total_entrada_nota_entrega','unidad_conversion', 'costo', 'piva','unidadcompra__nombre', 'presentacion_salida__nombre', 'total_reciclado'
        )
    
    productos = list(productos)  # Convierte a lista para JsonResponse
    data = {'productos': productos }
    return JsonResponse(data)


@add_group_name_to_context    
class agregar_factura_inventario(UserPassesTestMixin , TemplateView):
    template_name = 'agregar_factura_inventario.html'

    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Inventario') 
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        laboratorios = LaboratorioMedicina.objects.all().order_by('nombre')
        proveedores = Proveedor.objects.filter(activo=True).order_by('nombre')
        categorias = CategoriaInventario.objects.all().order_by('nombre')
        clasificacion = UnidadProducto.objects.all().order_by('nombre')
        presentaciones = PresentacionMedicina.objects.all().order_by('nombre')
        productos = Inventario.objects.filter(producto_activo=True).order_by('nombre')
        depositos = Deposito.objects.all().order_by('nombre')
        incremento = MontoIncremento.objects.first()
        unidadcompra = UnidadCompra.objects.all().order_by('nombre')
        retenciones = Retencion.objects.all().order_by('nombre')
        action = 'A'
        tasa_hoy = CambioDiaBcv(datetime.now())
        tasa_hoy = float(str(tasa_hoy).replace(',', '.'))

        FacturaProveedor.objects.filter(tipo = 'XX').delete()
        
        context['presentaciones'] = presentaciones
        context['clasificacion'] = clasificacion
        context['laboratorios'] = laboratorios
        context['proveedores'] = proveedores
        context['unidadcompra'] = unidadcompra
        context['retenciones'] = retenciones
        context['categorias'] = categorias
        context['fecha_hoy'] = datetime.now()
        context['incremento'] =incremento
        context['productos'] = productos
        context['depositos'] = depositos
        context['tasa_hoy'] = tasa_hoy
        context['action'] = action
        return context


def agregarFacturaInventario(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nroControl = datos['nroDocumento']
        nroDocumento = datos['nroFactura']
        idRetencion = datos['idRetencion']
        idProveedor = datos['idProveedor']
        fechaEntrega = datos['fechaEntrega']
        categoria = datos['categoria']
        clasificacion = datos['clasificacion']
        costo = datos['costo']
        venta = datos['venta']
        idInventario = datos['idInventario']
        #presentacion = datos['presentacion']
        presentacion_salida = datos['presentacion_salida']
        lote = datos['lote']
        laboratorio = datos['laboratorio']
        fechaelabora = datos['fechaelabora']
        fechavence = datos['fechavence']
        nombreProducto = datos['nombreProducto']
        piva = datos['piva']
        depositocarga = datos['depositocarga']
        #conversion = datos['conversion']
        unidad_compra = datos['unidad_compra']
        nombrecomercial = datos['nombrecomercial']
        cantidadcompra = datos['cantidadcompra']
        tasa_aplicable = datos['tasa_aplicable']
        moneda_factura = datos['moneda_factura']
        cantidad_critica = datos['cantidad_critica']
        cantidad_minima = datos['cantidad_minima']
        totalcantidad_compra = datos['totalcantidad_compra']

        costo = float(costo.replace(',','.'))
        tasa_aplicable = float(tasa_aplicable)

        categorianombre = CategoriaInventario.objects.filter(id=categoria).first()
        if idInventario:
            producto = Inventario.objects.filter(id=idInventario).first()
            codigonew = producto.codigo
        else:
            idInventario = 0
            proximocodigo = Inventario.objects.aggregate(Max('id'))['id__max']
            proximocodigo = int(proximocodigo)
            proximocodigo = proximocodigo + 1
            codigonew = categorianombre.nombre[:3].upper()
            codigonew = codigonew + str(proximocodigo).zfill(10)


        #detalles = datos.get('detalles')
        if int(moneda_factura) == 1:
            costo_dl = Decimal(costo)
            costo_bs = Decimal(costo) * Decimal(tasa_aplicable)
            #costo_bs = costo_bs.quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        else:
            costo_bs = costo
            costo_dl = costo / tasa_aplicable

        porcentaje_impuesto = 0
        retencion = Retencion.objects.filter(id = idRetencion).first()
        proveedor = Proveedor.objects.filter(id = idProveedor).first()
        sustraendo_bs = 0
        if retencion and proveedor:
            tipo_persona = proveedor.rif[:1]
            if tipo_persona == 'J' or tipo_persona == 'G':
                porcentaje_impuesto = retencion.juridica 
                sustraendo_bs =  retencion.sustraendojuridica
            else:
                porcentaje_impuesto = retencion.natural
                sustraendo_bs =  retencion.sustraendonatural

        
        notaexiste = FacturaProveedor.objects.filter(numerodocumento = nroDocumento.strip(), proveedor_compra_id = idProveedor).first()

        
        if notaexiste:
            FacturaProveedor.objects.filter(numerodocumento = nroDocumento.strip(), proveedor_compra_id = idProveedor).update(
                numerocontrol=nroControl.strip(),
                numerodocumento=nroDocumento.strip(),
                proveedor_compra_id = idProveedor,
                fecha_entrega = fechaEntrega,
                fecha_cambio = fechaEntrega,
                usuario_id = request.user.id,
                cambio_congelado = tasa_aplicable,
                congelar_moneda = True,
                tipomoneda_id = moneda_factura,
                tipodocumento_id = 1,
                porcentaje_retencion_islr = porcentaje_impuesto,
                sustraendo_bs = sustraendo_bs
                )
            
            factura_id = notaexiste.id
        else:
            factura = FacturaProveedor.objects.create(
                numerocontrol=nroControl.strip(),
                numerodocumento=nroDocumento.strip(),
                proveedor_compra_id = idProveedor,
                fecha_entrega = fechaEntrega,
                fecha_cambio = fechaEntrega,
                usuario_id = request.user.id,
                cambio_congelado = tasa_aplicable,
                congelar_moneda = True,
                tipomoneda_id = moneda_factura,
                tipodocumento_id = 1,
                tipo = 'XX',
                porcentaje_retencion_islr = porcentaje_impuesto,
                sustraendo_bs = sustraendo_bs
                )
            
            factura_id = factura.id

           
        if idInventario == 0:
            idInventario = None


        factor_unidad_compra = UnidadCompra.objects.filter(id = unidad_compra).first()
        DetalleFacturaProveedor.objects.create(
            cantidad  = float(cantidadcompra),
            precio_unitario = costo_bs,
            porc_iva = piva,
            descripcion = nombreProducto,
            factura_id = factura_id,
            montoiva = (costo_bs * float(cantidadcompra)) * (float(piva)/100),
            precio_bs = costo_bs,
            subtotal = costo_bs * float(cantidadcompra),
            cambio_bcv = tasa_aplicable,
            congelar_moneda = True,
            subtotal_bs = costo_bs * float(cantidadcompra),
            subtotal_dl = costo_dl * float(cantidadcompra),
            precio_dl = costo_dl,
            inventario_id = idInventario,
            usuario_id = request.user.id,
            deposito_carga_id = int(depositocarga),
            nueva_categoria_id = categoria,
            nuevo_laboratorio_id = laboratorio,
            nueva_presentacion_salida_id = presentacion_salida,
            nuevo_lote = lote,
            nueva_unidadcompra_id = unidad_compra,
            nueva_clasificacion_id = clasificacion,
            nuevo_nombre_comercial = nombrecomercial,
            nueva_fechaelaboracion = fechaelabora, 
            nueva_fechavencimiento = fechavence,
            unidades_con_factor = Decimal(totalcantidad_compra),
            precio_unico_factor_dl = (Decimal(costo_bs) / Decimal(factor_unidad_compra.cantidad_unidad_bulto))/Decimal(tasa_aplicable) ,
            
        )
        

        data = {'idNota' : factura_id}
        return JsonResponse(data)
    else:
        return JsonResponse({'mensaje': 'Error al GUARDAR Nota de entrega'})


def refresh_table_detalle_factura(request):
    idfactura = request.GET.get('idNota')
    print('idfactura', idfactura)
    detallenota = DetalleFacturaProveedor.objects.filter(factura_id = idfactura)
    factura = FacturaProveedor.objects.filter(id=idfactura).first()

    return render(request, 'tabla_inventario_factura.html', {'detallenota': detallenota, 'factura':factura})

def refresh_table_detalle_factura_medico(request):
    idfactura = request.GET.get('idNota')
    facturadetalle = DetalleFacturaProveedor.objects.filter(factura_id = idfactura)
    factura = FacturaProveedor.objects.filter(id=idfactura).first()

    return render(request, 'tabla_factura.html', {'facturadetalle': facturadetalle, 'factura':factura})

def creaProductoNuevoInventario(inventario_id,detalle_factura_id, usuario):
    detalle = DetalleFacturaProveedor.objects.filter(id = detalle_factura_id).first()
    factor = UnidadCompra.objects.filter(id = detalle.nueva_unidadcompra_id).first()
    if not inventario_id:
        nomcategoria  = CategoriaInventario.objects.filter(id=detalle.nueva_categoria_id).first()
        proximocodigo = Inventario.objects.aggregate(Max('id'))['id__max']
        proximocodigo = int(proximocodigo)
        proximocodigo = proximocodigo + 1
        codigonew = nomcategoria.nombre[:3].upper()
        codigonew = codigonew + str(proximocodigo).zfill(10)

        nuevo_inventario = Inventario.objects.create(
            categoria_id = detalle.nueva_categoria_id,
            codigo = codigonew,
            clasificacion_id = detalle.nueva_clasificacion_id,
            presentacion_salida_id = detalle.nueva_presentacion_salida_id,
            unidadcompra_id = detalle.nueva_unidadcompra_id,
            laboratorio_id = detalle.nuevo_laboratorio_id,
            lote = detalle.nuevo_lote,
            fecha_elaboracion = detalle.nueva_fechaelaboracion,
            fecha_vencimiento = detalle.nueva_fechavencimiento,
            nombre_comercial = detalle.nuevo_nombre_comercial,
            nombre = detalle.descripcion,
            usuario_id = usuario
        )
        inventario_id = nuevo_inventario.id
        print('aqui creo un nuevo producto en el inventario')
    else:
        Inventario.objects.filter(id = inventario_id).update(
            clasificacion_id = detalle.nueva_clasificacion_id,
            presentacion_salida_id = detalle.nueva_presentacion_salida_id,
            unidadcompra_id = detalle.nueva_unidadcompra_id,
            laboratorio_id = detalle.nuevo_laboratorio_id,
            lote = detalle.nuevo_lote,
            fecha_elaboracion = detalle.nueva_fechaelaboracion,
            fecha_vencimiento = detalle.nueva_fechavencimiento,
            nombre_comercial = detalle.nuevo_nombre_comercial,
            usuario_id =usuario
        )
        print('aqui actualizo el producto que ya existe')

    return inventario_id



def guardarInventarioFactura(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        numeroFactura = datos['numeroFactura']
        proveedor_id = datos['proveedorId']
        concepto_id = datos['concepto_id']
        factura_nueva =  FacturaProveedor.objects.filter(numerodocumento = numeroFactura.strip(), proveedor_compra_id = proveedor_id, tipo = 'XX').first()
        if factura_nueva:
            FacturaProveedor.objects.filter(id = factura_nueva.id).update(
                tipo = 'FC',
                usuario_id = request.user.id,
                concepto_id = concepto_id
                
            )

            productos = DetalleFacturaProveedor.objects.filter(factura_id = factura_nueva.id, no_inventario = False)
            generardepositos = Deposito.objects.all()
            for producto in productos:
                inventario_id = creaProductoNuevoInventario(producto.inventario_id, producto.id, request.user.id)
                costo_actual_dl = 0
                costo_nuevo_dl = producto.precio_unico_factor_dl
                inventario = Inventario.objects.filter(id=inventario_id).first()
                if inventario:
                    costo_actual_dl = inventario.costo
                    if costo_nuevo_dl > costo_actual_dl:
                       Inventario.objects.filter(id=inventario_id).update(
                           costo = costo_nuevo_dl,
                           piva = producto.porc_iva,
                           usuario_id = request.user.id
                       ) 

                deposito_id = producto.deposito_carga_id
                producto_existe_en_deposito = DepositoUso.objects.filter(deposito_id = deposito_id, inventario_id = inventario_id).first()
                if producto_existe_en_deposito:
                    DepositoUso.objects.filter(id = producto_existe_en_deposito.id).update(
                        usuario_id = request.user.id,
                        cantidad_deposito = F('cantidad_deposito') + producto.unidades_con_factor
                    )

                else:
                    for depo in generardepositos:
                        if depo.id == deposito_id:
                            cantidad = producto.unidades_con_factor
                        else:
                            cantidad = 0

                        DepositoUso.objects.create(
                            inventario_id = inventario_id,
                            usuario_id = request.user.id,
                            deposito_id = depo.id,
                            cantidad_deposito = cantidad
                            )

                InventarioDescarga.objects.create(
                    cantidad = producto.unidades_con_factor,
                    nota = 'Carga desde Factura :'+str(numeroFactura),
                    depositoentrada_id = deposito_id,
                    inventario_id = inventario_id,
                    usuario_id = request.user.id,
                    tipodescarga_id = 4,

                )

                factor = UnidadCompra.objects.filter(id= producto.nueva_unidadcompra_id).first()
                monto_venta_unidad = 0
                incremento_venta = MontoIncremento.objects.filter(id=1).first()
                if incremento_venta:
                    monto_venta_unidad = Decimal(costo_nuevo_dl) * Decimal(incremento_venta.porcentaje / 100)

                InventarioHistoria.objects.create(
                    inventario_id = inventario_id,
                    costo = producto.precio_dl,
                    tasa = producto.cambio_bcv,
                    piva = producto.porc_iva,
                    venta = monto_venta_unidad,
                    unidadcompra_id = producto.nueva_unidadcompra_id,
                    presentacion_salida_id = producto.nueva_presentacion_salida_id,
                    usuario_id = request.user.id,
                    lote = producto.nuevo_lote,
                    factor = factor.cantidad_unidad_bulto,
                    laboratorio_id = producto.nuevo_laboratorio_id,
                    cantidad = producto.cantidad,
                    fecha_vencimiento = producto.nueva_fechavencimiento,
                    factura_compra_id = producto.factura_id 

                )


        data = {'idNota' : 0}
        return JsonResponse(data)
    else:
        return JsonResponse({'mensaje': 'Error al GUARDAR FActura de entrega'})


def agregar_nota_credito_al_pago(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        monto_total_abono_bs = 0
        monto_total_abono_dl = 0
        numerodedocumentos = ''
        for item in data:
            notacredito_id = item['id']
            numerofactura = item['numerofactura']
            nota_abonar = FacturaProveedor.objects.filter(id = notacredito_id).first()
            factura = FacturaProveedor.objects.filter(numerodocumento = numerofactura, proveedor_compra_id = nota_abonar.proveedor_compra_id).first()
            FacturaProveedor.objects.filter(id = notacredito_id).update(
                estatus = 'PAG',
                usuario_id = request.user.id,
            )

            if nota_abonar:
                monto_total_abono_bs += nota_abonar.total_operacion_bs
                monto_total_abono_dl += nota_abonar.total_operacion_dl
                numerodedocumentos +=  '( '+str(nota_abonar.numerodocumento)+' )'


        if monto_total_abono_bs > 0:
            abono = AbonoCuentaPagar.objects.create(
                montopago = monto_total_abono_dl ,
                montopago_bs = monto_total_abono_bs,
                descripcion = 'Nota de credito aplicada Nro Notas:' + str(numerodedocumentos),
                factura_id = factura.id,
                usuario_id = request.user.id,
                referencia = 'GEN_AUTO',
                fecha_pago = datetime.now().date(),
                nota_credito_generada_id = nota_abonar.id,
                nota_credito = True

            )

            for item in data:
                notacredito_id = item['id']
                FacturaProveedor.objects.filter(id = notacredito_id).update(
                    abono_id = abono.id,
                )

        return JsonResponse({'status': 'success', 'message': 'Datos procesados correctamente', 'procesados': len(data)})


def refresh_tabla_disponible_pt(request):
    depositoId = request.GET.get('depositoId')
    deposito_seleccion = DepositoUso.objects.filter(deposito_id = depositoId, inventario__categoria_id__in=['1', '2'], inventario__producto_activo =True)
        
    return render(request, 'tabla_farmacia_disponible_pt.html', {'deposito_seleccion': deposito_seleccion, 'depositoId':depositoId})  


def agregar_producto_bd_terminado(request):
     if request.method == 'POST':
        datos = json.loads(request.body)
        nCantidad = datos['nCantidad']
        inventario_id = datos['inventario_id']
        deposito_id = datos['deposito_id']
        producto_terminado_id = datos['producto_terminado_id']
        producto = Inventario.objects.filter(id = inventario_id).first()
        if producto:
            monto_costo = producto.costo
            monto_iva = producto.piva / 100

            materiaprima = MateriaPrimaInventario.objects.create(
                cantidad = nCantidad,
                precio_dl = monto_costo + monto_iva,
                subtotal_precio_dl = Decimal(monto_costo + monto_iva) * Decimal(nCantidad),
                deposito_id = deposito_id,
                materia_prima_id = inventario_id,
                producto_terminado_id = producto_terminado_id,
                usuario_id = request.user.id

            )

            """ InventarioDescarga.objects.create(
                cantidad = nCantidad,
                nota = 'USO EN PRODUCCION DE PRODUCTO TERMINADO COD:'+str(producto_terminado_id),
                deposito_id = deposito_id,
                inventario_id = inventario_id,
                usuario_id = request.user.id,
                tipodescarga_id = 24,
                materiaprima_id = materiaprima.id
            ) """

            
            data = {
                'codigo': producto.codigo,
                'lote': producto.lote,
            
            }
            # Agrega aquí los campos que deseas mostrar
            return JsonResponse(data)

def eliminar_materia_prima(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        id_materia_prima = datos['id_materia_prima']
        MateriaPrimaInventario.objects.filter(id = id_materia_prima ).delete()
        data = {
                'codigo': '01',
                'lote': '0',
            
            }
            # Agrega aquí los campos que deseas mostrar
        return JsonResponse(data)

def RevisarExistenciaMateriaPrima(materiaprimaexiste, cantidad_agregar):
    proceder = True
    for materia in materiaprimaexiste:
        cantidad_requerida = materia.cantidad * Decimal(cantidad_agregar)
        existencia_deposito = 0
        disponible_inventario = DepositoUso.objects.filter(deposito_id = materia.deposito_id, inventario_id = materia.materia_prima_id).first()
        if disponible_inventario:
            existencia_deposito = disponible_inventario.existenciaUnd

        if cantidad_requerida > existencia_deposito:
            proceder = False
            return proceder
        
        
    return proceder


def agregar_producto_terminado_a_inventario(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        producto_terminado_id = datos['producto_id']
        cantidad_agregar = datos['cantidad_agregar']
        deposito_id = datos['depositonew']
        
        existe = 'NO'
        materiasprima = MateriaPrimaInventario.objects.filter(producto_terminado_id = producto_terminado_id)
        hay_existencias = RevisarExistenciaMateriaPrima(materiasprima, cantidad_agregar)
        if hay_existencias == False:
            existe = 'SI'

        print('existencia', hay_existencias)
        if materiasprima and hay_existencias:
            existe = 'SI'
            for mp in materiasprima:
                cantidad_descarga = mp.cantidad * Decimal(cantidad_agregar)
                InventarioDescarga.objects.create(
                    cantidad = cantidad_descarga,
                    nota = 'USO EN PRODUCCION DE PRODUCTO TERMINADO COD:'+str(producto_terminado_id),
                    deposito_id = mp.deposito_id,
                    inventario_id = mp.materia_prima_id,
                    usuario_id = request.user.id,
                    tipodescarga_id = 24,
                    materiaprima_id = mp.id
                )
            

            DepositoUso.objects.filter(inventario_id = producto_terminado_id, deposito_id = deposito_id).update(
                cantidad_deposito = F('cantidad_deposito') + Decimal(cantidad_agregar)
            )
            
            InventarioDescarga.objects.create(
                    cantidad = Decimal(cantidad_agregar),
                    nota = 'CARGA DESDE PRODUTO TERMINADO:'+str(producto_terminado_id),
                    depositoentrada_id = deposito_id,
                    inventario_id = mp.producto_terminado_id,
                    usuario_id = request.user.id,
                    tipodescarga_id = 4,
                )
            
            
        data = {
                'existe': existe,
                'existencias': hay_existencias,
                }
            # Agrega aquí los campos que deseas mostrar
        return JsonResponse(data)


def cambio_precio_costo_inventario(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        inventario_id = datos['inventario_id']
        nuevo_precio_costo = datos['nuevo_precio_costo']
        nuevo_precio_venta = datos['nuevo_precio_venta']
        
        if inventario_id:
            inventario = Inventario.objects.filter(id = inventario_id).first()
            Inventario.objects.filter(id = inventario_id).update(
                usuario_id = request.user.id,
                costo = nuevo_precio_costo,
                venta = inventario.monto_venta
            )
            
            
        data = {
                'existe': '0',
                }
            # Agrega aquí los campos que deseas mostrar
        return JsonResponse(data)


def guardar_nuevo_producto_inventario(request):
     if request.method == 'POST':
        datos = json.loads(request.body)
        conversion = datos['conversion']
        categoria = datos['categoria']
        loteUpdate = datos['loteUpdate']
        pivaUpdate = datos['pivaUpdate']
        costoUpdate = datos['costoUpdate']
        ventaUpdate = datos['ventaUpdate']
        laboratorioUpdate = datos['laboratorioUpdate']
        presentacion_entradaUpdate = datos['presentacion_entradaUpdate']
        presentacion_salidaUpdate = datos['presentacion_salidaUpdate']
        nombreComercialUpdate = datos['nombreComercialUpdate']
        unidad_compra = datos['unidad_compra']
        fechaelaboraUpdate = datos['fechaelaboraUpdate']
        fechavenceUpdate = datos['fechavenceUpdate']
        cantidad_minima = datos['cantidad_minima']
        cantidad_critica = datos['cantidad_critica']
        nombreUpdate = datos['nombreUpdate']
        
        inventario_max = Inventario.objects.order_by('-id').first()
        nuevo_codigo = int(inventario_max.id) + 1
        categoria_actual = CategoriaInventario.objects.filter(id = categoria).first()
        codigo_inventario = categoria_actual.nombre[:3] + (str(nuevo_codigo).zfill(10))

        inventario = Inventario.objects.create(
            codigo = codigo_inventario,
            nombre = nombreUpdate,
            lote = loteUpdate,
            fecha_elaboracion = fechaelaboraUpdate,
            costo =  Decimal(costoUpdate),
            venta = Decimal(ventaUpdate),
            categoria_id = categoria,
            usuario_id = request.user.id,
            laboratorio_id = laboratorioUpdate,
            presentacion_id = presentacion_entradaUpdate,
            fecha_vencimiento = fechavenceUpdate,
            cantidad_cri = cantidad_critica,
            cantidad_min = cantidad_minima,
            presentacion_salida_id = presentacion_salidaUpdate,
            piva = pivaUpdate,
            nombre_comercial = nombreComercialUpdate,
            unidad_conversion = conversion,
            unidadcompra_id = 1
        )

        generardepositos = Deposito.objects.all()
        for depo in generardepositos:
            DepositoUso.objects.create(
               inventario_id = inventario.id,
               usuario_id = request.user.id,
               deposito_id = depo.id,
            )


        data = {
            'codigo': codigo_inventario,
            'producto_id': inventario.id
        
        } 
        # Agrega aquí los campos que deseas mostrar
        return JsonResponse(data)


def xxx(request):
    consumos = ConsumoCirugia.objects.all()
    i=0
    for con in consumos:
        i+=1
        print(i)
        inventario = Inventario.objects.filter(id = con.inventario_id).first()
        precio_costo_unitario = precio_costo_producto_inventario(inventario.id)
        ConsumoCirugia.objects.filter(id = con.id).update(
            precio_costo_unitario = precio_costo_unitario
        )

    print('termine')
    return redirect('index')


def inactivar_retencion_baremo(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        detalle_baremo_id = datos['detalle_baremo_id']
        inactivar = datos['inactivar']
        detalle = DetalleBaremo.objects.filter(id=detalle_baremo_id).first()
        DetalleBaremo.objects.filter(id=detalle_baremo_id).update(
            activar_retencion =  inactivar,
            )
            
        LogEliminacion.objects.create(
                descripcion = 'Inactivacion de retencion en detalle de Baremo '+str(detalle.id)+' '+str(detalle.nombre)+ ' condicion:'+ str(inactivar),
                usuario_id = request.user.id
            )
           
            
        return JsonResponse({'mensaje': 'Creado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})

def generar_comprobante_retencion(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        medico_id = datos['medico_id']
        factura_id = datos['factura_id']
        ultimocomprobante = RetencionISLR.objects.count()+1
        nuevocomprobante_str = f"{ultimocomprobante:06d}"
        current_date = datetime.now()
        year_str = str(current_date.year)
        month_str = f"{current_date.month:02d}"
        nrocomprobante = year_str + month_str + nuevocomprobante_str
        total_baseimponible = total_montoretencion = porcentaje_retencion = id_comprobante = 0  
        medico = FacturaMedico.objects.filter(medico_id=medico_id, factura_id = factura_id).first()
        if medico:
            total_baseimponible += medico.factura.subtotal_factura_bs
            total_montoretencion +=  medico.factura.retencion_islr_monto_bs
            porcentaje_retencion = medico.factura.porcentaje_retencion_islr


            
        print('total_baseimponible', total_baseimponible)

        comprobanteislr = RetencionISLR.objects.create(
                comprobante = nrocomprobante,
                periodo = month_str + year_str,
                usuario_id = request.user.id,
                baseimponible = total_baseimponible,
                montoretencion = total_montoretencion,
                porcentaje_retencion = porcentaje_retencion
            ) 
        
        id_comprobante = comprobanteislr.id
        FacturaMedico.objects.filter(medico_id=medico_id, factura_id = factura_id).update(
                    comprobante_id = id_comprobante,
                    usuario_id = request.user.id
                ) 
       
            
        LogEliminacion.objects.create(
                descripcion = 'Comprobante generado a una factura '+str(medico_id)+' de la factura '+str(factura_id) ,
                usuario_id = request.user.id
            )
            
            
        return JsonResponse({'comprobante': id_comprobante})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})


def generar_comprobante_retencion_compra(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        proveedor_compra_id = datos['proveedor_compra_id']
        factura_id = datos['factura_id']
        ultimocomprobante = RetencionISLR.objects.count()+1
        nuevocomprobante_str = f"{ultimocomprobante:06d}"
        current_date = datetime.now()
        year_str = str(current_date.year)
        month_str = f"{current_date.month:02d}"
        nrocomprobante = year_str + month_str + nuevocomprobante_str
        total_baseimponible = total_montoretencion = porcentaje_retencion = id_comprobante = 0  
        facturaproveedor = FacturaProveedor.objects.filter(proveedor_compra_id=proveedor_compra_id, id = factura_id).first()
        if facturaproveedor:
            total_baseimponible = facturaproveedor.total_baseimponible_bs + facturaproveedor.total_exento_bs
            total_montoretencion =  facturaproveedor.retencion_islr_monto_bs
            porcentaje_retencion = facturaproveedor.porcentaje_retencion_islr
            total_montofactura = facturaproveedor.subtotal_factura_bs
            

            comprobanteislr = RetencionISLR.objects.create(
                    comprobante = nrocomprobante,
                    periodo = month_str + year_str,
                    usuario_id = request.user.id,
                    montofactura = total_montofactura,
                    baseimponible = total_baseimponible,
                    montoretencion = total_montoretencion*-1,
                    porcentaje_retencion = porcentaje_retencion,
                    tipo_comprobante = 'FC'
                ) 
            
            id_comprobante = comprobanteislr.id
            FacturaProveedor.objects.filter(id = factura_id).update(
                        comprobante_id = id_comprobante,
                        usuario_id = request.user.id
                    ) 
        
                
            LogEliminacion.objects.create(
                    descripcion = 'Comprobante generado a una factura de proveedor '+str(facturaproveedor.proveedor_compra)+' de la factura '+str(facturaproveedor.numerodocumento) ,
                    usuario_id = request.user.id
                )
           
            
        return JsonResponse({'comprobante': id_comprobante})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})


def eliminar_pago_medico_factura(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        id_transaccion = datos['id_transaccion']
        transaccion = Transaccion.objects.filter(id=id_transaccion).first()
        if transaccion:
            LogEliminacion.objects.create(
                descripcion = 'Eliminacion de Pago de medico de la factura id '+str(transaccion.cuentapagar.numerodocumento)+' del medico '+str(transaccion.cuentapagar.proveedor) ,
                usuario_id = request.user.id
            )

            Transaccion.objects.filter(id=id_transaccion).delete()       
            
        return JsonResponse({'comprobante': id_transaccion})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})


def procesar_ncr_seleccionada_misma_cuenta(request):
    if request.method == "POST":
        data = json.loads(request.body)
        seleccionados = data.get("datos", [])

        # Aquí puedes procesar los seleccionados
        # Ejemplo: recorrerlos e imprimir en consola
        total_monto_aplicar = 0
        notas_credito_id = ''
        pagador_id = None
        # Ordenar de mayor a menor por saldo
        seleccionados_ordenados = sorted(seleccionados, key=lambda x: x['saldo'], reverse=True)
        tasa_hoy = CambioDiaBcv(datetime.now())
        
        for fila in seleccionados_ordenados:
            cuentacobrar_id = fila["cuentacobrar_id"]
            saldo_cuenta = 0
            cxc = CuentaxCobrar.objects.filter(id = cuentacobrar_id).first()
            if cxc:
                saldo_cuenta = cxc.total_cobrar_monto

            notacredito_aplicar = NotaCreditoCtaCobrar.objects.filter(id = fila["id"]).first()
            monto_nota_credito_aplicar = 0
            if notacredito_aplicar:
                detalle_cxc_id = notacredito_aplicar.detallecuentaxcobrar_id
                detalle_cuenta_cobrar = DetalleCuentaCobrar.objects.filter(id = detalle_cxc_id ).first()
                if detalle_cxc_id:
                    monto_nota_credito_aplicar = notacredito_aplicar.saldo
                    if saldo_cuenta >= monto_nota_credito_aplicar :
                        DetalleCuentaCobrar.objects.filter(id = detalle_cxc_id ).update(
                            estatus = 'APLICADA MISMA CIRUGA'
                        )

                        NotaCreditoCtaCobrar.objects.filter(id=notacredito_aplicar.id).update(
                            usuario_id = request.user.id,
                            cuentaxcobrar_aplicada_id = cuentacobrar_id, 
                            aplicada = True,
                        ) 
                        LogEliminacion.objects.create(
                            descripcion = ' Nota de credito de la misma cirugia fue aplicada por variacion de monto, id de la cuenta por cobrar: '+str(cuentacobrar_id),
                            usuario_id = request.user.id,
                        )
                    else:
                        NotaCreditoCtaCobrar.objects.filter(id=notacredito_aplicar.id).update(
                            usuario_id = request.user.id,
                            cuentaxcobrar_aplicada_id = cuentacobrar_id, 
                            saldo = Decimal(monto_nota_credito_aplicar) - Decimal(saldo_cuenta),
                            saldo_bs = (Decimal(monto_nota_credito_aplicar) - Decimal(saldo_cuenta)) * F('tasa')
                        ) 
                        DetalleCuentaCobrar.objects.filter(id = detalle_cxc_id ).update(
                            estatus = 'SIN APLICAR',
                            montocobrar = saldo_cuenta - monto_nota_credito_aplicar,
                            montocobrar_bs = (saldo_cuenta - monto_nota_credito_aplicar) * F('tasa_bcv')
                        )

                        DetalleCuentaCobrar.objects.create(
                            montocobrar = Decimal(saldo_cuenta) * -1,
                            montocobrar_bs = (saldo_cuenta * detalle_cuenta_cobrar.tasa_bcv) *-1,
                            descripcion = 'PAGO CON PORCION DE N.C. id'+str(detalle_cxc_id),
                            cuentacobrar_id = cuentacobrar_id,
                            destino_pago_id = detalle_cuenta_cobrar.destino_pago_id,
                            origen_pago_id = detalle_cuenta_cobrar.origen_pago_id,
                            tasa_bcv = detalle_cuenta_cobrar.tasa_bcv,
                            transaccion_id = detalle_cuenta_cobrar.transaccion_id,
                            notacredito = True,
                            estatus = 'APLICADA'

                        ) 
                        LogEliminacion.objects.create(
                            descripcion = ' Nota de credito creada por diferencia de pago con la misma nota de credito: '+str(cuentacobrar_id),
                            usuario_id = request.user.id,
                        )

                
        # Devolver respuesta al frontend
        return JsonResponse({"status": "ok", "procesados": len(seleccionados)})

    return JsonResponse({"status": "error", "msg": "Método no permitido"}, status=405)

@add_group_name_to_context    
class ListadoAtencionCortesia(TemplateView):
    template_name='listado_atencion_cortesia.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        atencion_inmediata_cortesia = AtencionInmediataCortesia.objects.filter(estatus_id__lt = 9).order_by('-fecha_act')

        context['atencion_inmediata_cortesia']=atencion_inmediata_cortesia
        return context


@add_group_name_to_context    
class AtencionInmediataCortesiaView(UserPassesTestMixin,TemplateView):
    template_name='atencion_inmediata_cortesia.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Enfermeria')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        AtencionInmediataCortesia.objects.filter(estatus_id = 9).delete()
        #Paciente.objects.filter(status = 'X').delete()
        habitaciones = Habitacion.objects.all().order_by('habitacion')
        kit = KitInventario.objects.all().order_by('nombre')
        personal_medico = Medico.objects.filter(grupo='M').exclude(tipopersonal_id = 9).order_by('nombre')
        depositos = Deposito.objects.all().order_by('nombre')
        baremo = Baremo.objects.filter(inactivar = False).order_by('detalle__posicion')
        tipo_procedimiento = TipoProcedimiento.objects.filter(id=5).first()
        #edad_paciente=calcular_edad(cirugia.paciente.fecha_nac)
        atencioncreada = AtencionInmediataCortesia.objects.create(
            usuario_id = self.request.user.id
        )
        atencion_id = atencioncreada.id
        nuevo_codigo = generar_siguiente_codigo_cortesia()
        AtencionInmediataCortesia.objects.filter(id = atencion_id ).update(
            codigo = 'AMC'+str(nuevo_codigo).zfill(4)
        )
        fecha_hoy = datetime.now().date()
        hora_actual = datetime.now().time()
        medicosatencioninmediata = NotaQuirurgica.objects.filter(atencion_inmediata_id=atencion_id).order_by('medico__nombre')

        context['codigoatencion'] = 'AMC'+str(nuevo_codigo).zfill(4)
        context['kit'] = kit
        context['atencion_id'] = atencion_id
        context['personal_medico'] = personal_medico
        context['depositos'] = depositos
        context['baremo'] = baremo
        context['fecha_hoy'] = fecha_hoy
        context['hora_actual'] = hora_actual
        context['habitaciones'] = habitaciones
        context['tipo_procedimiento'] = tipo_procedimiento
        context['medicosatencioninmediata'] = medicosatencioninmediata
        
        return context
    
    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs) 
        if 'guardar_atencion' in request.POST:
            cedula_atencion_inmediata =  self.request.POST.get('cedula_atencion_inmediata')
            nombrepaciente =  self.request.POST.get('nombrepaciente')
            apellidopaciente =  self.request.POST.get('apellidopaciente')
            fecha_nac_paciente =  self.request.POST.get('fecha_nac_paciente')
            fecha_atencion =  self.request.POST.get('fecha_atencion')
            motivo_atencion =  self.request.POST.get('motivo_atencion')
            medico_ppal_atencion =  self.request.POST.get('medico_ppal_atencion')
            habitacion_atencion =  self.request.POST.get('habitacion_atencion')
            idPaciente_name =  self.request.POST.get('idPaciente_name')
            idatencion_name =  self.request.POST.get('id-atencion-name')
            hora_ingreso =  self.request.POST.get('hora_ingreso')
            
            
            Paciente.objects.filter(id=idPaciente_name).update(
                cedula = cedula_atencion_inmediata,
                nombre = nombrepaciente,
                apellido = apellidopaciente,
                fecha_nac = fecha_nac_paciente,
                status = 'A'
            )
            
            ami_cortesia = AtencionInmediataCortesia.objects.filter(id = idatencion_name).first()
            AtencionInmediataCortesia.objects.filter(id = idatencion_name).update(
                fecha_procedimiento = fecha_atencion,
                motivo_atencion = motivo_atencion,
                estatus_id = 2,
                medico_ppal_id = medico_ppal_atencion,
                paciente_id = idPaciente_name,
                tipo_procedimiento_id = 5,
                usuario_id = self.request.user.id,
                habitacion_id = habitacion_atencion,
                hora_procedimiento = hora_ingreso
                
            )
            presupuesto = Presupuesto.objects.filter(atencion_cortesia_id = idatencion_name).first()
            if presupuesto:
                Presupuesto.objects.filter(id = presupuesto.id).update(
                    medico_ppal_id = medico_ppal_atencion,
                    estatus_id = 2,
                )
            else:
                presupuesto = Presupuesto.objects.create(
                    atencion_cortesia_id =  idatencion_name,
                    fecha_procedimiento  = datetime.now(),
                    hora_procedimiento = datetime.now().time(),
                    nombre_procedimiento = 'Atencion Medica Cortesia ',
                    medico_ppal_id = medico_ppal_atencion,
                    paciente_id = idPaciente_name,
                    tipo_procedimiento_id = 5,
                    usuario_id = request.user.id,
                    estatus_id = 2,
                    convenio_id = 1,
                    )  
            
            consumohospital = ConsumoCirugia.objects.filter(atencion_cortesia_id = idatencion_name)
            descargainventario = ConsumoCirugia.objects.filter(atencion_cortesia_id = idatencion_name, conciliada = False)
            if consumohospital: 
                monto_subtotal_farmacia = consumohospital.aggregate(subtotal_farmacia=Sum(F('precio_costo_unitario')*F('cantidad_real_usada')))['subtotal_farmacia']
                for descarga in descargainventario:
                    ConsumoCirugia.objects.filter(id = descarga.id).update(
                        conciliada = True
                    )
            else:
                monto_subtotal_farmacia = 0
            
            presupuesto = Presupuesto.objects.filter(atencion_cortesia_id = idatencion_name).first()
            
            if presupuesto:
                presupuestoatencioninmediata = DetallePresupuesto.objects.filter(presupuesto__atencion_cortesia_id = idatencion_name)
                monto_subtotal_baremo = presupuestoatencioninmediata.aggregate(total=Sum(F('precio')))['total']
                if not presupuestoatencioninmediata:
                    monto_subtotal_baremo = 0
                    
                total_subtotal = Decimal(monto_subtotal_farmacia) + Decimal(monto_subtotal_baremo)
                
                cuenta_por_cobrar = CuentaxCobrar.objects.create(
                        pagado = False,
                        atencion_cortesia_id = idatencion_name,
                        paciente_id = idPaciente_name,
                        presupuesto_id = presupuesto.id,
                        usuario_id = self.request.user.id
                    )
                    
                DetalleCuentaCobrar.objects.create(
                        cuentacobrar_id = cuenta_por_cobrar.id,
                        montocobrar = total_subtotal,
                        descripcion = 'Atencion Medica Cortesia:'+str(ami_cortesia.codigo),
                    )
            
            
            
        return redirect('listado_atencion_cortesia')

#aplicacion de reconocimiento de voz a texto
def voice_view(request):
    imagen_paciente = ImagenPhoto.objects.filter(cedula = 'V18790551' ).first()
    context = {
        'imagen_paciente': imagen_paciente
    }
    return render(request, "historia_trasoperatoria.html",context )

def receive_voice(request):
    if request.method == "POST":
        data = json.loads(request.body)
        texto = data.get("text")
        print("Texto recibido:", texto)
        return JsonResponse({"ok": True, "texto": texto})

def calcular_imc(peso, talla):
    if peso and talla and talla > 0:
        return round(peso / (talla ** 2), 2)
    return 0


@add_group_name_to_context    
class HistoriaTrasoperatoria(UserPassesTestMixin,TemplateView):
    template_name='historia_trasoperatoria.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='Enfermeria')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['cirugia_id']
        cirugia = Cirugia.objects.filter(id = cirugia_id ).first()
        historia_trans = HistoriaTransOperatoria.objects.filter(cirugia_id = cirugia_id).first()
        if not historia_trans:
            HistoriaTransOperatoria.objects.create(
                cirugia_id = cirugia_id,
                usuario_id = self.request.user.id,
                nota_enfermeria = '',
                nota_cirugia = ''
            )
            historia_trans = HistoriaTransOperatoria.objects.filter(cirugia_id = cirugia_id).first()

        personal_medico = Medico.objects.filter(grupo='M').exclude(tipopersonal_id = 9)
        preanestesica = ConsultaPreanestesia.objects.filter(cirugia_id = cirugia_id).first()
        transoperatorio = HistoriaClinica.objects.filter(cirugia_id = cirugia_id).first()
        if not transoperatorio:
            transoperatorio = ConsultaPreanestesia.objects.filter(cirugia_id = cirugia_id).first()

        imagen_paciente = Paciente.objects.filter(id = cirugia.paciente_id).first()

        edad_paciente = calcular_edad(imagen_paciente.fecha_nac)

        medicos = NotaQuirurgica.objects.filter(cirugia_id = cirugia_id)
        imagen_fondo = 'C:/proyectoU58/photos/fondo.png'
        fecha_inicial = datetime.now().strftime("%Y-%m-%dT%H:%M")
        context['personal_medico'] = personal_medico
        context['imagen_paciente'] = imagen_paciente
        context['imagen_fondo'] = imagen_fondo
        context['edad_paciente'] = edad_paciente
        context['transoperatorio'] = transoperatorio
        context['preanestesica'] = preanestesica
        context['fecha_inicial'] = fecha_inicial
        context['historia_trans'] = historia_trans
        context['cirugia'] = cirugia
        context['medicos'] = medicos
        
        return context

def guardar_nota_enfermeria(request):
    if request.method == "POST":
        data = json.loads(request.body)
        historia_id = data.get("historia_id")
        nota = data.get("nota")
        print('ok0')
        historia = HistoriaTransOperatoria.objects.filter(id=historia_id).first()
        if historia:
            historia.nota_enfermeria = nota
            historia.save(update_fields=["nota_enfermeria", "fecha_act"])
            return JsonResponse({"ok": True})
        print('ok')

    return JsonResponse({"ok": False}, status=400)

@add_group_name_to_context    
class evaluacion_preanestesia(UserPassesTestMixin,TemplateView):
    template_name='evaluacion_preanestesia.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='medicos')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['cirugia_id']
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        religion = Religion.objects.all().order_by('nombre')
        medicos = Medico.objects.filter(grupo = 'M').exclude(tipopersonal_id = 9).order_by('nombre')
        fecha_hoy = datetime.now().date()
        edad_paciente=calcular_edad(cirugia.paciente.fecha_nac)

        medico_consulta_preanestesia_id = None
        medico_consulta_preanestesia = Medico.objects.filter(user_id = self.request.user.id).first()
        if medico_consulta_preanestesia:
            medico_consulta_preanestesia_id = medico_consulta_preanestesia.id

        consultapreanestesia = ConsultaPreanestesia.objects.filter(cirugia_id = cirugia_id ).first()
        if consultapreanestesia:
            fecha_hoy = consultapreanestesia.fecha_consulta
            if consultapreanestesia.medico:
                medico_consulta_preanestesia_id = consultapreanestesia.medico_id

        consulta = ConsultaPreanestesia.objects.filter(
                cirugia_id=kwargs["cirugia_id"]
            ).first()
        respuestas = {}
        if consulta:
            for r in RespuestaEvaluacion.objects.filter(consulta=consulta):
                respuestas[str(r.pregunta_id)] = {
                    "respuesta": r.respuesta,
                    "detalle": r.detalle,
                    "cantidad": r.cantidad
                }

        
        preguntas = list(EvaluacionPreanestesia.objects.all().order_by('id'))
        total = len(preguntas)

        num_columnas = 4
        base = total // num_columnas
        resto = total % num_columnas

        columnas = []
        inicio = 0

        for i in range(num_columnas):
            cantidad = base + (1 if i < resto else 0)
            columnas.append(preguntas[inicio:inicio + cantidad])
            inicio += cantidad

        context['religion'] = religion
        context['cirugia'] = cirugia
        context['medicos'] = medicos
        context['fecha_hoy'] = fecha_hoy
        context['edad_paciente'] = edad_paciente
        context['preguntas_col1'] = columnas[0]
        context['preguntas_col2'] = columnas[1]
        context['preguntas_col3'] = columnas[2]
        context['preguntas_col4'] = columnas[3]
        context['consultapreanestesia'] = consultapreanestesia
        context["respuestas"] = respuestas
        context["medico_consulta_preanestesia_id"] = medico_consulta_preanestesia_id

        return context

    def post(self, request,*args, **kwargs):
        context = super().get_context_data(**kwargs) 
        cirugia_id = self.kwargs['cirugia_id']
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        consultapreanestesia = ConsultaPreanestesia.objects.filter(cirugia_id = cirugia_id ).first()
        fecha_consulta =  self.request.POST.get('fecha_consulta')
        cedula =  request.POST.get('cedula')
        nombre_paciente =  request.POST.get('nombre_paciente')
        apellido_paciente =  request.POST.get('apellido_paciente')
        fecha_nac =  request.POST.get('fecha_nac')
        sexo =  request.POST.get('sexo')
        ocupacion =  request.POST.get('ocupacion')
        religion =  request.POST.get('religion')
        telefono1 =  request.POST.get('telefono1')
        medico =  request.POST.get('medico')
        nombre_procedimiento =  request.POST.get('nombre_procedimiento')
        antecedente_medico =  request.POST.get('antecedente_medico')
        antecedente_qx =  request.POST.get('antecedente_qx')
        nota =  request.POST.get('nota')
        dtm =  request.POST.get('dtm')
        dem =  request.POST.get('dem')
        ao =  request.POST.get('ao')
        rhmi =  request.POST.get('rhmi')
        aao =  request.POST.get('aao')
        ekg =  request.POST.get('ekg')
        rxtorax =  request.POST.get('rxtorax')
        ecomls =  request.POST.get('ecomls')
        eva_preoperatoria =  request.POST.get('preoperatoria')
        evaluaciones =  request.POST.get('evaluaciones')
        recomendaciones =  request.POST.get('recomendaciones')
        

        hb =  request.POST.get('hb')
        hb = hb.replace(',','.')
        glisemia =  request.POST.get('glisemia')
        glisemia = glisemia.replace(',','.')

        leucosito =  request.POST.get('leucosito')
        leucosito = leucosito.replace(',','.')

        hto =  request.POST.get('hto')
        hto = hto.replace(',','.')
        urea =  request.POST.get('urea')
        urea = urea.replace(',','.')

        plaq =  request.POST.get('plaq')
        plaq = plaq.replace(',','.')
        creatinina =  request.POST.get('creatinina')
        creatinina = creatinina.replace(',','.')

        pt =  request.POST.get('pt')
        pt = pt.replace(',','.')
        hiv =  request.POST.get('hiv')
        hiv = hiv.replace(',','.')

        ptt =  request.POST.get('ptt')
        ptt = ptt.replace(',','.')
        vdrl =  request.POST.get('vdrl')
        vdrl = vdrl.replace(',','.')
        peso =  request.POST.get('peso')
        peso = peso.replace(',','.')
        talla =  request.POST.get('talla')
        talla = talla.replace(',','.')
        imc =  request.POST.get('imc')
        imc = imc.replace(',','.')
        ta =  request.POST.get('ta')
        ta = ta.replace(',','.')
        fr =  request.POST.get('fr')
        fr = fr.replace(',','.')
        fc =  request.POST.get('fc')
        fc = fc.replace(',','.')

        if not peso:
            peso = 0

        if not talla:
            talla = 0

        if not imc:
            imc = 0

        if not ta:
            ta = 0

        if not fr:
            fr = 0

        if not fc:
            fc = 0

        if not hb:
            hb = 0

        if not glisemia:
            glisemia = 0

        if not leucosito:
            leucosito = 0

        if not hto:
            hto = 0

        if not urea:
            urea = 0

        if not plaq:
            plaq = 0

        if not creatinina:
            creatinina = 0

        if not pt:
            pt = 0

        if not hiv:
            hiv = 0

        if not ptt:
            ptt = 0

        if not vdrl:
            vdrl = 0

            
        alergia =  request.POST.get('alergia')
        malla1 = request.POST.get("malla1") == "on"
        malla2 = request.POST.get("malla2") == "on"
        malla3 = request.POST.get("malla3") == "on"
        malla4 = request.POST.get("malla4") == "on"
        categoria_asa_i = request.POST.get("uno") == "on"
        categoria_asa_ii = request.POST.get("dos") == "on"
        categoria_asa_iii = request.POST.get("tres") == "on"
        categoria_asa_iv = request.POST.get("cuatro") == "on"
        categoria_asa_v = request.POST.get("cinco") == "on"
        categoria_asa_e = request.POST.get("seis") == "on"

        anios = request.POST.get("detalle_15")
        cantidad_diaria = request.POST.get("diario_15")
        ipa = 0
        if anios and cantidad_diaria:
            ipa = float((float(cantidad_diaria)*float(anios))/20)


        Cirugia.objects.filter(id = cirugia_id).update(
            nombre_procedimiento = nombre_procedimiento,
            usuario_id = self.request.user.id
        )
        Paciente.objects.filter(id = cirugia.paciente_id).update(
            cedula = cedula, nombre = nombre_paciente, apellido = apellido_paciente, fecha_nac = fecha_nac, sexo = sexo, ocupacion = ocupacion, religion_id = religion,
            telefono1 = telefono1, usuario_id = self.request.user.id

        ) 

        consultapreanestesia, created = ConsultaPreanestesia.objects.update_or_create(
            cirugia_id=cirugia_id,
            defaults={
                "fecha_consulta": fecha_consulta,
                "medico_id": medico,
                "cirugia_id" : cirugia_id,
                "usuario_id": self.request.user.id,
                "antecedente_medico": antecedente_medico,
                "antecedente_qx": antecedente_qx,
                "alergia": alergia,
                "malla_i" : malla1,
                "malla_ii" : malla2,
                "malla_iii" : malla3,
                "malla_iv" : malla4,
                "peso" : peso,
                "talla" : talla,
                "imc" : imc,
                "ipa" : ipa,
                "ta": ta,
                "fr": fr,
                "fc": fc,
                "dtm" : dtm,
                "dem" : dem,
                "ao": ao,
                "rhmi": rhmi,
                "aao": aao,
                "nota": nota,
                "ekg": ekg,
                "rxtorax": rxtorax,
                "ecomls": ecomls,
                "hb": hb,
                "glisemia": glisemia,
                "hto": hto,
                "urea": urea,
                "plaq": plaq,
                "creatinina": creatinina,
                "pt": pt,
                "hiv": hiv,
                "ptt": ptt,
                "vdrl": vdrl,
                "eva_preoperatoria" : eva_preoperatoria,
                "evaluaciones" : evaluaciones,
                "recomendacion" : recomendaciones,
                "categoria_asa_i" : categoria_asa_i,
                "categoria_asa_ii" : categoria_asa_ii,
                "categoria_asa_iii" : categoria_asa_iii,
                "categoria_asa_iv" : categoria_asa_iv,
                "categoria_asa_v" : categoria_asa_v,
                "categoria_asa_e" : categoria_asa_e,
                "leucosito": leucosito

            }
        )

        consulta = ConsultaPreanestesia.objects.get(cirugia_id=kwargs["cirugia_id"])

        if medico:
            nota_qx = NotaQuirurgica.objects.filter(cirugia_id = kwargs["cirugia_id"], participante_id = 43).first()
            nota_qx, created = NotaQuirurgica.objects.update_or_create(
                cirugia_id=cirugia_id,
                participante_id = 43,
                defaults={
                    "cirugia_id":cirugia_id,
                    "medico_id": medico,
                    "usuario_id": self.request.user.id,
                    "nota": 'Agregado en consulta de preanestesia',
                    "fecha_elaboracion": datetime.now().date(),
                    "participante_id": 43,
                    "incluir": True,
                    
                }
        )

        

        for pregunta in EvaluacionPreanestesia.objects.filter(modulo = 'EVPA'):
            cantidad = 0
            respuesta_str = request.POST.get(f"pregunta_{pregunta.id}")

            if respuesta_str is None:
                continue  # no respondida

            respuesta = True if respuesta_str == "si" else False
            detalle = request.POST.get(f"detalle_{pregunta.id}", "").strip()

            if pregunta.id == 15 and detalle:
                diario = request.POST.get(f"diario_{pregunta.id}", "").strip()
                cantidad = diario

            RespuestaEvaluacion.objects.update_or_create(
                consulta=consulta,
                pregunta=pregunta,
                defaults={
                    "respuesta": respuesta,
                    "detalle": detalle,
                    "cantidad" : cantidad,
                    "usuario_id": self.request.user.id
                }
            )

        return redirect('evaluacion_preanestesia', cirugia_id = kwargs["cirugia_id"])

@add_group_name_to_context    
class historia_clinica(UserPassesTestMixin,TemplateView):
    template_name='historia_clinica.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='medicos')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['cirugia_id']
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        imagen_paciente = ImagenPhoto.objects.filter(cedula = cirugia.paciente.cedula).first()
        tratamientos = Tratamiento.objects.filter(cirugia_id = cirugia_id).order_by('-fecha_act')
                
        religion = Religion.objects.all().order_by('nombre')
        medicos = Medico.objects.filter(grupo = 'M').exclude(tipopersonal_id = 9).order_by('nombre')
        fecha_hoy = datetime.now().date()
        fecha_actual = datetime.now()
        edad_paciente=calcular_edad(cirugia.paciente.fecha_nac)
        peso = talla = imc = fr = fc = 0.00
        consultapreanestesia = ConsultaPreanestesia.objects.filter(cirugia_id = cirugia_id).first()
        if consultapreanestesia:
            peso = consultapreanestesia.peso
            talla = consultapreanestesia.talla
            imc = consultapreanestesia.imc
            fr = consultapreanestesia.fr
            fc = consultapreanestesia.fc

        evolucion_historia = []
        historia_clinica = HistoriaClinica.objects.filter(cirugia_id = cirugia_id).first()

        if historia_clinica:
            fecha_hoy = historia_clinica.fecha_consulta
            peso = historia_clinica.peso
            talla = historia_clinica.talla
            imc = historia_clinica.imc
            fr = historia_clinica.fr
            fc = historia_clinica.fc

            evolucion_historia = EvolucionHistoria.objects.filter(historiaclinica_id = historia_clinica.id).order_by('-fecha_consulta')

        
        context['peso'] = peso
        context['talla'] = talla
        context['imc'] = imc
        context['fr'] = fr
        context['fc'] = fc
        context['religion'] = religion
        context['cirugia'] = cirugia
        context['medicos'] = medicos
        context['fecha_hoy'] = fecha_hoy
        context['fecha_actual'] = fecha_actual
        context['edad_paciente'] = edad_paciente
        context['historia_clinica'] = historia_clinica
        context["tratamientos"] = tratamientos
        context["imagen_paciente"] = imagen_paciente
        context["evolucion_historia"] = evolucion_historia
        
        return context

    def post(self, request,*args, **kwargs):
        context = super().get_context_data(**kwargs) 
        cirugia_id = self.kwargs['cirugia_id']
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        fecha_consulta =  self.request.POST.get('fecha_consulta')
        cedula =  request.POST.get('cedula')
        nombre_paciente =  request.POST.get('nombre_paciente')
        apellido_paciente =  request.POST.get('apellido_paciente')
        fecha_nac =  request.POST.get('fecha_nac')
        sexo =  request.POST.get('sexo')
        direccion =  request.POST.get('direccion')
        religion =  request.POST.get('religion')
        telefono1 =  request.POST.get('telefono1')
        medico =  request.POST.get('medico')
        correo = request.POST.get('correo')
        telefono_contacto = request.POST.get('telefono_contacto')
        contacto = request.POST.get('contacto')
        req_imi = request.POST.get("req_imi") == "on"
        req_oi = request.POST.get("req_oi") == "on"
        req_cc = request.POST.get("req_cc") == "on"
        req_tap = request.POST.get("req_tap") == "on"
        req_ep = request.POST.get("req_ep") == "on"
        req_ec = request.POST.get("req_ec") == "on"
        req_epre = request.POST.get("req_epre") == "on"
        usu_epreoperatorio = request.POST.get("usu_epreoperatorio") == "on"
        usu_ecardiovascular = request.POST.get("usu_ecardiovascular") == "on"
        usu_preanestesica = request.POST.get("usu_preanestesica") == "on"
        motivo_consulta = request.POST.get("motivo_consulta") 
        enfermedad_actual = request.POST.get("enfermedad_actual") 
        idx = request.POST.get("idx") 
        servicio_cargo = request.POST.get("servicio_cargo") 
        antecedentes_familiar = request.POST.get("antecedentes_familiar")
        habito = request.POST.get("habito")
        antecedente_qx = request.POST.get("antecedente_qx")
        estudios = request.POST.get("estudios")
        diagnostico = request.POST.get("diagnostico")
        plan = request.POST.get("plan")

        peso =  request.POST.get('peso')
        peso = peso.replace(',','.')
        talla =  request.POST.get('talla')
        talla = talla.replace(',','.')
        imc =  request.POST.get('imc')
        imc = imc.replace(',','.')
        pa =  request.POST.get('pa')
        pa = pa.replace(',','.')
        fr =  request.POST.get('fr')
        fr = fr.replace(',','.')
        fc =  request.POST.get('fc')
        fc = fc.replace(',','.')
        temp =  request.POST.get('temp')
        temp = temp.replace(',','.')

        if not peso:
            peso = 0

        if not talla:
            talla = 0

        if not imc:
            imc = 0

        if not pa:
            pa = 0

        if not fr:
            fr = 0

        if not fc:
            fc = 0

        if not temp:
            temp = 0

        Paciente.objects.filter(id = cirugia.paciente_id).update(
            cedula = cedula, nombre = nombre_paciente, apellido = apellido_paciente, fecha_nac = fecha_nac, sexo = sexo,  religion_id = religion,
            telefono1 = telefono1, usuario_id = self.request.user.id, direccion = direccion, correo = correo

        ) 

        historiaclinica, created = HistoriaClinica.objects.update_or_create(
            cirugia_id=cirugia_id,
            defaults={
                "fecha_consulta": fecha_consulta,
                "medico_id": medico,
                "cirugia_id" : cirugia_id,
                "usuario_id": self.request.user.id,
                "contacto" : contacto,
                "telefono" : telefono_contacto,
                "req_imi" : req_imi,
                "req_oi" : req_oi,
                "req_cc" : req_cc,
                "req_tap" : req_tap,
                "req_ep" : req_ep,
                "req_ec" : req_ec,
                "req_epre" : req_epre,
                "usu_epreoperatorio" : usu_epreoperatorio,
                "usu_ecardiovascular" : usu_ecardiovascular,
                "usu_preanestesica" : usu_preanestesica,
                "motivo_consulta" : motivo_consulta,
                "enfermedad_actual" : enfermedad_actual,
                "idx" : idx,
                "servicio_cargo" : servicio_cargo,
                "antecedentes_familiar" : antecedentes_familiar,
                "habito" : habito,
                "antecedente_qx" : antecedente_qx,
                "estudios" : estudios,
                "diagnostico" : diagnostico,
                "plan" : plan,
                "peso" : peso,
                "talla" : talla,
                "imc" : imc,
                "pa": pa,
                "fr": fr,
                "fc": fc,
                "temp": temp,
            }
        )

        tipo_tratamiento = request.POST.get('tipo_historia_5')
        detalle_historia_5 = request.POST.get('detalle_historia_5')
        fecha_hora_tratamiento = request.POST.get('fecha_hora_tratamiento')

        historia_clinica_id = historiaclinica.id
        if tipo_tratamiento and detalle_historia_5:
            EvolucionHistoria.objects.create(
                historiaclinica_id = historia_clinica_id,
                detalle = detalle_historia_5,
                fecha_consulta = fecha_hora_tratamiento,
                usuario_id = self.request.user.id,
                tipo = tipo_tratamiento 
            )

            
        
        print('tipo_tratamiento', tipo_tratamiento)

        return redirect('historia_clinica',cirugia_id = cirugia_id )


def aplicar_descuento_corte_cuenta(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        id_detallepresupuesto = datos['id_detallepresupuesto']
        descuento = datos['descuento']
        tipo = datos['tipo']
        monto_actual = monto_descuento = porcentaje = nuevo_precio = monto_original =  0 
        cirugia_id = presupuesto_id = None
        detalle = DetallePresupuesto.objects.filter(id = id_detallepresupuesto).first()
        if detalle:
            presupuesto_id = detalle.presupuesto_id
            monto_actual = detalle.precio_usado
            if tipo == 'm' and float(descuento) > float(detalle.precio_usado):
                return JsonResponse({'mensaje': 'montomayor'})

            if tipo == 'm':
                porcentaje = float(float(descuento) / float(monto_actual)) * 100
                monto_descuento = float(descuento)

            if tipo == 'p':
                monto_descuento = float(float(monto_actual) * float(descuento))/100
                porcentaje = float(descuento)
                
            if monto_descuento > monto_actual:
                return JsonResponse({'mensaje': 'montomayor'})

            cirugia = Cirugia.objects.filter(presupuesto_id = detalle.presupuesto_id).first()
            if cirugia:
                cirugia_id = cirugia.id
                detalle_cirugia = DetalleCirugia.objects.filter(cirugia_id=cirugia.id, detalle_id=detalle.detalle_id).first()
                nuevo_precio = detalle_cirugia.precio - Decimal(monto_descuento)
                monto_original = detalle_cirugia.precio

                DetalleCirugia.objects.filter(cirugia_id=cirugia.id, detalle_id=detalle_cirugia.detalle_id).update(
                    precio= nuevo_precio  ,
                    alertaexcedente=False,
                    manual=True
                    )
                
                if detalle_cirugia.medico:
                    NotaQuirurgica.objects.filter(medico_id = detalle_cirugia.medico_id, cirugia_id = cirugia.id ).update(
                        montopendiente = float(nuevo_precio),
                        usuario_id = request.user.id,
                    )


            DetallePresupuesto.objects.filter(id = id_detallepresupuesto).update(
                        porcentaje_descuento = Decimal(porcentaje),
                        monto_descuento = Decimal(monto_descuento),
                        alertaexcedente=False,
                        precio_usado = nuevo_precio
                    )
            
            LogDescuento.objects.create(
                presupuesto_id = presupuesto_id,
                cirugia_id = cirugia_id ,
                monto_descuento = Decimal(monto_descuento),
                porcentaje_descuento = Decimal(porcentaje),
                monto_aplicar_descuento = monto_original,
                nuevo_monto = nuevo_precio,
                descripcion = 'Aplicacion de descuento',
                usuario_id = request.user.id

            )

        return JsonResponse({'mensaje': 'ok'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})


def cambio_medico_transoperatorio(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        id_notaqx = datos['id_notaqx']
        medico_id = datos['medico_id']
        cirugia = NotaQuirurgica.objects.filter(id = id_notaqx).first()
        NotaQuirurgica.objects.filter(id = id_notaqx).update(
            medico_id = medico_id,
            usuario_id = request.user.id
        )

        if cirugia:
            cirugia_id = cirugia.cirugia_id  
        else:
            cirugia_id = 0

        return JsonResponse({'idcirugia': cirugia_id})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})


def refresh_columna_medicos(request):
    id_cirugia = request.GET.get('id_cirugia')
    
    medicos = NotaQuirurgica.objects.filter(cirugia_id = id_cirugia)
    
    return render(request, 'columna_medicos.html', {'medicos': medicos})
    

def eliminar_evolucion_hc(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        evolucion_id = datos['evolucion_id']
        evolucion = EvolucionHistoria.objects.filter(id=evolucion_id).first()
        EvolucionHistoria.objects.filter(id=evolucion_id).delete()
        LogEliminacion.objects.create(
                    descripcion = 'Eliminacion de evolucion en historia clinica detalle: '+str(evolucion.detalle),
                    usuario_id = request.user.id
                )
            
            
        return JsonResponse({'mensaje': 'Eliminado'})
    else:
        return JsonResponse({'mensaje': 'Error Creando 8008 View.py'})


@csrf_exempt
def guardar_pdf(request):
    data = json.loads(request.body)
    cirugia = Cirugia.objects.get(id=data["cirugia_id"])

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)

    for pagina in data["paginas"]:
        img_data = base64.b64decode(pagina.split(",")[1])
        img = Image.open(io.BytesIO(img_data))
        pdf.setPageSize(img.size)
        pdf.drawInlineImage(img, 0, 0)
        pdf.showPage()

    pdf.save()

    archivo = ContentFile(buffer.getvalue(), f"examenes_{cirugia.id}.pdf")
    DocumentoCirugia.objects.create(cirugia=cirugia, archivo=archivo)

    return JsonResponse({"ok": True})

def paciente_documentos(request, paciente_id):
    paciente = Paciente.objects.get(id=paciente_id)

    cirugias = Cirugia.objects.filter(paciente=paciente).prefetch_related(
        'documentocirugia_set',
        'imagencirugia_set',
        'notaquirurgica_set',
    )

    cedula_img = ImagenPhoto.objects.filter(cedula=paciente.cedula).first()

    context = {
        'paciente': paciente,
        'cirugias': cirugias,
        'cedula_img': cedula_img,
        'placeholders': range(12)
    }
    return render(request, 'paciente_documentos.html', context)


def actualizar_monto_descuento(request):
    monto = request.GET.get('monto')
    tipo = request.GET.get('tipo')
    idDetalle = request.GET.get('idDetalle')
    detalle_presupuesto = DetallePresupuesto.objects.filter(id=idDetalle).first()
    if tipo == 'p':
        porcentaje = float(monto)
        montodescuento = Decimal(detalle_presupuesto.precio * Decimal(porcentaje / 100))
    else:
        montodescuento = float(monto)
        porcentaje = (float(montodescuento) / float(detalle_presupuesto.precio)) * 100
        
    if montodescuento < 0:
        if (montodescuento * -1) > detalle_presupuesto.precio:
            return JsonResponse({'precio': 'negado'})
        

    nuevo_monto = float(detalle_presupuesto.precio) + float(montodescuento)
    DetallePresupuesto.objects.filter(id=idDetalle).update(
        precio = nuevo_monto,
        porcentaje_descuento_pr = porcentaje,
        monto_descuento_pr = montodescuento,
        usuario_id = request.user.id
    )

    

    LogEliminacion.objects.create(
        descripcion='Modificacion de descuentos en presupuesto '+str(detalle_presupuesto.presupuesto_id)+ ' detalle: '+str(detalle_presupuesto.detalle),
        usuario_id = request.user.id
    )
    if detalle_presupuesto:
        actualizarCuentaxCobrar(detalle_presupuesto.presupuesto_id,detalle_presupuesto.presupuesto.paciente_id, request.user.id )
        
    

    return JsonResponse({'precio': nuevo_monto})


def actualizar_monto_en_grupo(request):
    monto = request.GET.get('monto')
    tipo = request.GET.get('tipo')
    grupo_id = request.GET.get('grupo_id')
    presupuesto_id = request.GET.get('presupuesto_id')
    presupuesto = Presupuesto.objects.filter(id = presupuesto_id).first()
    detalle_presupuesto = DetallePresupuesto.objects.filter(presupuesto_id=presupuesto_id, grupo_id = grupo_id)
    for detalle in detalle_presupuesto:
        if tipo == 'p':
            porcentaje = float(monto)
            montodescuento = Decimal(detalle.precio * Decimal(porcentaje / 100))
        else:
            montodescuento = float(monto)
            porcentaje = (float(montodescuento) / float(detalle.precio)) * 100
        
    
        nuevo_monto = float(detalle.precio) + float(montodescuento)
        DetallePresupuesto.objects.filter(id=detalle.id).update(
            precio = nuevo_monto,
            porcentaje_descuento_pr = porcentaje,
            monto_descuento_pr = montodescuento,
            usuario_id = request.user.id
        )

    

    LogEliminacion.objects.create(
        descripcion='Modificacion de descuentos en presupuesto x grupo presupuesto_id: '+str(presupuesto_id),
        usuario_id = request.user.id
    )
    if presupuesto:
        actualizarCuentaxCobrar(presupuesto_id,presupuesto.paciente_id, request.user.id )
        
    

    return JsonResponse({'precio': nuevo_monto})

def guardar_fecha_transoperatoria(request):
    if request.method == "POST":
        data = json.loads(request.body)
        historia_id = data.get("historia_id")
        fechaIF = data.get("fechaIF")
        tipo = data.get("tipo")
        fecha_dt = datetime.strptime(fechaIF, "%Y-%m-%dT%H:%M")
        print('fecha_inicio',historia_id  )
        if tipo == 'i':
            HistoriaTransOperatoria.objects.filter(cirugia_id=historia_id).update(
                fecha_inicio = fecha_dt,
                usuario_id = request.user.id
            )
        else:
            HistoriaTransOperatoria.objects.filter(cirugia_id=historia_id).update(
                fecha_fin = fecha_dt,
                usuario_id = request.user.id
            )
            
            print('fecha inicio guardada')
        
        return JsonResponse({"ok": True})

    return JsonResponse({"ok": False}, status=400)

""" from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import json """

@csrf_exempt
def guardar_cronometro(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        historia = HistoriaTransOperatoria.objects.get(
            id=data['historia_id']
        )

        c = data['cronometro']
        accion = data['accion']

        if accion == 'iniciar':
            setattr(historia, f'inicio_cronometro_{c}', timezone.now())
            setattr(historia, f'nombre_cronometro_{c}', data.get('nombre', ''))
            historia.save()

        elif accion == 'detener':
            duracion = timedelta(milliseconds=data['tiempo_ms'])
            setattr(historia, f'tiempo_cronometro_{c}', duracion)
            setattr(historia, f'inicio_cronometro_{c}', None)  # 👈 CLAVE
            historia.save()

        
        return JsonResponse({'ok': True})
    
    return JsonResponse({"ok": False}, status=400)
    

def guardar_nombre_cronometro(request):
    if request.method == "POST":
        data = json.loads(request.body)
        historia_id = data.get("historia_id")
        nombre_cronometro = data.get("nombre_cronometro")
        numero = data.get("numero")

        if numero == '1':
            HistoriaTransOperatoria.objects.filter(id=historia_id).update(
                nombre_cronometro_1 = nombre_cronometro,
                usuario_id = request.user.id
            )
            print('nombre guardado 1',historia_id )
        else:
            if numero == '2':
                HistoriaTransOperatoria.objects.filter(id=historia_id).update(
                    nombre_cronometro_2 = nombre_cronometro,
                    usuario_id = request.user.id
                )
                print('nombre guardado 2',historia_id )
            else:
                HistoriaTransOperatoria.objects.filter(id=historia_id).update(
                    nombre_cronometro_3 = nombre_cronometro,
                    usuario_id = request.user.id
                )
                print('nombre guardado 3',historia_id )
            
            
            
        
        return JsonResponse({"ok": True})

    return JsonResponse({"ok": False}, status=400)

def guardar_finalizacion_transoperatorio(request):
    if request.method == "POST":
        data = json.loads(request.body)
        historia_id = data.get("historia_id")
        HistoriaTransOperatoria.objects.filter(id=historia_id).update(
            finalizada = True,
            usuario_id = request.user.id
        )
        
        return JsonResponse({"ok": True})

    return JsonResponse({"ok": False}, status=400)

def change_numeros_factura(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        factura_id = datos['factura_id']
        numero = datos['numero']
        tipo = datos['tipo']
        proveedor_factura = datos['proveedor_factura']
        if tipo == 'nf':
            existe_numero = FacturaProveedor.objects.filter(numerodocumento = numero.strip(), proveedor_compra_id = proveedor_factura).exists()
        else:
            existe_numero = FacturaProveedor.objects.filter(numerocontrol = numero.strip(), proveedor_compra_id = proveedor_factura).exists()

        if existe_numero:
            return JsonResponse({'mensaje': 'YAEXISTENF'})


        if tipo == 'nf':
            FacturaProveedor.objects.filter(id = factura_id).update(
                usuario_id = request.user.id,
                numerodocumento = numero.strip(),
            )
        else:
            FacturaProveedor.objects.filter(id = factura_id).update(
                usuario_id = request.user.id,
                numerocontrol = numero.strip(),
            )

        LogEliminacion.objects.create(
            usuario_id = request.user.id,
            descripcion = 'Cambio de numero de factura / control: '+str(tipo)
        )

        
       
        return JsonResponse({'mensaje': 'PRECIO', 'id': factura_id})
    else:
        return JsonResponse({'mensaje': 'Error POST'})


def cambio_otros_gastos_medico_cirugia(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        id_detalle_cirugia = datos['id_detalle_cirugia']
        porcentaje_nuevo = datos['porcentaje_nuevo']
        
        DetalleFacturaProveedor.objects.filter(id = id_detalle_cirugia).update(
            porcentaje_retencion_gasto = porcentaje_nuevo,
            usuario_id = request.user.id
        )
            
    return JsonResponse({
                'congelar_cambio': 0,
            })


def cambio_otros_gastos_medico_cirugia_tx(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        id_detalle_cirugia = datos['id_detalle_cirugia']
        tx_cambio_bcv = datos['tx_cambio_bcv']
        detalle_factura = DetalleFacturaProveedor.objects.filter(id = id_detalle_cirugia).first()
        if detalle_factura.moneda_pago:
            moneda_principal = detalle_factura.moneda_pago_id
        else:
            moneda_principal = 0

        if moneda_principal > 0:
            if moneda_principal == 1:
                precio_unitario_bs = Decimal(detalle_factura.precio_unitario) * Decimal(tx_cambio_bcv)
                subtotal_bs = Decimal(precio_unitario_bs) * Decimal(detalle_factura.cantidad)
                DetalleFacturaProveedor.objects.filter(id = id_detalle_cirugia).update(
                    cambio_bcv = tx_cambio_bcv,
                    precio_bs = precio_unitario_bs,
                    subtotal_bs = subtotal_bs,
                    usuario_id = request.user.id
                )
            else:
                precio_unitario_dolares = Decimal(detalle_factura.precio_bs) / Decimal(tx_cambio_bcv)
                subtotal_dolar = Decimal(precio_unitario_dolares) * Decimal(detalle_factura.cantidad)
                DetalleFacturaProveedor.objects.filter(id = id_detalle_cirugia).update(
                    cambio_bcv = tx_cambio_bcv,
                    precio_unitario = precio_unitario_dolares,
                    subtotal = subtotal_dolar,
                    subtotal_dl = subtotal_dolar,
                    usuario_id = request.user.id
                )
            
        
            
    return JsonResponse({
                'congelar_cambio': 0,
            })


@csrf_exempt
def exportar_facturas_excel(request):

    data = json.loads(request.body)
    ids = data.get('ids', [])

    facturas = FacturaProveedor.objects.filter(id__in=ids)
           

    #print('ultima_fecha_pago', ultima_fecha_pago)
    wb = Workbook()
    ws = wb.active
    ws.title = "Facturas"

    ws.append([
        "Fecha",
        "Documento",
        "Control",
        "Proveedor",
        "Monto Bs.",
        "Base Imponible Bs",
        "Tasa BCV",
        "Base imponible $",
        "Monto $",
        "IVA",
        "Retencion IVA",
        "% I.S.L.R.",
        "Retencion I.S.L.R.",
        "I.G.T.F.",
        "Abono/Pago $",
        "Fecha Pago",
        "Saldo",
        "Forma de Pago",
        "Detalle"
    ])

    for f in facturas:
        fecha2 = ''
        ultima_fecha = AbonoCuentaPagar.objects.filter(factura_id = f.id).order_by('-fecha_pago').first()
        forma_pago = AbonoCuentaPagar.objects.filter(factura_id = f.id)
        i=0
        formas_pagos = detalle = banco_destino = monto_filtrado_pago = ''
        for fp in forma_pago:
            if i == 0:
                conector = ''
            else:
                conector = ' + '

            if fp.destino_pago:
                fp_resume = fp.destino_pago.formapago
                if fp.destino_pago.moneda_id == 1:
                    monto_filtrado_pago = str(fp.montopago)+' $'
                    banco_destino = fp.destino_pago.bancopago
                    if not banco_destino:
                        banco_destino = fp.destino_pago.formapago

                else:
                    monto_filtrado_pago = str(fp.montopago_bs)+' Bs'
                    banco_destino = fp.destino_pago.bancopago
            else:
                fp_resume = "Nota Credito"


            formas_pagos += (conector)+str(fp_resume) 
            detalle += (conector)+ str(monto_filtrado_pago) +' ' +str(banco_destino) + ' ' + str(fp.descripcion)

            i+=1


        resultado = " + ".join(dict.fromkeys(p.strip() for p in formas_pagos.split("+")))

        if ultima_fecha:
            ultima_fecha_pago = ultima_fecha.fecha_pago
        else:
            ultima_fecha = TransaccionFacturaMultiple.objects.filter(factura_id = f.id ).order_by('-transaccion_id').first()
            if ultima_fecha:
                ultima_fecha_pago = ultima_fecha.transaccion.fechatransaccion
                if ultima_fecha_pago:
                    fecha = ultima_fecha_pago.replace(tzinfo=None)
            else:
                ultima_fecha_pago = ''


        if ultima_fecha_pago != '':
            if isinstance(ultima_fecha_pago, datetime):
                fecha2 = ultima_fecha_pago.replace(tzinfo=None)

            else:
                fecha2 = ultima_fecha_pago

        ## forma pago transacciones
        if len(resultado.strip()) == 0:
            formas_pago_transaccion = TransaccionFacturaMultiple.objects.filter(factura_id = f.id)
            i=0
            forma_pago_cadena = detalle_pagado_multiple_factura = ''
            for fpt in formas_pago_transaccion:
                conector = '' if i == 0 else ' + '
                cadena = fpt.transaccion.mediomoneda
                forma_pago_cadena += str(conector) +str(cadena)
                if fpt.transaccion.mediomoneda.moneda_id == 1:
                    monto_pagado = fpt.transaccion.monto_dolar * -1 
                    signo_moneda = "$"
                else:
                    monto_pagado = fpt.transaccion.monto * -1
                    signo_moneda = "Bs"

                detalle_pagado_multiple_factura += (conector)+str(monto_pagado)+str(signo_moneda)+':'+str(fpt.transaccion.descripcion.strip())
                i+=1

            resultado = " + ".join(dict.fromkeys(p.strip() for p in forma_pago_cadena.split("+")))

        if len(detalle.strip()) == 0:
            detalle = detalle_pagado_multiple_factura + " ->(PAGO MULTIPLE FACTURAS)"

        proveedor = ""
        saldo_factura = float(f.total_operacion_dl - f.monto_abonado_factura_dl ) + f.monto_igtf_dl
        if saldo_factura < 0:
            saldo_factura = 0

        if f.proveedor_compra:
            proveedor = f.proveedor_compra.nombre

        if f.fecha_entrega:
            fecha = f.fecha_entrega.replace(tzinfo=None)

        row = [
            fecha,
            f.numerodocumento,
            f.numerocontrol,
            proveedor,
            float(f.subtotal_factura_bs),
            float(f.bi_factura_bs),
            float(f.cambio_congelado),
            float(f.bi_factura_usd),
            float(f.monto_iva_dl) + float(f.total_baseimponible_dl) + float(f.total_exento_dl)  ,
            float(f.monto_iva_bs),
            float(f.retencion_iva_monto_bs),
            float(f.porcentaje_retencion_islr),
            float(f.retencion_islr_monto_bs),
            float(f.monto_igtf),
            float(f.monto_abonado_factura_dl),
            fecha2,
            float(saldo_factura),
            resultado,
            detalle

            
        ]
        #monto_total_dolares_factura = facturascompra.monto_iva_dl + facturascompra.total_baseimponible_dl + facturascompra.total_exento_dl

        ws.append(row)

    for row in ws.iter_rows(min_row=2):
        row[0].number_format = 'DD/MM/YYYY'   # fecha

        # Columna 4 -> 2 decimales
        row[3].number_format = '#,##0.00'

        # Columna 5 -> 2 decimales
        row[4].number_format = '#,##0.00'

        # Columna 6 -> 4 decimales
        row[5].number_format = '#,##0.0000'

        # Columna 7 -> 2 decimales
        row[6].number_format = '#,##0.00'

        # Columna 8 -> 2 decimales
        row[7].number_format = '#,##0.00'

        # Columna 9 -> 2 decimales
        row[8].number_format = '#,##0.00'

        # Columna 10 -> 2 decimales
        row[9].number_format = '#,##0.00'

        # Columna 11 -> 2 decimales
        row[10].number_format = '#,##0.00'

        # Columna 12 -> 2 decimales
        row[11].number_format = '#,##0.00'

        # Columna 13 -> 2 decimales
        row[12].number_format = '#,##0.00'

        # Columna 14 -> 2 decimales
        row[13].number_format = '#,##0.00'

        row[15].number_format = 'DD/MM/YYYY'   # fecha
        row[16].number_format = '#,##0.00'

        

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = 'attachment; filename="facturas.xlsx"'

    for column in ws.columns:

        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass

        adjusted_width = max_length + 2
        ws.column_dimensions[column_letter].width = adjusted_width

    wb.save(response)

    return response


def actualizar_tasa_factura_multiple(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        fecha_cambio_congelado = datos['fecha_cambio']
        date_object = datetime.strptime(fecha_cambio_congelado, "%Y-%m-%d")
        # Query your database to retrieve the corresponding date
        monto_cambio = CambioDiaBcv(date_object)

    return JsonResponse({
                'monto_cambio': monto_cambio,
            })


def revisar_existe_factura_control(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        tipo_nro = datos['tipo_nro']
        numero = datos['numero']
        proveedor_id = datos['proveedor_id']
        if tipo_nro == 'NF':
            existe = FacturaProveedor.objects.filter(numerodocumento = numero.strip(), proveedor_compra_id = proveedor_id).exists()
        else:
            existe = FacturaProveedor.objects.filter(numerocontrol = numero.strip(), proveedor_compra_id = proveedor_id).exists()


    return JsonResponse({
                'existe': existe,
            })


def actualizar_resumen_factura(request):
    tasa_cambio = request.GET.get('tasa_cambio')
    notaentrega = NotaEntregaCompra.objects.filter(marca=True).first()
    por_retencion_iva = notaentrega.proveedor_compra.porcentaje_retencion
    print('iva retencion',por_retencion_iva )
    notatotales = NotaEntregaCompra.objects.filter(marca=True)
    total_costo_bs = total_costo_dl = porcentaje_descuento = monto_descuento_bs = monto_descuento_dl = total_exento_neto_bs = total_exento_neto_dl = total_base_imponible_neto_bs = total_base_imponible_neto_dl = total_iva_neto_bs = total_iva_dl = total_operacion_bs = total_operacion_dl = 0
    for total in notatotales:
        total_costo_bs += total.total_costo_bs_multiple + total.total_iva_bs_multiple
        #total_costo_dl += total.total_costo_dl
        porcentaje_descuento += total.porcentaje_descuento
        monto_descuento_bs += total.monto_descuento_bs
        monto_descuento_dl += total.monto_descuento_dl
        total_exento_neto_bs += total.total_exento_bs_multiple
        total_exento_neto_dl += total.total_exento_neto_dl
        total_base_imponible_neto_bs += total.total_base_imponible_bs_multiple
        total_base_imponible_neto_dl += total.total_base_imponible_neto_dl
        total_iva_neto_bs += total.total_iva_bs_multiple
        total_iva_dl += total.total_iva_dl
        total_operacion_dl += total.total_operacion_dl
        
    total_monto_retencion_iva_bs = total_iva_neto_bs * (por_retencion_iva/100)
    total_monto_retencion_iva_dl = total_iva_dl * (por_retencion_iva/100)
    monto_retencion_islr_bs = (total_exento_neto_bs + total_base_imponible_neto_bs) *  (notaentrega.porcentaje_retencion_islr/100)
    monto_retencion_islr_dl = (total_exento_neto_dl + total_base_imponible_neto_dl) *  (notaentrega.porcentaje_retencion_islr/100)

    total_operacion_bs = total_base_imponible_neto_bs + total_exento_neto_bs + total_iva_neto_bs +( total_monto_retencion_iva_bs*-1) + (monto_retencion_islr_bs*-1)
            

    detallenotaentrega = DetalleNotaEntrega.objects.filter(marca = True, notaentrega__proveedor_compra_id = notaentrega.proveedor_compra_id)

    context = {
        "total_costo_bs": total_costo_bs,
        "total_costo_dl": float(total_costo_bs) / float(tasa_cambio),
        "total_exento_neto_bs": total_exento_neto_bs,
        "total_exento_neto_dl": float(total_exento_neto_bs) / float(tasa_cambio),
        "total_base_imponible_neto_bs": total_base_imponible_neto_bs,
        "total_base_imponible_neto_dl": float(total_base_imponible_neto_bs) / float(tasa_cambio),
        "total_iva_neto_bs": total_iva_neto_bs,
        "total_iva_dl": float(total_iva_neto_bs) / float(tasa_cambio),
        "total_operacion_bs": total_operacion_bs,
        "total_operacion_dl": float(total_operacion_bs)/ float(tasa_cambio),
        "por_retencion_iva": por_retencion_iva,
        "porcentaje_retencion_islr": notaentrega.porcentaje_retencion_islr,
        "total_monto_retencion_iva_bs":total_monto_retencion_iva_bs * -1,
        "total_monto_retencion_iva_dl": (float(total_monto_retencion_iva_bs)/float(tasa_cambio)) * -1,
        "monto_retencion_islr_bs":monto_retencion_islr_bs *-1,
        "monto_retencion_islr_dl": (float(monto_retencion_islr_bs)/float(tasa_cambio))*-1
    }

    return render(request, 'tabla_conversion_multiple_factura_resume.html', context)


def agregarProductoNoInventario(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nroControl = datos['nroDocumento']
        nroDocumento = datos['nroFactura']
        idRetencion = datos['idRetencion']
        idProveedor = datos['idProveedor']
        fechaEntrega = datos['fechaEntrega']
        tasa_aplicable = datos['tasa_aplicable']
        cantidad = datos['cantidad']
        precio = datos['precio']
        descripcion = datos['descripcion']
        iva = datos['iva']
        if not iva:
            iva = 0

        precio_unico_dl = float(precio) / float(tasa_aplicable)
        tasa_aplicable = float(tasa_aplicable)

        
        porcentaje_impuesto = 0
        retencion = Retencion.objects.filter(id = idRetencion).first()
        proveedor = Proveedor.objects.filter(id = idProveedor).first()
        sustraendo_bs = 0
        if retencion and proveedor:
            tipo_persona = proveedor.rif[:1]
            if tipo_persona == 'J' or tipo_persona == 'G':
                porcentaje_impuesto = retencion.juridica 
                sustraendo_bs =  retencion.sustraendojuridica
            else:
                porcentaje_impuesto = retencion.natural
                sustraendo_bs =  retencion.sustraendonatural

        
        facturaexiste = FacturaProveedor.objects.filter(numerodocumento = nroDocumento.strip(),numerocontrol = nroControl.strip(),  proveedor_compra_id = idProveedor).first()
    
        
        if facturaexiste:
            FacturaProveedor.objects.filter(id = facturaexiste.id).update(
                numerocontrol=nroControl.strip(),
                numerodocumento=nroDocumento.strip(),
                proveedor_compra_id = idProveedor,
                fecha_entrega = fechaEntrega,
                fecha_cambio = fechaEntrega,
                usuario_id = request.user.id,
                cambio_congelado = tasa_aplicable,
                congelar_moneda = True,
                tipomoneda_id = 2,
                tipodocumento_id = 1,
                porcentaje_retencion_islr = porcentaje_impuesto,
                sustraendo_bs = sustraendo_bs,
                concepto_id = idRetencion,
                estatus = 'PEN',
                )
            
            factura_id = facturaexiste.id
        else:
            factura = FacturaProveedor.objects.create(
                numerocontrol=nroControl.strip(),
                numerodocumento=nroDocumento.strip(),
                proveedor_compra_id = idProveedor,
                fecha_entrega = fechaEntrega,
                fecha_cambio = fechaEntrega,
                usuario_id = request.user.id,
                cambio_congelado = tasa_aplicable,
                congelar_moneda = True,
                tipomoneda_id = 2,
                tipodocumento_id = 1,
                tipo = 'XX',
                porcentaje_retencion_islr = porcentaje_impuesto,
                sustraendo_bs = sustraendo_bs,
                concepto_id = idRetencion,
                )
            
            factura_id = factura.id


        DetalleFacturaProveedor.objects.create(
            factura_id = factura_id,
            no_inventario = True,
            cantidad  = float(cantidad),
            precio_unitario = precio,
            porc_iva = iva,
            descripcion = descripcion,
            montoiva = (float(precio) * float(cantidad)) * (float(iva)/100),
            precio_bs = precio,
            subtotal = float(precio) * float(cantidad),
            cambio_bcv = float(tasa_aplicable),
            congelar_moneda = True,
            subtotal_bs = float(precio) * float(cantidad),
            subtotal_dl = float(precio_unico_dl) * float(cantidad),
            precio_dl = float(precio_unico_dl),
            usuario_id = request.user.id,
            
        )
        
        data = {'idNota' : factura_id}
        return JsonResponse(data)
    else:
        return JsonResponse({'mensaje': 'Error al GUARDAR Nota de entrega'})

def lista_inventario(request):
    query = request.GET.get('q')

    inventarios = DepositoUso.objects.select_related(
        'inventario', 'deposito'
    ).filter(inventario__categoria_id__in=[1, 2],inventario__reusable = 1).exclude(deposito_id__gt = 2)

    if query:
        inventarios = inventarios.filter(
            Q(inventario__nombre__icontains=query) |
            Q(inventario__nombre_comercial__icontains=query) |
            Q(inventario__codigo__icontains=query) 
        )

    # 🔥 PAGINACIÓN (esto reemplaza el [:100])
    paginator = Paginator(inventarios, 25)
    page = request.GET.get('page')
    inventarios = paginator.get_page(page)

    # 🔥 AQUÍ ESTÁ LA CLAVE: pasamos el inventarios YA paginado
    return render(request, 'lista_inventario_reuso.html', {
        'inventarios': inventarios
    })

@csrf_exempt
def ingresar_reciclado_inventario(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        id_inventario = datos['id_inventario']
        cantidad_ingresar = datos['cantidad_ingresar']
        cantidad_no_reciclar = datos['cantidad_no_reciclar']
        deposito_afectado = datos['deposito_afectado']

        if Decimal(cantidad_ingresar) > 0:
            InventarioDescarga.objects.create(
                cantidad = Decimal(cantidad_ingresar),
                nota = 'Cantidad ingresada por reciclaje/esterizacion/uso',
                depositoentrada_id = deposito_afectado,
                inventario_id = id_inventario,
                usuario_id = request.user.id,
                tipodescarga_id = 4,
                reciclado = True,
            )
            

            DepositoUso.objects.filter(inventario_id = id_inventario, deposito_id = deposito_afectado).update(
                    cantidad_deposito = F('cantidad_deposito') + cantidad_ingresar,
                    usuario_id = request.user.id
                )

            ReutilizacionInventario.objects.create(
                inventario_id = id_inventario,
                cantidad = cantidad_ingresar,
                usuario_id =  request.user.id,
                deposito_id = deposito_afectado
            )
        
        if Decimal(cantidad_no_reciclar) > 0:
            ReutilizacionInventario.objects.create(
                inventario_id = id_inventario,
                cantidad = Decimal(cantidad_no_reciclar),
                usuario_id =  request.user.id,
                noreutilizable = True,
                deposito_id = deposito_afectado
            )

        
        return JsonResponse({'mensaje': 'Bien'})

@add_group_name_to_context    
class cuestionario_paciente(UserPassesTestMixin,TemplateView):
    template_name='cuestionario_paciente.html'
    
    def test_func(self):
        return self.request.user.groups.filter(
            Q(name='Administradores') | Q(name='medicos')
        ).exists()

    def handle_no_permission(self):
        return redirect('error_unautorized_user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cirugia_id = self.kwargs['cirugia_id']
        cirugia = Cirugia.objects.filter(id=cirugia_id).first()
        religion = Religion.objects.all().order_by('nombre')
        medicos = Medico.objects.filter(grupo = 'M').exclude(tipopersonal_id = 9).order_by('nombre')
        fecha_hoy = datetime.now().date()
        edad_paciente=calcular_edad(cirugia.paciente.fecha_nac)

        medico_consulta_preanestesia_id = None
        medico_consulta_preanestesia = Medico.objects.filter(user_id = self.request.user.id).first()
        if medico_consulta_preanestesia:
            medico_consulta_preanestesia_id = medico_consulta_preanestesia.id

        consultapreanestesia = ConsultaPreanestesia.objects.filter(cirugia_id = cirugia_id ).first()
        if consultapreanestesia:
            fecha_hoy = consultapreanestesia.fecha_consulta
            if consultapreanestesia.medico:
                medico_consulta_preanestesia_id = consultapreanestesia.medico_id

        consulta = ConsultaPreanestesia.objects.filter(
                cirugia_id=kwargs["cirugia_id"]
            ).first()
        respuestas = {}
        if consulta:
            for r in RespuestaEvaluacion.objects.filter(consulta=consulta):
                respuestas[str(r.pregunta_id)] = {
                    "respuesta": r.respuesta,
                    "detalle": r.detalle,
                    "cantidad": r.cantidad
                }


            print('respuesta', respuestas)

        
        
        preguntas = list(EvaluacionPreanestesia.objects.all().order_by('id'))
        total = len(preguntas)

        num_columnas = 4
        base = total // num_columnas
        resto = total % num_columnas

        columnas = []
        inicio = 0

        for i in range(num_columnas):
            cantidad = base + (1 if i < resto else 0)
            columnas.append(preguntas[inicio:inicio + cantidad])
            inicio += cantidad

        context['religion'] = religion
        context['cirugia'] = cirugia
        context['medicos'] = medicos
        context['fecha_hoy'] = fecha_hoy
        context['edad_paciente'] = edad_paciente
        context['preguntas_col1'] = columnas[0]
        context['preguntas_col2'] = columnas[1]
        context['preguntas_col3'] = columnas[2]
        context['preguntas_col4'] = columnas[3]
        context['consultapreanestesia'] = consultapreanestesia
        context["respuestas"] = respuestas
        context["medico_consulta_preanestesia_id"] = medico_consulta_preanestesia_id

        return context

    def post(self, request, *args, **kwargs):
        cirugia_id = self.kwargs['cirugia_id']
        
        # 1. Buscamos la consulta principal. Si no existe para esta cirugía, la creamos.
        consulta, created = ConsultaPreanestesia.objects.get_or_create(
            cirugia_id=cirugia_id,
            defaults={'usuario': request.user}
        )

        paciente = consulta.cirugia.paciente # Accedemos al modelo Paciente
        # --- 1. PROCESAR NUEVA FOTO (Si el paciente capturó una) ---
        foto_b64 = request.POST.get('foto_paciente')
        
        if foto_b64 and ";base64," in foto_b64:
            # Separamos el encabezado del contenido
            format, imgstr = foto_b64.split(';base64,') 
            ext = format.split('/')[-1] # Extraemos la extensión (jpeg, png, etc.)
            
            # Creamos un nombre de archivo único
            nombre_foto = f"perfil_{paciente.id}_{cirugia_id}.{ext}"
            
            # Convertimos el Base64 a un archivo de contenido de Django
            data = ContentFile(base64.b64decode(imgstr), name=nombre_foto)
            
            # Guardamos en el campo fotoperfil del modelo Paciente
            paciente.fotoperfil.save(nombre_foto, data, save=True)

        # --- PROCESAR FIRMA EN LA CONSULTA ---
        firma_b64 = request.POST.get('firma_paciente')
        if firma_b64 and ";base64," in firma_b64:
            # El signature_pad siempre envía PNG
            format_f, imgstr_f = firma_b64.split(';base64,')
            nombre_firma = f"firma_consulta_{consulta.id}.png"
            # Guardamos directamente en el nuevo campo del modelo
            consulta.firma.save(nombre_firma, ContentFile(base64.b64decode(imgstr_f)), save=True)

        
        # 2. Obtenemos todas las preguntas maestras para recorrerlas
        preguntas_maestras = EvaluacionPreanestesia.objects.all()
        
        for p_maestra in preguntas_maestras:
            # Extraer valores del formulario usando los nombres dinámicos pregunta_{id}
            # El checkbox de HTML envía 'on' si está marcado (True)
            resp_valor = request.POST.get(f'pregunta_{p_maestra.id}') == 'on'
            
            # Extraer detalle y cantidad
            detalle_valor = request.POST.get(f'detalle_{p_maestra.id}', '')
            
            # Caso especial para la pregunta 15 (cantidad de cigarrillos)
            cantidad_valor = 0
            if p_maestra.id == 15:
                cant_input = request.POST.get(f'diario_{p_maestra.id}', 0)
                cantidad_valor = int(cant_input) if cant_input and str(cant_input).isdigit() else 0

            # 3. Guardar o Actualizar la respuesta específica
            # Usamos update_or_create para no duplicar registros si el médico guarda varias veces
            RespuestaEvaluacion.objects.update_or_create(
                consulta=consulta,
                pregunta=p_maestra,
                defaults={
                    'respuesta': resp_valor,
                    'detalle': detalle_valor,
                    'cantidad': cantidad_valor,
                    'usuario': request.user
                }
            )

        # 4. (Opcional) Aquí puedes actualizar campos de la ConsultaPreanestesia 
        # si el formulario también incluye peso, talla, etc.
        # consulta.peso = request.POST.get('peso')
        # consulta.save()

        #return redirect('nombre_de_tu_vista_exito', cirugia_id=cirugia_id)
        return render(request, 'gracias.html')


def actualizar_retencion_factura_medico(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        concepto_id = datos['concepto_id']
        factura_id = datos['factura_id']

        FacturaProveedor.objects.filter(id = factura_id).update(
            concepto_id = concepto_id,
            usuario_id = request.user.id
        )
        
        return JsonResponse({'mensaje': 'CAMBIO CONGELADO correctamente'})
    else:
        return JsonResponse({'mensaje': 'Error CAMBIO CONGELADO datos'})



def nueva_distribucion(request, dpgo_id):
    if request.method == 'POST':
        moneda_id = request.POST.get('moneda_id')
        monto = request.POST.get('monto')
        monto_bs = request.POST.get('monto_bs')
        tasa_tx = request.POST.get('tasa_tx')
        dpgo = DistribucionPagoMedico.objects.filter(id=dpgo_id).first()
        factura = FacturaProveedor.objects.filter(id = dpgo.factura_id, tipo = 'FM').first()
        moneda = Moneda.objects.all()
        distribucion = DistribucionPagoMedico.objects.filter(factura_id = dpgo.factura_id).order_by('-id')

       
        if float(tasa_tx) == 0 or tasa_tx == '':
            return render(request, 'tabla_distribucion_pago.html', {
                'error': 'La tasa de cambio debe tener un valor !',
                'factura': factura,
                'distribucion' : distribucion,
                'moneda':moneda,
                'tasa_bcv_calculo':tasa_tx
            })


        if round(Decimal(monto),2) > round(Decimal(factura.saldo_dl_distribucion_pago),2):
            return render(request, 'tabla_distribucion_pago.html', {
                'error': 'El monto a pagar no puede exceder el saldo !',
                'factura': factura,
                'distribucion' : distribucion,
                'moneda':moneda,
                'tasa_bcv_calculo':tasa_tx
            })


        if not moneda_id:
            return render(request, 'tabla_distribucion_pago.html', {
                'error': 'Debe seleccionar una moneda',
                'factura': factura,
                'distribucion' : distribucion,
                'moneda':moneda,
                'tasa_bcv_calculo':tasa_tx
            })

        if float(monto) == 0 or float(monto_bs) == 0:
            return render(request, 'tabla_distribucion_pago.html', {
                'error': 'Ningun monto debe ir en 0, revise montos',
                'factura': factura,
                'distribucion' : distribucion,
                'moneda':moneda,
                'tasa_bcv_calculo':tasa_tx
            })


        

        # tu lógica aquí (crear nueva distribución)
        DistribucionPagoMedico.objects.create(
            factura_id=dpgo.factura_id,
            moneda_id = moneda_id,
            usuario=request.user,
            monto=Decimal(monto),
            monto_bs= Decimal(monto_bs),
            tx = Decimal(tasa_tx)
        ) 
        
        
        nuevo_registro = DistribucionPagoMedico.objects.filter(factura_id = dpgo.factura_id, monto = 0).exists()
        if not nuevo_registro:
            DistribucionPagoMedico.objects.create(
            factura_id = factura.id,
            monto = 0,
            usuario_id = request.user.id
        ) 

        factura = FacturaProveedor.objects.filter(id = dpgo.factura_id, tipo = 'FM').first()
        if nuevo_registro and Decimal(factura.saldo_dl_distribucion_pago) <= 0.01:
            DistribucionPagoMedico.objects.filter(factura_id = dpgo.factura_id, monto = 0).delete()
            distribucion = DistribucionPagoMedico.objects.filter(factura_id = dpgo.factura_id).order_by('-id')
        
        
        # recargar tabla
        return render(request, 'tabla_distribucion_pago.html', {
            'factura': factura,
            'distribucion' : distribucion,
            'moneda':moneda,
            'tasa_bcv_calculo':tasa_tx
        })


def eliminar_distribucion(request, dpgo_id):
    if request.method == 'POST':
        dpgo = DistribucionPagoMedico.objects.get(id=dpgo_id)
        factura = dpgo.factura
        moneda = Moneda.objects.all()
        
        distribucion = DistribucionPagoMedico.objects.filter(factura_id = dpgo.factura_id).order_by('id')
        dpgo.delete()

        factura = FacturaProveedor.objects.filter(id = dpgo.factura_id, tipo = 'FM').first()
        nuevo_registro = DistribucionPagoMedico.objects.filter(factura_id = dpgo.factura_id, monto = 0).exists()
        if not nuevo_registro and Decimal(factura.saldo_dl_distribucion_pago) > 0.01:
            DistribucionPagoMedico.objects.create(
                factura_id = factura.id,
                usuario_id = request.user.id,
            )


        # recargar tabla
        return render(request, 'tabla_distribucion_pago.html', {
            'factura': factura,
            'distribucion' : distribucion,
            'moneda':moneda,
            'tasa_bcv_calculo':dpgo.tx
        })

@add_group_name_to_context    
class pagos_prefactura_medico(TemplateView): 
    template_name='pagos_prefactura_medico.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        factura_id = self.kwargs['factura_id']
        factura = FacturaProveedor.objects.filter(id = factura_id, tipo = 'FM').first()
        if factura.numerodocumento[:3] != 'PRE':
            numero_factura = factura.numerodocumento
            numero_control = factura.numerocontrol
        else:
            numero_factura = ''
            numero_control = ''

        distribucion = DistribucionPagoMedico.objects.filter(factura_id = factura.id).order_by('id')
        nuevo_registro = DistribucionPagoMedico.objects.filter(factura_id = factura.id, monto = 0).exists()
        if not nuevo_registro and Decimal(factura.saldo_dl_distribucion_pago) > 0.01:
            DistribucionPagoMedico.objects.create(
            factura_id = factura.id,
            monto = 0,
            usuario_id = self.request.user.id
            ) 


        cambio_hoy=CambioDiaBcv(datetime.now())
        retencionpendiente = RetencionPendiente.objects.filter(medico_id = factura.proveedor_id, aplicado = False)
        
        DetalleFacturaProveedor.objects.filter(factura_id=factura_id, precio_unitario__lt = 0).delete()
        baseimponible_bs = 0
        baseimponible_usd = 0
        if retencionpendiente:
            baseimponible_bs = retencionpendiente.aggregate(total_bs=Sum('baseimponible'))['total_bs']
            baseimponible_usd = retencionpendiente.aggregate(total_usd=Sum('baseimponible_usd'))['total_usd']
            
        total_baseimponible=0
        facturadetalle = DetalleFacturaProveedor.objects.filter(factura_id=factura_id, precio_unitario__gt = 0).order_by('id')
        if facturadetalle:
            baseimponibleactual = facturadetalle.aggregate(baseimponible=Sum(F('precio_bs')*F('cantidad')))['baseimponible']
            gastos = facturadetalle.aggregate(totalgastos=Sum('gastos_bs'))['totalgastos']
            total_baseimponible = baseimponible_bs + (baseimponibleactual-gastos)
        
        resultado = montoaretener(total_baseimponible, 'N',factura.concepto_id )
        monto_retencion = resultado['monto_retener']
        sustraendo = resultado['sustraendo']
        porcentaje_retencion_islr = resultado['porcentaje']
        neto_retener = monto_retencion - sustraendo 

        if factura.tipodocumento_id in [1, 5]:
            FacturaProveedor.objects.filter(id = factura_id, tipo = 'FM').update(
                porcentaje_retencion_islr = porcentaje_retencion_islr,
                sustraendo_bs = sustraendo
            )
        else:
            FacturaProveedor.objects.filter(id = factura_id, tipo = 'FM').update(
                porcentaje_retencion_islr = 0,
                sustraendo_bs = 0
            )

        factura = FacturaProveedor.objects.filter(id = factura_id, tipo = 'FM').first()

        bancolocal = BancoLocal.objects.filter(activo = True).order_by('banco') 
        moneda_congelada = DetalleFacturaProveedor.objects.filter(factura_id=factura_id, congelar_moneda = True).count()
        facturadetalle = DetalleFacturaProveedor.objects.filter(factura_id=factura_id).order_by('id')
        if facturadetalle:
            total_gastos = facturadetalle.aggregate(total_gastos=Sum('gastos'))
            total_gastos_bs = facturadetalle.aggregate(total_gastos_bs=Sum('gastos_bs'))
            total_factura = facturadetalle.aggregate(total_factura=Sum(F('precio_unitario')*F('cantidad')))
            total_factura_bs = facturadetalle.aggregate(total_factura_bs=Sum(F('precio_bs')*F('cantidad')))
            total_gastos = total_gastos['total_gastos']
            total_gastos_bs = total_gastos_bs['total_gastos_bs']
            total_factura = total_factura['total_factura']
            total_factura_bs = total_factura_bs['total_factura_bs']
        else:
            total_gastos = 0
            total_gastos_bs = 0
            total_factura = 0
            total_factura_bs = 0

        proveedores = Medico.objects.filter(grupo='M').exclude(tipopersonal_id = 9).order_by('nombre')
        moneda = Moneda.objects.all()
        retenciones = Retencion.objects.all().order_by('nombre')
        tipodocumento = TipoDocumento.objects.filter(activo_factura_medico = True).order_by('nombre')
        retencion = Retencion.objects.filter(id=factura.concepto_id).first()
        """ if moneda_congelada > 0:
            pagomedico = PagoMedico.objects.filter(medico_id=factura.proveedor,moneda_id = 2 ).order_by('nombre')
        else: """
        pagomedico = PagoMedico.objects.filter(medico_id=factura.proveedor_id).order_by('nombre')
            
        ##
        gastos = factura.administrativo
        tasa_bcv_calculo = CambioDiaBcv(datetime.now())
        if factura.cambio_congelado > 0:
                tasa_bcv_calculo = factura.cambio_congelado
        
        
        pretencion=0
        montoretencion = 0
        fecha_hoy = datetime.now().date()
        formapago = FormaPago.objects.all().order_by('nombre')
        bancos = Banco.objects.all().order_by('nombre')

        registro_documento_factura = FacturaMedico.objects.filter(factura_id = factura.id, medico_id = factura.proveedor_id ).first()
        comprobante_retencion = 0
        if registro_documento_factura:
            if registro_documento_factura.comprobante:
                comprobante_retencion = 1

        monto_total_pagado = monto_correcto_a_pagar_con_retencion_aplicada = 0
        montoretencion_retencion_islr = factura.retencion_islr_monto_bs
        if montoretencion_retencion_islr < 0:
            montoretencion_retencion_islr = montoretencion_retencion_islr * -1
        
        total_monto_recibos = factura.total_pagos_recibos_bs

        if total_monto_recibos < 0:
            total_monto_recibos = total_monto_recibos * -1
            
        monto_total_pagado = total_monto_recibos + factura.total_transacciones_bs
        monto_correcto_a_pagar_con_retencion_aplicada = monto_total_pagado - montoretencion_retencion_islr
        nota_credito_favor_clinica = monto_correcto_a_pagar_con_retencion_aplicada - monto_total_pagado
        

        pagos_realizados = Transaccion.objects.filter(cuentapagar_id = factura.id).order_by('fecha_act')
        if not pagos_realizados:
            facturas_recibo_ids = PagoReciboFacturaMedico.objects.filter(
                factura_legal_id=factura.id
            ).values_list('factura_recibo_id', flat=True)
            pagos_realizados = Transaccion.objects.filter(cuentapagar_id__in=facturas_recibo_ids).order_by('fecha_act')
        
        context['moneda'] = moneda
        context['bancos'] = bancos
        context['numero_factura'] = numero_factura
        context['numero_control'] = numero_control
        context['bancolocal'] = bancolocal
        context['formapago'] = formapago
        context['factura'] = factura
        context['gastosadm'] = total_gastos
        context['fecha_hoy'] = fecha_hoy
        context['total_gastos_bs'] = total_gastos_bs
        context['tasa_bcv_calculo'] = tasa_bcv_calculo
        context['proveedores'] = proveedores
        context['pagomedico'] = pagomedico
        context['pretencion'] = pretencion
        context['distribucion'] = distribucion
        context['retenciones'] = retenciones
        context['tipodocumento'] = tipodocumento
        context['neto_pagar'] = total_factura - total_gastos
        context['neto_pagar_bolivar'] = total_factura_bs - total_gastos_bs
        context['montoretencion'] = montoretencion
        context['facturadetalle'] = facturadetalle
        context['moneda_congelada'] = moneda_congelada
        context['pagos_realizados'] = pagos_realizados
        context['comprobante_retencion'] = comprobante_retencion
        return context

    def post(self, request, **kwargs):
        context = super().get_context_data(**kwargs)  
        factura_id = self.kwargs['factura_id'] 
        factura_afectada = FacturaProveedor.objects.filter(id = factura_id).first()
        if not factura_afectada:
            return redirect('pagos_prefactura_medico', factura_id = factura_id)

        if 'guardar_prefactura' in request.POST:
            nrodocumento = request.POST['nrodocumento']
            nrocontrol = request.POST['nrocontrol']
            fechaentrega = request.POST['fechaentrega']
            if not nrodocumento.strip() or not nrocontrol.strip():
                messages.error(request, 'Error : Debe colocar un numero de factura y numero de control, revise!')
                return redirect('pagos_prefactura_medico', factura_id = factura_id)


            FacturaProveedor.objects.filter(id=factura_id).update(
                numerodocumento= nrodocumento,
                numerocontrol= nrocontrol,
                tipodocumento_id = 1,
                fecha_entrega = fechaentrega,
                usuario_id = self.request.user.id,
                tipo = 'FM'
            ) 
            return redirect('pagos_prefactura_medico', factura_id = factura_id)
            
            """ if factura.tipodocumento_id != 1:
                porcentaje_retencion_islr = 0
                montoretenido = 0
            else:
                porcentaje_retencion_islr = factura.porcentaje_retencion_islr
                montoretenido = (factura.retencion_islr_monto_bs) *-1 """
                
            """ 
            if not factura_medico:
                FacturaMedico.objects.create(
                    fecha_entrega = fechaentrega,
                    numerodocumento= nrodocumento,
                    numerocontrol= nrocontrol,
                    pretencion = porcentaje_retencion_islr,
                    baseimponible = (factura.total_baseimponible_bs + factura.total_exento_bs) ,
                    montoretenido = montoretenido,
                    concepto_id = factura.concepto_id,
                    medico_id = factura.proveedor_id,
                    usuario_id = self.request.user.id,
                    factura_id = factura.id
                    
                ) """
        
            """ if factura.congelar_moneda:
                tasa_bcv_calculo = factura.cambio_congelado """
                
            #retencion_aplicada = DetalleFacturaProveedor.objects.filter(factura_id=factura_id, precio_unitario__lt = 0).count()

            """ cirugiaspagadas = DetalleFacturaProveedor.objects.filter(factura_id=factura_id, precio_unitario__gt = 0)
            for cirpag in cirugiaspagadas:
                NotaQuirurgica.objects.filter(cirugia_id=cirpag.cirugia_id, participante_id=cirpag.detalle_id, medico_id = cirpag.factura.proveedor_id).update(
                    pagado=True
                )
                DetalleCirugia.objects.filter(cirugia_id=cirpag.cirugia_id, detalle_id=cirpag.detalle_id, medico_id = cirpag.factura.proveedor_id).update(
                    pagado=True
                ) """
            
        if 'guardar_pago' in request.POST:   
            for i in range(len(request.POST.getlist('mul_pago_cuenta_medico'))):
                selected_row_id = request.POST.getlist('mul_pago_cuenta_medico')[i]
                selected_origen_id = request.POST.getlist('mul_pago_origen_fondos')[i]
                montofraccion = (request.POST.getlist('mul_montofraccion')[i]).replace(',','.')
                monedafraccion = request.POST.getlist('mul_monedapago')[i]
                referencia = request.POST.getlist('mul_referencia')[i]
                descripcion = request.POST.getlist('mul_nota')[i]
                montofraccion = Decimal(montofraccion)
                if monedafraccion == 'Dolares':
                    montofraccion_usd = montofraccion
                    montofraccion_bs = montofraccion * factura_afectada.cambio_congelado
                else:
                    montofraccion_bs = montofraccion
                    montofraccion_usd = montofraccion / factura_afectada.cambio_congelado


                cuenta_origen = BancoLocal.objects.filter(id = selected_origen_id).first()
                forma_pago_medico = PagoMedico.objects.filter(id=selected_row_id).first()
                


                Transaccion.objects.create(
                    pagomedico_id = selected_row_id, #cuenta usada para pago del medico
                    bancolocal_id = selected_origen_id, #banco usado
                    referencia = referencia,
                    descripcion = 'Pago Medico : ' + str(factura_afectada.proveedor),
                    monto = montofraccion_bs * -1 ,
                    monto_dolar = montofraccion_usd * -1 ,
                    usuario_id =  self.request.user.id,
                    nota = descripcion,
                    mediomoneda_id = forma_pago_medico.formapago_id,
                    fechatransaccion = datetime.now(),
                    cuentapagar_id = factura_id
                    #registro_documento_id = registro_id,
                ) 
                
            return redirect('pagos_prefactura_medico', factura_id = factura_id)


def validar_factura_medico_existe(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        nFactura = datos['nFactura']
        nControl = datos['nControl']
        proveedor = datos['proveedor']
        idfactura = datos['idfactura']

        campo = datos['campo']
        if campo == 'F':
            existe = FacturaProveedor.objects.filter(proveedor_id = proveedor, numerodocumento = nFactura.strip()).exists()
        else:
            existe = FacturaProveedor.objects.filter(proveedor_id = proveedor, numerocontrol = nControl.strip()).exists()

        if existe:
            respuesta = 'existe'
        else:
            if campo == 'F':
                FacturaProveedor.objects.filter(id = idfactura).update(
                    numerodocumento = nFactura.strip()
                )
            else:
                FacturaProveedor.objects.filter(id = idfactura).update(
                    numerocontrol = nControl.strip()
                )


            respuesta = 'NO'
    
        return JsonResponse({'respuesta': respuesta})
    else:
        return JsonResponse({'respuesta': 'Error  8229 View.py'})

def actualizar_tabla_distribucion(request):
    factura_id = request.GET.get('factura_id')
    distribucion_pago = DistribucionPagoMedico.objects.filter(factura_id=factura_id)
    
    # Renderizamos solo el fragmento del HTML
    return render(request, 'tabla_distribucion_pago_en_pago.html', {
        'distribucion_pago': distribucion_pago
    })


""" class lista_medico_cxc(TemplateView):
    template_name = 'lista_medico_cxc.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cambio = float(CambioDiaBcv(datetime.now()))
        # 1. Obtenemos el ID del médico desde la URL (?medico_id=X)
        medico_id = self.request.GET.get('medico_id')
        
        # 2. Todos los médicos para el select
        context['todos_los_medicos'] = Medico.objects.filter(grupo='M').order_by('nombre')
        context['cambio'] = cambio
        
        if medico_id:
            try:
                medico = Medico.objects.get(id=medico_id)
                context['medico_seleccionado'] = medico
                
                # 3. Filtramos CIRUGIAS donde el médico es el PRINCIPAL
                context['cirugias'] = Cirugia.objects.filter(
                    medico_ppal=medico
                ).exclude(estatus_id=11).order_by('-fecha_procedimiento')
            except Medico.DoesNotExist:
                context['cirugias'] = []
            

            
        return context """

class lista_medico_cxc(TemplateView):
    template_name = 'lista_medico_cxc.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medico_id = self.request.GET.get('medico_id')
        context['todos_los_medicos'] = Medico.objects.filter(grupo='M').order_by('nombre')
        
        if medico_id:
            medico = Medico.objects.get(id=medico_id)
            context['medico_seleccionado'] = medico
            
            # 1. Obtenemos las cirugías base (excluyendo preingresos)
            cirugias_base = Cirugia.objects.filter(
                medico_ppal=medico,
                id__gt = 1100,
            ).exclude(
                estatus_id=11
            ).order_by('-fecha_procedimiento')
            
            cirugias_pendientes = []
            total_general_pendiente = 0

            # 2. Filtramos manualmente las que tienen saldo > 0
            for c in cirugias_base:
                cuenta = CuentaxCobrar.objects.filter(cirugia=c).first()
                
                # Calculamos el saldo usando las propiedades del modelo cuenta
                saldo = cuenta.total_cobrar_monto if cuenta else 0
                
                if saldo > 0:
                    c.monto_total = cuenta.total_monto
                    c.monto_pagado = abs(cuenta.total_monto_pagado)
                    c.saldo_pendiente = saldo
                    c.cxc_id = cuenta.id  # <--- GUARDAMOS EL ID PARA EL LINK
                    
                    total_general_pendiente += saldo
                    cirugias_pendientes.append(c)

            # 3. Enviamos al contexto solo las pendientes
            context['cirugias'] = cirugias_pendientes
            context['cantidad_pendientes'] = len(cirugias_pendientes) # <--- Agregamos esto
            context['total_general_pendiente'] = total_general_pendiente
                
        return context

def unidades_inventario(request):
    inventarios = Inventario.objects.filter(producto_activo = True)

    for inventario in inventarios:
        unidad_conversion = inventario.unidad_conversion
        DepositoUso.objects.filter(inventario_id = inventario.id).update(
            cantidad_deposito = F('cantidad_deposito') * Decimal(unidad_conversion)
        )

        Inventario.objects.filter(id=inventario.id).update( 
            unidad_conversion = 1
        )

    print('termine....')
    return redirect('index')