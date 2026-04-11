
function refrescarTableBaremito(id_cirugia, id_detalle, modo, detalle_presupuesto ) {
    
    $.ajax({
        type: 'GET',
        url: '/refresh_table_baremitos/' + '?id_cirugia=' + id_cirugia + '&id_detalle=' + id_detalle + '&modo=' + modo + '&detalle_presupuesto=' + detalle_presupuesto,
        dataType: 'json', // Cambiar a 'json'
        success: function(response) {
            // Actualizar el HTML de la tabla
            $('#tabla-baremitos').html(response.html);
            // Leer el valor de total_subtotal
            
           /*  $('#eliminarBaremo').modal('show')
                .on('shown.bs.modal', function () { // Solo cerrar cuando el modal esté totalmente renderizado
                $('#esperar_modal').modal('hide');
            }); */
        },
        error: function() {
            // Manejo de errores
            alert('Error al refrescar la tabla. Inténtalo de nuevo.');
            $('#modalSubBaremito').modal('hide');
        }
    }); 
}

function mostrarModalBaremito(id_detalle, id_detalle_presupuesto) {
    let id_cirugia = document.getElementById('codigoatencion').value
    document.getElementById('id_baremito').value = id_detalle
    document.getElementById('id_detallepresupuesto').value = id_detalle_presupuesto
    refrescarTableBaremito(id_cirugia, id_detalle, 'N', id_detalle_presupuesto)
    $('#modalSubBaremito').modal('show')
}

function agregarNuevoBaremito() {
    let id_cirugia = document.getElementById('codigoatencion').value
    let id_detalle = document.getElementById('id_baremito').value
    let id_detallepresupuesto = document.getElementById('id_detallepresupuesto').value
    const id_nombre_baremito = document.getElementById('id_nombre_baremito').value
    
    if (id_nombre_baremito == '') {
        Swal.fire("Debe colocar un nombre de detalle!");
    } else {
        const datos = {
            nombre_baremito : id_nombre_baremito,
            id_cirugia : id_cirugia,
            id_detalle : id_detalle,
            id_detallepresupuesto : id_detallepresupuesto
          };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/agregar_detalle_item_baremito/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
            refrescarTableBaremito(id_cirugia, id_detalle, 'N', id_detallepresupuesto)
          })
          .catch(error => console.error(error));
    }
        
    
}

function eliminarBaremito(id_baremito_consumo, detalle_id, cirugia_id) {
    const datos = {
            id_baremito_consumo : id_baremito_consumo,
          };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/eliminar_detalle_item_baremito/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
            refrescarTableBaremito(cirugia_id, detalle_id, 'E', 0)
          })
          .catch(error => console.error(error));
    
}