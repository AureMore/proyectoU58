from datetime import datetime
# IMPORTANTE: Asegúrate de importar el modelo CambioBcv desde donde lo tengas definido
from .models import CambioBcv 

def variables_globales(request):
    """
    Inyecta la tasa del BCV y el grupo del usuario en todas las plantillas.
    """
    # 1. Si el usuario no ha iniciado sesión, devolvemos variables vacías
    if not request.user.is_authenticated:
        return {'group_name': None, 'cambio': 0}
        
    # 2. Obtenemos el grupo del usuario
    group = request.user.groups.first()
    group_name = group.name if group else None
    
    # 3. Obtenemos la tasa del BCV del día
    # Usamos .date() para comparar solo la fecha y evitar problemas con las horas
    cambio_obj = CambioBcv.objects.filter(fecha_cambio=datetime.now().date()).first()
    
    # Asume que tu modelo CambioBcv tiene un campo llamado 'tasa' o similar.
    # Ajusta 'cambio_obj.tasa' al nombre real de tu campo si es diferente.
    cambio_valor = cambio_obj.cambio if cambio_obj else 0
    
    # 4. Retornamos un diccionario. Estas claves serán variables globales en el HTML.
    return {
        'group_name': group_name,
        'cambio': cambio_valor,
    }