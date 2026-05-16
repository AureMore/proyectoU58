from django import forms 
from datetime import datetime,date,timedelta
from django.forms import formset_factory
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Paciente, ImagenCirugia, Cirugia, KitInventario, Medico, Proveedor, Inventario, DepositoUso, Especialidad, BancoLocal, Cuenta
from django.forms import DateField
from django.db import models
from decimal import Decimal
from django.utils import timezone
from django.forms.widgets import HiddenInput, DateInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from .widgets import DateMaskInput

class PacienteForm(forms.ModelForm):
    cedula = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'oninput': 'handleCedulaInput(this);', 'class':'form-control mb-1'}))
    fecha_nac = forms.DateField(initial=datetime.now(), widget=DateMaskInput())  # <--- Utiliza el widget personalizado
    telefono1 = forms.CharField(widget=forms.TextInput(), label = 'Telefono Principal' )
    direccion = forms.CharField(widget=forms.Textarea(
        attrs={
            'rows':2,
            'label':'Direccion',
            'id':'id_direccion'}))

    class Meta:
        model = Paciente
        fields = ("id", "cedula","nombre","apellido","sexo" ,"direccion","fecha_nac", "telefono1","telefono2", "correo","lugar_nac","civil","nacionalidad" ,"ocupacion", "referencia", "religion")
        
        helper = FormHelper()
        helper.layout = Layout(
                Field('cedula'),
                Field('nombre'),
                Field('apellido'),
                Field('direccion'),
                Field('sexo'),
                Field('fecha_nac'),
                Field('lugar_nac'),
                Field('telefono1'),
                Field('telefono2'),
                Field('correo'),
                Field('civil'),
                Field('nacionalidad'),
                Field('ocupacion'),
                Field('referencia'),
                Field('usuario'),
                Submit('submit', 'Submit')     
                   
            )
        
        
class ImagenCirugiaForm(forms.ModelForm):
    descripcion = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-select-sm '}))
    imagen = forms.ImageField(widget=forms.FileInput(attrs={'class':'form-control form-control-sm bg-secondary'}))
    class Meta:
        model = ImagenCirugia
        fields = [ 'imagen', 'descripcion']
        
class CirugiaForm(forms.ModelForm):
    nombre_procedimiento = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control form-select-sm '}))
    class Meta:
        model = Cirugia
        fields = [ 'id', 'paciente', 'nombre_procedimiento', 'hora_procedimiento','horas_qx','notas','quirofano']
        


class KitInventarioForm(forms.ModelForm):
    class Meta:
        model = KitInventario
        fields = ('nombre',)


class MedicoForm(forms.ModelForm):
    prefijo_cedula = forms.ChoiceField(
        choices=[
            ('V', 'V'),
            ('E', 'E'),
            ('P', 'P')
        ],
        widget=forms.Select(attrs={'class': 'form-select form-select-sm w-auto', 'onchange':'limpiarCedula()'})
    )

    cedula = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'maxlength': '10',
            'oninput': 'validarCedula(this)'
        })
    )
    nueva_especialidad = forms.CharField(required=False, max_length=100)
    """ cedula = forms.CharField(max_length=11, widget=forms.TextInput(attrs={'oninput': 'handleCedulaInput(this);'})) """
    telefono1 = forms.CharField(widget=forms.TextInput(), label = 'Telefono Principal' )
    #rif = forms.IntegerField(label='Digito de Rif', widget=forms.NumberInput)
    rif = forms.ChoiceField(
        label='Digito de Rif',
        choices=[(str(i), str(i)) for i in range(10)],
        widget=forms.Select(attrs={'class': 'form-control form-control-sm w-25'})
    )

    #telefono2 = forms.CharField(widget=forms.TextInput(), label = 'Telefono Secundario' )
    direccion = forms.CharField(widget=forms.Textarea(
        attrs={
            'rows':2,
            'label':'Direccion',
            'id':'id_direccion'}))
    
    fecha_desde = forms.DateField(
        label='Fecha Ingreso',
        input_formats=['%d/%m/%Y'],   # 👈 formato que acepta al guardar
        widget=forms.DateInput(
            format='%d/%m/%Y',
            attrs={
                'type': 'text',                # 👈 text, no 'date', para usar JS datepicker
                'class': 'form-control form-control-sm datepicker w-25',  # 👈 clase para activarlo con JS
                'placeholder': 'dd/mm/yyyy'
            }
        ),
        initial=date.today
    )


    class Meta:
        model = Medico
        fields = ["id","cedula","nombre","rif" ,"direccion","especialidad","nueva_especialidad","nromsds", "nrocolegio","telefono1", "telefono2","correo","porcentajepago","por_descuento", "participaalta","tipopersonal","pagofrecuente", "fecha_desde","porcentaje_retencion_iva", "grupo"]

    def clean(self):
        cleaned_data = super().clean()

        prefijo = cleaned_data.get("prefijo_cedula")
        cedula = cleaned_data.get("cedula")

        if prefijo and cedula:
            cleaned_data["cedula"] = f"{prefijo}{cedula}"

        nueva_especialidad = cleaned_data.get('nueva_especialidad')

        if nueva_especialidad:
            especialidad, created = Especialidad.objects.get_or_create(nombre=nueva_especialidad)
            cleaned_data['especialidad'] = especialidad

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['grupo'].disabled = True
        self.fields['nromsds'].required = False
        self.fields['nrocolegio'].required = False

        if self.instance and self.instance.cedula:
            cedula_completa = self.instance.cedula

            prefijo = cedula_completa[0]
            numero = cedula_completa[1:]

            self.fields['prefijo_cedula'].initial = prefijo
            self.fields['cedula'].initial = numero

            # IMPORTANTE: evitar que Django coloque el valor completo
            self.initial['cedula'] = numero

