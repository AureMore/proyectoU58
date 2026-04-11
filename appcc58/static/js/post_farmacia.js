function muestraTablaDisponibleFarmacia() {
    let depositoId = document.getElementById('deposito-id').value
    if (depositoId == '') {
        alert('Seleccionar Deposito de Medicamentos')
        
    } else {
        $.ajax({
            type: 'GET',
            url: '/refresh_table_disponible_deposito/' + '?depositoId=' + depositoId,
            dataType: 'html',
            success: function(data) {
                $('#tabla-postoperatorio-deposito-disponible').html(data);
            }
        }); 

        $('#farmaciaModalHosp').modal('show')
    }
}



  function eliminarConsumo(idEliminar) {
    const datosEli = {
        idEliminar: idEliminar,

    }

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch('/eliminar_consumo/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datosEli)
        })
        
        .then(response => response.json())
        .then(data => {
            console.log(data.mensaje);
            if (data.mensaje == 'CUMPLIDO') {
                Swal.fire("El tratamiento fue cumplido y no puede eliminar el medicamento ! Comuniquese con el Dr. Agustin");
            } else {
                location.reload(); // Recargar la página manualmente
            }
            
        })
        .catch(error => console.error('Error:', error));


 }

 async function agregarConsumoCirugia(idInv,cantidad, compuesto) {
    const idCirugia = document.getElementById('iddeCirugia').value;
    const deposito = document.getElementById('deposito-id').value;
    venta = 0
    cantidad = cantidad.replace(',','.')
    if (await verificarExistenciaCompuesto(idCirugia, idInv)) {
        $('#farmaciaModalHosp').modal('hide')
        $('#modalCompuestos').modal('show')
        return
    } 

    var filaId = idInv
    const farmacia = 'True'

    const datos = {
      id: filaId,
      cantidad: cantidad,
      idCirugia: idCirugia,
      deposito_id: deposito,
      precio: venta,
    };

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/guardar_farmaco_hospital/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      }, 
      body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
      console.log(idCirugia);
        if (compuesto == '2') {
            $('#farmaciaModalHosp').modal('hide')
            $('#modalCompuestos').modal('show')
        } else {
            location.reload()
        }
      // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
      
    })
    .catch(error => console.error(error));

  }

  async function verificarExistenciaCompuesto(idCirugia, inventario_id) {
    
    var existe_compuesto = await revisarCompuesto(idCirugia, inventario_id);
    console.log('pase por aqui:',existe_compuesto)
    return existe_compuesto
}


async function revisarCompuesto(idcirugia, idproducto) {
    const datos = {
        idcirugia: idcirugia,
        idproducto: idproducto,
        lugar_consumo : 9
    };
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    try {
        const response = await fetch('/revisar_existe_compuesto_consumo/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
        });
        const data = await response.json();
        console.log(data);
        return data.consumo ? true : false;
    } catch (error) {
        console.error(error);
        return false; // O manejar el error de otra manera
    }
}

function validarexistencia(cantidadInput, cantidad_existencia) {

    cantidad_entregar = parseFloat(cantidadInput.value.replace(',','.'))
    cantidad_existencia = parseFloat(cantidad_existencia.replace(',','.'))
    if (cantidad_entregar > cantidad_existencia) {
        alert('No puede entregar una cantidad superior a la existencia. Si continua solo se agregara la cantidad disponible en deposito')
    }

    // Obtener la fila (tr) que contiene el input de cantidad
    const fila = cantidadInput.closest('tr');
    // Obtener el checkbox en la misma fila
    const checkbox = fila.querySelector('input[name="seleccionados"]');
    if (cantidad_entregar > 0) {
        checkbox.checked = true;
    } else {
        checkbox.checked = false;
    }
        

}
