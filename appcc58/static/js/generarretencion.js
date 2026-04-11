function generarComprobante(medico_id, factura_id, boton) {
    boton.style.display = 'none';
    const datos = {
        medico_id : medico_id,
        factura_id : factura_id,
      };
    
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/generar_comprobante_retencion/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(datos)
      })
      .then(response => response.json())
      .then(data => {
        console.log('data',data.comprobante )
        let nro_comprobante = parseFloat(data.comprobante)
        if (nro_comprobante > 0) {
            window.location.href = `/pdf_retencion/${data.comprobante}/`;
        }
      })
      .catch(error => console.error(error));



}

function eliminarPagoMedico(id_transaccion) {
    const datos = {
        id_transaccion : id_transaccion,
      };
    
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/eliminar_pago_medico_factura/', {
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