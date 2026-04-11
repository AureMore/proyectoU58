  var table = $('#tbldepositoprecarga').DataTable({
    pageLength : 10,
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

function notaTablapreCarga(idCirugia) {
    document.getElementById('id_cirugia').value = idCirugia
    console.log('inicio de refresh')
    //pendiente aca queda , continue luego del supermarket
    $.ajax({
        type: 'GET',
        url: '/obtener_consumoPrecarga/' + '?idCirugia=' + idCirugia,
        dataType: 'html',
        success: function(data) {
            $('#tbl-precarga-admision').html(data);
            console.log('refresco')
            console.log('inicio de refresh')
            //var cantidad_precarga_obligatoria = document.getElementById('id_precarga').value 
            //cantidad_precarga_obligatoria = cantidad_precarga_obligatoria.replace(',','.')
            /* var checkbox = document.getElementById("producto_obligatorio");
            if (cantidad_precarga_obligatoria > 0) {
                // Marca el checkbox
                checkbox.checked = true; // Para marcarlo
            } else {
                checkbox.checked = false; // Para marcarlo
            } */
        }
    });
   
    //$('#modalInventario').modal('show')
}

function refreshTablaPrecarga(idCirugia) {
    console.log('Llegando a la nueva función');
    
    return new Promise((resolve, reject) => {
        $.ajax({
            type: 'GET',
            url: '/obtener_consumoPrecarga/' + '?idCirugia=' + idCirugia,
            dataType: 'json',
            success: function(response) {
                // Actualizar el HTML de la tabla
                $('#tbl-precarga-admision').html(response.html);
                console.log('Nuevo js function');
                resolve(); // Resolvemos la promesa cuando la llamada es exitosa
            },
            error: function(xhr, status, error) {
                console.error('Error en la llamada AJAX:', error);
                reject(error); // Rechazamos la promesa en caso de error
            }
        });
    });
}


function refreshTablaDisponiblePrecarga(idCirugia) {
    console.log('Llegando a la nueva función refrescar solo a disponible');
    $('#staticBackdrop').modal('show');
    return new Promise((resolve, reject) => {
        $.ajax({
            type: 'GET',
            url: '/obtener_disponible_precarga/' + '?idCirugia=' + idCirugia,
            dataType: 'json',
            success: function(response) {
                // Actualizar el HTML de la tabla
                $('#tbl-precarga-disponible').html(response.html);
                resolve(); // Resolvemos la promesa cuando la llamada es exitosa
            },
            error: function(xhr, status, error) {
                console.error('Error en la llamada AJAX:', error);
                reject(error); // Rechazamos la promesa en caso de error
            }
        });
    });
}



function activarModalInventario(idCirugia) {
    document.getElementById('id_cirugia').value = idCirugia
     refreshTablaPrecarga(idCirugia).then(() => {
        $('#modalInventario').modal('show');
    }).catch((error) => {
        console.error('Error al refrescar la tabla:', error);
    });
    
}

function eliminar_Precarga(idConsumoprecarga) {
    idCirugia = document.getElementById('id_cirugia').value
    $.ajax({
        type: 'GET',
        url: '/eliminar_Precarga/' + '?idConsumoprecarga=' + idConsumoprecarga,
        dataType: 'html',
        success: function(data) {
           refreshTablaPrecarga(idCirugia)
           refreshTablaDisponiblePrecarga(idCirugia)
                .then(function() {
                    // Ocultar el modal después de que la tabla se haya actualizado
                    $('#staticBackdrop').modal('hide');
                })
                .catch(function(error) {
                    // Manejo de errores si es necesario
                    console.error('Error al refrescar la tabla:', error);
                })
           
        }
    });

}

function guardaCantReal(nCant, idDepositoUso, nCantExistencia) {
     nCantExistencia = parseFloat(nCantExistencia.replace(',','.'))
     const idCirugia_precarga_admicion = document.getElementById('id_cirugia').value
    console.log('muestro:'+idCirugia_precarga_admicion) 
     nCant = parseFloat(nCant.replace(',','.'))
    if (nCant > nCantExistencia ) {
        alert('Asignacion no puede ser mayor a la existencia')
        return
    } else {
        const datos = {
            nCant: nCant,
            idDepositoUso: idDepositoUso,
            idCirugia: idCirugia_precarga_admicion
            
            };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/aplicar_precarga_cirugia/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }, 
        body: JSON.stringify(datos)
        })
        .then(response => response.json())
        .then(data => {
            refreshTablaPrecarga(idCirugia_precarga_admicion)
            refreshTablaDisponiblePrecarga(idCirugia_precarga_admicion)
                .then(function() {
                    // Ocultar el modal después de que la tabla se haya actualizado
                    $('#staticBackdrop').modal('hide');
                })
                .catch(function(error) {
                    // Manejo de errores si es necesario
                    console.error('Error al refrescar la tabla:', error);
                })
            console.log('aplicar precarga')
        //refreshTable()
        //$('#modalInventario').modal('hide')
        // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
        })
        .catch(error => console.error(error));
    }

}

function rebajarPrecargaDeposito() {
    idCirugia = document.getElementById('id_cirugia').value

    console.log(idCirugia)
    const datos = {
         idCirugia: idCirugia
      
      };
      
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
      fetch('/rebajarPrecargaDeposito/', {
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
        location.reload()
        // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
      })
      .catch(error => console.error(error));


}

