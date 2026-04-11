const rows = document.querySelectorAll('#tbl-extras tbody tr');
const idCirugua = document.getElementById('id_idCirugia').value
// Agregar evento de doble click a cada fila
rows.forEach(row => {
  row.addEventListener('dblclick', (event) => {
    const selectedRow = event.target.parentNode; // Obtener la fila seleccionada
    const rowData = []; // Array para almacenar los datos de la fila

    // Obtener los datos de la fila
    const cells = selectedRow.cells;
    for (let i = 0; i < cells.length; i++) {
        //if (i === 2 || i === 3) { // Celdas 2 y 3 son inputs
        //    rowData.push(cells[i].querySelector('input').value); // Obtener el valor del input
        //} else {
            rowData.push(cells[i].textContent); // Obtener el texto de la celda
        }
        idBaremo = rowData[0]
    //guardar en django personal extra
    const datos = {
        idBaremo : idBaremo,
        idCirugua: idCirugua,
      };
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/agregar_personal_extra/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
      // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
      refreshTablePersonalExtra();
      $('#personalExtra').modal('hide')
    })
    .catch(error => console.error(error));

  });
});

function refreshTablePersonalExtra() {

    $.ajax({
        type: 'GET',
        url: '/refresh_table_extras/' + '?idCirugua=' + idCirugua,
        dataType: 'html',
        success: function(data) {
            $('#my_tabla_medicos_qx').html(data);
        }
    }); 
}

function eliminarNotaQx(idNotaqx) {

  const datos = {
    idNotaqx : idNotaqx,
  };
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/refresh_table_extras_eliminar/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
      // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
      refreshTablePersonalExtra();
      $('#personalExtra').modal('hide')
    })
    .catch(error => console.error(error));

}