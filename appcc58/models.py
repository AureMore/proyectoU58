from django.db import models
from django.contrib.auth.models import User
from datetime import date, datetime
from django.db.models import Sum,F, Q, Subquery, DecimalField, ExpressionWrapper
from decimal import Decimal
import math
import os

def get_current_time():
    return datetime.now().time()


# Create your models here.

class Referencia(models.Model):
    nombre=models.CharField(max_length=200,unique=True,blank=False,verbose_name='Nombre')
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Referencia'
        verbose_name_plural = 'Referencias'
        
class Religion(models.Model):
    nombre=models.CharField(max_length=200,unique=True,blank=False,verbose_name='Religion')
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Religion'
        verbose_name_plural = 'Religiones'
 

class CambioBcv(models.Model):
    cambio = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='Cambio Bcv')
    fecha = models.DateTimeField(auto_now=True,verbose_name='Fecha Actualizacion')
    fecha_cambio = models.DateField(unique=True, null=True, blank=True, verbose_name='Fecha del Cambio')

    class Meta:
            verbose_name = 'CambioBcv'
            verbose_name_plural = 'CambiosBcv'
            
    def __str__(self):
            return str(self.cambio)
    
class CentroCostoFacturaCompra(models.Model):
    nombre = models.CharField(max_length=25, unique=True, verbose_name='nombre')
    descripcion = models.CharField(max_length=150, null=True, blank=True,verbose_name='descripcion')
    cuenta_asociada =  models.CharField(max_length=50, null=True, blank=True, verbose_name='cuenta_asociada')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='fecha_creacion')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')

    def __str__(self):
        return str(self.nombre)

    class Meta:
        verbose_name = 'CentroCostoFacturaCompra'
        verbose_name_plural = 'CentroCostoFacturaCompras'
        

class Responsable(models.Model):
    SEXO_CHOICES = (
        ('F', 'Femenino'),
        ('M', 'Masculino'),
    )
    
    cedula= models.CharField(max_length=15, blank=True, null=True,unique=True, verbose_name='Cedula')
    nombre= models.CharField(max_length=100, null=False, default='Nombre responsable', verbose_name='Nombres ')
    apellido= models.CharField(max_length=100, null=False, default='Apellido responsable' , verbose_name='Apellidos ')
    direccion=models.TextField(max_length=250,null=True, blank=True, default="Escriba su direccion", verbose_name='Direccion / Zona')
    direccion_trabajo=models.TextField(max_length=250,null=True, blank=True, default="Direccion de trabajo", verbose_name='Direccion / Zona')
    fecha_desde=models.DateField(null=True, blank=True, default=date.today,verbose_name='Cliente desde')
    fecha_act=models.DateTimeField(null=True, blank=True, auto_now=True, verbose_name='Actualizado el')
    telefono1=models.CharField(max_length=11,null=False, blank=True, verbose_name='Telefono principal')
    sexo=models.CharField(max_length=1,choices=SEXO_CHOICES, default='M', verbose_name='Sexo')
    trabajo = models.CharField(max_length=50,null=True,blank=True,verbose_name='Trabajo')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    
    def __str__(self):
        return f'{self.cedula} - {self.nombre} - {self.apellido}'


    class Meta:
        verbose_name = 'Responsable'
        verbose_name_plural = 'Responsables'

class BaremoPagoTercero(models.Model):
    nombre = models.CharField(unique=True, max_length=250)
    precio = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name='precio')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True, verbose_name='Usuario')
    fecha_act=models.DateTimeField(null=True, blank=True, auto_now=True, verbose_name='Actualizado el')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'BaremoPagoTercero'
        verbose_name_plural = 'BaremoPagoTerceros'



class Paciente(models.Model):
    STATUS_CHOICES = (
        ('A', 'Activo'),
        ('S', 'Suspendido'),
        ('F', 'Fallecido'),
        ('X', 'Temporal'),
    )
    SEXO_CHOICES = (
        ('F', 'Femenino'),
        ('M', 'Masculino'),
    )
    
    STATUS_CIVIL = (
        ('S', 'Soltero(a)'),
        ('C', 'Casado(a)'),
        ('V', 'Viudo(a)'),
        ('D', 'Divorsiado(a)'),
        ('O', 'Otro'),
    )
    
    fotoperfil = models.ImageField(null=True, blank=True,default='C:/proyectoU58/photos/VU58Foto.png' ,upload_to="photos/")
    cedula= models.CharField(max_length=15, unique=True, blank=False, null=False, verbose_name='Cedula')
    rif= models.PositiveIntegerField(blank=True, null=True, verbose_name='Rif')
    nombre= models.CharField(max_length=100, null=False, default='Nombre Paciente', verbose_name='Nombres ')
    apellido= models.CharField(max_length=100, null=False, default='Apellido Paciente' , verbose_name='Apellidos ')
    direccion=models.TextField(max_length=500,null=True, blank=True, default="Escriba su direccion", verbose_name='Direccion / Zona')
    fecha_nac=models.DateField(null=True, blank=True, verbose_name='Fecha nacimiento')
    fecha_desde=models.DateField(null=True, blank=True,default=date.today, verbose_name='Cliente desde')
    fecha_act=models.DateTimeField(null=True, blank=True, auto_now=True, verbose_name='Actualizado el')
    lugar_nac=models.CharField(max_length=100,null=True, blank=True, verbose_name='Lugar nacimiento')
    telefono1=models.CharField(max_length=20,null=True, blank=True, verbose_name='Telefono principal')
    telefono2=models.CharField(max_length=20,null=True, blank=True, verbose_name='Telefono secundario')
    sexo=models.CharField(max_length=1,choices=SEXO_CHOICES, default='F', verbose_name='Sexo')
    correo=models.EmailField(blank=True,null=True, verbose_name='Email')
    civil=models.CharField(max_length=1,choices=STATUS_CIVIL, default='S', verbose_name='Estado civil')
    ocupacion = models.CharField(max_length=50,null=True,blank=True,verbose_name='Ocupacion')
    nacionalidad=models.CharField(max_length=50,blank=True,null=True, default='Venezolana', verbose_name='Nacionalidad')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Usuario')
    status=models.CharField(max_length=1,choices=STATUS_CHOICES, default='A', verbose_name='Estatus')
    referencia = models.ForeignKey(Referencia, on_delete=models.SET_NULL, null=True,blank=True, verbose_name='Referencia')
    religion = models.ForeignKey(Religion,null=True,blank=True, on_delete=models.SET_NULL, verbose_name='Religion')
    responsable = models.ForeignKey(Responsable, on_delete=models.SET_NULL, null=True, blank=True , verbose_name='Responsable')
    
    def __str__(self):
        return f'{self.cedula} - {self.nombre} - {self.apellido}'


    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        
class Habitacion(models.Model):
    habitacion = models.CharField(max_length=50, null=True,unique=True, blank=True, verbose_name='Habitacion')
    nota = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nota')
   
    def __str__(self):
        return self.habitacion

    class Meta:
        verbose_name = 'Habitacion'
        verbose_name_plural = 'Habitaciones'
        
        
class Plantilla(models.Model):
    nombre = models.CharField(max_length=50, null=True,unique=True, blank=True, verbose_name='Plantilla')
   
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Plantilla'
        verbose_name_plural = 'Plantillas Baremos'
        
class CategoriaInventario(models.Model):
    nombre = models.CharField(max_length=200, null=True, blank=True, verbose_name='Categoria Inventario')
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'CategoriaInventario'
        verbose_name_plural = 'Categorias de Inventarios' 
        
        
class Convenio(models.Model):
    rif = models.CharField(max_length=15, unique=True,null=False, blank=False, verbose_name='Rif Empresa')
    nombre = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nombre Empresa')
    sucursal = models.CharField(max_length=200, null=True, blank=True, verbose_name='Sucursal Empresa')
    telefono1 = models.CharField(max_length=11, null=True, blank=True, verbose_name='Telefonos')
    telefono2 = models.CharField(max_length=11, null=True, blank=True, verbose_name='Telefonos')
    correo=models.EmailField(blank=True,null=True, verbose_name='Email')
    nota = models.CharField(max_length=250, null=True, blank=True, verbose_name='Nota')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Convenio'
        verbose_name_plural = 'Convenios'  
        
class TipoProcedimiento(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True, verbose_name='Tipo Procedimiento')
   
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'TipoProcedimiento'
        verbose_name_plural = 'Tipos de Procedimientos'
        
 
        
class DetalleBaremo(models.Model):
    nombre = models.CharField(max_length=200, null=True, blank=True, verbose_name='Detalle')
    categoriainventario = models.ForeignKey(CategoriaInventario,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Categoria de Inventario')
    posicion = models.PositiveIntegerField(default=0,verbose_name='Posicion de Orden' )
    pagarmedico = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='% pagar medico')
    preingreso = models.BooleanField(verbose_name='preingreso', default=False)
    activar_subbaremo = models.BooleanField(verbose_name='activar_subbaremo', default=False)
    activar_retencion = models.BooleanField(verbose_name='activar_retencion', default=True)
   
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'DetalleBaremo'
        verbose_name_plural = 'Nombre Detalles Baremos'
        
class Moneda(models.Model):
    nombre = models.CharField(max_length=20,null=True, blank=True, verbose_name='Moneda')
        
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Moneda'
        verbose_name_plural = 'Monedas'  
        
        

        
        
class GrupoBaremo(models.Model):
    nombre = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nombre Grupo')
    posicion = models.PositiveIntegerField(default=0,verbose_name='Posicion de Orden' )
   
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'GrupoBaremo'
        verbose_name_plural = 'GruposBaremos'
        
class Unidad(models.Model):
    nombre = models.CharField(max_length=10, null=True,unique=True, blank=True,default='CANT', verbose_name='Unidad')
   
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'
        
class NombreSubBaremo(models.Model):
    nombre = models.CharField(max_length=100, null=True,unique=True, blank=True, verbose_name='nombre')
   
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'NombreSubBaremo'
        verbose_name_plural = 'Nombre SubBaremos'
        
class Baremo(models.Model):
    convenio = models.ForeignKey(Convenio,on_delete=models.CASCADE, verbose_name='Convenio')
    plantilla = models.ForeignKey(Plantilla,on_delete=models.CASCADE,default=1, verbose_name='Plantilla')
    grupo = models.ForeignKey(GrupoBaremo,on_delete=models.CASCADE, verbose_name='Grupo Baremo')
    detalle = models.ForeignKey(DetalleBaremo,on_delete=models.CASCADE, verbose_name='DetalleBaremo')
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Costo')
    venta = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='venta')
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='cantidad')
    unidad = models.ForeignKey(Unidad,on_delete=models.CASCADE, verbose_name='Unidad Baremo')
    exento = models.BooleanField(verbose_name='Exento', default=False)
    ntqx = models.BooleanField(verbose_name='Nota Quirurgica', default=False)
    xcantidad = models.BooleanField(verbose_name='Por Cantidad Precio', default=False)
    haymas = models.PositiveIntegerField(verbose_name='Hay Composicion en la hora', default=0)
    topedia = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Tope x dia')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    inactivar = models.BooleanField(verbose_name='Inactivar', default=False)
    
    def __str__(self):
        return self.detalle.nombre

    class Meta:
        verbose_name = 'Baremo'
        verbose_name_plural = 'Baremos'
        
class LugarConsumo(models.Model):
    nombre = models.CharField(max_length=50, null=True, blank=True, unique=True, verbose_name='Nombre Producto')
    posicion = models.PositiveIntegerField(verbose_name='posicion', default=0)
        
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'LugarConsumo'
        verbose_name_plural = 'LugarConsumo de Material'
        
class SubDetalleBaremo(models.Model):
    detalle = models.ForeignKey(DetalleBaremo,on_delete=models.CASCADE,null=True, verbose_name='Detalle')
    convenio = models.ForeignKey(Convenio,on_delete=models.CASCADE,null=True, verbose_name='Convenio')
    grupo = models.ForeignKey(GrupoBaremo,on_delete=models.CASCADE,null=True, verbose_name='Grupo Baremo')
    nombre = models.CharField(max_length=200, null=True, blank=True, verbose_name='SubDetalle')
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='cantidad')
    monto_tope = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Monto Tope')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
   
    def __str__(self):
        return self.detalle.nombre

    class Meta:
        verbose_name = 'SubDetalleBaremo'
        verbose_name_plural = 'SubDetalles Baremos'
        
class SubBaremo(models.Model):
    detalle = models.ForeignKey(DetalleBaremo,on_delete=models.CASCADE,null=True, verbose_name='DetalleBaremo')
    nombre_subbaremo = models.ForeignKey(NombreSubBaremo,on_delete=models.CASCADE, null=True, blank=True, verbose_name='nombre_subbaremo')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
   
    def __str__(self):
        return self.nombre_subbaremo.nombre

    class Meta:
        verbose_name = 'SubBaremo'
        verbose_name_plural = 'SubBaremos Baremos'        

    

        
class ComposicionDetalle(models.Model):
    convenio = models.ForeignKey(Convenio,on_delete=models.CASCADE,null=True, verbose_name='Convenio')
    grupo = models.ForeignKey(GrupoBaremo,on_delete=models.CASCADE,null=True, verbose_name='Grupo Baremo')
    detalle = models.ForeignKey(DetalleBaremo,on_delete=models.CASCADE,null=True, verbose_name='Detalle')
    nota = models.CharField(max_length=200, null=True, blank=True, verbose_name='SubDetalle')
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='cantidad')
    venta = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='venta')

   
    def __str__(self):
        return self.detalle.nombre

    class Meta:
        verbose_name = 'ComposicionDetalle'
        verbose_name_plural = 'Composicion de Detalle a Cobrar'
        
        
class TipoPersonal(models.Model):
    nombre= models.CharField(max_length=200, null=False, verbose_name='Nombre y Apellido')
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'TipoPersonal'
        verbose_name_plural = 'Tipo Personal'
        
