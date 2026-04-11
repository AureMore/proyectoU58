function activarIgtf() {
  const tfoot = document.getElementById("pedir_igtf");
  var monedaOrigen = document.getElementById('idmonedacuenta').value
  var monedaDestino = document.getElementById('monedaProveedor').value
  if (monedaOrigen == 'Dolares' && monedaDestino == 'Dolares') {
    tfoot.style.display = "table-footer-group"; // mostrar
  } else {
    tfoot.style.display = "none"; // ocultar
  }
  
}

function seleccionarOrigen(idOrigen, usoCuenta, monedaCuenta) {
    document.getElementById('idusocuenta').value = usoCuenta
    document.getElementById('idmonedacuenta').value =monedaCuenta
    colocarSaldo()
    activarIgtf()
    
}


function seleccionarDestino(idDestino,formaPago,bancoPago,monedaProveedor) {
    document.getElementById('idformapago').value = formaPago
    document.getElementById('idbancopago').value =bancoPago
    document.getElementById('monedaProveedor').value = monedaProveedor
    colocarSaldo()
    activarIgtf()
   
}

function validarCampos() {
    var msjValidacion = ''
    const idOrigenFondos = document.getElementById('idOrigenFondos').value
    let idmontopagar = document.getElementById('idmontopagar').value
    if (typeof idmontopagar === 'string') {
        idmontopagar = parseFloat(idmontopagar.replace(',','.')).toFixed(2)
    } else {
        idmontopagar = parseFloat(idmontopagar).toFixed(2)
    }
    const idnotapago = document.getElementById('idnotapago').value
    const idDestinoFondos = document.getElementById('idDestinoFondos').value
    const idreferenciapago = document.getElementById('idreferenciapago').value
    const monedau58 = document.getElementById('idmonedacuenta').value
    const monedaPro = document.getElementById('monedaProveedor').value
    let saldoTexto = document.getElementById("saldo_factura_pendiente").innerText;
    let to_fac_bs = document.getElementById("total_factura_en_bolivares").innerText;
    if (typeof to_fac_bs === 'string') {
        to_fac_bs = parseFloat(to_fac_bs.replace(',','.')).toFixed(2)
    } else {
        to_fac_bs = parseFloat(to_fac_bs).toFixed(2)
    }

    if (typeof saldoTexto === 'string') {
        saldoTexto = parseFloat(saldoTexto.replace(',','.')).toFixed(2)
    } else {
        saldoTexto = parseFloat(saldoTexto).toFixed(2)
    }

    const saldo_restante =  parseFloat(saldoTexto) - parseFloat(idmontopagar)



    if (idOrigenFondos == '' ){
        msjValidacion = 'Indicar origen de los fondos'
        Swal.fire({
        title: "Validando",
        text: msjValidacion,
        icon: "error"
        });
    }
    if (idmontopagar == 0 || idmontopagar == '' ){
        msjValidacion = 'Indicar monto a pagar'
        Swal.fire({
            title: "Validando",
            text: msjValidacion,
            icon: "error"
            });
    }
    if (idreferenciapago == ''  ){
        msjValidacion = 'Indicar referencia del pago'
        Swal.fire({
            title: "Validando",
            text: msjValidacion,
            icon: "error"
            });
    }
    if (idDestinoFondos == '' ){
        msjValidacion = 'Seleccionar destino del pago'
        Swal.fire({
            title: "Validando",
            text: msjValidacion,
            icon: "error"
            });
    }

    if (monedau58 != monedaPro ){
        msjValidacion = 'Monedas distintas del origen y destino del pago!'
        Swal.fire({
            title: "Validando",
            text: msjValidacion,
            icon: "error"
            });
    }





  
    if (msjValidacion == '') {
        if (parseFloat(saldo_restante) < 0) {
          alert('ℹ️ Información:\nSe generará una nota de crédito automática al proveedor');

        }
        
        $('#spinnerEsperar').modal('show')
        return true
    } else {
        //Swal.fire(msjValidacion);
        return false
    }
}


function eliminarPago(idEliminarPago, compuesto, idfactura) {
    if (compuesto == 'True') {
      var confirmacion = confirm("Este es un pago que comprende varias facturas.¿Desea eliminar los pagos de TODAS las facturas relacionadas?")
    } else {
      var confirmacion = true;
    }
    if (confirmacion == true) {
      const datos = {
        idEliminarPago: idEliminarPago,
        idfactura: idfactura,
      };
  
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
      fetch('/eliminar_abonoCuentaPagar/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        }, 
        body: JSON.stringify(datos)
      })
      .then(response => response.json())
      .then(data => {
        console.log('data.mensaje', data.mensaje)
        if (data.mensaje === 'NO') {
          alert('No puede eliminar este pago hasta eliminar el pago que genero la nota de credito o eliminar la nota de credito primero!')
        } else {
          const id = data.id;
          window.location.href = `/factura_compra_pagar/${id}/`;
        }
        /*  */
        // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
      })
      .catch(error => console.error(error));

    }

}

