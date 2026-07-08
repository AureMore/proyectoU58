from django.contrib import admin

# Register your models here.
from simple_history.admin import SimpleHistoryAdmin

from .models import Convenio, DetalleBaremo,SubDetalleBaremo,GrupoBaremo, Baremo, TipoProcedimiento, Unidad, Medico, Plantilla, ComposicionDetalle, Cirugia, Presupuesto,Habitacion,Quirofano, DetalleCirugia, Inventario, Proveedor, TipoProveedor, Deposito, CategoriaInventario, LaboratorioMedicina, PresentacionMedicina,CambioBcv, LugarConsumo, Tratamiento, EstatusCirugia, KitInventario, TipoPersonal, TipoDocumento,FacturaProveedor, FormaPago,TablaImpuesto, BancoLocal, Banco,Cuenta,Transaccion, Retencion,DepositoUso, MontoIncremento, TipoDescarga, NotaEntregaCompra, ConsumoCirugia, LogInventario, PreIngreso, Paciente, CuentaxCobrar, LogEliminacion, NumeracionFactura, AtencionInmediata, DebitoCredito, NotaCreditoCtaCobrar, EvaluacionPreanestesia, UnidadCompra, UnidadProducto, CentroCostoFacturaCompra, BaremoPagoTercero, PagoMedico, DetalleCuentaCobrar, HistoricalDetalleCuentaCobrar, DetalleHospitalCorteCuenta
from django.utils.html import format_html
admin.site.site_header = 'Administracion del las Tablas'
admin.site.index_title = 'Panel de Control'
admin.site.site_title = 'Tablas'

@admin.register(HistoricalDetalleCuentaCobrar)
class HistoricalDetalleCuentaCobrarAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'history_date',
        'history_type',
        'history_user',
    )

    readonly_fields = [f.name for f in HistoricalDetalleCuentaCobrar._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

class ConvenioAdmin(admin.ModelAdmin):
    list_display = ('id','rif','nombre','sucursal', 'telefono1',  'telefono2', 'correo', 'nota')
    list_filter = ('nombre',)
    
admin.site.register(Convenio, ConvenioAdmin )


class GrupoBaremoAdmin(admin.ModelAdmin):
    list_display = ('id','nombre','posicion')
    list_filter = ('nombre',)
    
admin.site.register(GrupoBaremo, GrupoBaremoAdmin )

class DetalleBaremoAdmin(admin.ModelAdmin):
    list_display = ('id','nombre','posicion')
    list_filter = ('nombre',)
    
admin.site.register(DetalleBaremo, DetalleBaremoAdmin )

class TipoProcedimientoAdmin(admin.ModelAdmin):
    list_display = ('id','nombre')
    list_filter = ('nombre',)
    
admin.site.register(TipoProcedimiento, TipoProcedimientoAdmin )

class UnidadAdmin(admin.ModelAdmin):
    list_display = ('id','nombre')
    list_filter = ('nombre',)


    
admin.site.register(Unidad, UnidadAdmin ) 

class PlantillaAdmin(admin.ModelAdmin):
    list_display = ('id','nombre')
    list_filter = ('nombre',)
    
admin.site.register(Plantilla, PlantillaAdmin ) 



class SubDetalleBaremoAdmin(admin.ModelAdmin):
    list_display = ('id','convenio','grupo' , 'detalle' ,'nombre','cantidad','monto_tope')
    list_filter = ('detalle',)
    
admin.site.register(SubDetalleBaremo, SubDetalleBaremoAdmin )

class BaremoAdmin(admin.ModelAdmin):
    list_display = ('id','convenio','grupo','detalle','topedia', 'get_detalle_posicion', 'plantilla','cantidad' ,'costo',  'venta', 'unidad', 'exento', 'ntqx' )
    list_filter = ('convenio','plantilla','grupo')
    
    def get_detalle_posicion(self, obj):
        return obj.detalle.posicion

    get_detalle_posicion.short_description = 'Posición'
    get_detalle_posicion.admin_order_field = 'detalle__posicion'
    
admin.site.register(Baremo, BaremoAdmin )

class MedicoAdmin(admin.ModelAdmin):
    list_display = ('id','cedula','nombre','user','especialidad', 'telefono1' ,'telefono2','correo',  'porcentajepago', 'observacion')
    search_fields = ['nombre']
    
admin.site.register(Medico, MedicoAdmin ) 

class TipoPersonalAdmin(admin.ModelAdmin):
    list_display = ('id','nombre')
    
admin.site.register(TipoPersonal, TipoPersonalAdmin ) 


class ComposicionDetalleAdmin(admin.ModelAdmin):
    list_display = ('id','convenio','grupo' , 'detalle' ,'cantidad','venta','nota' )
    list_filter = ('convenio',)
    
admin.site.register(ComposicionDetalle, ComposicionDetalleAdmin )

class CirugiaAdmin(admin.ModelAdmin):
    list_display = ('id','paciente','tipo_procedimiento','medico_ppal', 'fecha_procedimiento' ,'nombre_procedimiento','convenio',  'presupuesto', 'usuario')
    list_filter = ('paciente',)
    search_fields = ['id']
    
admin.site.register(Cirugia, CirugiaAdmin) 


class DetalleCirugiaAdmin(admin.ModelAdmin):
    list_display = ('id','cirugia','convenio','grupo', 'plantilla' ,'detalle' ,'cantidad','precio', 'usuario')
    list_filter = ('cirugia',)
    
admin.site.register(DetalleCirugia, DetalleCirugiaAdmin )



class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ('id','paciente','tipo_procedimiento','medico_ppal', 'fecha_procedimiento' ,'nombre_procedimiento','convenio',  'estatus', 'usuario')
    list_filter = ('paciente',)
    
admin.site.register(Presupuesto, PresupuestoAdmin ) 

class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('id','habitacion', 'nota')
    
admin.site.register(Habitacion, HabitacionAdmin ) 

class QuirofanoAdmin(admin.ModelAdmin):
    list_display = ('id','NQx', 'nota')
    
admin.site.register(Quirofano, QuirofanoAdmin )

""" class InventarioAdmin(admin.ModelAdmin):
    list_display = ('id','codigo', 'nombre', 'categoria', 'laboratorio','presentacion',  'lote', 'cantidad_total_producto', 'costo','venta','cantidad_unitaria','fecha_vencimiento', 'proveedor')
    search_fields = ['nombre']

admin.site.register(Inventario, InventarioAdmin ) """

@admin.register(Inventario)
class InventarioAdmin(SimpleHistoryAdmin):
    list_display = ('id','codigo', 'nombre')
    search_fields = ['id']

class DepositoUsoAdmin(admin.ModelAdmin):
    list_display = ('id','inventario', 'deposito', 'cantidad_deposito', 'cantidad_consumida')
    search_fields = ['inventario']

admin.site.register(DepositoUso, DepositoUsoAdmin )  

class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id','rif', 'nombre')
    
admin.site.register(Proveedor, ProveedorAdmin )

class TipoProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    
admin.site.register(TipoProveedor, TipoProveedorAdmin )

class DepositoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precarga')
    
admin.site.register(Deposito, DepositoAdmin )

class CategoriaInventarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    
admin.site.register(CategoriaInventario, CategoriaInventarioAdmin )

class LaboratorioMedicinaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    
admin.site.register(LaboratorioMedicina, LaboratorioMedicinaAdmin )

class PresentacionMedicinaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'cantidad', 'activo')
    
