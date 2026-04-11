function cambioConcepto(idConcepto, pNatural, pJuridico, pSustraendo, pTope){
    const idProveedor = document.getElementById('id_proveedor').value
    var rifProveedor = document.getElementById('rif-proveedor').value
    let baseimponbible = document.getElementById('baseimponible').value.replace(',','.')
    let montoIva = document.getElementById('monto_iva').value.replace(',','.')
    var typePerson = rifProveedor.charAt(0);

    if (idProveedor == '') {
        Swal.fire("Debe Seleccionar un proveedor");
        return
    }

    if (typePerson == 'J' || typePerson == 'G') {
        var porcentajeRetencion = pJuridico.replace(',','.')
    } else {
        var porcentajeRetencion = pNatural.replace(',','.')
    }

    var montoRetener = baseimponbible * (porcentajeRetencion/100)
    montoRetener = montoRetener.toFixed(2)
    let montoPagar = (baseimponbible - montoRetener)
    console.log(parseFloat(montoPagar)+(montoIva))
    document.getElementById('p_rentencion').value = porcentajeRetencion
    document.getElementById('m_retencion').value = montoRetener
    document.getElementById('monto_pagar_neto').value = montoPagar
    
}

function buscarCambio() { 
    const fecha_cambio_congelado = document.getElementById('fechaentrega').value
   
    const date = new Date(fecha_cambio_congelado);
    const fechaFormatted = `${date.getFullYear()}-${padZero(date.getMonth() + 1)}-${padZero(date.getDate() + 1)} ${padZero(date.getHours())}:${padZero(date.getMinutes())}:${padZero(date.getSeconds())}.${padZero(date.getMilliseconds(), 6)}`;
    console.log("Fecha")
    console.log(fechaFormatted)
    // Make an AJAX request to your Django backend
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `/buscar_cambio_desde_js/?fecha_cambio_congelado=${fechaFormatted}`, true);
    xhr.onload = function() {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        const monto = response.monto; // Assuming the Django backend returns a JSON response with a 'fecha' key
        document.getElementById('tasa_cambio').value = monto; // Update the input field with the retrieved date
      }
    };
    xhr.send();
  
  }
  
  function padZero(value, length = 2) {
    return String(value).padStart(length, '0');
  }