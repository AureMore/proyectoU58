new DataTable('#tbldisponiblevincular');

function vincularBaremo(detalle_vincular) {
        var baremo_principal = document.getElementById('baremo_principal').value
        if (baremo_principal == ' ' | baremo_principal == '') {
            alert('Debe seleccionar un Baremo Principal para vincular los otros')
        } else {
            if (baremo_principal == detalle_vincular ) {
                alert('No puede vincular el mismo baremo principal')
            } else {
                const datos = {
                    detalle_vincular : detalle_vincular,
                    baremo_principal : baremo_principal
                    };

                    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
                    fetch('/vincular_baremo/', {
                        method: 'POST',
                        headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                        },
                        body: JSON.stringify(datos)
                    })
                    .then(response => response.json())
                    .then(data => {
                        refrescarTablaVinculaciones(baremo_principal)
                    })
                    .catch(error => console.error(error));
            }
        }
}


function refrescarTablaVinculaciones(baremo_principal_id ) {
    
    $.ajax({
        type: 'GET',
        url: '/refresh_table_vinculados/' + '?baremo_principal_id=' + baremo_principal_id ,
        dataType: 'json', // Cambiar a 'json'
        success: function(response) {
            // Actualizar el HTML de la tabla
            $('#baremos-vinculados').html(response.html);
          
        },
        error: function() {
            // Manejo de errores
            alert('Error al refrescar la tabla. Inténtalo de nuevo.');
            
        }
    }); 
}

function eliminarVinculado(detalle_vincular) {
     var baremo_principal = document.getElementById('baremo_principal').value
    const datos = {
        detalle_vincular : detalle_vincular,
        };

        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/eliminar_vinculo_baremo/', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
        })
        .then(response => response.json())
        .then(data => {
            refrescarTablaVinculaciones(baremo_principal)
        })
        .catch(error => console.error(error));

}