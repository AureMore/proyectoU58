function buscarResponsable() {
    const cedulaResponsable = document.getElementById('id_cedula_rep').value;
    $.ajax({
        type: 'GET',
        url: '/buscar_responsable/',
        data: {'cedula': cedulaResponsable},
        dataType: 'json',
        success: function(data) {
          // Obtener el elemento tbody de la tabla
          if (data.length === 0) {
                document.getElementById('id_nombre_rep').value =''
                document.getElementById('id_apellido_rep').value = ''
                document.getElementById('id_sexo_rep').value = ''
                document.getElementById('id_direccion_rep').value = ''
                document.getElementById('id_trabajo_rep').value = ''
                document.getElementById('id_direccion_trabajo_rep').value = ''
                document.getElementById('id_telefono_rep').value = ''

          } else {
            data.forEach((dato, index) => {
                document.getElementById('id_nombre_rep').value = dato.nombre
                document.getElementById('id_apellido_rep').value = dato.apellido
                document.getElementById('id_sexo_rep').value = dato.sexo
                document.getElementById('id_direccion_rep').value = dato.direccion
                document.getElementById('id_trabajo_rep').value = dato.trabajo
                document.getElementById('id_direccion_trabajo_rep').value = dato.direccion_trabajo
                document.getElementById('id_telefono_rep').value = dato.telefono1

          });
        }
        },
        error: function(xhr, status, error) {
            console.log('Error:', error);
          }
        })
}
