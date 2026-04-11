function muestramodalabono(cantidad_de_notas) {
    
    if (cantidad_de_notas > 0) {
        $('#modalNotasCredito').modal('show')
    } else {
        $('#hacerAbonos').modal('show')
    }
   
}

function noaplicarNota() {
    $('#hacerAbonos').modal('show')
}

function procesarNotasSeleccionadas() {
    const numerofactura = document.getElementById('nrodocumento').value;
    const table = document.getElementById('tabla_nota_credito');  // Selecciona la tabla
        const checkboxes = table.querySelectorAll('input[type="checkbox"]');  // Selecciona todos los checkboxes
        let selectedRows = [];  // Array para almacenar las filas seleccionadas
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {  // Verifica si el checkbox está marcado
                const row = checkbox.closest('tr');  // Obtiene la fila padre (<tr>)
                const cells = row.querySelectorAll('td');  // Obtiene todas las celdas de la fila
                
                // Extrae los datos de las celdas (ajusta según necesites)
                const data = {
                    numero: cells[0].textContent.trim(),  // Columna # (e.g., 1)
                    id: cells[1].querySelector('a').textContent.trim(),  // Columna ID (es un enlace)
                    numeroNota: cells[2].textContent.trim(),  // Columna NRO. NOTA
                    monto: cells[3].textContent.trim(),  // Columna MONTO BS
                    usuario: cells[4].textContent.trim(),  // Columna USUARIO
                    idCheckbox: checkbox.id,  // El ID del checkbox, que es el mismo que nc.id
                    numerofactura: numerofactura
                };
                
                selectedRows.push(data);  // Añade los datos al array
            }
        });

        if (selectedRows.length > 0) {
                console.log('Filas seleccionadas:', selectedRows);  // Muestra en la consola para depuración

                const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                            
                fetch('/agregar_nota_credito_al_pago/', {
                    method: 'POST',
                    headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify(selectedRows)
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Respuesta del servidor:', data)
                    location.reload()
                })
                .catch(error => console.error(error));

        } else {
                alert('No se seleccionaron notas de credito');
        }

            

    
}