class GrupoMedicoForm(forms.ModelForm):
    prefijo_cedula = forms.ChoiceField(
        choices=[
            ('J', 'J'),
            ('G', 'G'),
            ('P', 'P')
        ],
        widget=forms.Select(attrs={'class': 'form-select form-select-sm w-auto', 'onchange':'limpiarCedula()'})
    )

    cedula = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'maxlength': '10',
            'oninput': 'validarCedula(this)'
        })
    )
    nueva_especialidad = forms.CharField(required=False, max_length=100)
    # cedula = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'oninput': 'handleRifInput(this);' }))
    telefono1 = forms.CharField(widget=forms.TextInput(), label = 'Telefono Principal' )
    rif = forms.IntegerField(label='Digito de Rif', widget=forms.NumberInput)
    #telefono2 = forms.CharField(widget=forms.TextInput(), label = 'Telefono Secundario' )
    direccion = forms.CharField(widget=forms.Textarea(
        attrs={
            'rows':2,
            'label':'Direccion',
            'id':'id_direccion'}))
    
    fecha_desde = forms.DateField(
        label='Fecha Ingreso',
        input_formats=['%d/%m/%Y'],   # 👈 formato que acepta al guardar
        widget=forms.DateInput(
            format='%d/%m/%Y',
            attrs={
                'type': 'text',                # 👈 text, no 'date', para usar JS datepicker
                'class': 'form-control form-control-sm datepicker w-25',  # 👈 clase para activarlo con JS
                'placeholder': 'dd/mm/yyyy'
            }
        ),
        initial=date.today
    )


    class Meta:
        model = Medico
        fields = ["id","cedula","nombre","rif" ,"direccion","especialidad","nueva_especialidad","nromsds", "nrocolegio","telefono1", "telefono2","correo","porcentajepago","por_descuento", "participaalta","tipopersonal","pagofrecuente", "fecha_desde","porcentaje_retencion_iva", "grupo"]

    def clean(self):
        cleaned_data = super().clean()

        prefijo = cleaned_data.get("prefijo_cedula")
        cedula = cleaned_data.get("cedula")

        if prefijo and cedula:
            cleaned_data["cedula"] = f"{prefijo}{cedula}"

        nueva_especialidad = cleaned_data.get('nueva_especialidad')

        if nueva_especialidad:
            especialidad, created = Especialidad.objects.get_or_create(nombre=nueva_especialidad)
            cleaned_data['especialidad'] = especialidad

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grupo'].disabled = True
        self.fields['rif'].required = False
        self.fields['nromsds'].required = False
        self.fields['nrocolegio'].required = False

        if self.instance and self.instance.cedula:
            cedula_completa = self.instance.cedula

            prefijo = cedula_completa[0]
            numero = cedula_completa[1:]

            self.fields['prefijo_cedula'].initial = prefijo
            self.fields['cedula'].initial = numero

            # IMPORTANTE: evitar que Django coloque el valor completo
            self.initial['cedula'] = numero


