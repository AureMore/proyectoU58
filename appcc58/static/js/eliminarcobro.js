function eliminarPagoCliente(id_detallectacobrar, montoeliminar) {
    Swal.fire({
        title: "Eliminar el pago de "+montoeliminar+" ?",
        text: "Se eliminaran las trasacciones relacionadas a este pago",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Si, Eliminar!"
        }).then((result) => {
        if (result.isConfirmed) {
            // eliminar en django pago
                const datos = {
                    id_detallectacobrar : id_detallectacobrar,
                };
                
                const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                fetch('/detalle_cuentacobrar_eliminar/', {
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
                    location.reload()
                    
                })
                .catch(error => console.error(error));

            // fin eliminar en django pago

        }
        });
}