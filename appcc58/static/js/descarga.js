function buscarFechas() {
    const desde = document.getElementById('fechadesde').value
    const hasta = document.getElementById('fechahasta').value
    $.ajax({
        type: 'GET',
        url: '/filtra_fecha_salida/' + '?desde=' + desde +'&hasta=' + hasta ,
        dataType: 'html',
        success: function(data) {
            $('#tblsalidafiltrada').html(data);

            
        }
    });
}