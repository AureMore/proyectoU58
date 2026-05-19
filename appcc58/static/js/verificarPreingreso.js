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
            //alerta
            Swal.fire({
              title: "Admitir sin cargar medicinas?",
              text: "Al admitirlo sin cargar medicina NO podra cargar medicinas en preingreso posteriormente",
              icon: "warning",
              showCancelButton: true,
              confirmButtonColor: "#3085d6",
              cancelButtonColor: "#d33",
              confirmButtonText: "Continuar sin cargar medicinas!"
            }).then((result) => {
              if (result.isConfirmed) {
                window.location.href = `/admisionpreingreso/${paciente_id}/`;
              }
            });
            // fin alerta
        } else {
            window.location.href = `/admisionpreingreso/${paciente_id}/`;
        }
      })
      .catch(error => console.error(error));
    
}