class FormaPago(models.Model)    :
    nombre = models.CharField(max_length=100, null=True, blank=True, verbose_name='Forma de pago')
    moneda = models.ForeignKey(Moneda,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Tipo Moneda')
    
    def __str__(self):
        return str(self.nombre)

    class Meta:
        verbose_name = 'FormaPago'
        verbose_name_plural = 'FormasdePagos'


class Especialidad(models.Model)    :
    nombre = models.CharField(max_length=200, null=True, blank=True, verbose_name='Especialidad')
    activo = models.BooleanField(verbose_name='activo', default=True)
    
    def __str__(self):
        return str(self.nombre)

    class Meta:
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'


        
        
class Medico(models.Model):
    GRUPO_CHOICES = (
        ('M', 'Medico y Enfermeria'),
        ('E', 'Empleados y Contratos'),
        ('G', 'Grupo Medico '),
        ('S', 'Seguros y Gobierno'),
    )

    cedula = models.CharField(max_length=15, unique=True, blank=False, null=False, verbose_name='Cedula / Rif')
    direccion = models.CharField(max_length=100,  blank=True, null=True, verbose_name='Direccion')
    rif= models.PositiveIntegerField(blank=True, null=True, verbose_name='Rif')
    nromsds = models.CharField(max_length=15,  blank=True, null=True, verbose_name='Nro MPPS')
    nrocolegio = models.CharField(max_length=15,  blank=True, null=True, verbose_name='Nro Colegio')
    nombre= models.CharField(max_length=200, null=False, verbose_name='Nombre y Apellido')
    especialidad = models.ForeignKey(Especialidad,on_delete=models.CASCADE,null=True,blank=True, verbose_name='especialidad')
    telefono1=models.CharField(max_length=11,null=True, blank=True, verbose_name='Telefono principal')
    telefono2=models.CharField(max_length=11,null=True, blank=True, verbose_name='Telefono secundario')
    correo=models.EmailField(blank=True,null=True, verbose_name='Email')
    porcentajepago = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='% Pago')
    por_descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='% Descuento')
    observacion = models.CharField(max_length=200, null=False, verbose_name='Observaciones')
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Usuario Aplicacion')
    fecha_desde=models.DateField(null=True, blank=True,default=date.today, verbose_name='Fecha Ingreso')
    participaalta = models.BooleanField(default=False,verbose_name="Participa en alta medica")
    tipopersonal = models.ForeignKey(TipoPersonal,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Tipo Personal')
    pagofrecuente = models.BooleanField(default=False,verbose_name="Pagador frecuente")
    grupo=models.CharField(max_length=1,choices=GRUPO_CHOICES,default='M', verbose_name='Grupo')
    fecha_act=models.DateTimeField(auto_now=True, verbose_name='Actualizado el')
    porcentaje_retencion_iva = models.DecimalField(max_digits=10, decimal_places=2, default=75,verbose_name='% Retencion IVA')
    fotoperfil = models.ImageField(null=True, blank=True,default='C:/proyectoU58/photos/MedicoU58.png' ,upload_to="photos/")

    @property
    def cantidad_cirugias(self):
        return self.detallecirugia_set.count()

    @property
    def total_precio_cirugias(self):
        total = (
            self.detallecirugia_set.aggregate(
                total=Sum('precio')
            )['total'] or 0
        )
        return total

    @property
    def total_montopendiente_pagado(self):
        total = (
            self.notaquirurgica_set.filter(pagado=True)
            .aggregate(total=Sum('montopendiente'))['total'] or 0
        )
        return total
    
    
    @property
    def total_saldo_por_pagar(self):
        total = (self.total_precio_cirugias - self.total_montopendiente_pagado)
        return total
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Medico'
        verbose_name_plural = 'Terceros Personal Medico'
        

class TempFecha(models.Model):
    fecha_desde=models.DateField(null=True, blank=True, verbose_name='Fecha Desde')
    fecha_hasta=models.DateField(null=True, blank=True, verbose_name='Fecha hasta')

    def __str__(self):
        return str(self.fecha_desde)

    class Meta:
        verbose_name = 'TempFecha'
        verbose_name_plural = 'Temporal Fechas'
        

class Cuenta(models.Model):
    numero = models.CharField(max_length=20,null=True, blank=True, unique=True, verbose_name='Numero')
        
    def __str__(self):
        return self.numero

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
        



class Banco(models.Model):
    nombre = models.CharField(max_length=250,null=True, blank=True, verbose_name='Banco')
    rif = models.CharField(max_length=250,null=False, blank=False,unique=True , verbose_name='Rif')
    codigo = models.CharField(max_length=250,null=False, blank=False,unique=True , verbose_name='Codigo')
    moneda = models.ForeignKey(Moneda,on_delete=models.CASCADE,null=True,blank=True,default=2, verbose_name='Moneda')
    fecha_act=models.DateTimeField(auto_now=True, verbose_name='Actualizado el')
        
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Banco'
        verbose_name_plural = 'Bancos'
        

class BancoLocal(models.Model):
    nombrecuenta = models.CharField(max_length=100,null=False, blank=False,unique=True , verbose_name='Nombre de la cuenta')
    banco = models.ForeignKey(Banco,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Banco (opcional)')
    uso = models.CharField(max_length=200,null=False, blank=False,unique=True , verbose_name='Uso de la Cuenta')
    numerocuenta = models.CharField(max_length=20,null=True, blank=True, verbose_name='numerocuenta')
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Saldo')
    moneda = models.ForeignKey(Moneda,on_delete=models.CASCADE,null=False,blank=False, verbose_name='Moneda')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    alias = models.CharField(max_length=10,null=True, blank=True, verbose_name='alias')
    activo = models.BooleanField(verbose_name='Activo', default=True)
    fecha_act=models.DateTimeField(auto_now=True, verbose_name='Actualizado el')
        
    @property
    def saldo(self):
        return self.transaccion_set.filter(bancolocal=self).aggregate(models.Sum('monto'))['monto__sum']
    
    @property
    def saldousd(self):
        return self.transaccion_set.filter(bancolocal=self).aggregate(models.Sum('monto_dolar'))['monto_dolar__sum']
    
    def __str__(self):
        return self.nombrecuenta

    class Meta:
        verbose_name = 'BancoLocal'
        verbose_name_plural = 'Bancos Internos'
        
        

      

class PagoMedico(models.Model):
    nombre= models.CharField(max_length=100, null=True,blank=True, verbose_name='Descripcion')
    numerocuenta = models.CharField(max_length=20, null=True, blank=True, verbose_name='Numero de Cuenta')
    numeropago = models.CharField(max_length=11, null=True, blank=True, verbose_name='Numero de Pago')
    correo=models.EmailField(blank=True,null=True, verbose_name='Email')
    formapago = models.ForeignKey(FormaPago,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Forma de Pago')
    medico = models.ForeignKey(Medico,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Opcion de Pago')
    bancopago = models.ForeignKey(Banco,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Banco de Pago')
    cedulapago = models.CharField(max_length=15, null=True, blank=True, verbose_name='Cedula de Pago')
    moneda = models.ForeignKey(Moneda,on_delete=models.CASCADE,null=True,blank=True,default=2, verbose_name='Moneda')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default = 1, verbose_name='Usuario')
    fecha_act=models.DateTimeField(auto_now=True, verbose_name='Actualizado el')
    
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'PagoMedico'
        verbose_name_plural = 'Pagos Medicos'
        


        
class EstatusCirugia(models.Model):
    nombre= models.CharField(max_length=20, unique=True, null=True,blank=True, verbose_name='Nombre Estatus')
    descripcion = models.CharField(max_length=100, null=True,blank=True, verbose_name='Descripcion Estatus')
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'EstatusCirugia'
        verbose_name_plural = 'Estatus Cirugias'
        
class AtencionInmediata(models.Model):  
    paciente = models.ForeignKey(Paciente,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Paciente')
    tipo_procedimiento = models.ForeignKey(TipoProcedimiento, on_delete=models.CASCADE,default=5 ,verbose_name='Tipo Procedimiento')
    medico_ppal = models.ForeignKey(Medico,on_delete=models.CASCADE,null=True,blank =True, verbose_name='Medico Ppal')
    fecha_act=models.DateTimeField(auto_now=True, verbose_name='Actualizado el')
    fecha_procedimiento=models.DateField(null=True, blank=True, default=date.today,verbose_name='Fecha Procedimiento')
    hora_procedimiento = models.TimeField(null=True,verbose_name='hora ingreso')
    motivo_atencion=models.CharField(max_length=250, null=True,blank=True, verbose_name='motivo_atencion')
    dias_hospitalizacion= models.PositiveIntegerField(default=0,verbose_name='Dias Hospitaliza.')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    estatus= models.ForeignKey(EstatusCirugia, on_delete=models.CASCADE,null=True,blank=True,default=9, verbose_name='EstatusCirugia')
    alta_medica = models.BooleanField(verbose_name='Alta Medica', default=False)
    codigo=models.CharField(max_length=10, null=False,blank=False, verbose_name='codigo')
    habitacion = models.ForeignKey(Habitacion,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Habitacion numero')
    
    def __str__(self):
        return self.motivo_atencion

    class Meta:
        verbose_name = 'AtencionInmediata'
        verbose_name_plural = 'AtencionesInmediatas'

class AtencionInmediataCortesia(models.Model):  
    paciente = models.ForeignKey(Paciente,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Paciente')
    tipo_procedimiento = models.ForeignKey(TipoProcedimiento, on_delete=models.CASCADE,default=5 ,verbose_name='Tipo Procedimiento')
    medico_ppal = models.ForeignKey(Medico,on_delete=models.CASCADE,null=True,blank =True, verbose_name='Medico Ppal')
    fecha_act=models.DateTimeField(auto_now=True, verbose_name='Actualizado el')
    fecha_procedimiento=models.DateField(null=True, blank=True, default=date.today,verbose_name='Fecha Procedimiento')
    hora_procedimiento = models.TimeField(null=True,verbose_name='hora ingreso')
    motivo_atencion=models.CharField(max_length=250, null=True,blank=True, verbose_name='motivo_atencion')
    dias_hospitalizacion= models.PositiveIntegerField(default=0,verbose_name='Dias Hospitaliza.')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    estatus= models.ForeignKey(EstatusCirugia, on_delete=models.CASCADE,null=True,blank=True,default=9, verbose_name='EstatusCirugia')
    alta_medica = models.BooleanField(verbose_name='Alta Medica', default=False)
    codigo=models.CharField(max_length=10, null=False,blank=False, verbose_name='codigo')
    habitacion = models.ForeignKey(Habitacion,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Habitacion numero')
    
    def __str__(self):
        return self.motivo_atencion

    class Meta:
        verbose_name = 'AtencionInmediataCortesia'
        verbose_name_plural = 'AtencionInmediatasCortesias'
        


class Presupuesto(models.Model):  
    paciente = models.ForeignKey(Paciente,on_delete=models.SET_NULL,null=True, verbose_name='Paciente')
    responsable = models.ForeignKey(Responsable,on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Responsable')
    tipo_procedimiento = models.ForeignKey(TipoProcedimiento, on_delete=models.SET_NULL,null=True,blank=True,verbose_name='Tipo Procedimiento')
    medico_ppal = models.ForeignKey(Medico,on_delete=models.SET_NULL,null=True, verbose_name='Medico Ppal')
    fecha_act=models.DateTimeField(null=True, blank=True, auto_now=True, verbose_name='Actualizado el')
    fecha_procedimiento=models.DateField(null=True, blank=True, default=date.today,verbose_name='Fecha Procedimiento')
    hora_procedimiento = models.TimeField(null=True)
    nombre_procedimiento=models.CharField(max_length=500, null=False, verbose_name='Nombre Procedimiento')
    diagnostico=models.CharField(max_length=500, null=False,blank=True, verbose_name='Nombre Diagnostico')
    dias_hospitalizacion= models.PositiveIntegerField(default=0,verbose_name='Dias Hospitaliza.')
    horas_qx= models.PositiveIntegerField(default=0,verbose_name='Horas Qx')
    notas= models.CharField(max_length=250,null=True, blank=True, verbose_name='Notas')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Usuario')
    estatus= models.ForeignKey(EstatusCirugia, on_delete=models.SET_NULL,null=True,blank=True, default=1, verbose_name='EstatusCirugia')
    convenio = models.ForeignKey(Convenio,on_delete=models.SET_NULL,null=True, verbose_name='Convenio')
    congelar_moneda = models.BooleanField(default=False, verbose_name = 'Congelar Cambio Moneda')
    cambio_congelado = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='Tasa Cambio Congelada')
    fecha_cambio=models.DateField(null=True, blank=True, verbose_name='Fecha Cambio')
    atencion_inmediata = models.ForeignKey(AtencionInmediata,null=True,blank=True, on_delete=models.SET_NULL, verbose_name='atencion_inmediata')
    atencion_cortesia = models.ForeignKey(AtencionInmediataCortesia,null=True,blank=True, on_delete=models.SET_NULL, verbose_name='atencion_cortesia')
    nombre_pc = models.CharField(max_length=250,null=True, blank=True, verbose_name='nombre_pc')
    nota=models.CharField(max_length=200, null=False,blank=True, verbose_name='nota')
    
    @property
    def total_monto_precio_usado(self):
        return self.detallepresupuesto_set.aggregate(total=models.Sum('precio_usado'))['total'] or 0
    
    @property
    def total_monto_precio(self):
        return self.detallepresupuesto_set.aggregate(total_precio=models.Sum('precio'))['total_precio'] or 0
    
    def __str__(self):
        return str(self.nombre_procedimiento)

    class Meta:
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        


        
class Quirofano(models.Model):
    NQx = models.PositiveSmallIntegerField(null=True,unique=True, blank=True, verbose_name='No. Quirofano')
    nota = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nota')
   
    def __str__(self):
        return str(self.NQx)

    class Meta:
        verbose_name = 'Quirofano'
        verbose_name_plural = 'Quirofanos'
 
        
class Cirugia(models.Model):  
    paciente = models.ForeignKey(Paciente,on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Paciente')
    tipo_procedimiento = models.ForeignKey(TipoProcedimiento, on_delete=models.SET_NULL,null=True, blank=True, verbose_name='Tipo Procedimiento')
    medico_ppal = models.ForeignKey(Medico, on_delete=models.SET_NULL,null=True,blank =True, verbose_name='Medico Ppal')
    fecha_act=models.DateTimeField(null=True, blank=True, auto_now=True, verbose_name='Actualizado el')
    fecha_procedimiento=models.DateField(null=True, blank=True, default=date.today,verbose_name='Fecha Procedimiento')
    hora_procedimiento = models.TimeField(null=True)
    nombre_procedimiento=models.CharField(max_length=500, null=False, verbose_name='Nombre Procedimiento')
    diagnostico=models.CharField(max_length=500, null=False,blank=True, verbose_name='Nombre Diagnostico')
    dias_hospitalizacion= models.PositiveIntegerField(default=0,verbose_name='Dias Hospitaliza.')
    horas_qx= models.PositiveIntegerField(default=0,verbose_name='Horas Qx')
    horas_qx_facturable= models.PositiveIntegerField(default=0,verbose_name='Horas Qx Facturable')
    notas= models.CharField(max_length=250,null=True, blank=True, verbose_name='Notas')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Usuario')
    convenio = models.ForeignKey(Convenio,on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Convenio')
    presupuesto = models.OneToOneField(Presupuesto, on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Presupuesto')
    estatus= models.ForeignKey(EstatusCirugia, on_delete=models.SET_NULL,null=True,blank=True,default=2, verbose_name='EstatusCirugia')
    quirofano = models.ForeignKey(Quirofano,on_delete=models.SET_NULL,null=True,blank=True, verbose_name='No. Quirofano')
    alta_medica = models.BooleanField(verbose_name='Alta Medica', default=False)
    pendiente = models.BooleanField(verbose_name='Pendiente', default=False)
    cambio_congelado = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='Tasa Cambio Congelada')
    fecha_cambio=models.DateField(null=True, blank=True, verbose_name='Fecha Cambio')
    congelar_moneda = models.BooleanField(default=False, verbose_name = 'Congelar Cambio Moneda')
    precarga = models.PositiveIntegerField(default=True,verbose_name='Precarga de medicina')
    uci = models.BooleanField(verbose_name='estubo uci', default=False)
    ultimo_estatus = models.PositiveIntegerField(default=7,verbose_name='ultimo_estatus')
    fecha_creacion=models.DateTimeField(null=True, blank=True, verbose_name='fecha_creacion')

    @property
    def total_consultas_preanestesia(self):
        return self.consultapreanestesia_set.count()
    
    @property
    def total_historia_clinica(self):
        return self.historiaclinica_set.count()
     
    
    def __str__(self):
        return str(self.nombre_procedimiento)

    class Meta:
        verbose_name = 'Cirugia'
        verbose_name_plural = 'Cirugias'
        
class PreIngreso(models.Model):  
    cirugia = models.ForeignKey(Cirugia,on_delete=models.CASCADE,null=True,blank=True, verbose_name='cirugia')
    fecha_act=models.DateTimeField(null=True, blank=True, auto_now=True, verbose_name='Actualizado el')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Usuario')
    estatus= models.ForeignKey(EstatusCirugia, on_delete=models.SET_NULL,null=True,blank=True,default=9, verbose_name='EstatusCirugia')
    codigo=models.CharField(max_length=15, null=False,blank=False, verbose_name='codigo')
    habitacion = models.ForeignKey(Habitacion,on_delete=models.SET_NULL, null=True,blank=True, verbose_name='habitacion')
    nombre_procedimiento=models.CharField(max_length=500, null=True, blank=True, verbose_name='Nombre Procedimiento')
    
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'PreIngreso'
        verbose_name_plural = 'PreIngresos'
    
        

        
class DetallePresupuesto(models.Model):  
    presupuesto = models.ForeignKey(Presupuesto,related_name='detallepresupuesto_set', on_delete=models.CASCADE,null=True, verbose_name='Presupuesto')
    convenio = models.ForeignKey(Convenio,on_delete=models.CASCADE,null=True, verbose_name='Convenio')
    grupo = models.ForeignKey(GrupoBaremo,on_delete=models.CASCADE,null=True, verbose_name='Grupo Baremo')
    detalle = models.ForeignKey(DetalleBaremo,on_delete=models.CASCADE,null=True, verbose_name='Detalle') 
    plantilla = models.ForeignKey(Plantilla,on_delete=models.CASCADE,default=1, verbose_name='Plantilla')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='cantidad')
    cantidad_usada = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='cantidad usada')
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Precio')
    precio_usado = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Precio Usado')
    unidad = models.ForeignKey(Unidad,on_delete=models.CASCADE,null=True, verbose_name='Unidad Baremo')
    notas= models.CharField(max_length=100,null=True, blank=True, verbose_name='Notas')
    tx = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='Tasa')
    fecha_cambio=models.DateField(null=True, blank=True, default=date.today,verbose_name='Fecha Cambio')
    ntqx = models.BooleanField(verbose_name='Nota Quirurgica', default=False)
    montotope = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Monto Tope')
    montoconsumo = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Monto Consumo')
    excedente = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Monto Excedente') 
    medico = models.ForeignKey(Medico,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Medico')
    alertaexcedente = models.BooleanField(verbose_name='Alertar Excedentes', default=True)
    precio_congelado_cirugia = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Precio Congelado Cirugia')
    precio_congelado_presupuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Precio Congelado Presupuesto')
    precio_congelado_excedente = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Precio Congelado excedente')
    fecha_act=models.DateTimeField(null=True, blank=True, auto_now=True, verbose_name='Actualizado el')
    lugar_consumo = models.ForeignKey(LugarConsumo,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Lugar Tratamiento')
    factor = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Factor Incremento')
    modificacion_cerrado = models.BooleanField(verbose_name='modificacion_cerrado', default=False)
    preingreso = models.ForeignKey(PreIngreso, on_delete=models.CASCADE,null=True, blank=True, verbose_name='preingreso')
    baremo = models.ForeignKey(Baremo, on_delete=models.CASCADE,null=True, blank=True, verbose_name='Baremo')
    porcentaje_descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='porcentaje_descuento')
    monto_descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='monto_descuento')
    porcentaje_descuento_pr = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='porcentaje_descuento_pr')
    monto_descuento_pr = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='monto_descuento_pr')
    
    
    @property
    def total_consumo_preingreso(self):
        return ConsumoCirugia.objects.filter(detalle_presupuesto=self).aggregate(
            total=Sum(F('cantidad_real_usada') * F('precio_unitario'))
        )['total'] or 0
    
    @property
    def monto_total_general(self):
        return (self.precio - self.monto_descuento_pr)
        
    @property
    def precio_unitario(self):
        if self.cantidad == 0:
            return 0
        
        return (self.precio/self.cantidad)   
        
    
    @property
    def subtotal(self):
        return (self.precio)+self.excedente
    
    @property
    def subtotal_usado(self):
        return (self.precio_usado)+self.excedente
    
    
    def __str__(self):
        return str(self.presupuesto.nombre_procedimiento)

    class Meta:
        verbose_name = 'DetallePresupuesto'
        verbose_name_plural = 'Detalles de Presupuesto'

class DetalleCirugia(models.Model):  
    cirugia = models.ForeignKey(Cirugia,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Cirugia')
    convenio = models.ForeignKey(Convenio,on_delete=models.CASCADE,null=True, verbose_name='Convenio')
    grupo = models.ForeignKey(GrupoBaremo,on_delete=models.CASCADE,null=True, verbose_name='Grupo Baremo')
    plantilla = models.ForeignKey(Plantilla,on_delete=models.CASCADE,default=1, verbose_name='Plantilla')
    detalle = models.ForeignKey(DetalleBaremo,on_delete=models.CASCADE,null=True, verbose_name='Detalle') 
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='cantidad')
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Precio')
    unidad = models.ForeignKey(Unidad,on_delete=models.CASCADE,null=True, blank=True, verbose_name='Unidad Baremo')
    notas= models.CharField(max_length=100,null=True, blank=True, verbose_name='Notas')
    tx = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='Tasa')
    fecha_cambio=models.DateField(null=True, blank=True, default=date.today,verbose_name='Fecha Cambio')
    ntqx = models.BooleanField(verbose_name='Nota Quirurgica', default=False)
    facturable = models.BooleanField(verbose_name='Facturable', default=True)
    montoconsumo = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Monto Consumo')
    excedente = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Monto Excedente') 
    excedentehospital = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Monto excedentehospital') 
    medico = models.ForeignKey(Medico,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Medico')
    alertaexcedente = models.BooleanField(verbose_name='Alertar Excedentes', default=True)
    montotope = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Monto Tope') 
    pagado = models.BooleanField(verbose_name='Pagado', default=False)
    manual = models.BooleanField(verbose_name='Pagado', default=False)
    atencion_inmediata = models.ForeignKey(AtencionInmediata,null=True,blank=True, on_delete=models.CASCADE, verbose_name='atencion_inmediata')
    lugar_consumo = models.ForeignKey(LugarConsumo,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Lugar Tratamiento')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    modificacion_cerrado = models.BooleanField(verbose_name='modificacion_cerrado', default=False)
    
    def monto_facturar(self):
        return (self.montoconsumo - self.montotope) + self.precio
    
    def __str__(self):
        return str(self.cirugia)

    class Meta:
        verbose_name = 'DetalleCirugia'
        verbose_name_plural = 'Detalles de Cirugias'
        
class NotaQuirurgica(models.Model):
    cirugia = models.ForeignKey(Cirugia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Cirugia')
    atencion_inmediata = models.ForeignKey(AtencionInmediata,null=True,blank=True, on_delete=models.CASCADE, verbose_name='atencion_inmediata')
    atencion_cortesia = models.ForeignKey(AtencionInmediataCortesia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='atencion_cortesia')
    preingreso = models.ForeignKey(PreIngreso,null=True,blank=True, on_delete=models.CASCADE, verbose_name='preingreso')
    medico = models.ForeignKey(Medico,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Participante')
    participante = models.ForeignKey(DetalleBaremo,on_delete=models.CASCADE,null=True, blank=True, verbose_name='Detalle') 
    nota = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nota')
    fecha_elaboracion = models.DateField(null=True, blank=True, default=date.today,verbose_name='Fecha Elaboracion')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    quirofano = models.ForeignKey(Quirofano,null=True,blank=True, on_delete=models.CASCADE, verbose_name='No. Quirofano')
    incluir = models.BooleanField(verbose_name='Incluido', default=True)
    pagado = models.BooleanField(verbose_name='Pagado', default=False)
    montopendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Monto Pendiente')
    pagoeliminado = models.BooleanField(verbose_name='Eliminado', default=False)
    notaeliminacion = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nota Eliminacion')
    lugar_consumo = models.ForeignKey(LugarConsumo,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Lugar Tratamiento')
    detallepresupuesto = models.ForeignKey(DetallePresupuesto,null=True,blank=True, on_delete=models.CASCADE, verbose_name='detallepresupuesto')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,default=4,null=True, blank=True, verbose_name='Usuario')
    caso_cerrado = models.BooleanField(verbose_name='caso_cerrado', default=False)
    
    def __str__(self):
        return self.participante.nombre

    class Meta:
        verbose_name = 'NotaQuirurgica'
        verbose_name_plural = 'Nota Quirurgicas'
    
        
class ImagenCirugia(models.Model):
    cirugia = models.ForeignKey(Cirugia,null=False,blank=False, on_delete=models.CASCADE, verbose_name='Cirugia')
    imagen = models.ImageField(upload_to="imagenes")
    fecha_publicacion = models.DateTimeField(auto_now_add=True,null=True)
    descripcion = models.CharField(max_length=100, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True, verbose_name='Usuario')
    
    class Meta:
        verbose_name = 'ImagenCirugia'
        verbose_name_plural = 'ImagenesCirugiaS'

    def __str__(self):
        return f"{self.cirugia.paciente}'s image"


class UnidadProducto(models.Model):
    acronimo = models.CharField(max_length=3)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'UnidadProducto'
        verbose_name_plural = 'Unidades Productos'        


class NombreInventario(models.Model):
    nombre = models.CharField(max_length=200, null=True,unique=True, blank=True, verbose_name='Nombre Inventario')
       
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'NombreItemInventario'
        verbose_name_plural = 'Nombre Inventario'
        
class TipoProveedor(models.Model):
    nombre = models.CharField(max_length=100, unique=True, null=False, blank=False, verbose_name='Nombre de tipo')
    descripcion = models.CharField(max_length=250, null=True, blank=True, verbose_name='descripcion de tipo')
    fecha = models.DateField(null=False, default=date.today,verbose_name='Fecha')
    activo = models.BooleanField(default=True,verbose_name='activo')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'TipoProveedor'
        verbose_name_plural = 'Tipos de Proveedores' 
        
class Proveedor(models.Model):
    rif = models.CharField(max_length=15, unique=True,null=False, blank=False, verbose_name='Rif Proveedor')
    nombre = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nombre Proveedor')
    telefono1 = models.CharField(max_length=15, null=True, blank=True, verbose_name='Telefonos')
    telefono2 = models.CharField(max_length=15, null=True, blank=True, verbose_name='Telefonos 2')
    zonapostal = models.CharField(max_length=10, null=True, blank=True, verbose_name='Zona Postal')
    contacto = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nombre Contacto')
    fecha = models.DateField(null=False, default=date.today,verbose_name='Fecha Creacion')
    tipoproveedor = models.ForeignKey(TipoProveedor,null=True,blank=True,on_delete=models.SET_NULL, verbose_name='Tipo Proveedor')
    correo=models.EmailField(blank=True,null=True, verbose_name='Email')
    correocontacto=models.EmailField(blank=True,null=True, verbose_name='Email Contacto')
    telefonocontacto = models.CharField(max_length=15, null=True, blank=True, verbose_name='Telefonos Contacto')
    activo = models.BooleanField(default=True,verbose_name='activo')
    porcentaje_retencion = models.DecimalField(max_digits=10, decimal_places=2, default=75,verbose_name='% Retencion IVA')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True, verbose_name='Usuario')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores' 
        
        
class FormaPagoProveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Proveedor Pago')
    nombre= models.CharField(max_length=100, null=True,blank=True, verbose_name='Descripcion')
    numerocuenta = models.CharField(max_length=20, null=True, blank=True, verbose_name='Numero de Cuenta')
    numeropago = models.CharField(max_length=11, null=True, blank=True, verbose_name='Numero de Pago')
    correo=models.EmailField(blank=True,null=True, verbose_name='Email')
    formapago = models.ForeignKey(FormaPago,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Forma de Pago')
    bancopago = models.ForeignKey(Banco,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Banco de Pago')
    cedulapago = models.CharField(max_length=15, null=True, blank=True, verbose_name='Cedula de Pago')
    moneda = models.ForeignKey(Moneda,on_delete=models.CASCADE,null=True,blank=True,default=2, verbose_name='Moneda')
    activo = models.BooleanField(default=True,verbose_name='activo')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True, verbose_name='Usuario')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'formaPagoProveedor'
        verbose_name_plural = 'Formas de Pagos Proveedores'



        
class Deposito(models.Model):
    nombre = models.CharField(max_length=200, null=True, blank=True, unique=True, verbose_name='Nombre Deposito')
    ubicacion = models.CharField(max_length=200, null=True, blank=True, verbose_name='Ubicacion Deposito')
    precarga = models.BooleanField(default=False,verbose_name='Precarga de Qx')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Deposito'
        verbose_name_plural = 'Depositos' 
        

        
class LaboratorioMedicina(models.Model):
    nombre = models.CharField(max_length=200, null=True, blank=True, unique=True, verbose_name='Laboratorio Medicina')
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'LaboratorioMedicina'
        verbose_name_plural = 'Laboratorios de Medicinas' 
        
class PresentacionMedicina(models.Model):
    nombre = models.CharField(max_length=200, null=True, blank=True,unique=True, verbose_name='Presentacion Medicina')
    cantidad = models.DecimalField(max_digits=10, decimal_places=4, default=1,verbose_name='cantidad')
    activo = models.BooleanField(default=True, verbose_name='activo')
    unidad = models.ForeignKey(UnidadProducto, on_delete=models.CASCADE, null=True, verbose_name='unidad')
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'PresentacionMedicina'
        verbose_name_plural = 'Presentaciones Medicina' 
        
class KitInventario(models.Model):
    nombre = models.CharField(max_length=100,unique=True ,null=False, blank=False, verbose_name='Nombre Kit')
  
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'KitInventario'
        verbose_name_plural = 'Kits de Inventarios' 


class UnidadCompra(models.Model):
    nombre = models.CharField(max_length=100,unique=True ,null=False, blank=False, verbose_name='UnidadCompra')
    cantidad_bulto = models.DecimalField(max_digits=10, decimal_places=4, default=1,verbose_name='cantidad_bulto')
    cantidad_unidad_bulto = models.DecimalField(max_digits=15, decimal_places=2, default=1,verbose_name='cantidad_unidad_bulto')
    activo = models.BooleanField(default=True, verbose_name='activo')
    unidad = models.ForeignKey(UnidadProducto, on_delete=models.CASCADE, null=True, verbose_name='unidad')
  
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'UnidadCompra'
        verbose_name_plural = 'Unidad Compra de Inventarios' 


class MontoIncremento(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Monto')
    porcentaje = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='porcentaje')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    
    def __str__(self):
        return str(self.porcentaje)

    class Meta:
        verbose_name = 'MontoIncremento'
        verbose_name_plural = 'Montos Incrementos'

        
class Inventario(models.Model):
    COMPUESTO_CHOICES = (
        ('1', 'Ninguno'),
        ('2', 'Compuesto'),
        ('3', 'Suministro Bomba'),
    )
    codigo = models.CharField(max_length=20,unique=True ,null=False, blank=False,default='codxxx', verbose_name='Codigo Producto')
    kit = models.ForeignKey(KitInventario,null=True,blank=True, on_delete=models.SET_NULL, verbose_name='Pertenece a Kit')
    proveedor = models.ForeignKey(Proveedor,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Proveedor')
    categoria = models.ForeignKey(CategoriaInventario,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Categoria')
    laboratorio = models.ForeignKey(LaboratorioMedicina,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Laboratorio')
    presentacion = models.ForeignKey(PresentacionMedicina,null=True,blank=True, on_delete=models.CASCADE,related_name='presentacion_entrada', verbose_name='Presentacion')
    presentacion_salida = models.ForeignKey(PresentacionMedicina,null=True,blank=True, on_delete=models.CASCADE,related_name='presentacion_salida', verbose_name='Presentacion Salida')
    nombre = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nombre Producto')
    nombre_comercial = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nombre Comercial Producto')
    lote = models.CharField(max_length=20, null=True, blank=True, verbose_name='Lote Producto')
    cantidad_unitaria = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='cantidad_unitaria')
    unidad_conversion = models.DecimalField(max_digits=10, decimal_places=2, default=1,verbose_name='unidad_conversion')
    capacidadunidad = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='capacidadunidad')
    cantidad_max = models.PositiveBigIntegerField(default=0,verbose_name='Cantidad Maxima')
    cantidad_kit = models.PositiveBigIntegerField(default=1,verbose_name='Cantidad Kit')
    cantidad_min = models.PositiveBigIntegerField(default=0,verbose_name='Cantidad Minima')
    cantidad_cri = models.PositiveBigIntegerField(default=0,verbose_name='Cantidad Critica')
    fecha_elaboracion = models.DateField(null=True, blank=True, default=date.today,verbose_name='Fecha Ingreso')
    fecha_vencimiento = models.DateField(null=True, blank=True, default=date.today,verbose_name='Fecha Vence')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Costo')
    venta = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='venta')
    piva = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='% IVA')
    venta_kit = models.DecimalField(max_digits=10, decimal_places=2,  default=0,verbose_name='Venta en KIT')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    cantidad_total_usada = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='cantidad_total_usada')
    unidadcompra = models.ForeignKey(UnidadCompra,null=True,blank=True, on_delete=models.CASCADE,related_name='unidadcompra', verbose_name='unidadcompra')
    incremento = models.ForeignKey(MontoIncremento, on_delete=models.CASCADE, default=1, verbose_name='incremento')
    compuesto=models.CharField(max_length=1,choices=COMPUESTO_CHOICES, default='1', verbose_name='compuesto')
    producto_activo=models.BooleanField(default=True, verbose_name='producto_activo')
    reusable=models.BooleanField(default=False, verbose_name='reusable')
    clasificacion = models.ForeignKey(UnidadProducto, on_delete=models.CASCADE, null=True, verbose_name='unidad')
    
    @property
    def cantidad_total_producto(self):
        return DepositoUso.objects.filter(inventario=self).aggregate(Sum('cantidad_deposito'))['cantidad_deposito__sum'] or 0

    @property
    def cantidad_total_descarga(self):
        return InventarioDescarga.objects.filter(inventario=self, deposito__isnull = False).aggregate(Sum('cantidad'))['cantidad__sum'] or 0

    @property
    def existencia(self):
        if self.unidad_conversion > 0:
            return self.cantidad_total_producto - (self.cantidad_total_descarga/self.unidad_conversion)
        else:
            return self.cantidad_total_producto - self.cantidad_total_descarga
    
    @property
    def existencia_und(self):
        return (self.cantidad_total_producto * self.unidad_conversion) - self.cantidad_total_descarga

    @property
    def unidades_existentes(self):
        return (self.cantidad_total_producto) - self.cantidad_total_descarga

    @property
    def monto_venta(self):
        # Calcular el monto de venta
        if self.unidad_conversion > 0:
            base_monto_venta = self.costo / self.unidad_conversion
        else:
            base_monto_venta = self.costo

        monto_con_incremento = base_monto_venta + (base_monto_venta * self.pincremento)
        monto_final = (monto_con_incremento + (monto_con_incremento * (self.piva / 100)))
                   
        # Asegurarse de que el monto final no sea menor que 0.01
        if monto_final < 0.01:
                return 0.01
        
        return monto_final
    
    @property
    def pincremento(self):
        # Obtener el porcentaje de incremento del objeto con id=1
        incremento_obj = MontoIncremento.objects.get(id=1)
        porcentaje_incremento = incremento_obj.porcentaje  # Asegúrate de que este campo exista
        return (porcentaje_incremento/100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.venta_kit:
            self.venta_kit = self.venta

    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios' 
        
        
class DepositoUso(models.Model):
    inventario = models.ForeignKey(Inventario,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Producto de Inventario', related_name='inventario')
    deposito = models.ForeignKey(Deposito,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Deposito')
    cantidad_deposito = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='cantidad_deposito')
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Costo')
    venta = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='venta')
    cantidad_consumida = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='cantidad_consumida')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')

    @property
    def descargadeposito_und(self):
        total_descargas = InventarioDescarga.objects.filter(
            inventario=self.inventario,
            deposito=self.deposito
        ).exclude(tipodescarga_id = 4).aggregate(total=Sum('cantidad'))['total'] or 0
    
        return total_descargas
    

    @property
    def descargadeposito_und_reciclado(self):
        qs = InventarioDescarga.objects.filter(
            inventario=self.inventario,
            depositoentrada=self.deposito,
            reciclado=True,
            tipodescarga_id=4
        )

        return qs.aggregate(totalsr=Sum('cantidad'))['totalsr'] or 0
    
    @property
    def cantidad_no_reciclar(self):
        qs = ReutilizacionInventario.objects.filter(
            inventario=self.inventario,
            deposito=self.deposito,
            noreutilizable=True,
        )

        return qs.aggregate(totalsr=Sum('cantidad'))['totalsr'] or 0
    
    @property
    def descargadeposito_contable(self):
        return self.descargadeposito_und - self.descargadeposito_und_reciclado

    @property
    def descargadeposito_contable_neto_reciclado(self):
        return (self.descargadeposito_und - self.descargadeposito_und_reciclado) - self.cantidad_no_reciclar
    
    @property
    def factorConversion(self):
        factor = Inventario.objects.filter(
            id=self.inventario_id
        ).first()
    
        return factor.unidad_conversion if factor else 0 
    
    @property
    def existenciaUnd(self):
        return (self.cantidad_deposito) - self.descargadeposito_und

    @property
    def existencia(self):
        return (self.existenciaUnd)


    
    def __str__(self):
        return str(self.deposito)

    class Meta:
        verbose_name = 'DepositoUso'
        verbose_name_plural = 'Depositos Usos' 


class RequisitoIngreso(models.Model):
    cirugia = models.ForeignKey(Cirugia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Cirugia')
    informe_med_ingreso = models.BooleanField(verbose_name='Informe Medico Ingreso', default=False)
    orden_ingreso = models.BooleanField(verbose_name='orden_ingreso', default=False)
    carta_compromiso = models.BooleanField(verbose_name='carta_compromiso', default=False)
    tramite_administrativo = models.BooleanField(verbose_name='tramite_administrativo', default=False)
    examen_preoperatorio = models.BooleanField(verbose_name='examen_preoperatorio', default=False)
    evaluacion_cardio = models.BooleanField(verbose_name='evaluacion_cardio', default=False)
    evaluacion_preanestesica = models.BooleanField(verbose_name='evaluacion_preanestesica', default=False)
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    
    def __str__(self):
        return str(self.cirugia.nombre_procedimiento)

    class Meta:
        verbose_name = 'RequisitoIngreso'
        verbose_name_plural = 'RequisitosIngresos' 
        

class TiempoQuirofano(models.Model):
    cirugia = models.ForeignKey(Cirugia,null=False,blank=False, on_delete=models.CASCADE, verbose_name='Cirugia')
    hora_entrada = models.TimeField(null=True , verbose_name='Entrada Qx')
    tiempo_qx = models.DurationField(null=True, verbose_name='Tiempo Qx')
    hora_salida = models.TimeField(null=True , verbose_name='Salida Qx')
    inicio_cirugia = models.TimeField(null=True , verbose_name='Inicio Cirugia')
    tiempo_cirugia = models.DurationField(null=True,verbose_name='Tiempo Cirugia')
    fin_cirugia = models.TimeField(null=True , verbose_name='Fin Cirugia')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    
    def __str__(self):
        return str(self.cirugia.nombre_procedimiento)

    class Meta:
        verbose_name = 'TiempoQuirofano'
        verbose_name_plural = 'Tiempos de Quirofano' 
        
        

        
class ConsumoCirugia(models.Model):
    COMPUESTO_CHOICES = (
        ('1', 'Ninguno'),
        ('2', 'Compuesto'),
        ('3', 'Suministro Bomba'),
    )
    cirugia = models.ForeignKey(Cirugia,null=True,blank=True, on_delete=models.SET_NULL, verbose_name='Cirugia')
    atencion_inmediata = models.ForeignKey(AtencionInmediata,null=True,blank=True, on_delete=models.CASCADE, verbose_name='atencion_inmediata')
    atencion_cortesia = models.ForeignKey(AtencionInmediataCortesia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='atencion_cortesia')
    preingreso = models.ForeignKey(PreIngreso,null=True,blank=True, on_delete=models.CASCADE, verbose_name='preingreso')
    inventario = models.ForeignKey(Inventario,null=False,blank=False, on_delete=models.CASCADE, verbose_name='Inventario')
    cantidad_uso = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='cantidad_uso')
    venta = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='venta')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Precio Unitario')
    precio_costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='precio_costo_unitario')
    hora = models.TimeField(null=True , default=get_current_time, verbose_name='Hora asignacion')
    hora_uso = models.TimeField(null=True , verbose_name='Hora Uso')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    consumo = models.ForeignKey(LugarConsumo,null=False,blank=False, default=1, on_delete=models.CASCADE, verbose_name='Lugar Afectado')
    cantidad_real_usada = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='cantidad_real_usada')
    farmacia = models.BooleanField(default=False,verbose_name='Pendiente Farmacia' )
    solicitante = models.ForeignKey(Medico,on_delete=models.CASCADE,null=True,blank=True, verbose_name='solicitante_medico', related_name='Solicitante')
    entregado = models.ForeignKey(Medico,on_delete=models.CASCADE,null=True,blank=True, verbose_name='entregado_medico', related_name='Entregado')
    nota = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nota Entrega')
    diferencia = models.IntegerField(default=0,verbose_name='Diferencia cantidades')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True, verbose_name='Usuario')
    disponible = models.PositiveBigIntegerField(default=0,verbose_name='Disponible')
    conciliada = models.BooleanField(default=False, verbose_name = 'Conciliada Farmacia')
    deposito = models.ForeignKey(Deposito,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Deposito Afectado')
    obligatoria = models.BooleanField(default=False, verbose_name = 'Obligatoria')
    advertencia = models.BooleanField(default=False, verbose_name = 'advertencia')
    compuesto=models.CharField(max_length=1,choices=COMPUESTO_CHOICES, default='1', verbose_name='compuesto')
    detalle_presupuesto = models.ForeignKey(DetallePresupuesto,null=True,blank=True, on_delete=models.CASCADE, verbose_name='DetallePresupuesto')
    baremo_cobro = models.ForeignKey(DetalleBaremo,null=True,blank=True, on_delete=models.SET_NULL, verbose_name='baremo_cobro')
    seleccionado =  models.BooleanField(default=False, verbose_name = 'seleccionado')
    
    def subtotal_costo(self):
        return self.cantidad_real_usada * self.precio_costo_unitario
    def subtotal(self):
        return self.cantidad_real_usada * self.precio_unitario

    def venta_disponible(self):
        return (self.cantidad_uso - self.cantidad_real_usada) * self.precio_unitario
    
    def total_diferencia(self):
        return self.cantidad_uso - self.cantidad_real_usada
    
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'ConsumoCirugia'
        verbose_name_plural = 'Consumo de Cirugia' 
        
        
class DetalleConsumoCirugia(models.Model):
    consumocirugia = models.ForeignKey(ConsumoCirugia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Cirugia')
    inventario = models.ForeignKey(Inventario,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Inventario')
    cantidad_uso = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='cantidad_uso')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Precio Unitario')
    hora = models.TimeField(null=True , verbose_name='Hora asignacion')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    usuario_farmacia = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True, verbose_name='Usuario', default=1, related_name='usuario_farmacia')
    usuario_cirugia = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True, verbose_name='Usuario', default=1, related_name='usuario_cirugia')
    nota = models.CharField(max_length=100, null=True, blank=True, verbose_name='Nota')
    
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'DetalleConsumoCirugia'
        verbose_name_plural = 'Detalles del Consumo'         



class Tratamiento(models.Model):
    cirugia = models.ForeignKey(Cirugia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Cirugia')
    atencion_inmediata = models.ForeignKey(AtencionInmediata,null=True,blank=True, on_delete=models.CASCADE, verbose_name='atencion_inmediata')
    atencion_cortesia = models.ForeignKey(AtencionInmediataCortesia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='atencion_cortesia')
    preingreso = models.ForeignKey(PreIngreso,null=True,blank=True, on_delete=models.CASCADE, verbose_name='preingreso')
    inventario = models.ForeignKey(Inventario,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Inventario')
    baremo = models.ForeignKey(Baremo,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Baremo')
    cantidad_uso = models.PositiveBigIntegerField(default=1,verbose_name='Cantidad Uso')
    tratamiento=models.TextField(max_length=500,null=True, blank=True, default="Tratamiento/Evolucion/Enfermeria", verbose_name='Tratamiento')
    medico_orden = models.ForeignKey(Medico,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Medico Orden', related_name='tratamientos_ordenados' )
    medico_aplicante = models.ForeignKey(Medico,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Aplicante', related_name='tratamientos_aplicados')
    fecha_act = models.DateTimeField(auto_now=True, verbose_name='Fecha Asignacion')
    fecha_aplicacion = models.DateTimeField(null=True,blank=True, verbose_name='Fecha Aplicacion')
    fecha_ultimaact = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha ULtima Actualizacion')
    cumplido = models.BooleanField(default=False,verbose_name='Cumplido' )
    consumo = models.ForeignKey(ConsumoCirugia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Consumo')
    lugar_consumo = models.ForeignKey(LugarConsumo,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Lugar Tratamiento')
    usuario = models.ForeignKey(User,null=True,blank=True, on_delete=models.CASCADE, verbose_name='usuario')
   
    
    def __str__(self):
        return self.tratamiento

    class Meta:
        verbose_name = 'Tratamiento'
        verbose_name_plural = 'Tratamientos'
        
class CirugiaHabitacion(models.Model):
    HABITACION_CHOICES = (
        ('O', 'Ocupada'),
        ('D', 'Disponible'),
        ('F', 'Fuera de Servicio'),
    )
    habitacion = models.ForeignKey(Habitacion,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Habitacion numero')
    cirugia = models.ForeignKey(Cirugia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Cirugia')
    status=models.CharField(max_length=1,choices=HABITACION_CHOICES, default='A', verbose_name='Estatus Habitacion')
    fecha_asignacion = models.DateTimeField(null=True,blank=True, verbose_name='Fecha Asignacion')
    fecha_salida = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha salida')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    
    def __str__(self):
        return str(self.cirugia.nombre_procedimiento)

    class Meta:
        verbose_name = 'CirugiaHabitacion'
        verbose_name_plural = 'Cirugias Habitaciones'
    
    
class AltaMedica(models.Model):
    cirugia = models.ForeignKey(Cirugia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Cirugia')
    fecha_salida = models.DateTimeField(null=True,blank=True, verbose_name='Fecha Alta')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    condiciones_egreso = models.TextField(max_length=1000,null=True, blank=True, default="Condiciones de Egreso", verbose_name='Condicion Egreso')
    diagnostico_egreso = models.TextField(max_length=1000,null=True, blank=True, default="Diagnostico de Egreso", verbose_name='Diagnostico Egreso')
    diagnostico_ingreso = models.TextField(max_length=1000,null=True, blank=True, default="Diagnostico de Ingreso", verbose_name='Diagnostico Ingreso')
    tratamiento_recibido = models.TextField(max_length=1000,null=True, blank=True, default="Tratamiento Recibido", verbose_name='Tratamiento recibido')
    medico_egreso = models.ForeignKey(Medico,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Medico de Egreso')
    atencion_inmediata = models.ForeignKey(AtencionInmediata,null=True,blank=True, on_delete=models.CASCADE, verbose_name='atencion_inmediata')
    atencion_cortesia = models.ForeignKey(AtencionInmediataCortesia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='atencion_cortesia')
    usuario =  models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True, verbose_name='Usuario')
    
    def __str__(self):
        return str(self.cirugia)

    class Meta:
        verbose_name = 'AltaMedica'
        verbose_name_plural = 'Altas Medicas'
        
class TrasladoUci(models.Model):
    cirugia = models.ForeignKey(Cirugia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Cirugia')
    fecha_salida = models.DateTimeField(null=True,blank=True, verbose_name='Fecha Alta')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    condiciones_egreso = models.TextField(max_length=1000,null=True, blank=True, default="Condiciones de Egreso", verbose_name='Condicion Egreso')
    diagnostico_egreso = models.TextField(max_length=1000,null=True, blank=True, default="Diagnostico de Egreso", verbose_name='Diagnostico Egreso')
    diagnostico_ingreso = models.TextField(max_length=1000,null=True, blank=True, default="Diagnostico de Ingreso", verbose_name='Diagnostico Ingreso')
    tratamiento_recibido = models.TextField(max_length=1000,null=True, blank=True, default="Tratamiento Recibido", verbose_name='Tratamiento recibido')
    medico_egreso = models.ForeignKey(Medico,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Medico de Egreso')
    
    def __str__(self):
        return str(self.cirugia.nombre_procedimiento)

    class Meta:
        verbose_name = 'AltaMedica'
        verbose_name_plural = 'Altas Medicas'
        
        
class MedicoAltaMedica(models.Model):
    altamedica = models.ForeignKey(AltaMedica,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Alta Medica')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    medico_tratamiento = models.ForeignKey(Medico,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Medico tratado')
    
    def __str__(self):
        return str(self.altamedica.cirugia.nombre_procedimiento)

    class Meta:
        verbose_name = 'MedicoAltaMedica'
        verbose_name_plural = 'Medicos Tratantes'


        
class Retencion(models.Model):
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    cod = models.CharField(max_length=20,null=True, blank=True, verbose_name='codigo')
    nombre = models.CharField(max_length=200,null=True, blank=True, verbose_name='Concepto')
    natural = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='por. retencion natural')
    topenatural = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='tope monto natural')
    juridica = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='por. retencion juridica')
    topejuridica = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='tope monto juridica')
    sustraendonatural = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='sustraendonatural')
    sustraendojuridica = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='sustraendojuridica')
    activo = models.BooleanField(default=True,verbose_name='activo' )
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Retencion'
        verbose_name_plural = 'Retenciones'
        

class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=50, null=True, blank=True, unique=True, verbose_name='Nombre Producto')
    activo_factura_medico =  models.BooleanField(default=True,verbose_name='activo_factura_medico' )
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'TipoDocumento'
        verbose_name_plural = 'TipoDocumento de Facturas' 
        
class RetencionISLR(models.Model):
    comprobante = models.CharField(max_length=12, null=True, blank=True, unique=True, verbose_name='Numero Comprobante')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    periodo = models.CharField(max_length=6, null=True, blank=True, verbose_name='Periodo Fiscal')
    usuario =  models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True, verbose_name='Usuario')
    montofactura = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name='montofactura')
    montoretencion = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name='montoretencion')
    baseimponible = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name='baseimponible')
    porcentaje_retencion = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='porcentaje_retencion')
    tipo_comprobante = models.CharField(max_length=2,default='FM', verbose_name='tipo_comprobante')
    
    def __str__(self):
        return self.comprobante

    class Meta:
        verbose_name = 'RetencionISLR'
        verbose_name_plural = 'RetencionISLR de Facturas' 

        
class NotaEntregaCompra(models.Model):
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    fecha_entrega = models.DateTimeField(null=True, blank=True, verbose_name='Fecha Entrega')
    numerodocumento = models.CharField(max_length=30,null=True, blank=True, verbose_name='Numero Documento') 
    proveedor_compra = models.ForeignKey(Proveedor,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Proveedor Compra')
    activo = models.BooleanField(default=False, verbose_name = 'Activo') 
    tasaaplicable = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='tasaaplicable')
    usuario = models.ForeignKey(User,null=True,blank=True, on_delete=models.CASCADE, verbose_name='usuario') 
    moneda_factura = models.PositiveIntegerField(default=1, verbose_name='moneda Documento') 
    cantidad_inventario_actualizado = models.BooleanField(default=False, verbose_name = 'cantidad_inventario_actualizado') 
    convertida_factura = models.BooleanField(default=False, verbose_name = 'convertida_factura') 
    monto_descuento_bs = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='monto_descuento_bs')
    porcentaje_descuento = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='porcentaje_descuento')
    porcentaje_retencion_islr = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='porcentaje_retencion_islr')
    marca = models.BooleanField(default=False, verbose_name = 'marca')
    concepto = models.ForeignKey(Retencion,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Concepto')
    convertida_factura_total = models.BooleanField(default=False, verbose_name = 'convertida_factura_total') 

    @property
    def total_costo_bs(self):
        return self.detallenotaentrega_set.aggregate(total=Sum(F('cantidad') * F('costo_bs')))['total'] or 0

    @property
    def total_costo_bs_multiple(self):
        return self.detallenotaentrega_set.filter(
            factura=True,
            convertido_a_factura = False
        ).aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('cantidad') * F('costo_bs'),
                    output_field=DecimalField()
                )
            )
        )['total'] or 0

   
    @property
    def total_costo_dl(self):
        return self.total_costo_bs / self.tasaaplicable

    @property
    def total_exento_bs(self):
        return self.detallenotaentrega_set.aggregate(tota_exento=Sum(F('cantidad') * F('costo_bs'), filter=Q(piva = 0)))['tota_exento'] or 0
    
    @property
    def total_exento_bs_multiple(self):
        return self.detallenotaentrega_set.aggregate(tota_exento=Sum(F('cantidad') * F('costo_bs'), filter=Q(piva = 0, factura=True, convertido_a_factura = False)))['tota_exento'] or 0
    
    @property
    def total_exento_neto_bs(self):
        return (self.total_exento_bs - (self.total_exento_bs * (self.porcentaje_descuento/100)) )
    
    @property
    def total_exento_neto_dl(self):
        return (self.total_exento_neto_bs / self.tasaaplicable)
    
    @property
    def total_exento_dl(self):
        return self.total_exento_bs / self.tasaaplicable

    @property
    def total_base_imponible_bs(self):
        return round((self.detallenotaentrega_set.aggregate(total_base=Sum(F('cantidad') * F('costo_bs'), filter=Q(piva__gt = 0)))['total_base'] or 0),2)

    @property
    def total_base_imponible_bs_multiple(self):
        return round((self.detallenotaentrega_set.aggregate(total_base=Sum(F('cantidad') * F('costo_bs'), filter=Q(piva__gt = 0, factura=True, convertido_a_factura = False)))['total_base'] or 0),2)
    
    @property
    def total_base_imponible_neto_bs(self):
        return (self.total_base_imponible_bs - (self.total_base_imponible_bs * (self.porcentaje_descuento/100))) 
    
    @property
    def total_base_imponible_neto_dl(self):
        return (self.total_base_imponible_neto_bs / self.tasaaplicable) 
    
    @property
    def total_base_imponible_dl(self):
        return self.total_base_imponible_bs / self.tasaaplicable
    
    @property
    def total_iva_bs(self):
        return (self.detallenotaentrega_set.aggregate(total_iva_b=Sum((F('cantidad') * F('costo_bs')*(F('piva')/100))))['total_iva_b'] or 0) 

    @property
    def total_iva_bs_multiple(self):
        return (self.detallenotaentrega_set.filter(factura=True, convertido_a_factura = False).aggregate(total_iva_b=Sum((F('cantidad') * F('costo_bs')*(F('piva')/100))))['total_iva_b'] or 0) 
    
    @property
    def monto_descuento_dl(self):
        return self.monto_descuento_bs / self.tasaaplicable

    @property
    def total_iva_neto_bs(self):
        return self.total_iva_bs - (self.total_iva_bs * (self.porcentaje_descuento/100) )

    @property
    def total_iva_dl(self):
        return self.total_iva_neto_bs / self.tasaaplicable

    @property
    def total_operacion_bs(self):
        return self.total_base_imponible_neto_bs + self.total_iva_neto_bs + self.total_exento_neto_bs

        
    @property
    def total_operacion_dl(self):
        return self.total_operacion_bs / self.tasaaplicable
    
    def __str__(self):
        return str(self.proveedor_compra)

    class Meta:
        verbose_name = 'NotaEntregaCompra'
        verbose_name_plural = 'Notas Entrega Compra Proveedores'
        
