
function refrescarTableMedicos(id_cirugia) {
    
    $.ajax({
        type: 'GET',
        url: '/refresh_columna_medicos/' + '?id_cirugia=' + id_cirugia,
        dataType: 'html',
        success: function(data) {
             $('#modalMedico').modal('hide')
            $('#my_columna_medicos').html(data);
        }
    }); 
}



function cambiarMedico(id_medico) {
    $('#modalMedico').modal('show')
    document.getElementById('id_notaqx').value = id_medico
}

function cambioMedicoHT(medico_id) {
    id_notaqx = document.getElementById('id_notaqx').value

    const datos = {
            id_notaqx : id_notaqx,
            medico_id : medico_id
          };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/cambio_medico_transoperatorio/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
            console.log('data.idcirugia', data.idcirugia)
            refrescarTableMedicos(data.idcirugia)
          })
          .catch(error => console.error(error));
}