class SegurosForm(forms.ModelForm):
    prefijo_cedula = forms.ChoiceField(
        choices=[
            ('J', 'J'),
            ('G', 'G'),
            ('P', 'P')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm w-auto',
            'onchange':'limpiarCedula()'
            })
    )

    cedula = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'maxlength': '10',
            'oninput': 'validarCedula(this)',
            
        })
    )
    nueva_especialidad = forms.CharField(required=False, max_length=100)
    #cedula = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'oninput': 'handleRifInput(this);' }))
    telefono1 = forms.CharField(widget=forms.TextInput(), label = 'Telefono Principal' )
    rif = forms.IntegerField(label='Digito de Rif', widget=forms.NumberInput)
    #telefono2 = forms.CharField(widget=forms.TextInput(), label = 'Telefono Secundario' )
    direccion = forms.CharField(widget=forms.Textarea(
        attrs={
            'rows':2,
            'label':'Direccion',
            'id':'id_direccion'}))
    
    fecha_desde = forms.DateField(
        label='Fecha Ingreso',
        input_formats=['%d/%m/%Y'],   # 👈 formato que acepta al guardar
        widget=forms.DateInput(
            format='%d/%m/%Y',
            attrs={
                'type': 'text',                # 👈 text, no 'date', para usar JS datepicker
                'class': 'form-control form-control-sm datepicker w-25',  # 👈 clase para activarlo con JS
                'placeholder': 'dd/mm/yyyy'
            }
        ),
        initial=date.today
    )


    class Meta:
        model = Medico
        fields = ["id","cedula","nombre","rif" ,"direccion","especialidad","nueva_especialidad","nromsds", "nrocolegio","telefono1", "telefono2","correo","porcentajepago","por_descuento", "participaalta","tipopersonal","pagofrecuente", "fecha_desde","porcentaje_retencion_iva", "grupo"]

    def clean(self):
        cleaned_data = super().clean()

        prefijo = cleaned_data.get("prefijo_cedula")
        cedula = cleaned_data.get("cedula")

        if prefijo and cedula:
            cleaned_data["cedula"] = f"{prefijo}{cedula}"

        nueva_especialidad = cleaned_data.get('nueva_especialidad')

        if nueva_especialidad:
            # Verifica si la especialidad ya existe
            especialidad, created = Especialidad.objects.get_or_create(nombre=nueva_especialidad)
            cleaned_data['especialidad'] = especialidad

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grupo'].disabled = True
        self.fields['rif'].required = False
        self.fields['nromsds'].required = False
        self.fields['nrocolegio'].required = False

        if self.instance and self.instance.cedula:
            cedula_completa = self.instance.cedula

            prefijo = cedula_completa[0]
            numero = cedula_completa[1:]

            self.fields['prefijo_cedula'].initial = prefijo
            self.fields['cedula'].initial = numero

            # IMPORTANTE: evitar que Django coloque el valor completo
            self.initial['cedula'] = numero
    
    
        
class ProveedorForm(forms.ModelForm):
    prefijo_rif = forms.ChoiceField(
        choices=[
            ('J', 'J'),
            ('G', 'G'),
            ('P', 'P'),
            ('V', 'V'),
            ('E', 'E')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm w-auto',
            'onchange':'limpiarCedula()'
            })
    )

    rif = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'maxlength': '15',
            'oninput': 'validarCedula(this)',
            
        })
    )
    fecha_desde = forms.DateField(initial=datetime.now(), widget=DateMaskInput(),label = 'Fecha Ingreso')  # <--- Utiliza el widget personalizado
    telefono1 = forms.CharField(widget=forms.TextInput(), label = 'Telefono Principal' )
    correocontacto  = forms.EmailField(required=False,  label = 'Correo Contacto' )
    correo  = forms.EmailField(required=False)
    #telefono2 = forms.CharField(widget=forms.TextInput(),required=False, label = 'Telefono Secundario' )

    class Meta:
        model = Proveedor
        fields = ["id","rif","nombre","correo", "tipoproveedor",  "telefono1","telefono2","contacto","correocontacto","telefonocontacto","porcentaje_retencion" ]
        
    def clean(self):
        cleaned_data = super().clean()

        prefijo = cleaned_data.get("prefijo_rif")
        rif = cleaned_data.get("rif")

        if rif:
            rif = rif[1:] if rif[0].isalpha() else rif

        if prefijo and rif:
            cleaned_data["rif"] = f"{prefijo}{rif}"

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.rif:

            rif_completo = self.instance.rif.strip()

            if len(rif_completo) > 1:
                self.fields['prefijo_rif'].initial = rif_completo[0]
                self.fields['rif'].initial = rif_completo[1:]
                self.initial['rif'] = rif_completo[1:]
        
        
class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ('codigo', 'kit', 'proveedor', 'categoria', 'laboratorio', 'presentacion', 'presentacion_salida', 'nombre', 'lote', 'cantidad_unitaria', 'cantidad_max', 'cantidad_kit', 'cantidad_min', 'cantidad_cri', 'fecha_elaboracion', 'fecha_vencimiento', 'costo', 'venta', 'venta_kit')

class DepositoUsoForm(forms.ModelForm):
    class Meta:
        model = DepositoUso
        fields = ('inventario', 'deposito', 'cantidad_deposito', 'costo', 'venta', 'cantidad_consumida')


class BancoLocalForm(forms.ModelForm):
    

    class Meta:
        model = BancoLocal
        fields = ['nombrecuenta', 'banco', 'uso', 'numerocuenta', 'moneda']
        widgets = {
            'nombrecuenta': forms.TextInput(attrs={'class': 'form-control','style': 'width: 600px; overflow:auto;'}),
            'numerocuenta': forms.TextInput(attrs={'class': 'form-control '}),
            'banco': forms.Select(attrs={'class': 'form-control'}),
            'uso': forms.TextInput(attrs={'class': 'form-control ', 'style': 'width: 600px; overflow:auto;'}),
            'moneda': forms.Select(attrs={'class': 'form-control'}),
            
        }

    def save(self, commit=True, user=None):
        # Llamar al método save de la clase padre
        banco_local = super(BancoLocalForm, self).save(commit=False)
        # Asignar el usuario logueado
        if user is not None:
            banco_local.usuario = user
        if commit:
            banco_local.save()
        return banco_local

          
        
