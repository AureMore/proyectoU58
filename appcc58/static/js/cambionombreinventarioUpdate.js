$(document).ready(function() {
  $('#exampleDataListUpdate').on('input', function() {
      var selectedOption = $(this).val();
      var selectedId = $('option[value="' + selectedOption + '"]').data('id');
      $('#producto_id_update').val(selectedId);
  });
});



function cambioNombreInventarioUpdate() {
    let producto_id = document.getElementById('producto_id_update').value
    console.log(producto_id)
    if (producto_id != '') {
        const datos = {
            producto_id: producto_id,
          };
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/obtener_producto_inventario/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            }, 
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
    
            //$('#tabla-detalle-inventario').html(data);
            document.getElementById('codigoUpdate').value = data['codigo'];
            document.getElementById('loteUpdate').value =data['lote'];
            document.getElementById('categoriaUpdate').value = data['categoria'];
            document.getElementById('pivaUpdate').value =data['piva'];
            document.getElementById('costoUpdate').value = data['costo'];
            document.getElementById('ventaUpdate').value = data['venta'];
            document.getElementById('laboratorioUpdate').value = data['laboratorio'];
            document.getElementById('presentacion_entradaUpdate').value = data['presentacion'];
            document.getElementById('presentacion_salidaUpdate').value = data['presentacion_salida'];
            document.getElementById('fechaelaboraUpdate').value = data['fecha_elaboracion'];
            document.getElementById('fechavenceUpdate').value = data['fecha_vencimiento'];



            // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
          })
          .catch(error => console.error(error));

        /////

    }
}


function cambioTasaEdicion(fechaCambio) {

    const fecha_cambio_congelado = fechaCambio + ' 20:00:00.000'
    // Make an AJAX request to your Django backend
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `/buscar_cambio_desde_js/?fecha_cambio_congelado=${fecha_cambio_congelado}`, true);
    xhr.onload = function() {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        let monto = response.monto; // Assuming the Django backend returns a JSON response with a 'fecha' key
        document.getElementById('tasacambiofactura').value = parseFloat(monto).toFixed(4)
        const div = document.getElementById('muestratasa');
        div.classList.remove('oculta');
      }
    };
    xhr.send();
    
}

function recargaPagina() {
  location.reload()
}


