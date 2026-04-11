function eliminarPago(idNotaQx) {
    
    const datos = {
      idNotaQx : idNotaQx,
    };
  
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
    fetch('/eliminarPagoMedico/', {
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
      // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
      location.reload()
    })
    .catch(error => console.error(error));
}

function eliminarPagosMedico(medico_id, nombre_medico) {
  console.log(nombre_medico)
  const datos = {
      medico_id : medico_id,
    };

    Swal.fire({
      title: "Seguro de Continuar ?",
      text: "Esta opcion eliminara todos los pagos pendiente a este medico :"+nombre_medico,
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Si, Eliminar"
    }).then((result) => {
      if (result.isConfirmed) {

        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch('/eliminarTodosPagoMedico/', {
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
          // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
          location.reload()
        })
        .catch(error => console.error(error));

        Swal.fire({
          title: "Eliminado",
          text: "Todos los pagos eliminados",
          icon: "success"
        });

      }
    });
    
}