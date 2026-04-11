var groupColumn = 2;
var table = $('#tblbaremo').DataTable({
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
    columnDefs: [{ visible: false, targets: groupColumn }],
    order: [[groupColumn, 'asc']],
    displayLength: 25,
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
    },

    initComplete: function () {
        this.api()
            .columns()
            .every(function () {
                let column = this;
                let columnIndex = column.index(); 
               
                
                // Create select element
                let select = document.createElement('select');
                select.classList.add('select-filtros'); // Agrega la clase 'mi-clase'
                select.add(new Option(''));
                let th = column.header();
                th.appendChild(select);

                
                // Apply listener for user change in value
                select.addEventListener('change', function () {
                    column
                        .search(select.value, {exact: true})
                        .draw();
                });
 
                // Add list of options
                column
                    .data()
                    .unique()
                    .sort()
                    .each(function (d, j) {
                        select.add(new Option(d));
                    });
            });
    }
});


// Order by the grouping
$('#tblbaremo tbody').on('click', 'tr.group', function () {
    var currentOrder = table.order()[0];
    if (currentOrder[0] === groupColumn && currentOrder[1] === 'asc') {
        table.order([groupColumn, 'desc']).draw();
    }
    else {
        table.order([groupColumn, 'asc']).draw();
    }
});

// script para generar los item en el html principal dinamicamente
// Seleccionar todas las filas de la tabla modal
const filasModal = document.querySelectorAll('#tblbaremo tbody tr');

// Agregar evento de doble clic a cada fila
filasModal.forEach((fila) => {
  fila.addEventListener('dblclick', (e) => {
    // Obtener los datos de la fila seleccionada
    const datosFila = {
      id_baremo: fila.cells[0].textContent,
      convenio: fila.cells[1].textContent,
      detalle: fila.cells[2].textContent,
      cantidad: fila.cells[3].textContent,
      precio: fila.cells[4].textContent,
      unidad: fila.cells[5].textContent,
      convenio_id: fila.cells[6].textContent,
      grupo_id: fila.cells[7].textContent,
      detalle_id: fila.cells[8].textContent,
    };

    // Llamar a la función que genera la tabla dinámicamente
    generarTablaDinamica(datosFila);
  });
});
 

function generarTablaDinamica(datosFila) {

    // Seleccionar la tabla existente en el HTML principal
    const tabla = document.getElementById('tblplantilla');
  
    // Seleccionar el tbody existente
    const tbody = tabla.querySelector('tbody');
  
    // Agregar fila al tbody con los datos seleccionados
    const fila = document.createElement('tr');
    fila.style.fontSize = '8pt';
    fila.style.color = '#FF0000';
    const celda0 = document.createElement('td');
    const celda6 = document.createElement('td');
    celda6.textContent = datosFila.convenio
    celda0.textContent = datosFila.id_baremo;
    const celda1 = document.createElement('td');
    celda1.style.color = '#FF0000';
    celda1.textContent = datosFila.detalle;
    const celda2 = document.createElement('td');
    const input = document.createElement('input');
    const celda3 = document.createElement('td');
    const input2 = document.createElement('input');
    input2.style.textAlign = 'right';
    input2.type='text';
    input2.name = 'baremo_fila';
    input.type = 'number';
    input.step = '1'
    input.name = 'baremo_fila'
    input2.classList.add('precio-venta');
    let c=0
    input.value = datosFila.cantidad.replace(',','.');
        // Agrega el evento de cambio para determinar cuando cambie la cantidad
        input.addEventListener('change', function() {
            const cantidad = input.value;
            const idBaremo = datosFila.id_baremo;
            const idBaremo1 = idBaremo.trim();
            const cantidad1 = cantidad.trim();
            // nueva funcion para cambiar precio
            $.ajax({
                type: "GET",
                url: "/actualizar-precio/",
                data: {
                    idBaremo1: idBaremo1,
                    cantidad1: cantidad1,
                },
                success: function(data) {
                    const data = data.precio ;
                    input2.value = data;
                    recalcularTotal()
                    c=1;
            //fin nueva funcion para cambiar precio


            // Hacer solicitud AJAX al servidor Django
            fetch(`/actualizar-precio/${idBaremo1}/${cantidad1}`)
            .then(response => response.json())
            .then(resultado  => {
                // Actualizar el precio en la celda 3
                const data = resultado.precio ;
                
                if (data == 0){

                }
                //celda3.textContent = data;
                input2.value = data;
                recalcularTotal()
                c=1;
            })
            .catch(error => console.error(error));
            console.log('El campo precio ha cambiado');
            // Por ejemplo, puedes actualizar el valor de la celda 3 con el nuevo valor
            
        })
         // Fin del evento de cambio para determinar cuando cambie la cantidad
    celda2.appendChild(input);
    celda3.appendChild(input2);
    if (c==0) {
        input2.value = datosFila.precio;
        //celda3.textContent = datosFila.precio;
        
    }
    
    const celda4 = document.createElement('td');
    const input3 = document.createElement('input');
    input3.value = datosFila.unidad;
    input3.name = 'baremo_fila';
    celda4.style.textAlign = 'center';
    celda4.appendChild(input3);
    //celda4.textContent = datosFila.unidad;
    const celda5 = document.createElement('td');
    const botonEliminar = document.createElement('button');
    botonEliminar.type="button";
    botonEliminar.innerHTML = '<i class="fas fa-trash"></i>';
    botonEliminar.style.backgroundColor = 'red';
    botonEliminar.style.color = 'white';
    botonEliminar.style.border = 'none';
    botonEliminar.style.padding = '5px 10px';

    // Agrega el evento de click al botón de eliminar
    botonEliminar.addEventListener('click', function() {
        // Elimina la fila padre del botón
        const fila = this.parentNode.parentNode;
        fila.parentNode.removeChild(fila);
      });

    botonEliminar.innerHTML = '<i class="fas fa-trash"></i>';
    celda5.appendChild(botonEliminar);

    const celda7 = document.createElement('td');
    const input7 = document.createElement('input')
    input7.name = 'baremo_fila'
    celda7.style.display = 'none'
    input7.value = datosFila.convenio_id;
    celda7.appendChild(input7)

    const celda8 = document.createElement('td');
    const input8 = document.createElement('input')
    input8.name = 'baremo_fila'
    celda8.style.display = 'none'
    input8.value = datosFila.grupo_id;
    celda8.appendChild(input8)

    const celda9 = document.createElement('td');
    const input9 = document.createElement('input')
    input9.name = 'baremo_fila'
    celda9.style.display = 'none'
    input9.value = datosFila.detalle_id;
    celda9.appendChild(input9)

    const celda10 = document.createElement('td');
    celda10.textContent = ''
    const celda11 = document.createElement('td');
    celda11.textContent = ''
    const celda12 = document.createElement('td');
    celda12.textContent = ''
  
    //fila.appendChild(celda0);
    //fila.appendChild(celda6);
    fila.appendChild(celda1);
    fila.appendChild(celda2);
    fila.appendChild(celda3);
    fila.appendChild(celda4);
    fila.appendChild(celda5);
    fila.appendChild(celda7);
    fila.appendChild(celda8);
    fila.appendChild(celda9);
    fila.appendChild(celda10);
    fila.appendChild(celda11);
    fila.appendChild(celda12);
     // agrega el botón a la celda
    tbody.appendChild(fila);
    recalcularTotal()
  }