function cambioUci(idCirugia) {
    Swal.fire({
        title: "Cambio de paciente a UCI",
        text: "Desea Continuar?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Si, Continuar!"
      }).then((result) => {
        if (result.isConfirmed) {
            const datos = {
                idCirugia: idCirugia,
              };
            
              const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
              fetch('/change_uci/', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': csrftoken
                }, 
                body: JSON.stringify(datos)
              })
              .then(response => response.json())
              .then(data => {
                console.log(data.mensaje)
                if (data.mensaje == 'UnautorizedUser') {
                  Swal.fire({
                    icon: "error",
                    title: "No posee autorizacion para realizar esta accion...",
                    text: "para autorizacion dirigirse al Dr. Agustin Gutierrez",
                  });
                } else {
                  window.location.href = `/atencion_uci/${idCirugia}/`;
                }
                //
                // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
              })
              .catch(error => console.error(error));
        }
      });
}

function muestraTablaDisponibleFarmacia(idAtencion) {

  document.getElementById('atencion-inmediata-id').value = idAtencion
  let depositoId = document.getElementById('deposito-id').value
  if (depositoId == '') {
      alert('Seleccionar Deposito de Medicamentos')
      
  } else {
      $.ajax({
          type: 'GET',
          url: '/refresh_table_disponible_deposito/' + '?depositoId=' + depositoId,
          dataType: 'html',
          success: function(data) {
              $('#tabla-atencion-inmediata-deposito-disponible').html(data);
          }
      }); 

      $('#farmaciaModalHosp').modal('show')
  }
}

function agregarConsumoCirugia(inventario_id,cantidad_aplicar) {
  let idCirugia = document.getElementById('id_historia_medica').value
  let depositoId = document.getElementById('deposito-id').value
  const datos = {
      inventario_id : inventario_id,
      cantidad_aplicar : cantidad_aplicar,
      idCirugia : idCirugia,
      depositoId : depositoId,

    };
  
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
  fetch('/agregar_a_consumo_cirugia_uci/', {
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
      //document.getElementById('personal-id').value = ''
      refreshTablaConsumoCirugia(idCirugia)
    })
    .catch(error => console.error(error));

 
}

function refreshTablaConsumoCirugia(idCirugia) {
  $.ajax({
      type: 'GET',
      url: '/refresh_table_consumo_cirugia_uci/' + '?idCirugia=' + idCirugia,
      dataType: 'json',
      success: function(response) {
          // Actualizar el HTML de la tabla
          $('#tabla-consumo-farmacia-atencion').html(response.html);
          // Leer el valor de total_subtotal
          var totalSubtotal = response.total_subtotal_farmacia;
          if (totalSubtotal == '' || totalSubtotal == null) {
              totalSubtotal = 0
          }
         
          totalSubtotal = parseFloat(totalSubtotal).toFixed(2)
          document.getElementById('subtotal-farmacia').textContent = totalSubtotal 
          colocar_total()
      }


  }); 
}

function colocar_total() {
  let subtotal_baremo = document.getElementById('subtotal-value').textContent
  let subtotal_farmacia = document.getElementById('subtotal-farmacia').textContent
  subtotal_baremo = subtotal_baremo.replace(',','.')
  subtotal_farmacia = subtotal_farmacia.replace(',','.')
 
  if ( subtotal_baremo == '' || subtotal_baremo == null ) {
      subtotal_baremo = 0
  }
  if ( subtotal_farmacia == '' || subtotal_farmacia == null) {
      subtotal_farmacia = 0
  }
  
  
  subtotal_farmacia = parseFloat(subtotal_farmacia).toFixed(2)
  subtotal_baremo = parseFloat(subtotal_baremo).toFixed(2)
  let total_control= parseFloat(subtotal_farmacia) +  parseFloat(subtotal_baremo)
  total_control = parseFloat(total_control).toFixed(2)
  document.getElementById('total_control_costos').textContent = total_control
  
}

function eliminarConsumo(consumo_id) {
  let idCirugia = document.getElementById('id_historia_medica').value
  const datos = {
      consumo_id : consumo_id,
    };
  
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
  fetch('/eliminar_consumo_cirugia_atencionmedica/', {
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
      refreshTablaConsumoCirugia(idCirugia)
    })
    .catch(error => console.error(error));

}

function muestraBaremo() {
  
      $('#modalBaremoAtencion').modal('show')
}

