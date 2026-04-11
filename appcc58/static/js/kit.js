


function eliminarKitId(inventarioId) {
        const datos = {
          inventarioId : inventarioId,
        };
      
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      
        fetch('/eliminar_kit_inventario/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
          },
          body: JSON.stringify(datos)
        })
        .then(response => response.json())
        .then(data => {
          console.log(data);
          // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
          refreshTable();
        })
        .catch(error => console.error(error));
      
}


function refreshTable() {
    var idKit = document.getElementById('producto').value // Obtener el valor del input con id "id_filter"
    $.ajax({
        type: 'GET',
        url: '/refresh_table_kit/' + '?idKit=' + idKit,
        dataType: 'html',
        success: function(data) {
            $('#my_table_kit').html(data);
        }
    });
}


function agregaraKit(idInventario) {
    var idKit = document.getElementById('producto').value // Obtener el valor del input con id "id_filter"
    if (idKit != '') {
        const datos = {
            idInventario : idInventario,
            idKit: idKit, 
        };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/agregar_kit_inventario/', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
            refreshTable();
        })
        .catch(error => console.error(error));
    }

}

/* function cambioKit() {
    let deposito_seleccionado = document.getElementById('deposito').value
    if (deposito_seleccionado != '') {
        refreshTable()
    } else {
        Swal.fire("Seleccione Deposito para Kit");
        document.getElementById('producto').value = ''
    }
   
} */


function totalPrecio(idInventario,nCantidad) {
    const datos = {
        idInventario : idInventario,
        nCantidad: nCantidad
      };
    
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
      fetch('/update_kit_inventario/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(datos)
      })
      .then(response => response.json())
      .then(data => {
        console.log(data);
        // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
        refreshTable();
      })
      .catch(error => console.error(error));

}

function inventario_deposito() {
    const idDeposito = document.getElementById('deposito').value
    if (idDeposito != '') {
        refreshTableInventario(idDeposito)
    }
}

function refreshTableInventario(idDeposito) {
    
    $.ajax({
        type: 'GET',
        url: '/resfresh_tabla_inventario/' + '?idDeposito=' + idDeposito,
        dataType: 'html',
        success: function(data) {
            $('#tabla-inventario-deposito').html(data);
        }
    });
}