async function cargarPagosDesdeDjango() {
    
    // Capturamos los dos valores que queremos enviar
    const factura_id = document.getElementById('factura_id').value;
    const proveedor_id = document.getElementById('medico_id_pago').value;

    const params = new URLSearchParams({
        factura_id: factura_id,
        proveedor_id: proveedor_id
    });

    const url = `/tus-pagos-url/?${params.toString()}`;

    try {
        const response = await fetch(url);
        const datos = await response.json();

        let tablaBody = document.getElementById('tbodypagos');
        tablaBody.innerHTML = ''; // Limpiar tabla antes de rellenar

        datos.forEach(pago => {
            let fila = tablaBody.insertRow();
            
            // Reutilizamos tu estructura de inputs para que el formulario siga siendo funcional
            fila.innerHTML = `
                <td><input type="text" readonly style="display:none;" name="mul_pago_cuenta_medico" value="${pago.id_destino}" /></td>
                <td><input type="text" readonly style="display:none;" name="mul_pago_origen_fondos" value="${pago.id_origen}" /></td>
                <td><input type="text" readonly style="text-align:right;" name="mul_montofraccion" value="${parseFloat(pago.monto).toFixed(2)}" /></td>
                <td><input type="text" readonly name="mul_monedapago" value="${pago.moneda}" /></td>
                <td><input type="text" readonly name="mul_referencia" value="${pago.referencia}" /></td>
                <td><input type="text" readonly name="mul_nota" value="${pago.nota || ''}" /></td>
                <td><button type="button" class="btn btn-danger btn-sm" onclick="eliminarFila(this, ${pago.monto}, '${pago.moneda}')">Eliminar</button></td>
            `;
            
            // Opcional: Si quieres que estos pagos ya existentes resten de la deuda inicial
            // saldoCuentas(pago.monto, pago.moneda);
        });

    } catch (error) {
        console.error("Error cargando pagos:", error);
    }
}


function mostrarCuentaOrigen(idbancolocal, moneda, uso) {
    document.getElementById('tipo_moneda_pago').textContent = moneda
    document.getElementById('uso_cuenta_origen').textContent = uso
    saldoCuentas(0,moneda )

}


function mostrarCuentaDestino(idbancolocal, moneda, uso, forma) {
    document.getElementById('tipo_moneda_destino').textContent = moneda
    document.getElementById('uso_cuenta_destino').textContent = uso
    document.getElementById('tipo_pago_destino').textContent = forma

}


async function aplicarPago(monedaCongelada) {
    const config = document.getElementById('metadata-pago');
    
    // Validación de seguridad
    if (!config) {
        console.error("Error: El elemento #metadata-pago no existe en el DOM.");
        // Intentar abrir el modal de todos modos si es crítico
        $('#myModalPago').modal('show');
        return;
    }

    const urlBusqueda = config.getAttribute('data-url');
    const facturaId = config.getAttribute('data-factura');

    try {
        await htmx.ajax('GET', urlBusqueda, {
            target: '#mostrar_distribucion_pago',
            values: { factura_id: facturaId },
            swap: 'innerHTML'
        });
        
        // Abrimos el modal después de que HTMX termine la petición
        $('#myModalPago').modal('show');
    } catch (err) {
        console.error("Error en la petición HTMX:", err);
        $('#myModalPago').modal('show'); // Abrir igual aunque falle la tabla
    }
}

function refrescarMedioPago() {
    medico_id_pago = document.getElementById('medico_id_pago').value
      $.ajax({
          type: 'GET',
          url: '/actualizar_cuentas_pagomedico/' + '?medico_id=' + medico_id_pago,  // Asegúrate de que esta URL sea correcta
          dataType: 'json', // Cambiar a 'json'
          success: function(data) {
              $('#selectDinamico').html(data.html);  // Actualiza el contenedor del select
          },
          error: function(xhr, status, error) {
              console.error(error);
          }
      });

}

