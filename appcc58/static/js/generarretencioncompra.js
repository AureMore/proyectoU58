function generarComprobanteCompra(proveedor_compra_id, factura_id, boton) {
    boton.style.display = 'none';
    const datos = {
        proveedor_compra_id : proveedor_compra_id,
        factura_id : factura_id,
      };
    
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/generar_comprobante_retencion_compra/', {
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