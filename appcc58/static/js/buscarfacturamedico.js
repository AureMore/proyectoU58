function buscarNumeroRepetido(numero, campo, idfactura) {
    if (campo == 'F') {
        var nFactura = numero
        var nControl = document.getElementById('nrocontrol').value
    } else {
        var nFactura = document.getElementById('nrodocumento').value
        var nControl = numero
    }

    let proveedor = document.getElementById('medico_id_pago').value

    const datos = {
        nFactura : nFactura,
        nControl : nControl,
        proveedor : proveedor,
        campo : campo,
        idfactura: idfactura
    };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/validar_factura_medico_existe/', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.respuesta);
        if (data.respuesta == 'existe' & campo =='F') {
            alert('Ya esta en uso ese numero de factura')
            document.getElementById('nrodocumento').value = 0
        } else if (data.respuesta == 'existe' & campo =='C') {
            alert('Ya esta en uso ese numero de control')
            document.getElementById('nrocontrol').value = 0
        }
        
    })
    .catch(error => console.error(error));
}