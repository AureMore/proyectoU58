var table = $('#tbl-cortecuenta').DataTable({
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



function muestraConsumo(idPresupuesto, idDetalle, detalle, iddetallepresupuesto) {
    let idCategoria = 0
   
    if (idDetalle==19) {
        idCategoria=1
    }
    if (idDetalle==18) {
        idCategoria=2
    }
    if (idDetalle==85) {
        idCategoria=3
    }
    if (idDetalle==90) {
        idCategoria=4
    }
    if (idDetalle==40) {
        idCategoria=5
    }
    if (idDetalle==94) {
        idCategoria=8
    }


   const h6Element = document.querySelector('#titulo_consumo');
   h6Element.textContent = detalle; 
   fetch(`/filtro-Consumo/?presupuesto=${idPresupuesto}&detalle=${idCategoria}&iddetallepresupuesto=${iddetallepresupuesto}`, {
       method: 'GET',
   })

   .then(response => response.json())
   .then(data => {
        // Create an HTML table with the results
       let fila=0
        let tableHtml = '';
        data.forEach(item => {
            fila += 1;
            tableHtml += '<tr>';
            tableHtml += `<td>${fila}</td>`;
            tableHtml += `<td>${item.nombre}   </td>`;
            tableHtml += `<td>${item.cantidad_real_usada}</td>`;
            tableHtml += `<td>${parseFloat(item.monto_unitario).toFixed(2)}</td>`;
            tableHtml += `<td>${parseFloat(item.monto_venta).toFixed(2)}</td>`; // Formatear a 2 decimales
            // Formatear la fecha y hora
            const fechaHora = new Date(item.hora);
            const dia = String(fechaHora.getDate()).padStart(2, '0'); // Obtener el día y agregar un cero a la izquierda si es necesario
            const mes = String(fechaHora.getMonth() + 1).padStart(2, '0'); // Obtener el mes (0-11) y agregar un cero a la izquierda
            const anio = fechaHora.getFullYear(); // Obtener el año
            const horas = String(fechaHora.getHours()).padStart(2, '0'); // Obtener las horas
            const minutos = String(fechaHora.getMinutes()).padStart(2, '0'); // Obtener los minutos

            // Formatear la fecha y hora
            const fechaFormateada = `${dia}/${mes}/${anio}`;
            const horaFormateada = `${horas}:${minutos}`;

            tableHtml += `<td>${fechaFormateada} ${horaFormateada}</td>`; // Mostrar la fecha y hora formateadas
            tableHtml += `<td>${item.lugar}</td>`;


            // Add more columns as needed
            tableHtml += '</tr>';
        });
        tableHtml += '';

        // Append the table to your HTML element
        document.getElementById('tblconsumo').innerHTML = tableHtml;
    })
   .catch(error => console.error('Error:', error));

    $('#exampleModal').modal('show');

}


function cambiarPrecio(idPresupuesto, precioUsado, detalle, idCirugia) {
    
    // Código a ejecutar cuando se cambie el precio_usado
    var datos = {
        'id_presupuesto': idPresupuesto,
        'precio_usado': precioUsado,
        'detalle': detalle,
        'id_cirugia': idCirugia
    };

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/modificacion_corte_cuenta/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      }, 
      body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        if (data.mensaje === 'pagado') {
            alert("Item pagado en cuentas por pagar no puede modificar")
        }
        location.reload(); // Recargar la página manualmente
        
    })
    .catch(error => console.error(error));
}



function setReadOnlyBasedOnGroupName(groupName) {
    const isAdmin = groupName === 'Administradores';
    const inputs = document.querySelectorAll('.cambio-precio');
    inputs.forEach(input => {
      if (isAdmin) {
        input.removeAttribute('readonly');
      } else {
        input.setAttribute('readonly', 'readonly');
      }
    });
  }
  const groupNameInput = document.getElementById('group-name');
  const groupName = groupNameInput.value;
  setReadOnlyBasedOnGroupName(groupName);



// dobleclik y guardarlo en prespuesto y cirugia detalle
 function agregarFilaBaremo(idBaremo, idDetalle,idGrupo, idPlantilla, cantidad, precio, idConvenio, idCirugia, idPresupuesto, ntqx, unidad ) {
    var datos = {
        'idBaremo': idBaremo,
        'idDetalle': idDetalle,
        'idGrupo': idGrupo,
        'idPlantilla': idPlantilla,
        'cantidad': cantidad,
        'precio': precio,
        'idConvenio': idConvenio,
        'idCirugia': idCirugia,
        'idPresupuesto': idPresupuesto,
        'ntqx': ntqx,
        'unidad': unidad
    };

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/guardar_item_corte_cuenta/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      }, 
      body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.mensaje);
        location.reload(); // Recargar la página manualmente
    })
    .catch(error => console.error(error));
 }


function cambiarMedicoCuenta(idNotaQx, idMedico) {
    id_cirugia = document.getElementById('id_cirugia').value
    console.log("id de nota :" + idNotaQx)
        var datos = {
            'idNotaQx': idNotaQx,
            'idMedico': idMedico,
            'id_cirugia': id_cirugia,
        } 

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/cambiar_medico_en_cortecuenta/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }, 
        body: JSON.stringify(datos)
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.mensaje);
            location.reload(); // Recargar la página manualmente
        })
        .catch(error => console.error(error));

}


function eliminaritemCorteCuenta(idDetallePresupuestoDelete) {

    $.ajax({
        type: 'GET',
        url: '/eliminar_detalle_cortecuenta/' + '?idDetallePresupuestoDelete=' + idDetallePresupuestoDelete,
        dataType: 'json',
        success: function(data) {
            if (data.mensaje === "pagado") {
                Swal.fire({
                    icon: "error",
                    title: "Operacion Negada",
                    text: "Este item tiene factura pagada y no puede eliminarse",
                    });
            } else {
                location.reload()
            }
            
        }
    });

}


function cambiaritemBaremo(idDetallePresupuestoDelete) {

    $.ajax({
        type: 'GET',
        url: '/cambiar_detalle_cortecuenta/' + '?idDetallePresupuestoDelete=' + idDetallePresupuestoDelete,
        dataType: 'json',
        success: function(data) {
            if (data.mensaje == 'unautorized') {
                alert('Ya posee los dos item de hospitalizacion en el corte de cuenta')
            } else {
                location.reload()
            }
          
            
        }
    });

}



function cambioCantidad(idDetalle, newCantidad, cirugia_id) {
    $.ajax({ 
        type: "GET",
        url: "/actualizar_precio_detalle_cirugia_presupuesto/",  
        data: {
            idDetalle: idDetalle,
            cantidad1: newCantidad,
            cirugia_id: cirugia_id,
        },
        success: function(data) { 
            const precioventa = data.precio ;
            location.reload()
        }
    })
    
}

function muestraComentario() {
    
    Swal.fire({
        title: 'Información',
        text: 'Este item fue incluido posterior al presupuesto original del cliente, por tal motivo su precio es cero (0) en el presupuesto.',
        customClass: {
            popup: 'swal-custom'
        }
    });
    
}