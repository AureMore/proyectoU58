function revisarCargaMedicinas(cirugia_id, paciente_id) {

    const datos = {
        cirugia_id : cirugia_id,
      };
    
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/revisar_carga_preingreso/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(datos)
      })
      .then(response => response.json())
      .then(data => {
        if (data.mensaje == 'NO') {
            alert('NO puede realizar admision hasta cargar MEDICINAS y/o MMQ en PRE-INGRESO')
        } else {
            window.location.href = `/admisionpreingreso/${paciente_id}/`;
        }
      })
      .catch(error => console.error(error));
    
}