function cambio_gasto(id_detalle_cirugia, porcentaje_nuevo) {
    if (typeof porcentaje_nuevo === 'string') {
        porcentaje_nuevo = parseFloat(porcentaje_nuevo.replace(',','.')).toFixed(2)
    } else {
        porcentaje_nuevo = parseFloat(porcentaje_nuevo).toFixed(2)
    } 

    const datos = {
        id_detalle_cirugia : id_detalle_cirugia,
        porcentaje_nuevo : porcentaje_nuevo,
    };

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/cambio_otros_gastos_medico_cirugia/', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        console.log('data.congelar_cambio', data.congelar_cambio)
        location.reload()
        
    })
    .catch(error => console.error(error));



}

function cambio_gasto_tx(id_detalle_cirugia, porcentaje_nuevo) {
    if (typeof porcentaje_nuevo === 'string') {
        porcentaje_nuevo = parseFloat(porcentaje_nuevo.replace(',','.')).toFixed(4)
    } else {
        porcentaje_nuevo = parseFloat(porcentaje_nuevo).toFixed(4)
    } 

    const datos = {
        id_detalle_cirugia : id_detalle_cirugia,
        tx_cambio_bcv : porcentaje_nuevo,
    };

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/cambio_otros_gastos_medico_cirugia_tx/', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        console.log('data.congelar_cambio', data.congelar_cambio)
        location.reload()
        
    })
    .catch(error => console.error(error));



}