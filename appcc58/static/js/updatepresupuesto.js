document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        console.log("Evita el prevent")
        event.preventDefault();
    }
});


function eliminarDetalle(idDetalle) {
    const datos = {
      idDetalle: idDetalle,
    };

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/eliminardetallepresupuesto/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      }, 
      body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        console.log('respuesta')
        location.reload()
      // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
    })
    .catch(error => console.error(error));

}

function actualizarCampos() {
    
    idPresupuesto = document.getElementById('presupuestoid').value
    tipoProcedimiento = document.getElementById('tipo').value
    medicoPpal = document.getElementById('medico').value
    diagnostico = document.getElementById('id_diagnostico').value
    procedimiento = document.getElementById('id_procedimiento').value
    fechaProcedimiento = document.getElementById('id_fecha_procedimiento').value
    horaProcedimiento = document.getElementById('id_hora_procedimiento').value
    hospital = document.getElementById('id_hospital').value
    horasQx = document.getElementById('id_horasqx').value

    const datos = {
        idPresupuesto: idPresupuesto,
        tipoProcedimiento: tipoProcedimiento,
        medicoPpal: medicoPpal,
        diagnostico: diagnostico,
        procedimiento: procedimiento,
        fechaProcedimiento: fechaProcedimiento,
        horaProcedimiento: horaProcedimiento,
        hospital: hospital,
        horasQx: horasQx,

      };
  
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
      fetch('/actualizardatospresupuesto/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        }, 
        body: JSON.stringify(datos)
      })
      .then(response => response.json())
      .then(data => {
          console.log('respuesta')
          location.reload()
        // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
      })
      .catch(error => console.error(error));


}


function actualizarCamposHorasqx() {
    idPresupuesto = document.getElementById('presupuestoid').value
    tipoProcedimiento = document.getElementById('tipo').value
    medicoPpal = document.getElementById('medico').value
    diagnostico = document.getElementById('id_diagnostico').value
    procedimiento = document.getElementById('id_procedimiento').value
    fechaProcedimiento = document.getElementById('id_fecha_procedimiento').value
    horaProcedimiento = document.getElementById('id_hora_procedimiento').value
    hospital = document.getElementById('id_hospital').value
    horasQx = document.getElementById('id_horasqx').value

    const datos = {
        idPresupuesto: idPresupuesto,
        tipoProcedimiento: tipoProcedimiento,
        medicoPpal: medicoPpal,
        diagnostico: diagnostico,
        procedimiento: procedimiento,
        fechaProcedimiento: fechaProcedimiento,
        horaProcedimiento: horaProcedimiento,
        hospital: hospital,
        horasQx: horasQx,

      };
  
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
      fetch('/actualizardatospresupuestoHqx/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        }, 
        body: JSON.stringify(datos)
      })
      .then(response => response.json())
      .then(data => {
          console.log('respuesta')
          location.reload()
        // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
      })
      .catch(error => console.error(error));
    
}

function actualizarCampoHospitalizacion() {
    idPresupuesto = document.getElementById('presupuestoid').value
    tipoProcedimiento = document.getElementById('tipo').value
    medicoPpal = document.getElementById('medico').value
    diagnostico = document.getElementById('id_diagnostico').value
    procedimiento = document.getElementById('id_procedimiento').value
    fechaProcedimiento = document.getElementById('id_fecha_procedimiento').value
    horaProcedimiento = document.getElementById('id_hora_procedimiento').value
    hospital = document.getElementById('id_hospital').value
    horasQx = document.getElementById('id_horasqx').value

    const datos = {
        idPresupuesto: idPresupuesto,
        tipoProcedimiento: tipoProcedimiento,
        medicoPpal: medicoPpal,
        diagnostico: diagnostico,
        procedimiento: procedimiento,
        fechaProcedimiento: fechaProcedimiento,
        horaProcedimiento: horaProcedimiento,
        hospital: hospital,
        horasQx: horasQx,

      };
  
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
      fetch('/actualizardatospresupuestoHosp/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        }, 
        body: JSON.stringify(datos)
      })
      .then(response => response.json())
      .then(data => {
          console.log('respuesta')
          location.reload()
        // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
      })
      .catch(error => console.error(error));
    
}

function cambioCantidad(idDetalle, newCantidad) {
    $.ajax({ 
        type: "GET",
        url: "/actualizar_precio_detalle/",  
        data: {
            idDetalle: idDetalle,
            cantidad1: newCantidad,
        },
        success: function(data) { 
            const precioventa = data.precio ;
            console.log('precio nuevo:')
            location.reload()
        }
    })
    
}

function cambioMonto(idDetalle, newPrecio) {
    $.ajax({ 
        type: "GET",
        url: "/actualizar_solo_precio_detalle/",  
        data: {
            idDetalle: idDetalle,
            cantidad1: newPrecio,
        },
        success: function(data) { 
            const precioventa = data.precio ;
            console.log('precio nuevo:')
            location.reload()
        }
    })

}

function agregarBaremo(idBaremo){
  idPresupuesto = document.getElementById('presupuestoid').value

  $.ajax({ 
    type: "GET",
    url: "/agregar_baremo_presupuesto/",  
    data: {
        idBaremo: idBaremo,
        idPresupuesto : idPresupuesto
    },
    success: function(data) { 
        const precioventa = data.precio ;
        console.log('precio nuevo:')
        location.reload()
    }
})

}


  new DataTable('#tblupdatepresupuesto', {
    language: {
            "decimal": "",
            "emptyTable": "No hay datos disponibles en la tabla",
            "info": "Mostrando _START_ a _END_ de _TOTAL_ registros",
            "infoEmpty": "Mostrando 0 a 0 de 0 registros",
            "infoFiltered": "(filtrado de _MAX_ registros totales)",
            "infoPostFix": "",
            "thousands": ",",
            "lengthMenu": "Mostrar _MENU_ registros",
            "loadingRecords": "Cargando...",
            "processing": "Procesando...",
            "search": "Buscar:",
            "zeroRecords": "No se encontraron registros coincidentes",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            },
            "aria": {
                "sortAscending": ": activar para ordenar la columna ascendente",
                "sortDescending": ": activar para ordenar la columna descendente"
            }
        }

  })

  function Descuento(monto, tipo, idDetalle) {
    
    if (typeof monto === 'string') {
        monto = parseFloat(monto.replace(',','.')).toFixed(2)
    } else {
        monto = parseFloat(monto).toFixed(2)
    }

    $.ajax({ 
        type: "GET",
        url: "/actualizar_monto_descuento/",  
        data: {
            idDetalle: idDetalle,
            monto: monto,
            tipo: tipo,
        },
        success: function(data) { 
            const precioventa = data.precio ;
            if (precioventa == 'negado') {
                alert('El monto de descuento no puede ser mayor al precio actual, Revise!')
            } 
            console.log('precio nuevo:')
            location.reload()
        }
    })
    
  }

function DescuentoxTotal(monto, tipo, grupo_id, presupuesto_id) {
    if (typeof monto === 'string') {
        monto = parseFloat(monto.replace(',','.')).toFixed(2)
    } else {
        monto = parseFloat(monto).toFixed(2)
    }
    $.ajax({ 
        type: "GET",
        url: "/actualizar_monto_en_grupo/",  
        data: {
            grupo_id: grupo_id,
            monto: monto,
            tipo: tipo,
            presupuesto_id: presupuesto_id,
        },
        success: function(data) { 
            const precioventa = data.precio ;
            console.log('precio nuevo:')
            location.reload()
        }
    }) 
}