class DetalleNotaEntrega(models.Model):
    notaentrega = models.ForeignKey(NotaEntregaCompra,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Nota entrega')
    laboratorio = models.ForeignKey(LaboratorioMedicina,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Laboratorio')
    presentacion = models.ForeignKey(PresentacionMedicina,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Presentacion Entrada', related_name="presentacionentra")
    presentacion_salida = models.ForeignKey(PresentacionMedicina,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Presentacion Salida', related_name="presentacionsalida")
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    codigo = models.CharField(max_length=20,null=True, blank=True, verbose_name='Codigo Producto') 
    categoria = models.ForeignKey(CategoriaInventario,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Categoria')
    clasificacion = models.ForeignKey(UnidadProducto,null=True,blank=True, on_delete=models.CASCADE, verbose_name='clasificacion')
    costo_dl = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Costo usd')
    venta_dl = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Venta usd')
    costo_bs = models.DecimalField(max_digits=15, decimal_places=5, default=0,verbose_name='Costo Bs')
    cambioaplicado = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='cambioaplicado')
    piva = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Porc Iva')
    nombre = models.CharField(max_length=200,null=True, blank=True, verbose_name='Nombre Producto') 
    inventario = models.ForeignKey(Inventario,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Inventario') 
    lote = models.CharField(max_length=20,null=True, blank=True, verbose_name='Numero Lote') 
    fechaelaboracion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha elaboracion')
    fechavencimiento = models.DateTimeField(null=True, blank=True, verbose_name='Fecha vencimiento')
    eninventario = models.BooleanField(default=False, verbose_name = 'En inventario')
    unidad_conversion = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='unidad_conversion')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='cantidad')
    unidadcompra = models.ForeignKey(UnidadCompra,null=True,blank=True, on_delete=models.CASCADE, verbose_name='unidad compra')
    nombre_comercial = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nombre Comercial Producto')
    usuario = models.ForeignKey(User,null=True,blank=True, on_delete=models.CASCADE, verbose_name='usuario') 
    deposito = models.ForeignKey(Deposito,null=True,blank=True, on_delete=models.CASCADE, verbose_name='deposito') 
    marca = models.BooleanField(default=False, verbose_name = 'marca')
    factura = models.BooleanField(default=True, verbose_name = 'factura')
    cantidad_a_factura = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='cantidad_a_factura')
    convertido_a_factura = models.BooleanField(default=False, verbose_name = 'convertido_a_factura')
    
    
    @property
    def subtotal_dl(self):
        return self.subtotal_bs / self.cambioaplicado
    
    @property
    def subtotal_bs(self):
        return self.cantidad * self.costo_bs
    
    @property
    def cantidad_salida(self):
        return self.cantidad * self.unidad_conversion
    
    @property
    def monto_iva_dl(self):
        return self.subtotal_dl * (self.piva/100)

    @property
    def monto_iva_bs(self):
        return self.subtotal_bs * (self.piva/100)

    def __str__(self):
        return str(self.notaentrega)

    class Meta:
        verbose_name = 'DetalleNotaEntrega'
        verbose_name_plural = 'Detalles Notas Entrega'

class FacturaProveedor(models.Model):
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    fecha_entrega = models.DateTimeField(null=True, blank=True, verbose_name='Fecha Entrega')
    numerodocumento = models.CharField(max_length=30,null=True, blank=True, verbose_name='Numero Documento') 
    numerocontrol = models.CharField(max_length=30,null=True, blank=True, verbose_name='Numero control')
    proveedor = models.ForeignKey(Medico,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Proveedor Medico') 
    proveedor_compra = models.ForeignKey(Proveedor,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Proveedor Compra') 
    tipodocumento = models.ForeignKey(TipoDocumento,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Tipo Documento') 
    concepto = models.ForeignKey(Retencion,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Concepto') 
    nota = models.CharField(max_length=250,null=True, blank=True, verbose_name='Nota')
    tipomoneda = models.ForeignKey(Moneda,null=True,blank=True,default=1, on_delete=models.CASCADE, verbose_name='Moneda') 
    administrativo = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Administracion %')
    congelar_moneda = models.BooleanField(default=False, verbose_name = 'Cambio congelado')
    cambio_congelado = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='Tasa Cambio Congelada')
    monto_descuento_bs = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='monto_descuento_bs')
    porcentaje_descuento = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='porcentaje_descuento')
    fecha_cambio = models.DateField(null=True, blank=True, verbose_name='Fecha Cambio')
    tipo = models.CharField(max_length=2,null=True, blank=True, verbose_name='Tipo Factura')
    notaentrega = models.ForeignKey(NotaEntregaCompra,null=True,blank=True, on_delete=models.CASCADE, verbose_name='NotaEntregaCompra') 
    usuario = models.ForeignKey(User,null=True,blank=True, on_delete=models.CASCADE, verbose_name='usuario') 
    actualizada = models.BooleanField(default=False, verbose_name = 'actualizada')
    porcentaje_retencion_islr = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='porcentaje_retencion_islr')
    estatus =  models.CharField(max_length=3,null=True, blank=True, default='PEN', verbose_name='estatus') 
    abono_id = models.PositiveBigIntegerField(default=0, verbose_name='id_abono_correspondiente')
    sustraendo_bs = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='sustraendo_bs')
    comprobante = models.ForeignKey(RetencionISLR,null=True,blank=True, on_delete=models.CASCADE, verbose_name='RetencionISLR') 
    igtf = models.BooleanField(default=False, verbose_name = 'igtf')
    centro_costo = models.ForeignKey(CentroCostoFacturaCompra,null=True,blank=True, on_delete=models.SET_NULL, verbose_name='centro_costo') 

    @property
    def total_con_iva(self):
        total_subtotal_bs = sum(detalle.subtotal_bs for detalle in self.detallefacturaproveedor_set.all())
        total_iva = sum(detalle.subtotal_bs * (detalle.porc_iva / 100) for detalle in self.detallefacturaproveedor_set.all())
        return (total_subtotal_bs + total_iva) - ((total_subtotal_bs + total_iva) * (self.porcentaje_descuento/100))

    @property
    def subtotal_bs(self):
        return sum(detalle.subtotal_bs - detalle.monto_descuento_bs  for detalle in self.detallefacturaproveedor_set.all())
    
    @property
    def subtotal_factura_bs(self):
        return self.total_baseimponible_bs + self.total_exento_bs + self.monto_iva_bs

    @property
    def bi_factura_bs(self):
        return self.total_baseimponible_bs + self.total_exento_bs 
    
    @property
    def subtotal_factura_dl(self):
        return self.total_baseimponible_dl + self.total_exento_dl + self.monto_iva_dl
    
    @property
    def bi_factura_usd(self):
        if self.cambio_congelado > 0:
            return self.bi_factura_bs /  self.cambio_congelado
        else:
            return 0
    
    @property
    def total_gastos_bs(self):
        return sum(detalle.gastos_bs for detalle in self.detallefacturaproveedor_set.all())
    
    @property
    def total_gastos_medicos_bs(self):
        return ((self.total_baseimponible_bs + self.total_exento_bs) * (self.administrativo/100))*-1
    
    @property
    def total_gastos_medicos_dl(self):
        return ((self.total_baseimponible_dl + self.total_exento_dl) * (self.administrativo/100))*-1
    
    @property
    def total_gastos_dl(self):
         return sum(detalle.gastos for detalle in self.detallefacturaproveedor_set.all())
    
    @property
    def subtotal_dl(self):
        return self.subtotal_bs / self.cambio_congelado
    
    @property
    def monto_descuento_dl(self):
        return self.monto_descuento_bs / self.cambio_congelado
    
    @property
    def exento_bs(self):
        return self.detallefacturaproveedor_set.aggregate(tota_exento=Sum(((F('subtotal_bs'))-F('monto_descuento_bs')), filter=Q(porc_iva = 0)))['tota_exento'] or 0
    
    @property
    def total_retencion_en_detalle(self):
        resultado = self.detallefacturaproveedor_set.aggregate(
            total_retencion=Sum(
                F('subtotal_bs'),
                filter=Q(subtotal_bs__lt=0)
            )
        )
        return resultado['total_retencion'] or 0
    
    @property
    def total_exento_bs(self):
        return (self.exento_bs - (self.exento_bs * (self.porcentaje_descuento/100)) )

    @property
    def total_exento_dl(self):
        total_exento_detalle = self.detallefacturaproveedor_set.aggregate(tota_exento=Sum(((F('precio_bs')*F('cantidad'))/F('cambio_bcv') - (F('monto_descuento_bs')/F('cambio_bcv'))), filter=Q(porc_iva = 0)))['tota_exento'] or 0
        return total_exento_detalle


    @property
    def baseimponible_bs(self):
        return self.detallefacturaproveedor_set.aggregate(total_base=Sum((F('subtotal_bs')-F('monto_descuento_bs')), filter=Q(porc_iva__gt = 0)))['total_base'] or 0
    
    @property
    def total_baseimponible_bs(self):
        return (self.baseimponible_bs - (self.baseimponible_bs * (self.porcentaje_descuento/100)) )

    @property
    def monto_igtf(self):
        if self.igtf:
            return (float(self.total_baseimponible_bs) + float(self.total_exento_bs)) * (3/100)
        else:
            return 0

    @property
    def monto_igtf_dl(self):
        if self.igtf and self.monto_igtf > 0 and self.cambio_congelado > 0:
            return float(self.monto_igtf) / float(self.cambio_congelado)
        else:
            return 0

    @property
    def total_baseimponible_dl(self):
        total_baseimponible_dl_detalle = self.detallefacturaproveedor_set.aggregate(total_base=Sum(((F('precio_bs')*F('cantidad'))/F('cambio_bcv') - (F('monto_descuento_bs')/F('cambio_bcv'))), filter=Q(porc_iva__gt = 0)))['total_base'] or 0
        return total_baseimponible_dl_detalle

    @property
    def iva_bs(self):
        return (self.detallefacturaproveedor_set.aggregate(total_iva_b=Sum(((F('subtotal_bs')-F('monto_descuento_bs'))*(F('porc_iva')/100))))['total_iva_b'] or 0) 

    @property
    def total_otros_gastos_medicos_bs(self):
        monto_total_otros_gastos_medicos_bs = self.detallefacturaproveedor_set.aggregate(total_otros=Sum(F('subtotal_bs') * (F('porcentaje_retencion_gasto')/100), filter=Q(porcentaje_retencion_gasto__gt = 0)))['total_otros'] or 0
        return (monto_total_otros_gastos_medicos_bs * -1)

    @property
    def total_otros_gastos_medicos_dl(self):
        monto_total_otros_gastos_medicos_dl = self.detallefacturaproveedor_set.aggregate(total_otros=Sum((F('subtotal_bs') * (F('porcentaje_retencion_gasto')/100)/F('cambio_bcv')), filter=Q(porcentaje_retencion_gasto__gt = 0)))['total_otros'] or 0
        return (monto_total_otros_gastos_medicos_dl * -1)
    
    @property
    def monto_iva_bs(self):
        return self.iva_bs - (self.iva_bs * (self.porcentaje_descuento/100) )
    
    @property
    def monto_iva_dl(self):
        if self.monto_iva_bs == 0:
            return 0
        else:
            return (self.detallefacturaproveedor_set.aggregate(total_iva_d=Sum((((F('precio_bs')*F('cantidad'))/ F('cambio_bcv') -(F('monto_descuento_bs') / F('cambio_bcv')) )*(F('porc_iva')/100))))['total_iva_d'] or 0) 
    
    @property
    def retencion_iva_monto_bs(self):
        if self.proveedor_compra and hasattr(self.proveedor_compra, 'porcentaje_retencion'):
            return (self.monto_iva_bs * (self.proveedor_compra.porcentaje_retencion / 100))*-1
        return 0
    
    @property
    def retencion_medico_iva_monto_bs(self):
        if self.proveedor and hasattr(self.proveedor, 'porcentaje_retencion_iva'):
            return (self.monto_iva_bs * (self.proveedor.porcentaje_retencion_iva / 100))*-1
        return 0
    
    @property
    def retencion_medico_iva_monto_dl(self):
        if self.proveedor and hasattr(self.proveedor, 'porcentaje_retencion_iva'):
            return (self.monto_iva_dl * (self.proveedor.porcentaje_retencion_iva / 100))*-1
        return 0
    
    @property
    def retencion_iva_monto_dl(self):
        if self.proveedor_compra and hasattr(self.proveedor_compra, 'porcentaje_retencion'):
            return (self.monto_iva_dl * (self.proveedor_compra.porcentaje_retencion / 100))*-1
        return 0
    
    @property
    def retencion_islr_monto_bs(self):
        if (self.total_baseimponible_bs + self.total_exento_bs) > 0:
            return ((((self.total_baseimponible_bs + self.total_exento_bs)) * (self.porcentaje_retencion_islr/100))- self.sustraendo_bs) *-1
        else:
            return 0
        
    @property
    def sustraendo_dl(self):
        if self.sustraendo_bs == 0:
            return 0
        else:
            return self.sustraendo_bs / self.cambio_congelado

    @property
    def retencion_islr_monto_dl(self):
        if (self.total_baseimponible_dl + self.total_exento_dl) > 0:
            return ((((self.total_baseimponible_dl + self.total_exento_dl)) * (self.porcentaje_retencion_islr/100))- (self.sustraendo_dl )) *-1
        else:
            return 0

    @property
    def total_operacion_bs(self):
        return (((self.total_exento_bs + self.total_baseimponible_bs)-self.total_gastos_bs) + self.monto_iva_bs) + (self.retencion_islr_monto_bs + self.retencion_iva_monto_bs)

    @property
    def total_operacion_dl(self):
        return (((self.total_exento_dl + self.total_baseimponible_dl)-self.total_gastos_dl) + self.monto_iva_dl) + (self.retencion_islr_monto_dl + self.retencion_iva_monto_dl)

    
    @property
    def monto_abonado_factura_bs(self):
        # Abonos directos
        total_directo = self.factura_afectada.aggregate(
            total=Sum('montopago_bs')
        )['total'] or 0

        # Abonos múltiples que realmente afectan esta factura
        abonos_multiples_ids = TransaccionFacturaMultiple.objects.filter(
            factura=self
        ).values_list('abono_id', flat=True)

        total_multiple = AbonoCuentaPagar.objects.filter(
            id__in=abonos_multiples_ids,
            factura_pago_multiple=True
        ).aggregate(
            total=Sum('montopago_bs')
        )['total'] or 0

        return total_directo + total_multiple
    
    @property
    def monto_abonado_factura_dl(self):
        # Abonos directos
        total_directo = self.factura_afectada.aggregate(
            total=Sum('montopago')
        )['total'] or 0

        # Abonos múltiples que realmente afectan esta factura
        abonos_multiples_ids = TransaccionFacturaMultiple.objects.filter(
            factura=self
        ).values_list('abono_id', flat=True)

        total_multiple = AbonoCuentaPagar.objects.filter(
            id__in=abonos_multiples_ids,
            factura_pago_multiple=True
        ).aggregate(
            total=Sum('montopago')
        )['total'] or 0

        return total_directo + total_multiple
    
    @property
    def saldo_neto_factura_proveedor_bs(self):
        return self.total_operacion_bs - self.monto_abonado_factura_bs
    
    @property
    def saldo_neto_factura_proveedor_dl(self):
        if self.cambio_congelado > 0:
            return self.saldo_neto_factura_proveedor_bs / self.cambio_congelado
        else:
            return 0
    
    @property
    def total_transacciones_dolar(self):
        total = self.transaccion_set.aggregate(total_dl=Sum('monto_dolar'))['total_dl']
        return total or 0
    
    @property
    def total_transacciones_bs(self):
        total = self.transaccion_set.aggregate(total_dl=Sum('monto'))['total_dl']
        return total or 0
        
    @property
    def saldo_factura(self):
        return self.neto_pagar_medico_dl + (self.total_transacciones_dolar + self.total_pagos_recibos_dl )
    
    @property
    def saldo_factura_bs(self):
        return self.neto_pagar_medico_bs + (self.total_transacciones_bs + self.total_pagos_recibos_bs)

        
    @property
    def total_pagos_recibos(self):
        """
        Devuelve un diccionario con los totales en Bs y USD
        de las transacciones asociadas a las facturas recibo
        vinculadas a esta factura legal.
        """
        from .models import PagoReciboFacturaMedico, Transaccion  # Import local para evitar bucles

        totales = (
            Transaccion.objects.filter(
                cuentapagar_id__in=PagoReciboFacturaMedico.objects
                .filter(factura_legal_id=self.id)
                .values_list('factura_recibo_id', flat=True)
            )
            .aggregate(
                total_bs=Sum('monto'),
                total_usd=Sum('monto_dolar')
            )
        )
        return {
            'total_bs': totales['total_bs'] or 0,
            'total_usd': totales['total_usd'] or 0,
        }

    @property
    def total_pagos_recibos_bs(self):
        """Total de pagos en bolívares."""
        return self.total_pagos_recibos['total_bs']

    @property
    def total_pagos_recibos_dl(self):
        """Total de pagos en dólares."""
        return self.total_pagos_recibos['total_usd']
    
    @property
    def neto_pagar_medico_bs(self):
        return self.subtotal_factura_bs + self.retencion_medico_iva_monto_bs + self.total_gastos_medicos_bs + self.retencion_islr_monto_bs + self.total_otros_gastos_medicos_bs
    
    @property
    def neto_pagar_medico_dl(self):
        return self.subtotal_factura_dl + self.retencion_medico_iva_monto_dl + self.total_gastos_medicos_dl + self.retencion_islr_monto_dl + self.total_otros_gastos_medicos_dl

    @property
    def distribucion_medico_pago_monto_bs(self):
        return self.distribucionpagomedico_set.aggregate(tota_bolivar=Sum(F('monto_bs')))['tota_bolivar'] or 0

    @property
    def distribucion_medico_pago_monto_dl(self):
        return self.distribucionpagomedico_set.aggregate(tota_dolar=Sum(F('monto')))['tota_dolar'] or 0

    @property
    def saldo_bs_distribucion_pago(self):
        return self.neto_pagar_medico_bs - self.distribucion_medico_pago_monto_bs

    @property
    def saldo_dl_distribucion_pago(self):
        return self.neto_pagar_medico_dl - self.distribucion_medico_pago_monto_dl
        

    def __str__(self):
        return str(self.numerodocumento)

    class Meta:
        verbose_name = 'FacturaProveedor'
        verbose_name_plural = 'Facturas Proveedores'


class FacturaMedico(models.Model):
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    fecha_entrega = models.DateField(null=True, blank=True, verbose_name='Fecha Entrega')
    numerodocumento = models.CharField(max_length=15,null=True, blank=True, verbose_name='Numero Documento') 
    numerocontrol = models.CharField(max_length=15,null=True, blank=True, verbose_name='Numero control')
    medico = models.ForeignKey(Medico,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Proveedor') 
    factura = models.ForeignKey(FacturaProveedor,null=True,blank=True, on_delete=models.CASCADE, verbose_name='factura') 
    usuario = models.ForeignKey(User,null=True,blank=True, on_delete=models.CASCADE, verbose_name='usuario') 
    comprobante = models.ForeignKey(RetencionISLR,null=True,blank=True, on_delete=models.CASCADE, verbose_name='comprobante') 


    @property
    def total_pagado_medico_dolar(self):
        total = Transaccion.objects.filter(
            cuentapagar=self.factura
        ).aggregate(total=Sum('monto_dolar'))['total']

        return total or 0
    
    def __str__(self):
        return str(self.numerodocumento)

    class Meta:
        verbose_name = 'FacturaMedico'
        verbose_name_plural = 'Facturas Medicos'
        
class DetalleFacturaProveedor(models.Model):
    factura = models.ForeignKey(FacturaProveedor,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Factura')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='cantidad')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='precio_unitario')
    precio_modificado = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='precio_modificado')
    gastos = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Gastos ADM')
    gastos_bs = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Gastos ADM BS')
    porc_iva = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='IVA %')
    montoiva = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name='IVA MONTO')
    montoiva_dl = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='IVA MONTO DL')
    precio_bs = models.DecimalField(max_digits=15, decimal_places=5, default=0,verbose_name='Precio Bs')
    precio_dl = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Precio Dl')
    descripcion = models.CharField(max_length=500,null=True, blank=True, verbose_name='Descripcion')
    cirugia = models.ForeignKey(Cirugia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Cirugia')
    atencion_inmediata = models.ForeignKey(AtencionInmediata,null=True,blank=True, on_delete=models.CASCADE, verbose_name='atencion_inmediata')
    detalle = models.ForeignKey(DetalleBaremo,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Detalle') 
    manual = models.BooleanField(default=False, verbose_name = 'Ingreso Manual')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Sub Total')
    subtotal_bs = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Sub Total BS')
    subtotal_dl = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Sub Total DL')
    cambio_bcv = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='Cambio BCV Bs')
    congelar_moneda = models.BooleanField(default=False, verbose_name = 'Cambio Congelado')
    detallenotaentrega = models.ForeignKey(DetalleNotaEntrega,null=True,blank=True, on_delete=models.CASCADE, verbose_name='detallenotaentrega')
    monto_descuento_bs = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='descuento_bs')
    usuario = models.ForeignKey(User,null=True,blank=True, on_delete=models.CASCADE, verbose_name='usuario') 
    inventario = models.ForeignKey(Inventario,null=True,blank=True, on_delete=models.CASCADE, verbose_name='inventario_id') 
    deposito_carga = models.ForeignKey(Deposito,null=True,blank=True, on_delete=models.CASCADE, verbose_name='deposito_carga_id') 
    porcentaje_retencion_gasto = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='porcentaje_retencion_gasto')
    moneda_pago = models.ForeignKey(Moneda,null=True,blank=True, on_delete=models.CASCADE, verbose_name='moneda_pago')
    no_inventario =  models.BooleanField(default=False, verbose_name = 'no_inventario')
    nueva_categoria = models.ForeignKey(CategoriaInventario,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Categoria')
    nuevo_laboratorio = models.ForeignKey(LaboratorioMedicina,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Laboratorio')
    nueva_presentacion_salida = models.ForeignKey(PresentacionMedicina,null=True,blank=True, on_delete=models.CASCADE,related_name='nueva_presentacion_salida', verbose_name='Presentacion Salida')
    nuevo_lote = models.CharField(max_length=20, null=True, blank=True, verbose_name='Lote Producto')
    nuevo_nombre_comercial = models.CharField(max_length=200, null=True, blank=True, verbose_name='nuevo_nombre_comercial')
    nueva_unidadcompra = models.ForeignKey(UnidadCompra,null=True,blank=True, on_delete=models.CASCADE,related_name='nueva_unidadcompra', verbose_name='unidadcompra')
    nueva_clasificacion = models.ForeignKey(UnidadProducto, on_delete=models.CASCADE, null=True,blank=True, verbose_name='unidad')
    nueva_fechaelaboracion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha elaboracion')
    nueva_fechavencimiento = models.DateTimeField(null=True, blank=True, verbose_name='Fecha vencimiento')
    precio_unico_factor_dl = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name='precio_unico_factor_dl')
    unidades_con_factor = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name='unidades_con_factor')
    baremo_pago_tercero = models.ForeignKey(BaremoPagoTercero,null=True,blank=True,on_delete=models.SET_NULL, verbose_name='baremo_pago_tercero')
    nc =  models.BooleanField(default=False, verbose_name = 'nota credito')
    

    @property
    def neto_con_descuento(self):
        return self.subtotal_bs - self.monto_descuento_bs

    @property
    def gasto_dl(self):
        if self.porcentaje_retencion_gasto > 0:
            return (self.precio_unitario * self.cantidad) * (self.porcentaje_retencion_gasto/100)
        else:
            return 0

    @property
    def gasto_bs(self):
        if self.porcentaje_retencion_gasto > 0:
            return self.subtotal_bs * (self.porcentaje_retencion_gasto/100)
        else:
            return 0

    def apagar(self):
        return (self.cantidad * self.precio_unitario) 
    
    def netounico(self):
        return (self.precio_unitario) - (self.gastos/self.cantidad)
    
    def apagarbs(self):
        return (self.cantidad * self.precio_bs )
    
    def total_precio(self):
        return self.cantidad * self.precio_unitario
    
    def __str__(self):
        return str(self.factura.proveedor)

    class Meta:
        verbose_name = 'DetalleFacturaProveedor'
        verbose_name_plural = 'Detalles Facturas Proveedores'

