var table = $('#tblfarmacos-hospital').DataTable({
    displayLength: 10,
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
})



function guardarTratamiento() {
    idCirugia = document.getElementById('iddeCirugia').value
    tratamiento = document.getElementById('comentarios_tratamiento').value
    const datosTra = {
        idCirugia: idCirugia,
        tratamiento: tratamiento,
    }

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch('/guardar_tratamiento_medico/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datosTra)
        })
        
        .then(response => response.json())
        .then(data => {
            console.log(data.mensaje);
            location.reload(); // Recargar la página manualmente
        })
        .catch(error => console.error('Error:', error));

}

function eliminarTratamiento(idEliminar) {
    const datosEli = {
        idEliminar: idEliminar,

    }

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch('/eliminar_tratamiento/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datosEli)
        })
        
        .then(response => response.json())
        .then(data => {
            console.log(data.mensaje);
            location.reload(); // Recargar la página manualmente
        })
        .catch(error => console.error('Error:', error));


 }


 function modificarTratamiento(idtratamiento, descripcion) {
    document.getElementById('comentarios_tratamiento_mod').value = descripcion
    document.getElementById('id_tratamiento_mod').value = idtratamiento
    
    $('#tratamientoModModal').modal('show');
     
  }
 
  function updateTratamiento() {
     var tratamiento = document.getElementById('comentarios_tratamiento_mod').value
     const idTratamiento = document.getElementById('id_tratamiento_mod').value
     const datosUpt = {
         idTratamiento: idTratamiento,
         tratamiento: tratamiento,
     }
 
     const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
         fetch('/update_tratamiento/', {
             method: 'POST',
             headers: {
                 'Content-Type': 'application/json',
                 'X-CSRFToken': csrftoken
             },
             body: JSON.stringify(datosUpt)
         })
         
         .then(response => response.json())
         .then(data => {
             console.log(data.mensaje);
             location.reload(); // Recargar la página manualmente
         })
         .catch(error => console.error('Error:', error));
  }


  const tblFarmacoHosp = document.getElementById('tblfarmacos-hospital');
  idCirugia = document.getElementById('iddeCirugia').value
  tipoProcedimiento = document.getElementById('idtipoProcedimiento')

  // Agregar evento dblclick a las filas de la tabla
  tblFarmacoHosp.addEventListener('dblclick', (e) => {
    idtopecantidadmedicina = document.getElementById('idlimite').value
    idintervalohoras = document.getElementById('id-horas').value
    fechayhorainicio = document.getElementById('fecha-asignacion-id').value
      const filaSeleccion = e.target.closest('tr');
      if (filaSeleccion) {
          const datosSel = {
              tipoProcedimiento:tipoProcedimiento,
              idCirugia: idCirugia,
              fechayhorainicio:fechayhorainicio,
              idintervalohoras: idintervalohoras,
              idtopecantidadmedicina:idtopecantidadmedicina,
              id: filaSeleccion.cells[0].textContent,
              codigo: filaSeleccion.cells[1].textContent,
              categoria: filaSeleccion.cells[2].textContent,
              descripcion: filaSeleccion.cells[4].textContent,
              lote: filaSeleccion.cells[5].textContent,
              cantidad: filaSeleccion.cells[6].children[0] ? filaSeleccion.cells[6].children[0].value : filaSeleccion.cells[6].textContent,
              precio: filaSeleccion.cells[7].textContent,
              presentacion: filaSeleccion.cells[8].textContent,
              deposito: filaSeleccion.cells[9].textContent,
              existencia: filaSeleccion.cells[11].textContent
           };
           if (parseFloat(datosSel.cantidad) > parseFloat(datosSel.existencia.replace(',','.'))) {
                alert('Cantidad asignar es mayor a lo disponible en deposito, intente otra cantidad')
                return
           }

          const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
          fetch('/guardar_farmaco_hospital_medico/', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': csrftoken
              },
              body: JSON.stringify(datosSel)
          })
          
          .then(response => response.json())
          .then(data => {
              console.log(data.mensaje);
              location.reload(); // Recargar la página manualmente
          })
          .catch(error => console.error('Error:', error));
          
           
      }
  
  })


document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        console.log("Evita el prevent")
        event.preventDefault();
    }
});


