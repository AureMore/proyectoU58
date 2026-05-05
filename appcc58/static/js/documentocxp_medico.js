function colocaPorcentaje(concepto_id, natural, juridico) {
    // Aquí puedes utilizar los valores de "natural" y "juridico"
    natural = parseFloat(natural.replace(',','.')).toFixed(2)

    document.getElementById('retencion').value = natural
    let factura_id = document.getElementById('factura_id').value
    const datos = {
      concepto_id: concepto_id, 
      factura_id:factura_id
    
    }; 

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
    fetch('/actualizar_retencion_factura_medico/', {
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


    // ...
  }


  function validateFields(botonPresionado) {
    // Obtienes los valores de los campos que deseas validar
    
    // ...
    if (botonPresionado === 'guardar_factura') {
      // Obtienes los valores de los campos que deseas validar
      var nrodocumento = document.getElementById('nrodocumento').value;
      var nrocontrol = document.getElementById('nrocontrol').value;

      // Realizas la validación de los campos
      if (nrodocumento === '' || nrocontrol === '') {
        Swal.fire({
          title: "Campos Necesarios",
          text: "Numero de documento y numero de control deben completarse",
          icon: "error"
        });
        return false; // Si la validación falla, se cancela el envío del formulario
      } else {
        return true
      }
    }
  
    // Si la validación es correcta o se presionó otro botón, se permite el envío del formulario
    return true;
  }


function agregaraFactura(idFactura) {

let guardar = document.getElementById("guardar-producto").checked;
  
var cantidad = document.getElementById('cantidad-agregar').value
var descripcion = document.getElementById('descripcion-agregar').value
var precio = document.getElementById('precio-unico').value
var iva = document.getElementById('iva-agregar').value
var gastos = document.getElementById('administrativo').value
let id_moneda_pago = document.getElementById('id_moneda_pago').value
let producto_id = document.getElementById('producto-id').value


if (descripcion == '') {
  alert('Debe indicar una descripcion')
  return
}
if (id_moneda_pago == '') {
  alert('Debe indicar una Moneda del nuevo item')
  return
}

  const datos = {
    idFactura: idFactura, 
    cantidad: cantidad,
    descripcion: descripcion,
    precio: precio,
    iva: iva,
    gastos: gastos,
    id_moneda_pago : id_moneda_pago,
    producto_id: producto_id,
    guardar : guardar
  
  }; 

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
 
  fetch('/guardar_detalle_factura/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    }, 
    body: JSON.stringify(datos)
  }) 
  .then(response => response.json())
  .then(data => {
    /* refreshTable(idFactura)
    $('#agregarDetalleFactura').modal('hide');
    
    refreshTableResumen(idFactura)
    $('#tblresumen').html(data);  */ 
    
    location.reload()
    // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
  })
  .catch(error => console.error(error));
}

function refreshTable(idFactura) {
  // Obtener el valor del input con id "id_filter"
  $.ajax({
      type: 'GET',
      url: '/refresh_table_detalle_factura_medico/' + '?idFactura=' + idFactura,
      dataType: 'html',
      success: function(data) {
          $('#tabla-detalle-factura').html(data);
      }
  });
}

function refreshTableResumen(idFactura) {
  // Obtener el valor del input con id "id_filter"
  $.ajax({
      type: 'GET',
      url: '/refresh_table_resumen_factura/' + '?idFactura=' + idFactura,
      dataType: 'html',
      success: function(data) {
          $('#tblresumen').html(data);
          
      }
  });
}

function cambiaTipoDocumento(idFactura) {
  var tipoDocumento = document.getElementById('tipodocumento').value
    const datos = {
      idFactura: idFactura,
      tipoDocumento: tipoDocumento,
    };

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/cambiar_tipo_documento/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      }, 
      body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
      /* refreshTable(idFactura)
      refreshTableResumen(idFactura) */
      location.reload()
      // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
    })
    .catch(error => console.error(error));
}


function cambiaGastos(idFactura, newGasto) {
  $.ajax({
    type: 'GET',
    url: '/cambia_gastos_administrativo/' + '?idFactura=' + idFactura + '&newGasto=' + newGasto,
    dataType: 'html',
    success: function(data) {
      console.log("RELOAD")
      location.reload();
       /*  refreshTable(idFactura)
        refreshTableResumen(idFactura)
        $('#tblresumen').html(data);  
        $('#tabla-detalle-factura').html(data); */
       
    }
});
}