admin.site.register(PresentacionMedicina, PresentacionMedicinaAdmin )


class CambioBcvAdmin(admin.ModelAdmin):
    list_display = ('id', 'cambio', 'fecha_cambio')
    
admin.site.register(CambioBcv, CambioBcvAdmin )


class LugarConsumoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'posicion')
    
admin.site.register(LugarConsumo, LugarConsumoAdmin )

class UnidadCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'cantidad_bulto', 'cantidad_unidad_bulto' , 'unidad','activo')
    
admin.site.register(UnidadCompra, UnidadCompraAdmin )


class UnidadProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'acronimo')
    
admin.site.register(UnidadProducto, UnidadProductoAdmin )

class TratamientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cirugia','inventario','baremo','cantidad_uso','tratamiento','medico_orden',  'medico_aplicante','fecha_act')
    
admin.site.register(Tratamiento, TratamientoAdmin )



class EstatusCirugiaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre','descripcion')
    
admin.site.register(EstatusCirugia, EstatusCirugiaAdmin )


class KitInventarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

admin.site.register(KitInventario, KitInventarioAdmin)

class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

admin.site.register(TipoDocumento, TipoDocumentoAdmin)

class FacturaProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha_entrega', 'numerodocumento', 'numerocontrol','tipodocumento')

admin.site.register(FacturaProveedor, FacturaProveedorAdmin)


class FormaPagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'moneda')

admin.site.register(FormaPago, FormaPagoAdmin)


class TablaImpuestoAdmin(admin.ModelAdmin):
    list_display = ('id', 'sustraendo')

admin.site.register(TablaImpuesto, TablaImpuestoAdmin)

class BancoLocalAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombrecuenta', 'banco', 'uso', 'numerocuenta','saldo', 'moneda')

admin.site.register(BancoLocal, BancoLocalAdmin)

class BancoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'rif', 'codigo', 'moneda')

admin.site.register(Banco, BancoAdmin)


class CuentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero')

admin.site.register(Cuenta, CuentaAdmin)

class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'pagomedico', 'monto','monto_dolar', 'fechatransaccion', 'descripcion','usuario')

admin.site.register(Transaccion, TransaccionAdmin)


class RetencionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'natural', 'topenatural', 'juridica','topejuridica', 'sustraendonatural', 'sustraendojuridica')
    search_fields = ['nombre']

