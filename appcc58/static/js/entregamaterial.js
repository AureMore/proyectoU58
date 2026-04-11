
function validarCampos() {
    const accion = document.getElementById('accion').value;
    if (accion == 'imprimir'){
        return true
    }
    if (accion == 'compuesto'){
        return true
    }
    medicoSel = document.getElementById('medico').value
    cantidadEntregar = document.getElementById('cantidad_a_entregar').innerText
    if (medicoSel == "") {
        Swal.fire("Seleccione persona a entregar");
        return false
    } else {
        if (cantidadEntregar == "None") {
            Swal.fire("Seleccione productos a entregar");
            return false
        } else {
            return true
        }
    }

   
}


function updateDiferencia(input, rowNumber, cantidad_entregada, cantidad_tope) {
    var cantidad_nueva = input.replace(',','.');
    //const cantidad_nueva = parseInt(input.value);
    var cantidadUso = document.getElementById(`cantidad_usada_${rowNumber}`).value; // Lee el valor de cantidad_uso
    //const cantidadUso = parseInt(document.querySelector(`#cantidad_usada-${rowNumber}`).getAttribute('data-cantidad-uso'));
    cantidad_tope = cantidad_tope.replace(',','.')
    const diferencia = cantidad_tope - cantidad_nueva;

    console.log('cantidad tope:'+cantidad_tope)
     console.log('cantidad_nueva:'+cantidad_nueva)
   
    if (diferencia < 0) {
        Swal.fire("No puede usar una cantidad mayor a la entregada");
        //alert('No puede usar una cantidad mayor a la entregada')
        document.getElementById(`cantidad_usada_${rowNumber}`).value = cantidad_entregada
        
    } else {
        document.querySelector(`#diferencia_${rowNumber}`).textContent = diferencia;
        //actualiza en django
        const datos = {
            consumo_id : rowNumber,
            cantidad_real_usada : cantidad_nueva,
          };
        
          const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/cambiar_cantidad_conciliacion/', {
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
          })
          .catch(error => console.error(error));



    }
    
  }

function extractData() {
    var table = document.getElementById("consumo-table");
    var rows = table.rows;
    var data = [];

    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var cells = row.cells;
        var rowData = {};

        rowData.id = cells[1].textContent; // celda oculta con ID
        rowData.codigo = cells[2].textContent;
        rowData.cantidad_uso = cells[3].textContent;
        rowData.inventario = cells[4].textContent;
        var inputField = cells[5].querySelector("input");
        if (inputField) {
            rowData.cantidad_usada = inputField.value;
        } else {
            rowData.cantidad_usada = ""; // or some default value
        }
        rowData.presentacion = cells[6].textContent;
        rowData.solicitante = cells[7].textContent;
        rowData.entregado = cells[8].textContent;
        rowData.diferencia = cells[9].textContent;

        data.push(rowData);
    }

    return data;
}

function sendData() {
    var data = extractData();
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/guardar_conciliacion/", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify(data));
}


function advertenciaInventario(event) { 
    event.preventDefault();

    Swal.fire({
        title: "Importante !",
        text: "Al aceptar la devolucion , las cantidades seran actualizadas en el inventario, este proceso no tiene reverso! ",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Si, Proceder!"
      }).then((result) => {
        if (result.isConfirmed) {
            event.target.submit();
        } 
      });

}


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
                $('#tabla-atencion-inmediata-deposito-disponible').html(data);
            }
        }); 
  
        $('#modalentregaFarmacia').modal('show')
    }
  }



async function agregarConsumoCirugia(inventario_id,cantidad_aplicar, compuesto) {
    let idCirugia = document.getElementById('id_idCirugia').value
    let depositoId = document.getElementById('deposito-id').value
    
    if (typeof cantidad_aplicar === 'string') {
        cantidad_aplicar = parseFloat(cantidad_aplicar.replace(',','.')).toFixed(2)
    } else {
        cantidad_aplicar = parseFloat(cantidad_aplicar).toFixed(2)
    }

    //cantidad_aplicar = parseFloat(cantidad_aplicar.replace(',','.'))

    // revisar si ya existe una bomba de infusion
    if (await verificarExistenciaCompuesto(idCirugia, inventario_id)) {
        $('#modalentregaFarmacia').modal('hide')
        $('#modalCompuestos').modal('show')
        return
    }
    const datos = {
        inventario_id : inventario_id,
        cantidad_aplicar : cantidad_aplicar,
        idCirugia : idCirugia,
        depositoId : depositoId,
  
      };
    
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/agregar_a_consumo_cirugia_farmacia/', {
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
       if (data.mensaje == 'SINCANTIDAD') {
            alert('NO DISPONE SUFICIENTE PARA ASIGNAR ESA CANTIDAD')
       } else {
            if (compuesto == '2') {
                $('#modalCompuestos').modal('show')
            }
            
            refreshTableFarmacia()
            $('#modalentregaFarmacia').modal('hide')
       }
       
       
      })
      .catch(error => console.error(error));
  
   
  }



function validarexistencia(cantidadInput, cantidad_existencia) {

    if (typeof cantidadInput.value === 'string') {
        cantidad_entregar = parseFloat(cantidadInput.value.replace(',','.')).toFixed(2)
    } else {
        cantidad_entregar = parseFloat(cantidadInput.value).toFixed(2)
    }

    if (typeof cantidad_existencia === 'string') {
        cantidad_existencia = parseFloat(cantidad_existencia.replace(',','.')).toFixed(2)
    } else {
        cantidad_existencia = parseFloat(cantidad_existencia).toFixed(2)
    }

    //cantidad_entregar = parseFloat(cantidadInput.value.replace(',','.'))
    //cantidad_existencia = parseFloat(cantidad_existencia.replace(',','.'))
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

async function verificarExistenciaCompuesto(idCirugia, inventario_id) {
    var existe_compuesto = await revisarCompuesto(idCirugia, inventario_id);
    return existe_compuesto
}


async function revisarCompuesto(idcirugia, idproducto) {
    const datos = {
        idcirugia: idcirugia,
        idproducto: idproducto,
        lugar_consumo : 10
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
  