function verBoton() {
    var div = document.getElementById('tasatxnew');
    div.classList.remove('ocultar');
}



function nuevaTasa(idFactura) {
    let nuevoCambio = document.getElementById('new_cambio').value;
    let fecha_new_cambio = document.getElementById('fechaentrega').value;
    nuevoCambio = parseFloat(nuevoCambio.replace(',','.'))
    const datos = {
        idFactura: idFactura,
        nuevoCambio : nuevoCambio,
        fecha_new_cambio : fecha_new_cambio
      };
  
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
      fetch('/change_TasaCambio/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        }, 
        body: JSON.stringify(datos)
      })
      .then(response => response.json())
      .then(data => {
        console.log('cambiado')
        const id = data.id;
        window.location.href = `/factura_compra_modificar/${id}/`;
        // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
      })
      .catch(error => console.error(error));



}

function cambiarPrecioUsd(montoNew,idDetallefactura) {
  montoNew = montoNew.replace(',','.')
  const datos = {
    idDetallefactura: idDetallefactura,
    montoNew : montoNew,
  };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  fetch('/change_precio_usd_factura/', {
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
    // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
  })
  .catch(error => console.error(error));
}

function cambiarDescuentoBs(montoNew,idDetallefactura) {
  montoNew = montoNew.replace(',','.')
  const datos = {
    idDetallefactura: idDetallefactura,
    montoNew : montoNew,
  };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  fetch('/change_descuento_bs_factura/', {
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
    // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
  })
  .catch(error => console.error(error));
}


function cambiartasa(fecha) {
    monto_usd = document.getElementById('idmontopagarusd').value
    if (typeof monto_usd === 'string') {
        monto_usd = parseFloat(monto_usd.replace(',','.')).toFixed(2)
    } else {
        monto_usd = parseFloat(monto_usd).toFixed(2)
    }

    const datos = {
        nfechaCambio : fecha,
    };

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/buscar_tasa_bcv_cxp/', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('tasacambio').value = parseFloat(data.congelar_cambio).toFixed(4)
        if (monto_usd > 0) {
            cambioMonto('D', monto_usd)
        }
        
    })
    .catch(error => console.error(error));
  
}

function cambioMonto(moneda, monto) {
    var monedaOrigen = document.getElementById('idmonedacuenta').value
    var monedaDestino = document.getElementById('monedaProveedor').value
    var origen = document.getElementById('idOrigenFondos').value
    var destino = document.getElementById('idDestinoFondos').value
    if (monedaOrigen != monedaDestino) {
      alert('Origen de pago y Destino deben manejar la misma moneda')
      document.getElementById('idmontopagar').value = 0.00
      document.getElementById('idmontopagarusd').value = 0.00
      return
    }
    if (origen == '' || destino == '') {
      alert('Seleccione origen y destino de los fondos primero')
      document.getElementById('idmontopagar').value = 0.00
      document.getElementById('idmontopagarusd').value = 0.00
      return
    }


    var tasatx = document.getElementById('tasacambio').value
    if (typeof monto === 'string') {
        monto = parseFloat(monto.replace(',','.')).toFixed(2)
    } else {
        monto = parseFloat(monto).toFixed(2)
    }
        
    tasatx = parseFloat(tasatx.replace(',','.'))

    if (moneda == 'D') {
        document.getElementById('idmontopagarusd').value = monto
        let nuevo_monto = (monto * tasatx).toFixed(2)
        document.getElementById('idmontopagar').value = nuevo_monto
    } else {
        document.getElementById('idmontopagar').value = monto
        let nuevo_monto = (monto / tasatx).toFixed(2)
        document.getElementById('idmontopagarusd').value = nuevo_monto
    }
}


function cambioProveedorFactura(notaentrega_id, facturacompra_id, nuevoproveedor_id, proveedor_actual_id) {
  if (nuevoproveedor_id != '') {
    const datos = {
        notaentrega_id : notaentrega_id,
        facturacompra_id : facturacompra_id,
        nuevoproveedor_id : nuevoproveedor_id,
        proveedor_actual_id : proveedor_actual_id,
    };

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/cambio_proveedor_factura/', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        alert('Proveedor Modificado, se modifica la la factura y nota de entrega (si existe!) a este nuevo proveedor')
        //location.reload()
        
    })
    .catch(error => console.error(error));

  } else {
    document.getElementById('proveedor_factura').value = proveedor_actual_id
    alert('El proveedor no puede estar en blanco, seleccione proveedor valido')

  }
  

}

