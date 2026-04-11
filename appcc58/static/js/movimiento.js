function movimientoBanco(idBanco) {
        
        $.ajax({
            type: 'GET',
            url: '/refresh_table_movimientos/' + '?idBanco=' + idBanco,
            dataType: 'html',
            success: function(data) {
                $('#tabla-movimientos').html(data);
                $('#movimientosCuenta').modal('show')
            }
        });
}