class PagoReciboFacturaMedico(models.Model):
    factura_legal = models.ForeignKey(FacturaProveedor,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Factura', related_name='factura_legal')
    factura_recibo = models.ForeignKey(FacturaProveedor,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Factura', related_name='factura_recibo')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True, verbose_name='Usuario')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')


    def __str__(self):
        return str(self.factura.proveedor)

    class Meta:
        verbose_name = 'PagoReciboFacturaMedico'
        verbose_name_plural = 'PagosRecibosFacturasMedicos'


class DepositoTransito(models.Model):
    detallenota = models.ForeignKey(DetalleNotaEntrega,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Detalle Nota')
    deposito = models.ForeignKey(Deposito,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Deposito')
    cantidad_deposito = models.PositiveBigIntegerField(default=50000,verbose_name='Cantidad Total') 
    
    def __str__(self):
        return str(self.deposito)

    class Meta:
        verbose_name = 'DepositoTransito'
        verbose_name_plural = 'Depositos Destinos' 




class TablaImpuesto(models.Model):
    sustraendo = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='sustraendo')
    montotope = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='monto mayor a')
        
    def __str__(self):
        return str(self.sustraendo)

    class Meta:
        verbose_name = 'TablaImpuesto'
        verbose_name_plural = 'Sustraendo Facturas Proveedores'
        
        
class OrigenPago(models.Model):
    nombre= models.CharField(max_length=250, null=True,blank=True, verbose_name='Descripcion')
    numerocuenta = models.CharField(max_length=20, null=True, blank=True, verbose_name='Numero de Cuenta')
    numeropago = models.CharField(max_length=15, null=True, blank=True, verbose_name='Numero de Pago')
    correo=models.EmailField(blank=True,null=True, verbose_name='Email')
    formapago = models.ForeignKey(FormaPago,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Forma de Pago')
    bancopago = models.ForeignKey(Banco,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Banco de Pago')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Pago')
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'OrigenPago'
        verbose_name_plural = 'Origen del Pago'


class CuentaxCobrar(models.Model):
    paciente = models.ForeignKey(Paciente,null=True,blank=True, on_delete=models.SET_NULL, verbose_name='Paciente')
    presupuesto = models.ForeignKey(Presupuesto,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Presupuesto', related_name='presupuesto')
    preingreso = models.ForeignKey(PreIngreso,null=True,blank=True, on_delete=models.CASCADE, verbose_name='preingreso')
    cirugia = models.ForeignKey(Cirugia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Cirugia', related_name='cirugia')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    pagado = models.BooleanField(default=False, verbose_name = 'Pagado')
    atencion_inmediata = models.ForeignKey(AtencionInmediata,null=True,blank=True, on_delete=models.CASCADE, verbose_name='atencion_inmediata')
    atencion_cortesia = models.ForeignKey(AtencionInmediataCortesia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='atencion_cortesia')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True, verbose_name='Usuario')
    
    @property
    def total_cobrar_monto(self):
        total_subtotal = sum(detalle.montocobrar for detalle in self.detallecuentacobrar_set.all()) + self.total_nc_sin_aplicar_dl
        if total_subtotal < 0:
            total_subtotal = 0
        
        return total_subtotal
    
    @property
    def total_monto(self):
        total_subtotal_monto = sum(detalle.montocobrar for detalle in self.detallecuentacobrar_set.all() if detalle.montocobrar > 0)
        return total_subtotal_monto
    
    @property
    def total_monto_pagado(self):
        total_subtotal_monto_pagado = sum(detalle.montocobrar for detalle in self.detallecuentacobrar_set.all() if detalle.montocobrar < 0)
        return total_subtotal_monto_pagado

    @property
    def total_monto_pagado_bs(self):
        total_monto_pagado_bs = sum(detalle.montocobrar_bs for detalle in self.detallecuentacobrar_set.all() if detalle.montocobrar_bs < 0)
        return total_monto_pagado_bs
    
    @property
    def total_nc_sin_aplicar_bs(self):
        total = Decimal('0')

        # Recorremos cada detalle de la cuenta
        for detalle in self.detallecuentacobrar_set.all():
            # Recorremos cada nota de crédito asociada a ese detalle
            for nc in detalle.notacredito_origen.all():
                if not nc.aplicada:  # solo si aplicada = False
                    total += nc.saldo_bs

        return total
    
    @property
    def total_nc_sin_aplicar_dl(self):
        total = Decimal('0')

        # Recorremos cada detalle de la cuenta
        for detalle in self.detallecuentacobrar_set.all():
            # Recorremos cada nota de crédito asociada a ese detalle
            for nc in detalle.notacredito_origen.all():
                if not nc.aplicada:  # solo si aplicada = False
                    total += nc.saldo

        return total
   
    def __str__(self):
        return str(self.paciente)

    class Meta:
        verbose_name = 'CuentaxCobrar'
        verbose_name_plural = 'Cuentas x Cobrar'
        
 
        

class RegistroDocumento(models.Model):
    factura = models.ForeignKey(FacturaProveedor,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Documento')
    facturamedico = models.ForeignKey(FacturaMedico,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Factura Medico')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    fecha_entrega = models.DateTimeField(auto_now=True, verbose_name='Fecha Entrega')
    total_bruto = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Total Bruto')
    total_neto = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Total Neto')
    total_gastos = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Total Gastos')
    total_bruto_bs = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Total Bruto BS')
    total_neto_bs = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Total Neto BS')
    total_gastos_bs = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Total Gastos BS')
    total_iva = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Total Iva')
    total_retencion = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Total Retencion')
    tipodocumento = models.ForeignKey(TipoDocumento,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Tipo Documento') 
    tasa_bcv_calculo = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='tasa_bcv_calculo')
    
    
    def __str__(self):
        return str(self.factura.proveedor)

    class Meta:
        verbose_name = 'RegistroDocumento'
        verbose_name_plural = 'Registro Documentos'

class Transaccion(models.Model):
    bancolocal = models.ForeignKey(BancoLocal, on_delete=models.CASCADE,null=True,blank=True, verbose_name = 'Banco Local')
    pagomedico = models.ForeignKey(PagoMedico, on_delete=models.CASCADE, null=True, blank=True, verbose_name = 'Pago Medico')
    banco = models.ForeignKey(FormaPagoProveedor, on_delete=models.CASCADE,null=True, blank=True, verbose_name = 'Pago Proveedor')
    monto = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name='Monto')
    monto_dolar = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Monto Dolar')
    tasa_bcv = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='Tasa BCV')
    fechatransaccion=models.DateTimeField(null=True, blank=True, verbose_name='Fecha transaccion')
    fecha_act=models.DateTimeField(null=True, blank=True, auto_now_add=True, verbose_name='Actualizado el')
    descripcion = models.CharField(max_length=250,null=False, blank=False, verbose_name='Descripcion')
    referencia = models.CharField(max_length=20,null=False, blank=False, verbose_name='Referencia')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    nota = models.CharField(max_length=250,null=True, blank=True, verbose_name='Nota del Pago')
    cuentacobrar = models.ForeignKey(CuentaxCobrar, on_delete=models.CASCADE,null=True, blank=True, verbose_name = 'Detalle Cuenta Cobrar')
    cuentapagar = models.ForeignKey(FacturaProveedor, on_delete=models.CASCADE,null=True, blank=True, verbose_name = 'Factura proveedor')
    registro_documento = models.ForeignKey(RegistroDocumento, on_delete=models.CASCADE,null=True, blank=True, verbose_name = 'RegistroDocumento')
    fechatasa=models.DateTimeField(null=True, blank=True, verbose_name='Fecha tasa bcv')
    mediomoneda = models.ForeignKey(FormaPago, on_delete=models.CASCADE,null=True, blank=True, verbose_name = 'mediopago')
    notacredito = models.PositiveIntegerField(default=0, verbose_name='id notacredito')
    multiple_factura = models.BooleanField(default=False, verbose_name="Pago de multiples facturas")
    
    def __str__(self):
        return str(self.bancolocal)

    class Meta:
        verbose_name = 'Transaccion'
        verbose_name_plural = 'Transacciones'

class DetalleCuentaCobrar(models.Model):
    cuentacobrar = models.ForeignKey(CuentaxCobrar,null=True,blank=True, on_delete=models.CASCADE, verbose_name='CuentaxCobrar')
    montocobrar = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='monto cobrar')
    montocobrar_bs = models.DecimalField(max_digits=14, decimal_places=2, default=0,verbose_name='monto cobrar BS')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    descripcion = models.CharField(max_length=250,null=True, blank=True, verbose_name='Descripcion')
    estatus = models.CharField(max_length=50,null=True, blank=True, default=' * ', verbose_name='status')
    origen_pago = models.ForeignKey(OrigenPago,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Origen Pago')
    destino_pago = models.ForeignKey(BancoLocal,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Destino Pago')
    retencion = models.ForeignKey(Retencion,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Retencion')
    transaccion = models.ForeignKey(Transaccion,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Transaccion ID')
    nroretencion = models.CharField(max_length=15,null=True, blank=True, verbose_name='Nro Retencion')
    tasa_bcv = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='Tasa BCV')
    notacredito = models.BooleanField(default=False, verbose_name='Nota de credito aplicada')
    notacredito_manual_id = models.PositiveIntegerField(default=0, verbose_name='id notacredito_manual_id')
    usuario = models.ForeignKey(User,null=True,blank=True, on_delete=models.CASCADE, verbose_name='usuario')
    
    
    def __str__(self):
        return str(self.cuentacobrar.paciente.nombre)

    class Meta:
        verbose_name = 'DetalleCuentaCobrar'
        verbose_name_plural = 'Detalle de CuentaCobrar'
        

        
class PagadorUnico(models.Model):
    cedula = models.CharField(max_length=15,null=False, blank=False, unique=True, verbose_name='Cedula')
    nombre = models.CharField(max_length=200,null=True, blank=True, verbose_name='Nombre y Apellido')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    direccion = models.CharField(max_length=100,null=True, blank=True, verbose_name='Direccion')
    telefono = models.CharField(max_length=20,null=True, blank=True, verbose_name='Telefono')
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'PagadorUnico'
        verbose_name_plural = 'PagadoresUnicos'
        
class NotaCreditoCtaCobrar(models.Model):
    pagador = models.ForeignKey(PagadorUnico,null=True,blank=True, on_delete=models.CASCADE, verbose_name='pagador')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='saldo')
    saldo_bs = models.DecimalField(max_digits=14, decimal_places=2, default=0,verbose_name='saldo_bs')
    tasa = models.DecimalField(max_digits=14, decimal_places=4, default=0,verbose_name='tasa')
    fechatasa=models.DateField(null=True, blank=True, verbose_name='Fecha tasa bcv')
    descripcion = models.CharField(max_length=250,null=True, blank=True, verbose_name='Descripcion pago')
    detallecuentaxcobrar = models.ForeignKey(DetalleCuentaCobrar,null=True,blank=True, on_delete=models.CASCADE, verbose_name='DetalleCuentaCobrar', related_name='notacredito_origen')
    cuentaxcobrar_aplicada = models.ForeignKey(CuentaxCobrar,null=True,blank=True, on_delete=models.CASCADE, verbose_name='CuentaCobrar',  related_name='notacredito_aplicada')
    aplicada = models.BooleanField(default=False, verbose_name = 'aplicada')
    presupuesto_referencia = models.ForeignKey(Presupuesto,null=True,blank=True, on_delete=models.SET_NULL, verbose_name='presupuesto_referencia')
    fecha_pago = models.DateTimeField(null=True, blank=True, verbose_name='fecha_pago')
    autogenerada = models.BooleanField(default=False, verbose_name='Nota de credito autogenerada')
    forma_pago = models.ForeignKey(FormaPago, on_delete=models.CASCADE,null=True, blank=True, verbose_name = 'forma_pago')

    @property
    def saldo_actual_nota_dl(self):
        total_aplicado = self.historiales.aggregate(
            total=Sum('monto_aplicado_dl')
        )['total'] or Decimal('0.00')

        return self.saldo - total_aplicado
    
    def __str__(self):
        return self.pagador.nombre

    class Meta:
        verbose_name = 'NotaCreditoCtaCobrar'
        verbose_name_plural = 'NotasCreditosCtaCobrar'

class HistoriaNotaCreditoCC(models.Model):
    notacredito = models.ForeignKey(NotaCreditoCtaCobrar, on_delete=models.CASCADE, verbose_name='nota credito padre', related_name='historiales')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    monto_aplicado_dl = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='saldo')
    monto_aplicado_bs = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name='saldo_bs')
    tasa = models.DecimalField(max_digits=14, decimal_places=4, default=0,verbose_name='tasa')
    fechatasa=models.DateField(null=True, blank=True, verbose_name='Fecha tasa bcv')
    descripcion = models.CharField(max_length=250,null=True, blank=True, verbose_name='Descripcion pago')
    detallecuentaxcobrar = models.ForeignKey(DetalleCuentaCobrar,null=True,blank=True, on_delete=models.CASCADE, verbose_name='DetalleCuentaCobrar')
    cuentaxcobrar_aplicada = models.ForeignKey(CuentaxCobrar,null=True,blank=True, on_delete=models.CASCADE, verbose_name='CuentaCobrar')
    fecha_pago = models.DateTimeField(null=True, blank=True, verbose_name='fecha_pago')
    
    def __str__(self):
        return str(self.notacredito.pagador.nombre)

    class Meta:
        verbose_name = 'HistoriaNotaCreditoCC'
        verbose_name_plural = 'HistoriasNotasCreditoCCs'
        
        
class Pagador(models.Model):
    cedula = models.CharField(max_length=15,null=True, blank=True, verbose_name='Cedula')
    nombre = models.CharField(max_length=200,null=True, blank=True, verbose_name='Nombre y Apellido')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    direccion = models.CharField(max_length=100,null=True, blank=True, verbose_name='Direccion')
    telefono = models.CharField(max_length=20,null=True, blank=True, verbose_name='Telefono')
    detallecuentaxcobrar = models.ForeignKey(DetalleCuentaCobrar,null=True,blank=True, on_delete=models.CASCADE, verbose_name='DetalleCuentaCobrar')
    notacredito_origen = models.ForeignKey(NotaCreditoCtaCobrar,null=True,blank=True, on_delete=models.CASCADE, verbose_name='notacredito_origen', related_name='notacredito_origen')
    
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Pagador'
        verbose_name_plural = 'Pagadores Factura'
        
        
class AbonoCuentaPagar(models.Model):
    factura = models.ForeignKey(FacturaProveedor,null=True,blank=True, on_delete=models.CASCADE, verbose_name='factura pagar', related_name='factura_afectada')
    montopago = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='monto pago USD')
    montopago_bs = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='monto pago BS')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    fecha_pago = models.DateField(null=True, blank=True, verbose_name='FECHA_PAGO')
    descripcion = models.CharField(max_length=500,null=True, blank=True, verbose_name='Descripcion pago')
    referencia = models.CharField(max_length=30,null=True, blank=True, verbose_name='referencia pago')
    usuario = models.ForeignKey(User,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Pagador')
    origen_pago = models.ForeignKey(BancoLocal,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Origen Pago')
    destino_pago = models.ForeignKey(FormaPagoProveedor,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Destino Pago')
    transaccion = models.ForeignKey(Transaccion,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Transaccion_ID')
    tasa_bcv = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='Tasa BCV')
    factura_pago_multiple = models.BooleanField(default=False, verbose_name='pago multiple facturas')
    nota_credito_generada = models.ForeignKey(FacturaProveedor,null=True,blank=True, on_delete=models.CASCADE, verbose_name='nota_credito_generada pagar', related_name='nota_credito_generada')
    nota_credito = models.BooleanField(default=False, verbose_name='nota_credito')
    igtf = models.BooleanField(default=False, verbose_name='igtf')
    
    
    def __str__(self):
        if self.factura:
            return f"Abono Factura #{self.factura.id} - {self.montopago}"
        return f"Abono Múltiple #{self.id} - {self.montopago}"

    class Meta:
        verbose_name = 'AbonoCuentaPagar'
        verbose_name_plural = 'AbonosCuentasPagar'

    @classmethod
    def total_montopago_dl(cls, factura_id):
        return cls.objects.filter(
            Q(factura_id=factura_id) |
            Q(
                id__in=Subquery(
                    TransaccionFacturaMultiple.objects.filter(
                        factura_id=factura_id
                    ).values('abono_id')
                )
            )
        ).aggregate(total=Sum('montopago'))['total'] or 0
    
    @classmethod
    def total_montopago_bs(cls, factura_id):
        return cls.objects.filter(
            Q(factura_id=factura_id) |
            Q(
                id__in=Subquery(
                    TransaccionFacturaMultiple.objects.filter(
                        factura_id=factura_id
                    ).values('abono_id')
                )
            )
        ).aggregate(total_bs=Sum('montopago_bs'))['total_bs'] or 0
        
        
class RetencionPendiente(models.Model):
    medico = models.ForeignKey(Medico,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Medico')
    baseimponible = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='baseimponible bs')
    baseimponible_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='baseimponible usd')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    documento = models.ForeignKey(RegistroDocumento,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Recibo')
    aplicado = models.BooleanField(default=False, verbose_name = 'Aplicado')
    factura = models.ForeignKey(FacturaProveedor,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Factura')
    
    def __str__(self):
        return str(self.medico)

    class Meta:
        verbose_name = 'RetencionPendiente'
        verbose_name_plural = 'RetencionesPendientes Medicos'
        
        



class TipoDescarga(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True, unique=True, verbose_name='TipoDescarga')
    descripcion = models.CharField(max_length=250, null=True, blank=True,  verbose_name='descripcion')
    comprobante = models.BooleanField(verbose_name='Comprobante', default=False)
    solicitud = models.BooleanField(verbose_name='solicitud', default=False)
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'TipoDescarga'
        verbose_name_plural = 'Movimiento de Producto' 


class MateriaPrimaInventario(models.Model):
    nota = models.CharField(max_length=200,  blank=True, null=True, verbose_name='nota')
    materia_prima = models.ForeignKey(Inventario,on_delete=models.CASCADE, null=True, blank=True, verbose_name='materia_prima', related_name='materia_prima')
    producto_terminado = models.ForeignKey(Inventario,on_delete=models.CASCADE, null=True, blank=True, verbose_name='producto_terminado', related_name='producto_terminado')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='cantidad')
    precio_dl = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='precio_dl')
    subtotal_precio_dl = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='subtotal_precio_dl')
    deposito = models.ForeignKey(Deposito, on_delete=models.CASCADE, null=True, blank=True, verbose_name='deposito')

    
    def __str__(self):
        return str(self.producto_terminado)

    class Meta:
        verbose_name = 'MateriaPrimaInventario'
        verbose_name_plural = 'Materias Primas Inventarios'



class InventarioDescarga(models.Model):
    inventario = models.ForeignKey(Inventario,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Inventario', related_name='InventarioDescarga')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='cantidad')
    tipodescarga = models.ForeignKey(TipoDescarga,null=True,blank=True, on_delete=models.CASCADE, verbose_name='TipoDescarga')
    deposito = models.ForeignKey(Deposito,null=True,blank=True, on_delete=models.CASCADE,related_name='deposito' , verbose_name='Deposito Salida')
    depositoentrada = models.ForeignKey(Deposito,null=True,blank=True, on_delete=models.CASCADE,related_name='depositoentrada' , verbose_name='Deposito Entrada')
    nota = models.CharField(max_length=250, null=True, blank=True, verbose_name='Notas')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    usuario = models.ForeignKey(User,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Usuario')
    cirugia = models.ForeignKey(Cirugia,on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Cirugia ID')
    persona = models.ForeignKey(Medico,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Persona entrega')
    descargamanual = models.CharField(max_length=10, null=True, blank=True, verbose_name='descargamanual')
    cantidad_traslado = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='cantidad_traslado')
    atencion_inmediata = models.ForeignKey(AtencionInmediata,null=True,blank=True, on_delete=models.CASCADE, verbose_name='atencion_inmediata')
    atencion_cortesia = models.ForeignKey(AtencionInmediataCortesia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='atencion_cortesia')
    preingreso = models.ForeignKey(PreIngreso,null=True,blank=True, on_delete=models.CASCADE, verbose_name='preingreso')
    consumocirugia = models.ForeignKey(ConsumoCirugia,null=True,blank=True, on_delete=models.CASCADE, verbose_name='consumocirugia')
    materiaprima = models.ForeignKey(MateriaPrimaInventario,null=True,blank=True, on_delete=models.CASCADE, verbose_name='materiaprima')
    reciclado = models.BooleanField(verbose_name='reciclado', default=False)

    
    def __str__(self):
        return self.tipodescarga.nombre

    class Meta:
        indexes = [
            models.Index(fields=['inventario', 'deposito']),
            models.Index(fields=['tipodescarga']),
        ]
        verbose_name = 'InventarioDescarga'
        verbose_name_plural = 'Movimiento de Inventario' 
        
class NumeracionFactura(models.Model):
    numero_factura = models.PositiveIntegerField(null=False, blank=False, verbose_name='Numero Factura' )
    numero_control = models.PositiveIntegerField(null=False, blank=False, verbose_name='Numero control' )
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Usuario')
    cirugia = models.ForeignKey(Cirugia,on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Cirugia ID')
    fecha_act = models.DateTimeField(auto_now=True,verbose_name='Fecha Actualizacion')
    fecha_creacion = models.DateTimeField(auto_now_add=True,verbose_name='fecha_creacion')
    fecha_factura = models.DateField(null=True, blank=True, verbose_name='fecha_factura')
    
    def __str__(self):
        return str(self.cirugia.paciente)

    class Meta:
        verbose_name = 'NumeracionFactura'
        verbose_name_plural = 'NumeracionesFacturas'


class DetallePrefactura(models.Model): 
    factura =  models.ForeignKey(NumeracionFactura,on_delete=models.CASCADE,null=True,blank=True, verbose_name='factura')
    detallepresupuesto = models.ForeignKey(DetallePresupuesto,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Detalle de Presupuesto')
    convenio = models.ForeignKey(Convenio,on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Convenio')
    grupo = models.ForeignKey(GrupoBaremo,on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Grupo Baremo')
    detalle = models.ForeignKey(DetalleBaremo,on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Detalle') 
    plantilla = models.ForeignKey(Plantilla,on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Plantilla')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Usuario')
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='cantidad')
    cantidad_usada = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='cantidad usada')
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Precio')
    precio_usado = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Precio Usado')
    unidad = models.ForeignKey(Unidad,on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Unidad Baremo')
    notas= models.CharField(max_length=100,null=True, blank=True, verbose_name='Notas')
    tx = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='Tasa')
    ntqx = models.BooleanField(verbose_name='Nota Quirurgica', default=False)
    montotope = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Monto Tope')
    montoconsumo = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Monto Consumo')
    excedente = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Monto Excedente') 
    medico = models.ForeignKey(Medico,on_delete=models.SET_NULL,null=True,blank=True, verbose_name='Medico')
    alertaexcedente = models.BooleanField(verbose_name='Alertar Excedentes', default=True)
    precio_congelado_cirugia = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Precio Congelado Cirugia')
    precio_congelado_presupuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Precio Congelado Presupuesto')
    precio_congelado_excedente = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Precio Congelado excedente')
    grupo_factura = models.PositiveIntegerField(default=0,verbose_name='grupo_factura')
    fecha_act = models.DateTimeField(auto_now=True,verbose_name='Fecha Actualizacion')
    fecha_creacion = models.DateTimeField(auto_now_add=True,verbose_name='fecha_creacion')
    cirugia =  models.ForeignKey(Cirugia,on_delete=models.CASCADE,null=True,blank=True, verbose_name='cirugia')
    
    @property
    def precio_unitario(self):
        if self.cantidad_usada > 0:
            total_unitario = self.precio_congelado_cirugia / self.cantidad_usada
        else:
            total_unitario = self.precio_congelado_cirugia / 1
            
        return total_unitario
    
    def __str__(self):
        return str(self.detallepresupuesto)

    class Meta:
        verbose_name = 'DetallePrefactura'
        verbose_name_plural = 'DetallesPrefactura'


class InventarioSolicitud(models.Model):
    producto = models.ForeignKey(Inventario,on_delete=models.CASCADE,null=True,blank=True, verbose_name='Inventario')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='cantidad')
    usuario = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True, verbose_name='usuario')
    fecha_solicitud = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Solicitud')
    fecha_despacho = models.DateTimeField(null=True, auto_now=True, verbose_name='Fecha Actualizacion')
    pendiente = models.BooleanField(verbose_name='Apendiente', default=True)
    depositoorigen = models.ForeignKey(Deposito,on_delete=models.CASCADE,null=True,blank=True, related_name='depositoorigen', verbose_name='depositoorigen')
    existenciaorigen = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='existenciaorigen')
    solicitante = models.ForeignKey(Deposito,on_delete=models.CASCADE,null=True,blank=True,related_name='depositosolicitante', default=1 ,verbose_name='depositosolicitante')


    def __str__(self):
        return str(self.producto)

    class Meta:
        verbose_name = 'InventarioSolicitud'
        verbose_name_plural = 'InventarioSolicitudes'



class InventarioHistoria(models.Model):
    inventario = models.ForeignKey(Inventario,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Producto')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Costo')
    venta = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='venta')
    tasa = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='tasa')
    piva = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='piva')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    unidadcompra = models.ForeignKey(UnidadCompra,null=True,blank=True, on_delete=models.CASCADE,verbose_name='unidadcompra')
    presentacion = models.ForeignKey(PresentacionMedicina,null=True,blank=True, on_delete=models.CASCADE,related_name='presentacion_entrada_his', verbose_name='Presentacion')
    presentacion_salida = models.ForeignKey(PresentacionMedicina,null=True,blank=True, on_delete=models.CASCADE,related_name='presentacion_salida_his', verbose_name='Presentacion Salida')
    notaentrega = models.ForeignKey(NotaEntregaCompra,null=True,blank=True, on_delete=models.CASCADE, related_name='nota_entrega', verbose_name='NotaEntregaCompra')
    factura_compra = models.ForeignKey(FacturaProveedor,null=True,blank=True, on_delete=models.CASCADE, related_name='nota_entrega', verbose_name='factura_compra')
    lote = models.CharField(max_length=20, null=True, blank=True, verbose_name='Lote Producto')
    laboratorio = models.ForeignKey(LaboratorioMedicina, null=True, blank=True, on_delete=models.CASCADE, verbose_name='laboratorio')
    fecha_vencimiento = models.DateField(null=True, blank=True, default=date.today,verbose_name='Fecha Vence')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='cantidad')
    factor = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name='factor')

    def unidades(self):
        return (self.cantidad * self.factor) 

    def monto_bs(self):
        return (self.costo * self.tasa) 
    
    def __str__(self):
        return str(self.inventario)

    class Meta:
        verbose_name = 'InventarioHistoria'
        verbose_name_plural = 'InventarioHistorias' 


