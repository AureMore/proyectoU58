function mostrarRelacionadosPresupuesto(presupuesto_id) {
    $.ajax({
        type: 'GET',
        url: '/item_relacionados_presupuesto_eliminar/' + '?presupuesto_id=' + presupuesto_id,
        dataType: 'json', // Cambiar a 'json'
        success: function(response) {
            // Actualizar el HTML de la tabla
            $('#tabla-relacionados-eliminar').html(response.html);
            // Leer el valor de total_subtotal
            
            $('#eliminarPresupuesto').modal('show')
                
        },
       
    }); 
}


function eliminarPresupuesto(presupuesto_id,nombre_presupuesto) {
    document.getElementById('id_presupuesto_eliminar').value = presupuesto_id
     Swal.fire({
        title: "Eliminar presupuesto :"+presupuesto_id+' ?',
        text: "Este proceso no tiene reverso , debe estar seguro(a) si desea continuar! ",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#e65148",
        cancelButtonColor: "#2141cf",
        confirmButtonText: "Si, Continuar!"
        }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById('eliminarPresupuestoLabel').textContent = 'Eliminacion de presupuesto: '+ presupuesto_id+ ' de: '+ nombre_presupuesto;
             $('#eliminarPresupuesto').modal('show')
             mostrarRelacionadosPresupuesto(presupuesto_id);
        }
        });

}