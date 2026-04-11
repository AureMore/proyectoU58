function aplicarDescuento(nMoneda, nBaseimponible, nMontoDescuento, idNota) {
    nBaseimponible = nBaseimponible.replace(',','.');
    let baseimponible = parseFloat(nBaseimponible).toFixed(2)
    nMontoDescuento = nMontoDescuento.replace(',','.');
    let montoDescuento = parseFloat(nMontoDescuento).toFixed(2)
    if (nMoneda == 2) {
        
        const datos = {
            baseimponible: baseimponible,
            montoDescuento : montoDescuento,
            idNota : idNota
          };
        
          const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
          fetch('/actualizarDescuentoNotaentrega/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            }, 
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
            console.log("descuento actualizado")
            location.reload()
            
          })
          .catch(error => console.error(error));
        
    }
}

function cambiar_piva(nuevo_piva, id_detallenotaentrega) {
  nuevo_piva = nuevo_piva.replace(',','.')
  const datos = {
    nuevo_piva: nuevo_piva,
    id_detallenotaentrega : id_detallenotaentrega,
  };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  fetch('/actualizar_piva_notaentrega/', {
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

}


function cambiar_precio_unitario(nuevo_precio_unitario, id_detallenotaentrega) {
  nuevo_precio_unitario = nuevo_precio_unitario.replace(',','.')
  const datos = {
    nuevo_precio_unitario: nuevo_precio_unitario,
    id_detallenotaentrega : id_detallenotaentrega,
  };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  fetch('/actualizar_precio_unitario_notaentrega/', {
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

}


function cambiar_cantidad_a_factura(nueva_cantidad, id_detallenotaentrega) {
  // cuando esten preparados se habilita esta funcionalidad

}

function item_a_factura(checkbox, producto_id ) {
  if (checkbox.checked){
        var marcado = true
    } else {
        var marcado = false
    }

  let tasacambiofactura = parseFloat(document.getElementById('tasacambiofactura').value).toFixed(4)

  const datos = {
    marcado: marcado,
    producto_id : producto_id,
  };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  fetch('/actualizar_marca_a_factura/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    }, 
    body: JSON.stringify(datos)
  })
  .then(response => response.json())
  .then(data => {
    //location.reload()
    htmx.ajax('GET', `/actualizar_resumen_factura/?tasa_cambio=${tasacambiofactura}`, '#resume-ne-multiple');    
  })
  .catch(error => console.error(error));


}


function guardar_retencion_ne(porcentaje, id_notaentrega, id_concepto) {

  const datos = {
    porcentaje: porcentaje,
    id_notaentrega : id_notaentrega,
    id_concepto : id_concepto
  };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  fetch('/actualizar_retencion_islr_ne/', {
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
  
}


function cambio_retencion(id_concepto,ne_id){
    var tipo_persona = document.getElementById("proveedor_rif").value;

    let select = document.getElementById("conceptoretencion");
    let option = select.options[select.selectedIndex];

    let natural = option.dataset.natural;
    let juridica = option.dataset.juridica;

    let retencion_aplicar = 0

    if (tipo_persona.charAt(0) == 'J') {
      retencion_aplicar = juridica
    } 

    if (tipo_persona.charAt(0) == 'N') {
      retencion_aplicar = natural
    } 

     document.getElementById("porcentaje_retencion").value = retencion_aplicar
    guardar_retencion_ne(retencion_aplicar, ne_id, id_concepto)

}


function cambioTasa() {
  var fecha_cambio = document.getElementById("fechadocumento").value;

  const datos = {
    fecha_cambio: fecha_cambio,
  };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  fetch('/actualizar_tasa_factura_multiple/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    }, 
    body: JSON.stringify(datos)
  })
  .then(response => response.json())
  .then(data => {
    if ( parseFloat(data.monto_cambio).toFixed(4) > 0) {
        document.getElementById("tasacambiofactura").value = parseFloat(data.monto_cambio).toFixed(4)
    } else {
        document.getElementById("tasacambiofactura").value = 0.0000
        alert('No hay tasa de cambio de ese dia')
    }
    //location.reload()    
  })
  .catch(error => console.error(error)); 
  
}

function cambioNumero(numero, tipo_nro) {
  proveedor_id = document.getElementById("idproveedor").value;

  const datos = {
    numero: numero,
    tipo_nro: tipo_nro,
    proveedor_id: proveedor_id
  };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  fetch('/revisar_existe_factura_control/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    }, 
    body: JSON.stringify(datos)
  })
  .then(response => response.json())
  .then(data => {
      console.log('existe:', data.existe)
      if (data.existe) {
        console.log('existe:', data.existe)
        if (tipo_nro == 'NF') {
          document.getElementById("nrofactura").value = ''
          numero_descripcion = 'FACTURA'
        } else {
          document.getElementById("nrocontrol").value = ''
          numero_descripcion = 'CONTROL'
        }
          
        
        Swal.fire({
          icon: "error",
          title: "Numero de "+numero_descripcion+" Ya existe",
          text: "No puede incluir numeros iguales de factura / control al mismo proveedor!",
        });
        
      }
    //location.reload()    
  })
  .catch(error => console.error(error)); 

  
}