class ImagenPhoto(models.Model):
    image = models.ImageField(upload_to='photos/')
    created_at = models.DateTimeField(auto_now_add=True)
    cedula= models.CharField(max_length=15, blank=True, null=True,unique=True, verbose_name='Cedula')

    def __str__(self):
        return f'Photo {self.id}'



class LogInventario(models.Model):
    inventario = models.ForeignKey(Inventario,null=True,blank=True, on_delete=models.SET_NULL, verbose_name='Inventario')
    cantidad = models.PositiveBigIntegerField(default=0,verbose_name='cantidad')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    usuario = models.ForeignKey(User,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Usuario')
    cirugia = models.ForeignKey(Cirugia, on_delete=models.SET_NULL, null=True,blank=True, verbose_name='Cirugia ID')
    nota= models.CharField(max_length=500, blank=True, null=True, verbose_name='nota')

    def __str__(self):
        return self.inventario.nombre

    class Meta:
        verbose_name = 'LogInventario'
        verbose_name_plural = 'LogInventarios' 
        
class LogDetallePresupuesto(models.Model):
    detalle = models.CharField(max_length=200,null=True,blank=True, verbose_name='DetalleBaremo')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    usuario = models.ForeignKey(User,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Usuario')
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.SET_NULL, null=True,blank=True, verbose_name='presupuesto ID')
    nota= models.CharField(max_length=500, blank=True, null=True, verbose_name='nota')
    factor = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='factor')
    monto_original = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='monto_original')

    def __str__(self):
        return self.detalle.nombre

    class Meta:
        verbose_name = 'LogDetallePresupuesto'
        verbose_name_plural = 'LogDetallePresupuestos' 
        