function eliminarDetalleFactura(idDetalleFactura, idFactura) {
  
    const datos = {
      idDetalleFactura: idDetalleFactura,
    };
    if (confirm("¿Estás seguro de que deseas eliminar este item ?, al eliminarlo vuelve al pendiente de pago")) {

      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
      fetch('/eliminar_detalle_factura/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        }, 
        body: JSON.stringify(datos)
      }) 
      .then(response => response.json())
      .then(data => {
        //refreshTable(idFactura)
        //refreshTableResumen(idFactura)
        location.reload()
        // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
      })
      .catch(error => console.error(error));

    } 
  
    

}


function buscarRecibos() {
  const beneficiario = document.getElementById('id_medico').value
  if (beneficiario == '') {
    alert("Seleccione un Beneficiario")
  } else {
    refreshTableRecibos(beneficiario)
    $('#buscarReciboMedico').modal('show')


  }
}


function refreshTableRecibos(idmedico) {
  // Obtener el valor del input con id "id_filter"
  $.ajax({
      type: 'GET',
      url: '/refresh_table_recibos/' + '?idmedico=' + idmedico,
      dataType: 'html',
      success: function(data) {
          $('#tabla-recibo-medico').html(data);
      }
  });
}



  function agregarRecibo() {
    const table = document.getElementById('tabla-convertir-afactura');
    const container = document.getElementById('selected-rows-container');
    const rows = table.querySelectorAll('tr input[type="checkbox"]:checked').forEach((checkbox) => {
      const row = checkbox.parentNode.parentNode; // obtener la fila padre
      const cells = row.cells;
      const rowData = [];
      const idfactura = cells[0];
      const documento = cells[2];
      const control = cells[3];
      const concepto = cells[7];
      const nota = cells[5]
      const monto = cells[6];
      const fecha = cells[4];
      const txCambio = cells[9];
      let cambioDia = txCambio.textContent.trim().replace(',','.')
      let montoDolar = parseFloat(monto.textContent.trim().replace(',','.')) /  parseFloat(cambioDia)
     
      rowData.push(`<td><input type="text" name="convertir_factura" readonly value="${fecha.textContent.trim()}" ></td>`); 
      rowData.push(`<td><input type="text" name="convertir_factura" readonly value="${documento.textContent.trim()}" ></td>`); 
      rowData.push(`<td><input type="text" name="convertir_factura" readonly value="${control.textContent.trim()}" ></td>`); 
      rowData.push(`<td><input type="text" name="convertir_factura" readonly value="${concepto.textContent.trim()}" ></td>`); 
      rowData.push(`<td><input type="text" name="convertir_factura" readonly value="${nota.textContent.trim()}" ></td>`); 
      rowData.push(`<td><input type="text" name="convertir_factura" readonly value="${monto.textContent.trim()}" style="text-align: right;"></td>`); 
      rowData.push(`<td><button class="delete-button"><i class="fa-solid fa-trash"></i></button></td>`); 
      rowData.push(`<td style="display: none;"><input type="text"   name="id_factura_documento" value="${idfactura.textContent.trim()}" ></td>`); 
      rowData.push(`<td style="display: none;"><input type="text"   name="id_factura_dolar" value="${montoDolar.toFixed(2)}" ></td>`); 
      const rowHTML = `<tr>${rowData.join('')}</tr>`; // crear una fila de tabla con campos de entrada
      const tableBody = document.getElementById('items-recibo').getElementsByTagName('tbody')[0];
      tableBody.innerHTML += rowHTML; // agregar la fila HTML al cuerpo de la tabla
      const deleteButtons = document.querySelectorAll(".delete-button");
        deleteButtons.forEach(button => {
          button.addEventListener("click", function() {
            const row = button.parentNode.parentNode; // obtener la fila correspondiente
            row.remove(); // eliminar la fila
            const montoInputs = tableBody.querySelectorAll('tr td:nth-child(6) input'); // asumiendo que la columna "monto" es la sexta columna
            const montoInputsDolar = tableBody.querySelectorAll('tr td:nth-child(9) input')

            // Inicializar la suma
            let suma = 0; 
            
            // Iterar sobre los inputs y sumar sus valores
            for (const input of montoInputs) {
              var valor = parseFloat(input.value.replace(',', '.')); 
              if (!isNaN(valor)) {
                suma += valor;
              }
            }

            let sumaDolar = 0;
            for (const input of montoInputsDolar) {
              var valor = parseFloat(input.value.replace(',', '.')); 
              if (!isNaN(valor)) {
                sumaDolar += valor;
              }
            }
            
            const totalElement = document.getElementById('total-monto');
            totalElement.textContent = `${suma.toFixed(2)}`; // mostrar el total
            document.getElementById('baseimponible').value = suma.toFixed(2)
            document.getElementById('baseimponible_usd').value = sumaDolar.toFixed(2)
            calculaRetencion()
          });
        });
    });
  const tableBody = document.getElementById('items-recibo').getElementsByTagName('tbody')[0];
  const montoInputs = tableBody.querySelectorAll('tr td:nth-child(6) input'); // asumiendo que la columna "monto" es la sexta columna
  const montoInputsDolar = tableBody.querySelectorAll('tr td:nth-child(9) input')
  // Inicializar la suma
  let suma = 0;

  // Iterar sobre los inputs y sumar sus valores
  for (const input of montoInputs) {
    var valor = parseFloat(input.value.replace(',', '.')); 
    if (!isNaN(valor)) {
      suma += valor;
    }
  } 


  let sumaDolar = 0;

  // Iterar sobre los inputs y sumar sus valores
  for (const input of montoInputsDolar) {
    var valor = parseFloat(input.value.replace(',', '.')); 
    if (!isNaN(valor)) {
      sumaDolar += valor;
    }
  } 


  const totalElement = document.getElementById('total-monto');
  totalElement.textContent = `${suma.toFixed(2)}`; // mostrar el total
  document.getElementById('baseimponible').value = suma.toFixed(2)
  document.getElementById('baseimponible_usd').value = sumaDolar.toFixed(2)
  


  calculaRetencion()
  $('#buscarReciboMedico').modal('hide')
}
 