admin.site.register(Retencion, RetencionAdmin)

@admin.register(PagoMedico)
class PagoMedicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_medico', 'nombre', 'numerocuenta')
    search_fields = ('medico__nombre',)
    list_filter = ('medico',)

    # Oculta el campo usuario del formulario
    exclude = ('usuario',)

    def nombre_medico(self, obj):
        return obj.medico.nombre if obj.medico else ""

    nombre_medico.short_description = 'Médico'

    # Guarda automáticamente el usuario que hizo la modificación
    def save_model(self, request, obj, form, change):
        obj.usuario = request.user
        super().save_model(request, obj, form, change)

class MontoIncrementoAdmin(admin.ModelAdmin):
    list_display = ('id', 'monto', 'porcentaje','fecha_act')

admin.site.register(MontoIncremento, MontoIncrementoAdmin)


class TipoDescargaAdmin(admin.ModelAdmin):
    list_display = ('id','nombre')
    list_filter = ('nombre',)
    
admin.site.register(TipoDescarga, TipoDescargaAdmin )

class NotaEntregaCompraAdmin(admin.ModelAdmin):
    list_display = ('id','numerodocumento')
    
    
admin.site.register(NotaEntregaCompra, NotaEntregaCompraAdmin )


class ConsumoCirugiaAdmin(admin.ModelAdmin):
    list_display = ('id','cirugia_id','inventario_id' ,'inventario','deposito', 'usuario')
    search_fields = ['cirugia_id__id']
    
admin.site.register(ConsumoCirugia, ConsumoCirugiaAdmin )

class LogInventarioAdmin(admin.ModelAdmin):
    list_display = ('id','fecha_act','cirugia_id','cirugia' ,'inventario', 'usuario', 'nota')
    search_fields = ['cirugia_id__id']
    
admin.site.register(LogInventario, LogInventarioAdmin )

class PreIngresoAdmin(admin.ModelAdmin):
    list_display = ('id','codigo', 'cirugia_id', 'cirugia')
    
admin.site.register(PreIngreso, PreIngresoAdmin ) 

class PacienteAdmin(admin.ModelAdmin):
    list_display = ('id','cedula', 'nombre', 'apellido')
    
admin.site.register(Paciente, PacienteAdmin ) 


@admin.register(CuentaxCobrar)
class CuentaxCobrarAdmin(SimpleHistoryAdmin):
    pass

@admin.register(DetalleCuentaCobrar)
class DetalleCuentaCobrarAdmin(SimpleHistoryAdmin):
    pass

class LogEliminacionAdmin(admin.ModelAdmin):
    list_display = ('id','descripcion', 'usuario', 'fecha_act')
    
admin.site.register(LogEliminacion, LogEliminacionAdmin ) 

class NumeracionFacturaAdmin(admin.ModelAdmin):
    list_display = ('id','numero_factura', 'numero_control')
    
admin.site.register(NumeracionFactura, NumeracionFacturaAdmin ) 

class AtencionInmediataAdmin(admin.ModelAdmin):
    list_display = ('id','motivo_atencion', 'fecha_act')
    
admin.site.register(AtencionInmediata, AtencionInmediataAdmin ) 

class DebitoCreditoAdmin(admin.ModelAdmin):
    list_display = ('id','cuenta_origen', 'cuenta_destino', 'monto_dolar')
    
admin.site.register(DebitoCredito, DebitoCreditoAdmin ) 

@admin.register(NotaCreditoCtaCobrar)
class NotaCreditoCtaCobrarAdmin(SimpleHistoryAdmin):
    pass

class EvaluacionPreanestesiaAdmin(admin.ModelAdmin):
    list_display = ('id','pregunta')
    
admin.site.register(EvaluacionPreanestesia, EvaluacionPreanestesiaAdmin )

class EvaluacionPreanestesiaAdmin(admin.ModelAdmin):
    list_display = ('id','pregunta')
    
class CentroCostoFacturaCompraAdmin(admin.ModelAdmin):
    list_display = ('id','nombre','descripcion','cuenta_asociada')
    
admin.site.register(CentroCostoFacturaCompra, CentroCostoFacturaCompraAdmin )


from .models import ModuloSistema, OpcionEspecificaModulo, SolicitudSoporte

@admin.register(ModuloSistema)
class ModuloSistemaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    search_fields = ('nombre',)

@admin.register(OpcionEspecificaModulo)
class OpcionEspecificaModuloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'modulo', 'activo')
    list_filter = ('modulo', 'activo')
    search_fields = ('nombre', 'modulo__nombre')

@admin.register(SolicitudSoporte)
class SolicitudSoporteAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'modulo', 'opcion_especifica', 'tipo_solicitud', 'fecha_creacion')
    list_filter = ('tipo_solicitud', 'modulo', 'fecha_creacion')


@admin.register(DetalleHospitalCorteCuenta)
class DetalleHospitalCorteCuentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'activo',  'detalle', 'fecha_act', 'usuario')