function cambioRetencion(nueva_retencion_id, facturacompra_id) {
  const datos = {
        nueva_retencion_id : nueva_retencion_id,
        facturacompra_id : facturacompra_id,
    };

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/cambio_retencion_factura/', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        alert('Cambio de Retencion Aplicado')
        location.reload()
        
    })
    .catch(error => console.error(error));
}


function cambiarporcentajeiva(montoNew,idDetallefactura) {
    if (typeof montoNew === 'string') {
        montoNew = parseFloat(montoNew.replace(',','.')).toFixed(2)
    } else {
        montoNew = parseFloat(montoNew).toFixed(2)
    }


  const datos = {
    idDetallefactura: idDetallefactura,
    montoNew : montoNew,
  };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  fetch('/change_porcentaje_iva_factura/', {
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
    // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
  })
  .catch(error => console.error(error));
}

function modificarNumero(numero, factura_id, tipo) {
  proveedor_factura = document.getElementById('proveedor_factura').value

   const datos = {
      factura_id: factura_id,
      numero : numero,
      tipo: tipo,
      proveedor_factura:proveedor_factura,
    };

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/change_numeros_factura/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      }, 
      body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
      if (data.mensaje == 'YAEXISTENF') {
        alert('Numero de documento y/o numero de control ya existe en ese proveedor')
        document.getElementById('nrodocumento').value = '0'
        
      }
      //location.reload()
      // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
    })
    .catch(error => console.error(error));
  
}

function pagarEnDecenas(monto) {
    return Math.floor(monto / 10) * 10;
}

function cambioIgtf() {
  const checkbox = document.getElementById("my_check_igtf");
  let tasa_igtf = document.getElementById("new_cambio").value;
  if (typeof tasa_igtf === 'string') {
        tasa_igtf = parseFloat(tasa_igtf.replace(',','.')).toFixed(4)
    } else {
        tasa_igtf = parseFloat(tasa_igtf).toFixed(4)
    }

  if (checkbox.checked) {
    const celdaexenta = document.getElementById("exento_igtf");
    const celda = document.getElementById("base_imponible_igtf");
    let valorTexto = celda.textContent.trim();
    let valorExento = celdaexenta.textContent.trim();

    if (typeof valorTexto === 'string') {
        valorTexto = parseFloat(valorTexto.replace(',','.')).toFixed(2)
    } else {
        valorTexto = parseFloat(valorTexto).toFixed(2)
    }
    if (typeof valorExento === 'string') {
        valorExento = parseFloat(valorExento.replace(',','.')).toFixed(2)
    } else {
        valorExento = parseFloat(valorExento).toFixed(2)
    }

    let base_imponible_igtf_bs = parseFloat(valorTexto) + parseFloat(valorExento)
    console.log('base_imponible_igtf_bs', base_imponible_igtf_bs)
    let monto_dolares_igtf = parseFloat(base_imponible_igtf_bs  / tasa_igtf)

    let monto_pagar_dolares = pagarEnDecenas(monto_dolares_igtf)

    cambioMonto('D', parseFloat(monto_pagar_dolares) )
    document.getElementById("idmontopagarusd").value = parseFloat(monto_pagar_dolares).toFixed(2)
    //document.getElementById("idmontopagarusd").readOnly = true
    document.getElementById("idmontopagar").readOnly = true
    document.getElementById("monto_pagar_igtf_bs").value = parseFloat(base_imponible_igtf_bs * (3 / 100)).toFixed(2)
  } else {
    document.getElementById("idmontopagarusd").value = 0.00
    document.getElementById("idmontopagar").value = 0.00
    document.getElementById("idmontopagarusd").readOnly = false
    document.getElementById("idmontopagar").readOnly = false
    document.getElementById("monto_pagar_igtf_bs").value = 0.00
    colocarSaldo()
      console.log("No está marcado");
  }
  
}

function cambioTasa(fechaCambio) {

    const fecha_cambio_congelado = fechaCambio + ' 20:00:00.000'
    // Make an AJAX request to your Django backend
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `/buscar_cambio_desde_js/?fecha_cambio_congelado=${fecha_cambio_congelado}`, true);
    xhr.onload = function() {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        let monto = response.monto; // Assuming the Django backend returns a JSON response with a 'fecha' key
        document.getElementById('new_cambio').value = parseFloat(monto).toFixed(4)
        var div = document.getElementById('tasatxnew');
        div.classList.remove('ocultar');
      }
    };
    xhr.send();
    

}