function agregarNuevoMetodoMedico() {
  var aliasdepago = document.getElementById('id_aliasdepago').value
  let id_formadepago = document.getElementById('id_formadepago').value
  var cuentabancaria = document.getElementById('id_cuentabancaria').value
  let id_bancodestino = document.getElementById('id_bancodestino').value
  let id_moneda = document.getElementById('id_moneda').value
  let id_correodestinopago = document.getElementById('id_correodestinopago').value
  var cedula_pagomovil = document.getElementById('id_cedula_pagomovil').value
  var telefono_pagomovil = document.getElementById('id_telefono_pagomovil').value
  if (aliasdepago == '') {
    alert('Colocar el nombre del alias de la cuenta')
    return
  }
  if (id_formadepago == '') {
    alert('Seleccionar la forma de pago ')
    return
  }

  if (id_formadepago == 1) {
    if (id_bancodestino == '') {
      alert('Seleccionar el Banco para pago movil ')
      return
    }
    if (cedula_pagomovil == '') {
      alert('Seleccionar cedula para pago movil ')
      return
    }
    if (telefono_pagomovil == '') {
      alert('Seleccionar el telefono para pago movil ')
      return
    }
  }
  medico_id_pago = document.getElementById('medico_id_pago').value
  const datos = {
    aliasdepago : aliasdepago,
    id_formadepago : id_formadepago,
    cuentabancaria : cuentabancaria,
    id_bancodestino : id_bancodestino,
    id_moneda : id_moneda,
    id_correodestinopago : id_correodestinopago,
    cedula_pagomovil : cedula_pagomovil,
    telefono_pagomovil : telefono_pagomovil,
    medico_id_pago : medico_id_pago,


  };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

fetch('/agregar_medio_pago_medico/', {
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
    refrescarMedioPago()
  })
  .catch(error => console.error(error));

}


function validarFormulario() {

  let saldo = document.getElementById('idsaldo').value
  if (parseFloat(saldo) > 0) {
    let respuesta = confirm("¿El pago de la factura no esta completo, deseas continuar?");
    if (respuesta) {
        return true;
    } else {
        return false;
    }
    
  } else {
    return true
  }
  
}


function distribucionpago() {
    $('#distribucionPagoModal').modal('show')
}


function cambioMoneda(tipo_moneda, id) {
  let tx = parseFloat(document.getElementById('tasa_tx').value).toFixed(4)
  let saldo_bs = parseFloat(document.getElementById('saldo_bs').dataset.valor).toFixed(2);
  if (tipo_moneda == 1) {
    let montodolares = calcularPagoRedondo(id);
    document.getElementById('idmonto_'+id).value = montodolares.toFixed(2)
    document.getElementById('idmontobs_'+id).value = parseFloat(montodolares.toFixed(2) * tx).toFixed(2)
    
  } else if ( tipo_moneda == 2 ) {
    document.getElementById('idmontobs_'+id).value = parseFloat(saldo_bs).toFixed(2)
    cambiomonto(parseFloat(saldo_bs).toFixed(2),id,'B')
  } else {
    document.getElementById('idmonto_'+id).value = 0
    document.getElementById('idmontobs_'+id).value = 0
  }
}

function cambiomonto(nuevo_monto, id, tipo) {
  let tx = parseFloat(document.getElementById('tasa_tx').value).toFixed(4)
  nuevo_monto = parseFloat(nuevo_monto).toFixed(2)
  if (tipo == 'D') {
    document.getElementById('idmontobs_'+id).value = parseFloat(nuevo_monto * tx).toFixed(2)
  } else {
    document.getElementById('idmonto_'+id).value = parseFloat(nuevo_monto / tx).toFixed(2)
  }
}


function calcularPagoRedondo(id_monto) {
    let saldo = parseFloat(document.getElementById('saldo_dl').dataset.valor).toFixed(2);

    // redondear hacia abajo al múltiplo de 10
    let pago = Math.floor(saldo / 10) * 10;

    return pago;
}

function colocarMonedaPago(moneda) {

  console.log('moneda', moneda)
  document.getElementById('id_moneda').value = moneda
}




