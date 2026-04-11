function check_retencion(detalle_baremo_id) {
    var checkbox = document.getElementById('id_detalle_' + detalle_baremo_id);
    if (checkbox.checked) {
        inactivar = 'True'
        // Aquí puedes agregar la lógica que deseas ejecutar si está seleccionado
    } else {
        inactivar = 'False'
        // Aquí puedes agregar la lógica que deseas ejecutar si NO está seleccionado
    }

    const datos = {
        inactivar : inactivar,
        detalle_baremo_id : detalle_baremo_id
          };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/inactivar_retencion_baremo/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
            console.log('activar o no')
            //location.reload()
          })
          .catch(error => console.error(error));
    

}