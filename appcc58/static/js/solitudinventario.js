function agregarSolicituditem(itemId, cantidad, nexistencia, nsolicitante) {
    cantidad = parseFloat(cantidad.replace(',','.'))
    nexistencia = parseFloat(nexistencia.replace(',','.'))
    if (cantidad > nexistencia) {
        alert('No puede Solicitar cantidades superiores a los disponible en deposito')
        return
    }
    $.ajax({
        type: 'GET',
        url: '/agregarSolicituditem/' + '?itemId=' + itemId + '&cantidad=' + cantidad + '&nsolicitante=' + nsolicitante,
        dataType: 'html',
        success: function(data) {
            $('#tabla-inventariosolicitud').html(data);
        }
    });

    // Aquí puedes agregar la lógica para manejar la solicitud
}

function eliminarSolicituditem(itemId) {
    
    $.ajax({
        type: 'GET',
        url: '/eliminarSolicituditem/' + '?itemId=' + itemId ,
        dataType: 'html',
        success: function(data) {
            $('#tabla-inventariosolicitud').html(data);
        }
    });


}