var table = $('#tblbaremohosp').DataTable({
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
    "order": [[ 0, "desc" ]]
});

function cambiarIcono(td) {
    if (confirm("¿Estás seguro de cambiar el estado?")) {
        var icono = td.querySelector("i");
        if (icono.classList.contains("fa-square-check")) {
            icono.classList.remove("fa-square-check ");
            icono.classList.add("fa-xmark");
            icono.style.color = "#fe0101";
        } else {
            icono.classList.remove("fa-xmark");
            icono.classList.remove("fa-beat");
            icono.classList.add("fa-square-check");
            icono.style.color = "#3a7a29";
        }
    }
    return false;
}



var groupColumn = 2;
var table = $('#tblfarmacos').DataTable({
    columnDefs: [{ visible: true, targets: groupColumn }],
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
                            '<tr class="group"><td colspan="5" style="background-color:red;color:white;">' +
                                group +
                                '</td></tr>'
                        );
 
                    last = group;
                }
            });
    }
});
 
// Order by the grouping
$('#tblfarmacos tbody').on('click', 'tr.group', function () {
    var currentOrder = table.order()[0];
    if (currentOrder[0] === groupColumn && currentOrder[1] === 'asc') {
        table.order([groupColumn, 'desc']).draw();
    }
    else {
        table.order([groupColumn, 'asc']).draw();
    }
});


