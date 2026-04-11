function verificarFecha(fecha_factura) {
    console.log('fecha:', fecha_factura)
    const datos = {
            fecha_factura : fecha_factura,
          };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/verificar_fecha_factura_valida/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
            if (data.mensaje == 'fecha_invalida') {
                Swal.fire("Fecha Invalida para la factura, hay facturas con fecha mayor a esta!");
                document.getElementById('fecha_factura_final').value = ''
            } 
          })
          .catch(error => console.error(error));


}