class InventarioCompuesto(models.Model):
    consumo = models.ForeignKey(ConsumoCirugia,on_delete=models.CASCADE,null=True,blank=True, verbose_name='consumo')
    usuario = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True, verbose_name='usuario')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='cantidad')


    def __str__(self):
        return str(self.consumo.inventario.nombre)

    class Meta:
        verbose_name = 'InventarioCompuesto'
        verbose_name_plural = 'InventariosCompuestos'
        
       
class DebitoCredito(models.Model):
    transaccion = models.ForeignKey(Transaccion, on_delete=models.CASCADE,null=True,blank=True, verbose_name = 'transaccion')
    cuenta_origen = models.CharField(max_length=250,null=True, blank=True, verbose_name='Cuenta')
    cuenta_destino = models.CharField(max_length=250,null=True, blank=True, verbose_name='cuenta_destino')
    medico_proveedor = models.CharField(max_length=250,null=True, blank=True, verbose_name='medico proveedor')
    monto_bolivares = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name='Monto Bolivar')
    monto_dolar = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='Monto Dolar')
    tasa_bcv = models.DecimalField(max_digits=10, decimal_places=4, default=0,verbose_name='Tasa BCV')
    movimiento = models.CharField(max_length=20,null=True, blank=True, verbose_name='movimiento')
    fechatransaccion=models.DateTimeField(null=True, blank=True, auto_now_add=True, verbose_name='Actualizado el')
    descripcion = models.CharField(max_length=250,null=True, blank=True, verbose_name='Descripcion')
    referencia = models.CharField(max_length=20,null=True, blank=True, verbose_name='Referencia')
    usuario = models.CharField(max_length=50,null=True, blank=True, verbose_name='username')
    formapago = models.CharField(max_length=100,null=True, blank=True, verbose_name='formapago')
    moneda = models.CharField(max_length=20,null=True, blank=True, verbose_name='moneda')
    monto_unico =  models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name='monto_unico')
    dolares =  models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name='dolares')
    motivo =  models.CharField(max_length=300,null=True, blank=True, verbose_name='motivo')
    notacredito = models.ForeignKey(NotaCreditoCtaCobrar, on_delete=models.CASCADE,null=True,blank=True, verbose_name = 'notacredito')
    
    
    def __str__(self):
        return self.descripcion

    class Meta:
        verbose_name = 'DebitoCredito'
        verbose_name_plural = 'DebitosCreditos'
        
        
