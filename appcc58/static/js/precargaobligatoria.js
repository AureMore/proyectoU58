function precargaObligatoria() {
    var checkbox = document.getElementById('producto_obligatorio');

    if (checkbox.checked) {
        var operacionAplicar = 'C'; //create
    } else {
        var operacionAplicar = 'D'; //delete
    }
    const idCirugia_precarga_admicion = document.getElementById('id_idCirugia').value
    const datos = {
        idCirugia: idCirugia_precarga_admicion,
        operacionAplicar: operacionAplicar
    };
    
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    
        fetch('/aplicar_precarga_cirugia_obligatoria/', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
        }, 
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        refreshTable()
        //$('#modalInventario').modal('hide')
        // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
    })
    .catch(error => console.error(error));
        

}