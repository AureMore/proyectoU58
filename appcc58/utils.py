from .models import CambioBcv, DetalleFacturaProveedor, FacturaProveedor, Retencion
from django.db.models import Subquery, OuterRef, Sum, F
from dateutil.relativedelta import relativedelta
from datetime import datetime
import pyautogui as pg
import webbrowser as web
#import pywhatkit
import time




def CambioDiaBcv(fecha_cambio):
    fecha_formateada = fecha_cambio.strftime("%Y-%m-%d")
    tasa_tx = CambioBcv.objects.filter(fecha_cambio=fecha_formateada).first()
    tasa_del_dia = 0
    if tasa_tx:
        tasa_del_dia = tasa_tx.cambio
    return tasa_del_dia

def calcular_edad(fecha_nacimiento):
    edad = relativedelta(datetime.now(), fecha_nacimiento)
    return edad.years

def calculo_neto_pagar_medico(factura_id):
    detallefactura = DetalleFacturaProveedor.objects.filter(factura_id=factura_id)
    total_bruto = detallefactura.aggregate(total_bruto=Sum(F('precio_unitario')*F('cantidad')))
    total_gasto = detallefactura.aggregate(total_gasto=Sum('gastos'))
    
    monto_neto_pagar = total_bruto['total_bruto'] - total_gasto['total_gasto']
    return monto_neto_pagar

def calculo_neto_pagar_medico_bs(factura_id):
    detallefactura = DetalleFacturaProveedor.objects.filter(factura_id=factura_id)
    total_bruto = detallefactura.aggregate(total_bruto=Sum(F('precio_bs')*F('cantidad')))
    total_gasto = detallefactura.aggregate(total_gasto=Sum('gastos_bs'))
    
    monto_neto_pagar_bs = total_bruto['total_bruto'] - total_gasto['total_gasto']
    return monto_neto_pagar_bs


def calculo_neto_pagar_factura(factura_id):
    detallefactura = DetalleFacturaProveedor.objects.filter(factura_id=factura_id, precio_unitario__gt = 0)
    total_bruto = detallefactura.aggregate(total_bruto=Sum(F('precio_unitario')*F('cantidad')))
    total_gasto = detallefactura.aggregate(total_gasto=Sum('gastos'))
    
    monto_neto_pagar = total_bruto['total_bruto'] - total_gasto['total_gasto']
    return monto_neto_pagar

def calculo_neto_pagar_factura_bs(factura_id):
    detallefactura = DetalleFacturaProveedor.objects.filter(factura_id=factura_id, precio_bs__gt = 0)
    total_bruto = detallefactura.aggregate(total_bruto=Sum(F('precio_bs')*F('cantidad')))
    total_gasto = detallefactura.aggregate(total_gasto=Sum('gastos_bs'))
    
    monto_neto_pagar_bs = total_bruto['total_bruto'] - total_gasto['total_gasto']
    return monto_neto_pagar_bs


def calculo_retencion(baseimponible, persona, concepto, tipodocumento):
    monto_retener = 0
    retencion = Retencion.objects.filter(id=concepto).first()
    if persona == 'N':
        if baseimponible > retencion.topenatural:
            if tipodocumento == 5:
                print("CALCULO BASE TIPO 5")
                print("MONTO A RETENER")
                monto_retener = (baseimponible * (retencion.natural/100))
                print(monto_retener)
            else:
                print("CALCULO BASE NO 5")
                monto_retener = (baseimponible * (retencion.natural/100))- retencion.sustraendonatural
            
    else:
        if baseimponible > retencion.topejuridica:
            if tipodocumento == 5:
                monto_retener = (baseimponible * (retencion.juridica/100))
            else:
                monto_retener = (baseimponible * (retencion.juridica/100))- retencion.sustraendojuridica
    
    return monto_retener


def montoaretener(baseimponible, tipopersona, concepto):
    monto_retener = 0
    sustraendo = 0
    tope = 0
    retencion = Retencion.objects.filter(id=concepto).first()
    if retencion:
        if tipopersona == 'N':
            porcentaje = retencion.natural
            sustraendo = retencion.sustraendonatural
            tope = retencion.topenatural
        else:
            porcentaje = retencion.juridica
            sustraendo = retencion.sustraendojuridica
            tope = retencion.topejuridica
            
    if baseimponible > tope:
        monto_retener = (baseimponible * (porcentaje/100))
    
    # Crear un diccionario con los valores
    resultado = {
        'monto_retener': monto_retener,
        'sustraendo': sustraendo,
        'porcentaje':porcentaje
    }
    
    return resultado



def envioWhatsApp(mensaje, telefono):
    telefono = "+58"+telefono[1:]
    """ 
    web.open("https://web.whatsapp.com/send?phone="+telefono+"&text="+str(mensaje))
    time.sleep(6)
    pg.click(987,701)
    time.sleep(2)
    pg.press('enter')
    time.sleep(2)
    pg.hotkey('ctrl','w')
    """
    time.sleep(2)
    return


def envio_email(archivo):
    import smtplib
    import os
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication
    from email.mime.base import MIMEBase
    from email import encoders
    
    
    user_mail = "aemoreno1970@gmail.com"
    password = "blgmrncqnoxlgznz"
    usuario="aemoreno1970@gmail.com"
    asunto = "Presupuesto Solicitado"
    destinatarios = ['aemoreno1970@gmail.com']
    mensaje = "U58 le envia para sus registros y consideraciones"
    
    msg = MIMEMultipart()
    msg['From'] = usuario
    msg['Subject'] = asunto
    msg['To'] = ', '.join(destinatarios)
    msg.attach(MIMEText(mensaje))
     
    if archivo:
        with open(archivo, 'rb') as f:
            archivo_adjunto = MIMEApplication(f.read(), Name=os.path.basename(archivo))
            encoders.encode_base64(archivo_adjunto)
            archivo_adjunto['Content-Disposition'] = f'attachment; filename={os.path.basename(archivo)}'
            msg.attach(archivo_adjunto)
    
    
    
    with smtplib.SMTP('smtp.gmail.com',587) as server:
        server.starttls()
        server.login(user_mail, password)
        server.sendmail(user_mail, destinatarios, msg.as_string())
        print("Correo Enviado")
        
    return
    