function agregarBaremoAtencion(idBaremo) {
  let idCirugia = document.getElementById('id_historia_medica').value
  let idMedico = document.getElementById('medico_id').value
  let idPaciente = document.getElementById('idPaciente').value
  const datos = {
      idBaremo : idBaremo,
      idCirugia : idCirugia,
      idMedico : idMedico,
      idPaciente : idPaciente,
      
    };
  
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
  fetch('/agregar_presupuesto_uci/', {
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
      refreshTablaPresupuestoUci(idCirugia)
    })
    .catch(error => console.error(error));
  
}

function refreshTablaPresupuestoUci(idCirugia) {
  $.ajax({
      type: 'GET',
      url: '/refresh_table_baremo_uci/' + '?idCirugia=' + idCirugia,
      dataType: 'json', // Cambiar a 'json'
      success: function(response) {
          // Actualizar el HTML de la tabla
          $('#tabla-baremo-atencion').html(response.html);
          
          // Leer el valor de total_subtotal
          var totalSubtotal = response.total_subtotal;
          if ( totalSubtotal == '' || totalSubtotal == null) {
              totalSubtotal = 0
          } 
          if (typeof totalSubtotal == 'string') {
            // Si no es una cadena, convertir a cadena
            totalSubtotal = totalSubtotal.replace(',','.');
          }

          
          totalSubtotal = parseFloat(totalSubtotal).toFixed(2)
          document.getElementById('subtotal-value').textContent = totalSubtotal 
          colocar_total()

      }
  }); 
  
}


function nuevacantidad(ncantidad, idDetallepresupuesto,vCampo) {
  let idCirugia = document.getElementById('id_historia_medica').value
  const datos = {
      ncantidad : ncantidad,
      idDetallepresupuesto : idDetallepresupuesto,
      vCampo : vCampo,
      cirugia_id : idCirugia
    };
  
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
  fetch('/cambiar_precio_baremo_uci/', {
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
      refreshTablaPresupuestoUci(idCirugia)
    })
    .catch(error => console.error(error));

}

function mostrarMedicos(idDetallepresupuesto, varTitulo) {
  document.getElementById('id_detalle_presupuesto').value = idDetallepresupuesto
  var modalTitle = document.getElementById('modalPersonalMedicoLabel');
  modalTitle.innerText = 'Asignar el '+ varTitulo;
  $('#modalPersonalMedico').modal('show')
}

function asignarMedico(idMedico) {
  document.getElementById('medico-id').value = idMedico
  
}

function asignarMedicoPresupuesto() {
  let medico_id = document.getElementById('medico-id').value
  let id_detalle = document.getElementById('id_detalle_presupuesto').value 
  let idCirugia = document.getElementById('id_historia_medica').value
  const datos = {
      medico_id : medico_id,
      id_detalle : id_detalle,
      idCirugia : idCirugia,
    };
  
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
  fetch('/actualizar_medico_detalle_presupuesto_uci/', {
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
      refreshTablaPresupuestoUci(idCirugia)
    })
    .catch(error => console.error(error));


  
}

function eliminarDetallePresupuesto(idDetallepresupuesto) {
  let idCirugia = document.getElementById('id_historia_medica').value
  const datos = {
      idDetallepresupuesto : idDetallepresupuesto,
    };
  
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
  fetch('/eliminar_detallebaremo_atencionmedica/', {
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
      refreshTablaPresupuestoUci(idCirugia)
    })
    .catch(error => console.error(error));

  
}

function muestraTratamiento() {
      $('#tratamientoModal').modal('show')
}

function guardarTratamiento() {
  let cantidad = document.getElementById('cantidad_tratamiento').value
  let idCirugia = document.getElementById('id_historia_medica').value
  let comentarios_tratamiento = document.getElementById('comentarios_tratamiento').value
  const datos = {
      cantidad : cantidad,
      idCirugia : idCirugia,
      comentarios_tratamiento : comentarios_tratamiento,
    };
  
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
  fetch('/agregar_tratamiento_uci/', {
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
      refreshTratamientoUci(idCirugia)
    })
    .catch(error => console.error(error));
}

function refreshTratamientoUci(idCirugia) {
  $.ajax({
      type: 'GET',
      url: '/refresh_table_tratamiento_uci/' + '?idCirugia=' + idCirugia,
      dataType: 'html',
      success: function(data) {
          $('#tabla-tratamiento-aplicado').html(data);
      }
  }); 
}

function eliminarTratamientoAtencion(idTratamiento) {
  let idCirugia = document.getElementById('id_historia_medica').value
  const datos = {
      idTratamiento : idTratamiento,
    };
  
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
  fetch('/eliminar_tratamiento_atencionmedica/', {
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
      refreshTratamientoUci(idCirugia)
    })
    .catch(error => console.error(error));

}




