function cambioSeleccion(consumo_id) {
    const checkbox = document.getElementById('check_' + consumo_id);
    if (checkbox.checked) {
        var seleccion = 'True'
    } else {
        var seleccion = 'False'
    }
    const datos = {
            consumo_id : consumo_id,
            seleccion : seleccion
          };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/cambio_seleccion_consumo_cirugia/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
            let consumo = data.cantidad
            document.getElementById('cantidad_seleccion').textContent = consumo;
            return 
          })
          .catch(error => console.error(error));
     
}

function muestraDetalleBaremo() {
    let cantidad_seleccionados =  document.getElementById('cantidad_seleccion').textContent
    if (cantidad_seleccionados > 0) {
        $('#detalleBaremoFacturar').modal('show')
    } else {
        alert('Debe seleccionar los consumos a cambiar de baremo de facturacion')
    }
    
    
}


function cambiarnuevoBaremo(cirugia_id) {
   let nuevo_baremo = document.getElementById('nuevo_baremo_facturacion').value
   if (nuevo_baremo != "") {

        const datos = {
            nuevo_baremo : nuevo_baremo,
            cirugia_id : cirugia_id
          };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/cambiar_consumo_nuevo_baremo/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
            location.reload()
          })
          .catch(error => console.error(error));



   } else {
        alert('Seleccionar un item de baremo valido')
   }
    
}

document.addEventListener('DOMContentLoaded', function () {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl)
    })
});