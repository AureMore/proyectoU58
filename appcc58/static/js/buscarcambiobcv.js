function buscarCambioBcv(nfechaCambio,idFactura) {

console.log(idFactura)
  const datos = {
    nfechaCambio : nfechaCambio,
    idFactura : idFactura,
  };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  fetch('/buscar_tasa_bcv/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    },
    body: JSON.stringify(datos)
  })
  .then(response => response.json())
  .then(data => {
    document.getElementById('tasa_pago').value = data.congelar_cambio
    location.reload()
  })
  .catch(error => console.error(error));

    
}

function cambioTasaManual(nNuevocambio,idFactura) {

console.log(idFactura)
  const datos = {
    nNuevocambio : nNuevocambio,
    idFactura : idFactura,
  };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  fetch('/cambio_tasa_bcv_factura_medico/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    },
    body: JSON.stringify(datos)
  })
  .then(response => response.json())
  .then(data => {
    document.getElementById('tasa_pago').value = parseFloat(nNuevocambio).toFixed(4)
    location.reload()
  })
  .catch(error => console.error(error));

    
}