//datatable de baremos agrupado

var groupColumn = 0;
var table = $('#tblbaremoatencion').DataTable({
    columnDefs: [{ visible: false, targets: groupColumn }],
    order: [[groupColumn, 'asc']],
    displayLength: 25,
    language: {
        "processing": "Procesando...",
        "lengthMenu": "Mostrar _MENU_ registros",
        "zeroRecords": "No se encontraron resultados",
        "emptyTable": "Ningún dato disponible en esta tabla",
        "infoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
        "infoFiltered": "(filtrado de un total de _MAX_ registros)",
        "search": "Buscar:",
        "loadingRecords": "Cargando...",
        "paginate": {
            "first": "Primero",
            "last": "Último",
            "next": "Siguiente",
            "previous": "Anterior"
        },
        "aria": {
            "sortAscending": ": Activar para ordenar la columna de manera ascendente",
            "sortDescending": ": Activar para ordenar la columna de manera descendente"
        },
        "buttons": {
            "copy": "Copiar",
            "colvis": "Visibilidad",
            "collection": "Colección",
            "colvisRestore": "Restaurar visibilidad",
            "copyKeys": "Presione ctrl o u2318 + C para copiar los datos de la tabla al portapapeles del sistema. <br \/> <br \/> Para cancelar, haga clic en este mensaje o presione escape.",
            "copySuccess": {
                "1": "Copiada 1 fila al portapapeles",
                "_": "Copiadas %ds fila al portapapeles"
            },
            "copyTitle": "Copiar al portapapeles",
            "csv": "CSV",
            "excel": "Excel",
            "pageLength": {
                "-1": "Mostrar todas las filas",
                "_": "Mostrar %d filas"
            },
            "pdf": "PDF",
            "print": "Imprimir",
            "renameState": "Cambiar nombre",
            "updateState": "Actualizar",
            "createState": "Crear Estado",
            "removeAllStates": "Remover Estados",
            "removeState": "Remover",
            "savedStates": "Estados Guardados",
            "stateRestore": "Estado %d"
        },
        "autoFill": {
            "cancel": "Cancelar",
            "fill": "Rellene todas las celdas con <i>%d<\/i>",
            "fillHorizontal": "Rellenar celdas horizontalmente",
            "fillVertical": "Rellenar celdas verticalmente"
        },
        "decimal": ",",
        "searchBuilder": {
            "add": "Añadir condición",
            "button": {
                "0": "Constructor de búsqueda",
                "_": "Constructor de búsqueda (%d)"
            },
            "clearAll": "Borrar todo",
            "condition": "Condición",
            "conditions": {
                "date": {
                    "before": "Antes",
                    "between": "Entre",
                    "empty": "Vacío",
                    "equals": "Igual a",
                    "notBetween": "No entre",
                    "not": "Diferente de",
                    "after": "Después",
                    "notEmpty": "No Vacío"
                },
                "number": {
                    "between": "Entre",
                    "equals": "Igual a",
                    "gt": "Mayor a",
                    "gte": "Mayor o igual a",
                    "lt": "Menor que",
                    "lte": "Menor o igual que",
                    "notBetween": "No entre",
                    "notEmpty": "No vacío",
                    "not": "Diferente de",
                    "empty": "Vacío"
                },
                "string": {
                    "contains": "Contiene",
                    "empty": "Vacío",
                    "endsWith": "Termina en",
                    "equals": "Igual a",
                    "startsWith": "Empieza con",
                    "not": "Diferente de",
                    "notContains": "No Contiene",
                    "notStartsWith": "No empieza con",
                    "notEndsWith": "No termina con",
                    "notEmpty": "No Vacío"
                },
                "array": {
                    "not": "Diferente de",
                    "equals": "Igual",
                    "empty": "Vacío",
                    "contains": "Contiene",
                    "notEmpty": "No Vacío",
                    "without": "Sin"
                }
            },
            "data": "Data",
            "deleteTitle": "Eliminar regla de filtrado",
            "leftTitle": "Criterios anulados",
            "logicAnd": "Y",
            "logicOr": "O",
            "rightTitle": "Criterios de sangría",
            "title": {
                "0": "Constructor de búsqueda",
                "_": "Constructor de búsqueda (%d)"
            },
            "value": "Valor"
        },
        "searchPanes": {
            "clearMessage": "Borrar todo",
            "collapse": {
                "0": "Paneles de búsqueda",
                "_": "Paneles de búsqueda (%d)"
            },
            "count": "{total}",
            "countFiltered": "{shown} ({total})",
            "emptyPanes": "Sin paneles de búsqueda",
            "loadMessage": "Cargando paneles de búsqueda",
            "title": "Filtros Activos - %d",
            "showMessage": "Mostrar Todo",
            "collapseMessage": "Colapsar Todo"
        },
        "select": {
            "cells": {
                "1": "1 celda seleccionada",
                "_": "%d celdas seleccionadas"
            },
            "columns": {
                "1": "1 columna seleccionada",
                "_": "%d columnas seleccionadas"
            },
            "rows": {
                "1": "1 fila seleccionada",
                "_": "%d filas seleccionadas"
            }
        },
        "thousands": ".",
        "datetime": {
            "previous": "Anterior",
            "hours": "Horas",
            "minutes": "Minutos",
            "seconds": "Segundos",
            "unknown": "-",
            "amPm": [
                "AM",
                "PM"
            ],
            "months": {
                "0": "Enero",
                "1": "Febrero",
                "10": "Noviembre",
                "11": "Diciembre",
                "2": "Marzo",
                "3": "Abril",
                "4": "Mayo",
                "5": "Junio",
                "6": "Julio",
                "7": "Agosto",
                "8": "Septiembre",
                "9": "Octubre"
            },
            "weekdays": {
                "0": "Dom",
                "1": "Lun",
                "2": "Mar",
                "4": "Jue",
                "5": "Vie",
                "3": "Mié",
                "6": "Sáb"
            },
            "next": "Próximo"
        },
        "editor": {
            "close": "Cerrar",
            "create": {
                "button": "Nuevo",
                "title": "Crear Nuevo Registro",
                "submit": "Crear"
            },
            "edit": {
                "button": "Editar",
                "title": "Editar Registro",
                "submit": "Actualizar"
            },
            "remove": {
                "button": "Eliminar",
                "title": "Eliminar Registro",
                "submit": "Eliminar",
                "confirm": {
                    "_": "¿Está seguro de que desea eliminar %d filas?",
                    "1": "¿Está seguro de que desea eliminar 1 fila?"
                }
            },
            "error": {
                "system": "Ha ocurrido un error en el sistema (<a target=\"\\\" rel=\"\\ nofollow\" href=\"\\\">Más información&lt;\\\/a&gt;).<\/a>"
            },
            "multi": {
                "title": "Múltiples Valores",
                "restore": "Deshacer Cambios",
                "noMulti": "Este registro puede ser editado individualmente, pero no como parte de un grupo.",
                "info": "Los elementos seleccionados contienen diferentes valores para este registro. Para editar y establecer todos los elementos de este registro con el mismo valor, haga clic o pulse aquí, de lo contrario conservarán sus valores individuales."
            }
        },
        "info": "Mostrando _START_ a _END_ de _TOTAL_ registros",
        "stateRestore": {
            "creationModal": {
                "button": "Crear",
                "name": "Nombre:",
                "order": "Clasificación",
                "paging": "Paginación",
                "select": "Seleccionar",
                "columns": {
                    "search": "Búsqueda de Columna",
                    "visible": "Visibilidad de Columna"
                },
                "title": "Crear Nuevo Estado",
                "toggleLabel": "Incluir:",
                "scroller": "Posición de desplazamiento",
                "search": "Búsqueda",
                "searchBuilder": "Búsqueda avanzada"
            },
            "removeJoiner": "y",
            "removeSubmit": "Eliminar",
            "renameButton": "Cambiar Nombre",
            "duplicateError": "Ya existe un Estado con este nombre.",
            "emptyStates": "No hay Estados guardados",
            "removeTitle": "Remover Estado",
            "renameTitle": "Cambiar Nombre Estado",
            "emptyError": "El nombre no puede estar vacío.",
            "removeConfirm": "¿Seguro que quiere eliminar %s?",
            "removeError": "Error al eliminar el Estado",
            "renameLabel": "Nuevo nombre para %s:"
        },
        "infoThousands": "."
    },
    drawCallback: function (settings) {
        var api = this.api();
        var rows = api.rows({ page: 'current' }).nodes();
        var last = null;
 
        api.column(groupColumn, { page: 'current' })
            .data()
            .each(function (group, i) {
                if (last !== group) {
                    $(rows)
                        .eq(i)
                        .before(
                            '<tr class="group resaltar"><td colspan="5">' +
                                group +
                                '</td></tr>'
                        );
 
                    last = group;
                }
            });
    }
});



