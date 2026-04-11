function marcaGrupo(grupoid, presupuestoid) {
    let factor_aumento = document.getElementById('factor_aumento').value
    factor_aumento = parseFloat(factor_aumento.replace(',','.'))

}

function obtenerCheckboxesMarcados(idpresupuesto) {
    let factor_aumento = document.getElementById('factor_aumento').value
    factor_aumento = parseFloat(factor_aumento.replace(',','.'))
    console.log('presupuesto_id:'+idpresupuesto)
    console.log('factor_aumento:'+factor_aumento)
    // Obtener todos los checkboxes dentro del tbody
    const checkboxes = document.querySelectorAll('tbody input[type="checkbox"]');
    const checkboxesMarcados = [];
    // Iterar sobre los checkboxes y verificar cuáles están marcados
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            checkboxesMarcados.push(checkbox.id); // Guardar el id del checkbox marcado
        }
    });
    // Mostrar los checkboxes marcados en la consola (o hacer lo que necesites con ellos)

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch('/cambiar_precios_factor/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 
            checkboxes: checkboxesMarcados,
            idpresupuesto: idpresupuesto, // Agregar idpresupuesto
            factor_aumento: factor_aumento // Agregar factor_aumento
         }),
        
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload()
        } else {
            console.log('Error al guardar datos: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.log('Error en la solicitud: ' + error);
    });


}

function deshacerUltimo(idpresupuesto) {

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch('/cambiar_precios_factor_undo/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 
            idpresupuesto: idpresupuesto, // Agregar idpresupuesto
         }),
        
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload()
        } else {
            console.log('Error al guardar datos: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.log('Error en la solicitud: ' + error);
    });

    
}

function variarTx(cirugia_id, txNew) {
    txNew = parseFloat(txNew.replace(',','.'))
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch('/cambiar_tx_cambio_cirugia/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 
            cirugia_id: cirugia_id, // Agregar cirugia_id
            cambio_nuevo: txNew,
         }),
        
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload()
        } else {
            console.log('Error al guardar datos: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.log('Error en la solicitud: ' + error);
    });
    
}
