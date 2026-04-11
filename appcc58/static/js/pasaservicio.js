function abreModalPasaraServicio(id_detalle_presupuesto) {
    document.getElementById('id_detalle_presupuesto').value = id_detalle_presupuesto
    $('#pasarServicioaMedico').modal('show')
}

function trasladar_a_servicio(id_cirugia) {
   let id_detalle_presupuesto = document.getElementById('id_detalle_presupuesto').value 
   let id_baremo_medico_a_servicio = document.getElementById('medico_a_servicio').value
   if (id_baremo_medico_a_servicio != '') {
        $.ajax({ 
            type: "GET",
            url: "/pasar_medico_a_servicio/",  
            data: {
                id_cirugia: id_cirugia,
                id_detalle_presupuesto: id_detalle_presupuesto,
                new_servicio_baremo: id_baremo_medico_a_servicio,
            },
            success: function(data) { 
                //const precioventa = data.precio ;
                console.log('data',data )
                if (data.pagado == 1) {
                    Swal.fire({
                        icon: "error",
                        title: "Operacion Negada",
                        text: "Este Medico tiene este item pagado en cuentas por pagar medicos",
                        });
                } else {
                    location.reload()
                }
                
            }
        })

   } else {
        Swal.fire("Debe seleccionar un servicio!");
   }
       
    
}