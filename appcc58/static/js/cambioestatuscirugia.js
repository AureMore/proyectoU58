function cambioEstatus(estatus_actual, nuevo_estatus, cirugia_id ) {
    estatus_actual = parseInt(estatus_actual, 10);
    nuevo_estatus = parseInt(nuevo_estatus, 10);
    if ( estatus_actual == 6 || estatus_actual == 7 || estatus_actual == 8 ||  estatus_actual == 9 ) {
        if ( nuevo_estatus == 7 || nuevo_estatus == 6 ) {
            document.getElementById('estatus_cirugia_'+ cirugia_id).value = nuevo_estatus
            const datos = {
                cirugia_id : cirugia_id,
                nuevo_estatus : nuevo_estatus,
            };
            
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch('/cambiar_estatus_cirugia_manual/', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(datos)
            })
            .then(response => response.json())
            .then(data => {
                if (data.mensaje == 'SIN-ALTA') {
                    document.getElementById('estatus_cirugia_'+ cirugia_id).value = estatus_actual
                    alert('El alta medica debe ser ejecutado por alta medica al paciente')
                } else {
                    alert('Cambio de estatus ejecutado')
                }
                
            })
            .catch(error => console.error(error));


        } else {
            document.getElementById('estatus_cirugia_'+ cirugia_id).value = estatus_actual
            Swal.fire({
                icon: "error",
                title: "Denegado",
                text: "Nuevo estatus no valido",
                });
        }
    } else {
        document.getElementById('estatus_cirugia_'+ cirugia_id).value = estatus_actual
        Swal.fire({
            icon: "error",
            title: "Denegado",
            text: "Este estatus no puede modificarse por esta opcion",
            });

    }
    

}