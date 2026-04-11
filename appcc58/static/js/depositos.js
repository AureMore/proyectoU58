function verDeposito(idInventario) {
    document.getElementById('id_producto').value = idInventario
    motivoDescarga = document.getElementById('motivo').value
    personaEntrega = document.getElementById('personaEntregar').value
    if (motivoDescarga == ''){
        alert('Seleccionar Motivo de Descarga')
        return
    }
    if (personaEntrega == ''){
        alert('Seleccionar persona a entregar')
        return
    }


    $('#modalentregaFarmacia').modal('show')
    $.ajax({
        type: 'GET',
        url: '/refresh_tableDepositoUsoDownload/' + '?idInventario=' + idInventario,
        dataType: 'html',
        success: function(data) {
            $('#tabla-deposito').html(data);
        }
    });



}

function verificarDescarga(cantidadDeposito, cantidadDescargar, fila) {
    const errorSpan = document.getElementById('error_' + fila);
    cantidadDescargar = cantidadDescargar.replace(',','.')
    cantidadDeposito = cantidadDeposito.replace(',','.')
    if (parseInt(cantidadDescargar) > parseInt(cantidadDeposito)) {
        errorSpan.style.display = 'inline'; // Muestra el mensaje de error
    } else {
        errorSpan.style.display = 'none'; // Oculta el mensaje de error
    }
}

function cargarProductosDescargaInventario() {

    // Selecciona la tabla por su ID
    const table = document.getElementById('tbldepositoUsoDownload');
    const motivoretiro_id = document.getElementById('motivo').value
    const codigodescarga = document.getElementById('codigo_descarga').value
    const entregar_id = document.getElementById('personaEntregar').value
    const nota = document.getElementById('id_nota_entrega').value
    const inventario_id = document.getElementById('id_producto').value

    // Selecciona el cuerpo de la tabla
    const tbody = table.querySelector('tbody');
    const inputValues = [];

    // Itera sobre cada fila del cuerpo de la tabla
    for (let row of tbody.rows) {
        const input = row.querySelector('input[name="cantidad_descargar"]');
        const inputIdDeposito = row.querySelector('input[type="number"][name^="id_"]'); // Captura el input del ID del depósito
        //const deposito = row.cells[2].textContent.trim(); // Deposito
        const ubicacion = row.cells[3].textContent.trim(); // Ubicacion
        const cantidadDeposito = row.cells[4].textContent.trim(); // Existencia

        if (input) {
            inputValues.push({
                id_deposito: inputIdDeposito.value,
                ubicacion: ubicacion,
                motivoretiro : motivoretiro_id,
                codigodescarga : codigodescarga,
                nota : nota,
                entregar_a : entregar_id,
                cantidad_a_descargar: input.value,
                cantidad_deposito: cantidadDeposito,
                inventario_id : inventario_id,
            });
        }
    }

    // Aquí puedes hacer lo que necesites con los datos de la fila
    console.log(inputValues);
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
 
    fetch('/guardar_descargaInventario/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
    }, 
    body: JSON.stringify({ rowData : inputValues })
    }) 
    .then(response => response.json())
    .then(data => {
        refreshTableDescarga(codigodescarga)
        $('#modalentregaFarmacia')         .modal('hide')
          // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
    })
    .catch(error => console.error(error));


}

function refreshTableDescarga(codigodescarga) {
     // Obtener el valor del input con id "id_filter"
    $.ajax({
        type: 'GET',
        url: '/refresh_table_descarga_ajuste/' + '?codigodescarga=' + codigodescarga,
        dataType: 'html',
        success: function(data) {
            $('#tabla-inventariodescarga').html(data);
            
        }
    });
}

function eliminarDescarga(idDescarga) {
    const codigo = document.getElementById('codigo_descarga').value
    $.ajax({
        type: 'GET',
        url: '/eliminarDescargaAjuste/' + '?idDescarga=' + idDescarga + '&codigo=' + codigo,
        dataType: 'html',
        success: function(data) {
            $('#tabla-inventariodescarga').html(data);
        }
    });


}