class LogCuentaCobrar(models.Model):
    monto_bs = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='monto_bs')
    monto_dl = models.DecimalField(max_digits=10, decimal_places=2, default=0,verbose_name='monto_dl')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    usuario = models.ForeignKey(User,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Usuario')
    cirugia = models.ForeignKey(Cirugia, on_delete=models.SET_NULL, null=True,blank=True, verbose_name='Cirugia ID')
    ami = models.ForeignKey(AtencionInmediata, on_delete=models.SET_NULL, null=True,blank=True, verbose_name='Ami ID')
    preingreso = models.ForeignKey(PreIngreso, on_delete=models.SET_NULL, null=True,blank=True, verbose_name='Preingreso ID')
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.SET_NULL, null=True,blank=True, verbose_name='presupuesto ID')
    nota = models.CharField(max_length=500, default="Eliminacion de Pago en cuenta x cobrar" , blank=True, null=True, verbose_name='nota')

    def __str__(self):
        return self.nota

    class Meta:
        verbose_name = 'LogCuentaCobrar'
        verbose_name_plural = 'LogsCuentasCobrar' 
        
class LogEliminacion(models.Model):
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    usuario = models.ForeignKey(User,null=True,blank=True, on_delete=models.CASCADE, verbose_name='Usuario')
    descripcion = models.TextField(default="" , blank=True, null=True, verbose_name='Auditoria')

    def __str__(self):
        return self.descripcion

    class Meta:
        verbose_name = 'LogEliminacion'
        verbose_name_plural = 'LogEliminaciones' 
        
 
        
