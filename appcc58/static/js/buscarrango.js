function buscarRango() {
    const fecha_desde = document.getElementById('fecha_desde').value
    const fecha_hasta = document.getElementById('fecha_hasta').value
    if ( fecha_desde != '' && fecha_hasta != '' ){
        $.ajax({
            type: 'GET',
            url: '/refresh_table_pagos_medicos/' + '?fecha_desde=' + fecha_desde + '&fecha_hasta=' + fecha_hasta,
            dataType: 'html',
            success: function(data) {
                $('#id_tabla_pagos_medicos').html(data);
            }
        });
    } else {
        Swal.fire("Deben colocar fecha desde y fecha hasta");
    }


}


$(document).ready(function() {
    $('#exampleDataList').on('input', function() {
        var selectedOption = $(this).val();
        var selectedId = $('option[value="' + selectedOption + '"]').data('id');
        $('#medico_id').val(selectedId);
        document.getElementById('cod-medico').value = selectedId
    });
});


function buscarMedico() {
    id = document.getElementById('cod-medico').value
        if (id != '') {
           
            $.ajax({
                type: "GET",
                url: "/get_medico_byid/",  
                data: {
                    id: id,
                },
                success: function(data) { 
                    document.getElementById('exampleDataList').value = data.nombre
                   
                }
            })
        }

}