function cambioConcepto(idConcepto, pNatural, pJuridico, pSustraendo, pTope){
  document.getElementById('p_rentencion').value = pNatural
  document.getElementById('m-sustraendo').value = pSustraendo
  document.getElementById('m-tope').value = pTope
  
  calculaRetencion()
}

function calculaRetencion() {
  let tasadeldia =  document.getElementById('tasa-del-dia').value
  let sustraendo =  document.getElementById('m-sustraendo').value
  let tope =  document.getElementById('m-tope').value
  let baseImponible = document.getElementById('baseimponible').value
  let porcRetencion = document.getElementById('p_rentencion').value
  let montoRetener = ((parseFloat(baseImponible.replace(',','.'))*(parseFloat(porcRetencion.replace(',','.')/100))))-parseFloat(sustraendo.replace(',','.'))
  if ((parseFloat(baseImponible.replace(',','.'))) < parseFloat(tope.replace(',','.'))) {
    montoRetener = 0
  }
  tasadeldia = parseFloat(tasadeldia.replace(',','.'))
  let montoRetenerDolares = montoRetener / tasadeldia

  document.getElementById('m_retencion').value = montoRetener.toFixed(2)
  document.getElementById('m_retencion_usd').value = montoRetenerDolares.toFixed(2)
  let montoNeto = parseFloat(baseImponible.replace(',','.')) - montoRetener
  let montoNetoDolar = montoNeto / tasadeldia
  document.getElementById('monto_pagar_neto').value = montoNeto.toFixed(2)
  document.getElementById('monto_pagar_usd').value = montoNetoDolar.toFixed(2)


}

document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        console.log("Evita el prevent")
        event.preventDefault();
    }
});

function validarCampos() {
  var msjValidacion = ''
  vMedico = document.getElementById('id_medico').value
  vNrodoc = document.getElementById('nrodocumento').value
  vNrocon = document.getElementById('nrocontrol').value
  vRetencion = document.getElementById('retencion').value
  vMonto = document.getElementById('monto_pagar_neto').value
  if (vMedico == '') {
    msjValidacion = 'Debe Seleccionar Medico'
  }
  if (vNrodoc == '') {
    msjValidacion = 'Colocar Numero de Factura'
  }
  if (vNrocon == '') {
    msjValidacion = 'Colocar Numero de Control de Factura'
  }
  if (vRetencion == '') {
    msjValidacion = 'Seleccionar Concepto de la Factura'
  }
  if (parseFloat(vMonto) <= 0) {
    msjValidacion = 'Factura con monto en 0 no se procesa'
  }

  if (msjValidacion != '') {

    Swal.fire({
      title: "Revise Campos!",
      text: msjValidacion,
      icon: "error"
    });

    return false
  } else {
    return true
  }

}