const id = document.getElementById('iddeCirugia').value.trim() ; //
fetch("/obtener_datos_consumo/"+ id + "/")
    .then(response => response.json())
    .then(data => {
      const tbody = document.getElementById('tbody-tabla-consumo');
      let total = 0;
      data.forEach(dato => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td class="oculto">${dato.id}</td>
          <td>
            ${new Date(dato.fecha_act).toLocaleDateString('es-VE', { day: 'numeric', month: 'short',  year: 'numeric' })}
            </td>
          <td>${dato.inventario__categoria__nombre}</td>
          <td>${dato.inventario__nombre}</td>
          <td>${dato.cantidad_uso}</td>
          <td>${dato.venta}</td>
          <td>${dato.consumo__nombre}</td>
          <td>${dato.hora}</td>
          <td style="text-align: center;">
            <button type="button" class="eliminar"><i class="fa-solid fa-trash"></i></button>
          </td>
        `;
        total += parseFloat(dato.venta);
        row.querySelector('.eliminar').addEventListener('click', () => {
            row.remove();
            total -= parseFloat(dato.venta);
            let total_general = calcularTotalGeneral()
            document.getElementById('total_consumo').innerHTML = total_general.toFixed(2);
          });
        tbody.appendChild(row);
      });
      let total_general = calcularTotalGeneral()
      document.getElementById('total_consumo').innerHTML = total_general.toFixed(2);
    })
    .catch(error => console.error('Error:', error));


// Obtener la tabla del modal
const tblFarmacos = document.getElementById('tblfarmacos');

// Agregar evento dblclick a las filas de la tabla
tblFarmacos.addEventListener('dblclick', (e) => {
    const filaSeleccionada = e.target.closest('tr');
    if (filaSeleccionada) {
        const datosFila = {
        id: filaSeleccionada.cells[0].textContent,
        codigo: filaSeleccionada.cells[1].textContent,
        categoria: filaSeleccionada.cells[2].textContent,
        descripcion: filaSeleccionada.cells[4].textContent,
        lote: filaSeleccionada.cells[5].textContent,
        cantidad: filaSeleccionada.cells[6].children[0] ? filaSeleccionada.cells[6].children[0].value : filaSeleccionada.cells[6].textContent,
        precio: filaSeleccionada.cells[7].textContent,
        presentacion: filaSeleccionada.cells[8].textContent,
        deposito: filaSeleccionada.cells[9].textContent
    };

    // Agregar la fila a la tabla que construiste
    const tbody = document.getElementById('tbody-tabla-consumo');
    const row = document.createElement('tr');
    let precioFila  =  datosFila.precio
    precioFila = precioFila.replace(',','.')
    let subtotalprecio = (parseFloat(precioFila)*datosFila.cantidad).toFixed(2)
    row.innerHTML = `
      <td class="oculto">${datosFila.id}</td>
      <td>${new Date().toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/\s/g, ' ').replace('de', '.').trim()}</td>
      <td>${datosFila.categoria}</td>
      <td>${datosFila.descripcion}</td>
      <td>${datosFila.cantidad}</td>
      <td>${subtotalprecio}</td>
      <td>HOSPITALIZACION</td>
      <td>${new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit', })}</td>
      <td style="text-align: center;">
        <button type="button" class="eliminar"><i class="fa-solid fa-trash"></i></button>
      </td>
    `;
    row.querySelector('.eliminar').addEventListener('click', () => {
        row.remove();
        let total_general = calcularTotalGeneral()
        document.getElementById('total_consumo').innerHTML = total_general.toFixed(2);
      });
    tbody.appendChild(row);

    // Actualizar el total
    let total_general = calcularTotalGeneral()
    document.getElementById('total_consumo').innerHTML = total_general.toFixed(2);
    
    // agregar a la tabla de tratamientos y evolucion
    const tbody_tratamiento = document.getElementById('tbody-evolucion-tratamiento');
    const row_tratamiento = document.createElement('tr');
    row_tratamiento.innerHTML = `
    <td class="oculto">${datosFila.id}</td>
    <td>${new Date().toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/\s/g, ' ').replace('de', '.').trim()} ${new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit', })}</td>
    <td>Sevicio</td>
    <td>${datosFila.descripcion}</td>
    <td>${datosFila.cantidad}</td>
    <td><input type="text" class="form-control form-control-sm fuente" style="width:100%;" value="${datosFila.descripcion}" /></td>
    <td>
      <select id="select-medicos" class="form-select form-select-sm fuente" style="width:100%;">
        <option value="">Seleccione un médico</option>
      </select>
    </td>
    <td> 
     <select id="select-medicos1" class="form-select form-select-sm fuente" style="width:100%;">
        <option value="">Seleccione un médico</option>
      </select>
    </td>
    <td>  <i class="fa-solid fa-xmark fa-beat fa-xl" style="color: #fe0101;"></i> </td>
    <td style="text-align: center;">
      <button type="button" class="eliminar"><i class="fa-solid fa-trash"></i></button>
    </td>
  `;
  tbody_tratamiento.appendChild(row_tratamiento);

  $.ajax({
    type: 'GET',
    url: '/medicos/', // URL de la vista que devuelve la lista de médicos
    dataType: 'json',
    success: function(data) {
      // Pobla el select con los datos recibidos
      $.each(data, function(index, medico) {
        $('#select-medicos').append('<option value="' + medico.id + '">' + medico.nombre + '</option>');
        $('#select-medicos1').append('<option value="' + medico.id + '">' + medico.nombre + '</option>');
      });
    }
  });


    //fin agregar tratamiento


  }
});


function calcularTotalGeneral() {
    let totalGeneral = 0;
    let rows = document.getElementById('tbody-tabla-consumo').rows; // selecciona todas las filas del tbody con id "tbody-tabla-consumo"
  
    for (let i = 0; i < rows.length; i++) {
      let row = rows[i];
      let precioCell = row.cells[5]; // selecciona la celda de la columna precio
      let precioCellText = precioCell.textContent;
      let precio = parseFloat(precioCellText.replace(/,/g, '.'));

      totalGeneral += precio; // suma el valor al total general
    }

    return totalGeneral;
  }


// construir tabla de tratamientos y evolucion medica

const idCirugia = document.getElementById('iddeCirugia').value.trim() ; //
fetch("/obtener_datos_tratamiento/"+ idCirugia + "/")
    .then(response => response.json())
    .then(data => {
      const tbody = document.getElementById('tbody-evolucion-tratamiento');
      data.forEach(dato => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td class="oculto">${dato.id}</td>
          <td>${new Date().toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/\s/g, ' ').replace('de', '.').trim()} ${new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}</td>
          <td>${dato.baremo}</td>
          <td>${dato.inventario__nombre}</td>
          <td>${dato.cantidad_uso}</td>
          <td>${dato.tratamiento}</td>
          <td>${dato.medico_aplicante__nombre}</td>
          <td>${dato.medico_orden__nombre}</td>
          <td>${dato.cumplido ? '  <i class="fa-regular fa-square-check fa-xl" style="color: #3a7a29;"></i>' : '<i class="fa-solid fa-xmark fa-beat fa-xl" style="color: #fe0101;"></i>'}</td>
          <td style="text-align: center;">
            <button type="button" class="eliminar"><i class="fa-solid fa-trash"></i></button>
          </td>
        `;
    
        row.querySelector('.eliminar').addEventListener('click', () => {
            row.remove();

          });
        tbody.appendChild(row);
      });

    })
    .catch(error => console.error('Error:', error));


    function agregarTratamiento() {
     
        // agregar tratamientos solos en el boton no depende de farmacias ni de servicios
        const tbody_tratamiento = document.getElementById('tbody-evolucion-tratamiento');
        const row_tratamiento = document.createElement('tr');
        row_tratamiento.innerHTML = `
        <td class="oculto">New</td>
        <td>${new Date().toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' }).replace(/\s/g, ' ').replace('de', '.').trim()} ${new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit', })}</td>
        <td>Sevicio</td>
        <td>Farmacia</td>
        <td>1</td>
        <td><input type="text" class="form-control form-control-sm fuente" style="width:100%;" value="Describa la accion a realizar..." /></td>
        <td>
        <select id="select-medicos" class="form-select form-select-sm fuente" style="width:100%;">
            <option value="">Seleccione un médico</option>
        </select>
        </td>
        <td> 
        <select id="select-medicos1" class="form-select form-select-sm fuente" style="width:100%;">
            <option value="">Seleccione un médico</option>
        </select>
        </td>
        <td>  <i class="fa-solid fa-xmark fa-beat fa-xl" style="color: #fe0101;"></i> </td>
        <td style="text-align: center;">
        <button type="button" class="eliminar"><i class="fa-solid fa-trash"></i></button>
        </td>
    `;
    tbody_tratamiento.appendChild(row_tratamiento);

    $.ajax({
        type: 'GET',
        url: '/medicos/', // URL de la vista que devuelve la lista de médicos
        dataType: 'json',
        success: function(data) {
        // Pobla el select con los datos recibidos
        $.each(data, function(index, medico) {
            $('#select-medicos').append('<option value="' + medico.id + '">' + medico.nombre + '</option>');
            $('#select-medicos1').append('<option value="' + medico.id + '">' + medico.nombre + '</option>');
        });
       
        }
    });
}


    // fin
