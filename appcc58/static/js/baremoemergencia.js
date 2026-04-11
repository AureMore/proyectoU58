var groupColumn = 3;
var table = $('#mitablaBaremo').DataTable({
    columnDefs: [{ visible: false, targets: groupColumn }],
    order: [[groupColumn, 'asc']],
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
    displayLength: 10,
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
                            '<tr class="group"><td colspan="5">' +
                                group +
                                '</td></tr>'
                        );
 
                    last = group;
                }
            });
    }
});


$(document).ready(function() {
    $('#mitablaBaremo').on('dblclick', 'tbody tr', function() {
      // Obtener la fila seleccionada
      var fila = $(this);
      // Agregar la fila a la tabla destino
      agregarBaremoSeleccionado(fila);
    });
});


var filaContador = 0;
function agregarBaremoSeleccionado(fila) {
    // Clonar la fila seleccionada
    var filaClonada = fila.clone();
    var idBaremo = fila.find('td:nth-child(1)').text();
    var descripcion = fila.find('td:nth-child(2)').text();
    var medico = fila.find('td:nth-child(3)').text();
    var Ntqx = fila.find('td:nth-child(4)').text();
    var horaActual = new Date().toLocaleTimeString();

    var nuevaFila = $('<tr>'); // Crea un nuevo elemento <tr>

    nuevaFila.append($('<td>').text(idBaremo)); // Agrega una celda con el valor de idBaremo
    nuevaFila.append($('<td>').text(descripcion)); // Agrega una celda con el valor de descripcion
    nuevaFila.append($('<td>').text(Ntqx));
    if (Ntqx=='True') {
    // select de medicos
        filaContador += 1
        var selectmedicoId = 'medico-select-' + filaContador;
        var selectmedico = $('<td><select id="' + selectmedicoId + '"><option value="">Seleccione un medico</option></select></td>');
        nuevaFila.append(selectmedico);
        if (!medico) {
            $('#' + selectmedicoId).append($('<option>').text('Seleccione un medico').attr('disabled', true).attr('selected', true));
        }

        // Hacer solicitud AJAX para obtener la lista de convenios
            $.ajax({
                type: 'GET',
                url: '/obtener_medicos/',
                dataType: 'json',
                success: function(data) {
                    $.each(data, function(index, medico) {
                        $('#' + selectmedicoId).append($('<option>').text(medico.nombre).val(medico.id));
                    });
                
                }
            });
    } else {
        nuevaFila.append($('<td>').text(medico));
    }
    // fin select de medicos

    nuevaFila.append($('<td>').text(horaActual)); // Agrega una celda con el valor de horaActual
    var botonEliminar = $('<td><button type="button" class="eliminar" style="border:none;" ><i class="fa-solid fa-trash fa-lg text-danger"></i></button></td>');
    nuevaFila.append(botonEliminar);
    
    $('#baremo-seleccionado').append(nuevaFila); // Agrega la nueva fila a la tabla con id "miTabla"

  }

  $(document).on('click', '.eliminar', function() {
    $(this).closest('tr').remove();

  });


function agregarPlantilla(idPlantilla) {
    if (idPlantilla != '') {
            // Obtener parámetros de filtro desde los campos de formulario
            var idconvenio = document.getElementById('idconvenio').value;
            // Realizar solicitud AJAX a la vista de Django con parámetros
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/filtrar_plantilla/?idconvenio='+idconvenio+'&idPlantilla='+idPlantilla , true);
            xhr.onload = function() {
                if (this.status === 200) {
                    var datos = JSON.parse(this.responseText);
                    var tbody = document.getElementById('baremo-seleccionado');
                    tbody.innerHTML = '';
                    var horaActual = new Date().toLocaleTimeString();
                    let medicos = [];
                    fetch('/obtener_medicos/')
                        .then(response => response.json())
                        .then(data => {
                            const medicos = data;
                            // Aquí puedes utilizar la variable medicos para crear el select
                            datos.forEach(function(item) {
                                var row = document.createElement('tr');
                                row.innerHTML = `
                                    <td>${item[0]}</td>
                                    <td>${item[1]}</td>
                                    <td>${item[2]}</td>
                                    <td>
                                    ${item[2] ? 
                                        `<select id="medico-select">
                                          <option value="">Seleccione un médico</option>
                                          ${medicos.map(medico => `<option value="${medico.id}">${medico.nombre}</option>`).join('')}
                                        </select>` 
                                        : item[3]}
                                    </td>
                                    <td>${horaActual}</td>
                                    <td>${'<button type="button" class="eliminar" style="border:none;" ><i class="fa-solid fa-trash fa-lg text-danger"></i></button>'}</td>
                                `;
                                tbody.appendChild(row);
                            });
                });
                    $(document).on('click', '.eliminar', function() {
                        $(this).closest('tr').remove();
                    
                      });
                    
                }
            };
            xhr.send();
    }
}

 
