function refrescarTableBaremo(id_eliminar) {
    
    $.ajax({
        type: 'GET',
        url: '/refresh_table_baremo_eliminar/' + '?id_eliminar=' + id_eliminar,
        dataType: 'json', // Cambiar a 'json'
        success: function(response) {
            // Actualizar el HTML de la tabla
            $('#table-cirugias-eliminar').html(response.html);
            // Leer el valor de total_subtotal
            
            $('#eliminarBaremo').modal('show')
                .on('shown.bs.modal', function () { // Solo cerrar cuando el modal esté totalmente renderizado
                $('#esperar_modal').modal('hide');
            });
        },
        error: function() {
            // Manejo de errores
            alert('Error al refrescar la tabla. Inténtalo de nuevo.');
            $('#esperar_modal').modal('hide');
        }
    }); 
    
}

function eliminarBaremo(id_eliminar, nombre_baremo) {
    Swal.fire({
        title: "Seguro(a) de Eliminar?",
        text: "Eliminara el item de TODAS las cirugias donde este usado!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#e65148",
        cancelButtonColor: "#2141cf",
        confirmButtonText: "Si, Continuar!"
        }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById('tituloeliminacion').textContent = 'Cirugias afectadas con eliminacion de: '+nombre_baremo;
            document.getElementById('itemeliminar').value = id_eliminar
            $('#esperar_modal').modal('show')
            refrescarTableBaremo(id_eliminar);
           
             
        }
        });
    
}

function eliminaritembaremo() {
    let ideliminarbaremo = document.getElementById('itemeliminar').value 
    
    const datos = {
            idbaremo : ideliminarbaremo,
          };
        
          const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
          fetch('/eliminar_item_baremo/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
           console.log('eliminados')
           location.reload()
           
          })
          .catch(error => console.error(error));

    
}

function activarDetalleBaremo(id_baremo) {
    var checkbox = document.getElementById('id_activar_subbaremo_' + id_baremo);
    if (checkbox.checked) {
        activar = 'True'
        // Aquí puedes agregar la lógica que deseas ejecutar si está seleccionado
    } else {
        activar = 'False'
        // Aquí puedes agregar la lógica que deseas ejecutar si NO está seleccionado
    }
    const datos = {
        activar : activar,
        id_baremo : id_baremo
          };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/activar_detalle_item_baremo/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
           console.log('activar o no')
           
          })
          .catch(error => console.error(error));
}


function inactivarBaremo(baremo_id) {
    var checkbox = document.getElementById('inactivar_' + baremo_id);
    if (checkbox.checked) {
        inactivar = 'True'
        // Aquí puedes agregar la lógica que deseas ejecutar si está seleccionado
    } else {
        inactivar = 'False'
        // Aquí puedes agregar la lógica que deseas ejecutar si NO está seleccionado
    }

    const datos = {
        inactivar : inactivar,
        baremo_id : baremo_id
          };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/inactivar_detalle_item_baremo/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
            console.log('activar o no')
            location.reload()
          })
          .catch(error => console.error(error));
    
}