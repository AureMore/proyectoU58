function colocaExistenciaDeposito(idDeposito, idSolicitud) {
    $.ajax({
        type: 'GET',
        url: '/colocaExistenciaDeposito/' + '?idDeposito=' + idDeposito + '&idSolicitud=' + idSolicitud ,
        dataType: 'html',
        success: function(data) {
           location.reload();
        }
    });

}

function validarCantidad(ncantidad_modificada, ncantidad_solicitada) {
    ncantidad_modificada = parseFloat(ncantidad_modificada.replace(',','.'))
    ncantidad_solicitada = parseFloat(ncantidad_solicitada.replace(',','.'))
    if (ncantidad_modificada > ncantidad_solicitada) {
        alert('ADVERTENCIA: va a despachar una cantidad mayor a la solicitada! cantidad solictada = '+ ncantidad_solicitada)
    }
}



