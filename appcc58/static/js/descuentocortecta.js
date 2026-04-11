function aplicarDescuentoCorteCuenta(id_detallepresupuesto, descuento, tipo) {
    if (typeof descuento === 'string') {
        descuento = parseFloat(descuento.replace(',','.')).toFixed(2)
    } else {
        descuento = parseFloat(descuento).toFixed(2)
    }
    if (tipo == 'p') {
        document.getElementById('p_descuento__'+id_detallepresupuesto).value = parseFloat(descuento).toFixed(2)
    } else {
        document.getElementById('m_descuento__'+id_detallepresupuesto).value = parseFloat(descuento).toFixed(2)
    }
    
    const datos = {
            id_detallepresupuesto : id_detallepresupuesto,
            descuento : descuento,
            tipo : tipo
          };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/aplicar_descuento_corte_cuenta/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
            console.log('data', data)
            if (data.mensaje == 'montomayor') {
                
                alert('Monto de descuento mayor a precio actual')
                document.getElementById('m_descuento__'+id_detallepresupuesto).value = parseFloat('0.00').toFixed(2)

            } 
            if (data.mensaje == 'ok') {
                
                location.reload()
            }
          })
          .catch(error => console.error(error));
    
        
}

function aplicarSoloLectura() {
    document.querySelectorAll('input[name="p_descuento"]').forEach(function(input) {
        input.readOnly = true;
    });
    document.querySelectorAll('input[name="m_descuento"]').forEach(function(input) {
        input.readOnly = true;
    });
}