class DetalleSubBaremoConsumo(models.Model):
    subbaremo = models.ForeignKey(SubBaremo,on_delete=models.CASCADE,null=True, verbose_name='SubBaremo')
    detalle = models.ForeignKey(DetalleBaremo,on_delete=models.CASCADE,null=True, verbose_name='DetalleBaremo')
    cirugia =  models.ForeignKey(Cirugia,on_delete=models.CASCADE,null=True, verbose_name='cirugia')
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='cantidad')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    detalle_presupuesto = models.ForeignKey(DetallePresupuesto,on_delete=models.CASCADE,null=True,blank=True, verbose_name='detalle_presupuesto')
    
   
    def __str__(self):
        return self.subbaremo.nombre_subbaremo

    class Meta:
        verbose_name = 'DetalleSubBaremoConsumo'
        verbose_name_plural = 'DetalleSubBaremoConsumos Baremos'
        
class BaremoVinculado(models.Model):
    detalle_baremo = models.ForeignKey(DetalleBaremo,on_delete=models.CASCADE,null=True, verbose_name='detalle_baremo', related_name='detalle_baremo')
    detalle_principal = models.ForeignKey(DetalleBaremo,on_delete=models.CASCADE,null=True, verbose_name='detalle_principal', related_name='detalle_principal')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    
   
    def __str__(self):
        return str(self.detalle_baremo)

    class Meta:
        verbose_name = 'BaremoVinculado'
        verbose_name_plural = 'BaremosVinculados '

class EvaluacionPreanestesia(models.Model):
    pregunta = models.CharField(max_length=250,null=False, blank=False,unique=True, verbose_name='pregunta')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    modulo = models.CharField(max_length=4,null=False, blank=False,default='EVPA', verbose_name='modulo')
   
    def __str__(self):
        return str(self.pregunta)

    class Meta:
        verbose_name = 'EvaluacionPreanestesia'
        verbose_name_plural = 'EvaluacionesPreanestesias '


class ConsultaPreanestesia(models.Model):
    cirugia = models.ForeignKey(Cirugia,on_delete=models.CASCADE,null=False, blank=False, verbose_name='cirugia')
    medico = models.ForeignKey(Medico,on_delete=models.CASCADE,null=True, blank=True, verbose_name='medico')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    fecha_consulta = models.DateField(null=True,blank=True, verbose_name='fecha_consulta')
    antecedente_medico = models.TextField(null=True, blank=True, verbose_name='antecedente_medico')
    antecedente_qx = models.TextField(null=True, blank=True, verbose_name='antecedente_qx')
    alergia = models.TextField(null=True, blank=True, verbose_name='alergia')
    peso = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='peso')
    talla = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='talla')
    imc = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='imc')
    ta = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='ta')
    fr = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='fr')
    fc = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='fc')
    malla_i = models.BooleanField(default=False, verbose_name='malla_i')
    malla_ii = models.BooleanField(default=False, verbose_name='malla_ii')
    malla_iii = models.BooleanField(default=False, verbose_name='malla_iii')
    malla_iv = models.BooleanField(default=False, verbose_name='malla_iv')
    dtm = models.CharField(max_length=40,null=True, blank=True, verbose_name='dtm')
    dem = models.CharField(max_length=40,null=True, blank=True, verbose_name='dem')
    ao = models.CharField(max_length=40,null=True, blank=True, verbose_name='ao')
    rhmi = models.CharField(max_length=40,null=True, blank=True, verbose_name='rhmi')
    aao = models.CharField(max_length=40,null=True, blank=True, verbose_name='aao')
    nota = models.CharField(max_length=100,null=True, blank=True, verbose_name='nota')
    hb = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='hb')
    hto = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='hto')
    plaq = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='plaq')
    pt = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='pt')
    ptt = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='ptt')
    glisemia = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='glisemia')
    leucosito = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='leucosito')
    urea = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='urea')
    creatinina = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='creatinina')
    hiv = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='hiv')
    vdrl = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='vdrl')
    ekg = models.CharField(max_length=100,null=True, blank=True, verbose_name='ekg')
    rxtorax = models.CharField(max_length=100,null=True, blank=True, verbose_name='rxtorax')
    ecomls = models.CharField(max_length=100,null=True, blank=True, verbose_name='ecomls')
    eva_preoperatoria = models.TextField(null=True, blank=True, verbose_name='eva_preoperatoria')
    evaluaciones = models.TextField(null=True, blank=True, verbose_name='evaluaciones')
    categoria_asa_i = models.BooleanField(default=False, verbose_name='categoria_asa_i')
    categoria_asa_ii = models.BooleanField(default=False, verbose_name='categoria_asa_ii')
    categoria_asa_iii = models.BooleanField(default=False, verbose_name='categoria_asa_iii')
    categoria_asa_iv = models.BooleanField(default=False, verbose_name='categoria_asa_iv')
    categoria_asa_v = models.BooleanField(default=False, verbose_name='categoria_asa_v')
    categoria_asa_e = models.BooleanField(default=False, verbose_name='categoria_asa_e')
    recomendacion = models.TextField(null=True, blank=True, verbose_name='recomendacion')
    ipa = models.TextField(null=True, blank=True,default=0, verbose_name='ipa')
    firma = models.ImageField(upload_to='firmas_anestesia/', null=True, blank=True, verbose_name='Firma del Paciente')

    

    @property
    def peso_magro(self):
        if self.peso and self.talla:
            peso = float(self.peso)
            talla = float(self.talla)

            if self.cirugia.paciente.sexo == 'M':
                return round((0.407 * peso) + (0.267 * talla) - 19.2, 2)
            elif self.cirugia.paciente.sexo == 'F':
                return round((0.252 * peso) + (0.473 * talla) - 48.3, 2)
        return 0
    
    @property
    def peso_ideal(self):
        talla = float(self.talla)
        return round(
            50 + 0.9 * (talla - 152) if self.cirugia.paciente.sexo == 'M'
            else 45.5 + 0.9 * (talla - 152), 2
        )

    @property
    def peso_ajustado(self):
        if self.imc >= 30:
            return round(self.peso_ideal + 0.4 * (float(self.peso) - self.peso_ideal), 2)
        return float(self.peso)
    
    @property
    def superficie_corporal(self):
        return round(math.sqrt((float(self.peso) * float(self.talla)) / 3600), 2)
    
    @property
    def volemia_estimada(self):
        factor = 70 if self.cirugia.paciente.sexo == 'M' else 65
        return int(float(self.peso) * factor)

    @property
    def php(self):
        if self.hto > 0:
            return float((float(self.hto - 30) / float(self.hto)) * self.volemia_estimada)
        else:
            return 0
    
    @property
    def hemoglobina_estimada(self):
        return float(self.hto)/3


   
    def __str__(self):
        return str(self.cirugia.paciente.nombre)

    class Meta:
        verbose_name = 'ConsultaPreanestesia'
        verbose_name_plural = 'ConsultasPreanestesias'


class RespuestaEvaluacion(models.Model):
    pregunta = models.ForeignKey(EvaluacionPreanestesia,on_delete=models.CASCADE,null=False, blank=False, verbose_name='pregunta')
    respuesta = models.BooleanField()
    detalle =  models.TextField(null=True, blank=True, verbose_name='detalle')
    cantidad =  models.IntegerField(default=0, verbose_name='cantidad')
    consulta = models.ForeignKey(ConsultaPreanestesia,on_delete=models.CASCADE,null=False, blank=False, verbose_name='consulta')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
   
    def __str__(self):
        return str(self.pregunta)

    class Meta:
        verbose_name = 'RespuestaEvaluacion'
        verbose_name_plural = 'RespuestaEvaluaciones '

class LogDescuento(models.Model):
    presupuesto = models.ForeignKey(Presupuesto,on_delete=models.CASCADE,null=True, blank=True, verbose_name='presupuesto')
    cirugia = models.ForeignKey(Cirugia,on_delete=models.CASCADE,null=True, blank=True, verbose_name='cirugia')
    monto_descuento =  models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='monto_descuento')
    porcentaje_descuento =  models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='porcentaje_descuento')
    monto_aplicar_descuento =  models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='monto_aplicar_descuento')
    nuevo_monto =  models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='nuevo_monto')
    descripcion =  models.TextField(null=True, blank=True, verbose_name='descripcion')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
   
    def __str__(self):
        return str(self.descripcion)

    class Meta:
        verbose_name = 'LogDescuento'
        verbose_name_plural = 'LogDescuentos '


class HistoriaClinica(models.Model):
    cirugia = models.ForeignKey(Cirugia,on_delete=models.CASCADE,null=False, blank=False, verbose_name='cirugia')
    medico = models.ForeignKey(Medico,on_delete=models.CASCADE,null=True, blank=True, verbose_name='medico')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    fecha_consulta = models.DateField(null=True,blank=True, verbose_name='fecha_consulta')
    contacto = models.CharField(max_length=200,null=True, blank=True, verbose_name='contacto')
    telefono=models.CharField(max_length=11,null=False, blank=True, verbose_name='Telefono principal')
    responsable = models.ForeignKey(Responsable,on_delete=models.CASCADE,null=True, blank=True, verbose_name='responsable')
    req_imi = models.BooleanField(default=False, verbose_name='req_imi')
    req_oi = models.BooleanField(default=False, verbose_name='req_oi')
    req_cc = models.BooleanField(default=False, verbose_name='req_cc')
    req_tap = models.BooleanField(default=False, verbose_name='req_tap')
    req_ep = models.BooleanField(default=False, verbose_name='req_ep')
    req_ec = models.BooleanField(default=False, verbose_name='req_ec')
    req_epre = models.BooleanField(default=False, verbose_name='req_epre')
    usu_epreoperatorio = models.BooleanField(default=False, verbose_name='usu_epreoperatorio')
    usu_ecardiovascular = models.BooleanField(default=False, verbose_name='usu_ecardiovascular')
    usu_preanestesica = models.BooleanField(default=False, verbose_name='usu_preanestesica')
    motivo_consulta = models.CharField(max_length=200,null=False, blank=False, verbose_name='motivo_consulta')
    enfermedad_actual = models.TextField(null=True, blank=True, verbose_name='enfermedad_actual')
    idx = models.CharField(max_length=200,null=True, blank=True, verbose_name='idx')
    servicio_cargo = models.CharField(max_length=200,null=True, blank=True, verbose_name='servicio_cargo')
    antecedentes_familiar = models.TextField(null=True, blank=True, verbose_name='antecedentes_familiar')
    habito = models.TextField(null=True, blank=True, verbose_name='habito')
    antecedente_qx = models.TextField(null=True, blank=True, verbose_name='antecedente_qx')
    estudios = models.TextField(null=True, blank=True, verbose_name='estudios')
    diagnostico = models.TextField(null=True, blank=True, verbose_name='diagnostico')
    plan = models.TextField(null=True, blank=True, verbose_name='plan')
    peso = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='peso')
    talla = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='talla')
    imc = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='imc')
    pa = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='pa')
    fr = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='fr')
    fc = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='fc')
    temp = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='temp')

    @property
    def peso_magro(self):
        if self.peso and self.talla:
            peso = float(self.peso)
            talla = float(self.talla)

            if self.cirugia.paciente.sexo == 'M':
                return round((0.407 * peso) + (0.267 * talla) - 19.2, 2)
            elif self.cirugia.paciente.sexo == 'F':
                return round((0.252 * peso) + (0.473 * talla) - 48.3, 2)
        return 0
    
    @property
    def peso_ideal(self):
        talla = float(self.talla)
        return round(
            50 + 0.9 * (talla - 152) if self.cirugia.paciente.sexo == 'M'
            else 45.5 + 0.9 * (talla - 152), 2
        )

    @property
    def peso_ajustado(self):
        if self.imc >= 30:
            return round(self.peso_ideal + 0.4 * (float(self.peso) - self.peso_ideal), 2)
        return float(self.peso)
    
    @property
    def superficie_corporal(self):
        return round(math.sqrt((float(self.peso) * float(self.talla)) / 3600), 2)
    
    @property
    def volemia_estimada(self):
        factor = 70 if self.cirugia.paciente.sexo == 'M' else 65
        return int(float(self.peso) * factor)

   
    def __str__(self):
        return str(self.cirugia.paciente.nombre)

    class Meta:
        verbose_name = 'HistoriaClinica'
        verbose_name_plural = 'HistoriasClinicas'

class EvolucionHistoria(models.Model):
    TIPO_CHOICES = (
        ('em', 'Evolucion medica'),
        ('ee', 'Evolucion enfermeria'),
        ('om', 'Ordenes medicas'),
    )
    historiaclinica = models.ForeignKey(HistoriaClinica,on_delete=models.CASCADE,null=True, blank=True, verbose_name='historiaclinica')
    detalle = models.CharField(max_length=1000,null=True, blank=True, verbose_name='detalle')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    fecha_consulta = models.DateTimeField(null=True,blank=True, verbose_name='fecha_consulta')
    tipo=models.CharField(max_length=2,null=True, blank=True, choices=TIPO_CHOICES, verbose_name='tipo')

    def __str__(self):
        return str(self.historiaclinica)

    class Meta:
        verbose_name = 'EvolucionHistoria'
        verbose_name_plural = 'EvolucionesHistorias'

def ruta_cirugia(instance, filename):
    return os.path.join(
        'cirugia',
        str(instance.cirugia.id),
        filename
    )


class DocumentoCirugia(models.Model):
    cirugia = models.ForeignKey(Cirugia, on_delete=models.CASCADE, verbose_name='cirugia')
    archivo = models.ImageField(upload_to=ruta_cirugia, verbose_name='archivo')
    cargado = models.ImageField(upload_to='cirugia/', verbose_name='cargado')
    tipo = models.CharField(max_length=50, default='laboratorio', verbose_name='tipo')
    fecha_subida = models.DateTimeField(auto_now_add=True, verbose_name='fecha_subida')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')

    def __str__(self):
        return str(self.cirugia)

    class Meta:
        verbose_name = 'DocumentoCirugia'
        verbose_name_plural = 'DocumentosCirugias'

class RegistroPresupuestoPDF(models.Model):
    presupuesto = models.ForeignKey(
        Presupuesto,
        on_delete=models.CASCADE,
        related_name='pdfs'
    )
    archivo = models.CharField(max_length=255)
    version = models.PositiveIntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Presupuesto {self.presupuesto.id} v{self.version}'
    

class HistoriaTransOperatoria(models.Model):
    cirugia = models.ForeignKey(Cirugia, on_delete=models.CASCADE, verbose_name='cirugia')
    fecha_inicio = models.DateTimeField(null=True, blank=True,verbose_name='fecha_inicio')
    fecha_fin = models.DateTimeField(null=True, blank=True,verbose_name='fecha_fin')
    inicio_cronometro_1 = models.DateTimeField(null=True, blank=True, verbose_name='inicio_cronometro_1')
    inicio_cronometro_2 = models.DateTimeField(null=True, blank=True,verbose_name='inicio_cronometro_2')
    inicio_cronometro_3 = models.DateTimeField(null=True, blank=True,verbose_name='inicio_cronometro_3')
    nombre_cronometro_1 = models.CharField(null=True, blank=True, max_length=500, verbose_name='nombre_cronometro_1')
    nombre_cronometro_2 = models.CharField(null=True, blank=True,  max_length=500,verbose_name='nombre_cronometro_2')
    nombre_cronometro_3 = models.CharField(null=True, blank=True,  max_length=500,verbose_name='nombre_cronometro_3')
    tiempo_cronometro_1 = models.DurationField(null=True,blank=True)
    tiempo_cronometro_2 = models.DurationField(null=True,blank=True)
    tiempo_cronometro_3 = models.DurationField(null=True,blank=True)
    nota_enfermeria = models.TextField(null=True, blank=True, verbose_name='nota_enfermeria')
    nota_cirugia = models.TextField(null=True, blank=True, verbose_name='nota_cirugia')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='fecha_creacion')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    finalizada = models.BooleanField(default=False, verbose_name='finalizada')
    actualizar = models.BooleanField(default=False, verbose_name='actualizar')

    def __str__(self):
        return str(self.cirugia)

    class Meta:
        verbose_name = 'HistoriaTransOperatoria'
        verbose_name_plural = 'HistoriaTransOperatorias'


class TransaccionFacturaMultiple(models.Model):
    transaccion = models.ForeignKey(
        Transaccion,
        on_delete=models.CASCADE,
        related_name="facturas"
    )
    abono = models.ForeignKey(
        AbonoCuentaPagar,
        on_delete=models.CASCADE,
        related_name="abono"
    )
    factura = models.ForeignKey(
        FacturaProveedor,
        on_delete=models.PROTECT
    )
    monto_aplicado = models.DecimalField(
        default=0,
        max_digits=15,
        decimal_places=2,
        verbose_name="Monto aplicado Bs"
    )
    monto_aplicado_dolar = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Monto aplicado USD"
    )

    class Meta:
        verbose_name = "Factura aplicada a transacción"
        verbose_name_plural = "Facturas aplicadas a transacción"


class ReutilizacionInventario(models.Model):
    cirugia = models.ForeignKey(Cirugia, on_delete=models.CASCADE,null=True, blank=True, verbose_name='cirugia')
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE, verbose_name='inventario')
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=0,verbose_name='cantidad')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='fecha_creacion')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')
    noreutilizable = models.BooleanField(default=False, verbose_name='noreuntilizable')
    deposito = models.ForeignKey(Deposito, on_delete=models.CASCADE, verbose_name='deposito')

    def __str__(self):
        return str(self.cirugia)

    class Meta:
        verbose_name = 'ReutilizacionInventario'
        verbose_name_plural = 'ReutilizacionesInventarios'


class DistribucionPagoMedico(models.Model):
    factura = models.ForeignKey(FacturaProveedor, on_delete=models.CASCADE,null=True, blank=True, verbose_name='factura')
    moneda = models.ForeignKey(Moneda, on_delete=models.CASCADE, null=True, blank=True, verbose_name='moneda')
    monto = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name='monto')
    tx = models.DecimalField(max_digits=15, decimal_places=4, default=0,verbose_name='tx')
    monto_bs = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name='monto bs')
    tipo = models.CharField(default='PGO',  max_length=3,verbose_name='tipo')
    fecha_act = models.DateTimeField(auto_now=True,null=True, verbose_name='Fecha Actualizacion')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='fecha_creacion')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario')

    def __str__(self):
        return str(self.factura.numerodocumento)

    class Meta:
        verbose_name = 'DistribucionPagoMedico'
        verbose_name_plural = 'DistribucionPagoMedicos'



  