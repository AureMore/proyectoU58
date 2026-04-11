$(document).ready(function(){

    new DataTable('#tbllistainventario',{
        ajax: { 
            url : "/dt_serverside_inventario/",
            dataSrc:'datos'
        },
        columns: [
            {data: "codigo"},
            {data: "nombre"},
            {data: "presentacion"},
            
            {
                data: "cantidad_cri",
                render: function(data, type, row) {
                    // Verifica si cantidad_min es menor o igual a existencia
                    if (data >= row.cantidad_min || data == 0) {
                        return `<div style=" background-color: orange; color:black; padding: 5px; text-align:right; font-weight: 900;">${data}</div>`;
                    }
                    return data;
                }
            },

            {
                data: "cantidad_min",
                render: function(data, type, row) {
                    // Verifica si cantidad_min es menor o igual a existencia
                    if (data >= row.existencia) {
                        return `<div style=" color: red; padding: 5px;text-align:right;">${data}</div>`;
                    }
                    return data;
                }
            },


            /* {
                data: "existencia",
                render: function(data, type, row) {
                    // Verifica si cantidad_min es menor o igual a existencia
                        return `<div style=" color: blue; padding: 5px;">${data}</div>`;
                    return data;
                }
            }, */
            {data: "existencia_und"},
            // {data: "unidad_conversion"},
            {data: "piva"},
            {
                data: "costo",
                render: function(data, type, row) {
                    // Verifica si el costo es 0
                    if (data == 0) {
                        return `<span style="color: red;">${data}</span>`; // Devuelve el costo en rojo
                    }
                    return data; // Devuelve el costo normalmente si no es 0
                }
            },
            {data: "monto_venta"},
            {data: "categoria"},
            {data: "laboratorio"},
            {data: "nombre_comercial"},
            {
                data: "fecha_vencimiento",
                render: function(data, type, row) {
                    // Verifica si el costo es 0
                    const fechaVencimiento = new Date(data);
                    const hoy = new Date();
                    hoy.setHours(0, 0, 0, 0);

                    function formatearFecha(fecha) {
                        const dia = ("0" + fecha.getDate()).slice(-2);  // agrega un cero si el día es menor a 10
                        const mes = ("0" + (fecha.getMonth() + 1)).slice(-2);  // los meses empiezan en 0
                        const anio = fecha.getFullYear();
                        return `${dia}/${mes}/${anio}`;
                    }
                    const fechaFormateada = formatearFecha(fechaVencimiento);

                    if (fechaVencimiento <= hoy) {
                        return `<div style="background-color: red; color: white; padding: 5px; text-align:center;">${fechaFormateada}</div>`; // Devuelve el costo en rojo
                    }
                    return fechaFormateada; // Devuelve el costo normalmente si no es 0
                }
            }, 


            {data: "id"},
        ], 
        columnDefs: [
        {
            targets: [-1],
            className: 'text-center',
            orderable: false,
            render: function (data, type, row) { 
                var id = row.id
                var urledit = `/editar_producto_inventario/${id}/`;
                var urlProvider = `/lista_proveedor_producto/${id}/`;
                var buttons = `<a type="button" href="${urledit}" class="btn btn-sm btn-outline-dark ps-1 pe-1 pt-0 pb-0"> <i class="fa-solid fa-pen-to-square"></i> </a>
                    <a type="button" href="${urlProvider}" class="btn btn-sm btn-primary ps-1 pe-1 pt-0 pb-0" ><i class="fa-regular fa-address-book"></i>  
                        
                    </a>
                `;
                return buttons
            }
        },
        {
            targets: [4,5,6,7,8,9], 
            className: 'color-cantidad',
           
        },
        ],
        select:false,
        dom: 'Bfrtip',
        processing: true,
        serverSide: true,
        pageLength: 50,
        lengthMenu: [10, 25, 50, 100],
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
    
})



function aplicarDescarga(iddepositouso,cantidadDescargar,tipoDescarga,nota,depositoentrada) {
    const unidadejecuciontraslado = document.getElementById('unidadejecuciontraslado').value // 1 -CALON/CAJAS/PACAS etc /2-Unidad
    
    const datos = {
        iddepositouso: iddepositouso,
        cantidadDescargar: cantidadDescargar,
        tipoDescarga: tipoDescarga,
        nota : nota,
        depositoentrada : depositoentrada,
        unidadejecuciontraslado : unidadejecuciontraslado,
      };
  
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
      fetch('/descargar_inventario/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        }, 
        body: JSON.stringify(datos)
      })
      .then(response => response.json())
      .then(data => {
        console.log('descargado')
        //window.location.href = '/listado_producto_inventario/';
        // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
        location.reload()
      })
      .catch(error => console.error(error));
  }


  function muestraDeposito(idDepositouso,nombreDeposito, cantidadDescarga) {
    cantidadDescarga=cantidadDescarga.replace(',','.')
    if (cantidadDescarga > 0) {
        document.getElementById('cantidadOriginal').value = cantidadDescarga
        document.getElementById('depositodescarga').value = nombreDeposito
        document.getElementById('iddepositodescarga').value = idDepositouso
        $('#descargaProducto').modal('show');
    } else {
        alert('No hay productos para descargar en este deposito')
    }
  }

  
  function cambioDeposito(idDepositouso, nombreDeposito, cantidadDescarga, idDepositoSalida, trasladoPpal) {
    console.log('depo:'+idDepositoSalida)
    if (trasladoPpal == 'True' && idDepositoSalida != 4 ) {
        alert('No Tiene Privilegios para hacer traslado de este deposito')
    } else {
        cantidadDescarga = cantidadDescarga.replace(',','.')
        if (cantidadDescarga > 0) {
            document.getElementById('cantidadOrigen').value = cantidadDescarga
            document.getElementById('depositodescargacambio').value = nombreDeposito
            document.getElementById('iddepositodescargacambio').value = idDepositouso
            document.getElementById('iddepositoSalida').value = idDepositoSalida
            $('#cambioDeposito').modal('show');
        } else {
            alert('No hay productos para cambiar en este deposito')
        }
    }
    
  }

  
function ejecutarTraslado() {
    var cantidadOrigen = document.getElementById('cantidadOrigen').value 
    var cantidadcambiar = document.getElementById('cantidadcambiar').value 
    var iddepositodescarga = document.getElementById('iddepositodescargacambio').value
    var depositocarga = document.getElementById('depositocarga').value
    var tipoDescarga = document.getElementById('motivoDescarga').value
    var depositoSalida = document.getElementById('iddepositoSalida').value
    var nota = document.getElementById('notacambio').value

    cantidadOrigen = parseFloat(cantidadOrigen)
    cantidadcambiar = parseFloat(cantidadcambiar)
    if (depositoSalida == depositocarga) {
        alert('Deposito de Carga y Descarga NO pueden ser el mismo')
        return
    }

    if (cantidadcambiar == 0) {
        alert('Debe colocar la cantidad a descargar')
        return
    }
    if (cantidadcambiar > cantidadOrigen) {
        alert('No puede descargar mas cantidad de lo que hay en deposito')
        return
    }
    if (depositocarga == '') {
        alert('Seleccionar deposito donde enviar el producto')
        return
    }
    if (cantidadcambiar <= cantidadOrigen) {
        
        aplicarDescarga(iddepositodescarga,cantidadcambiar,tipoDescarga,nota,depositocarga )

    }
  }

  
  function cambioConversion(pincremento, newConversion) {
    pincremento = pincremento.replace(',','.')
    newConversion = newConversion.replace(',','.')
    var costoUpdate = document.getElementById('costoUpdate').value
    const costoActual = parseFloat(costoUpdate.replace(',','.'))

    // Convertir a números
    let incremento = parseFloat(pincremento);
    let factorconversion = parseFloat(newConversion);
    



    let montoaincrementar = costoActual + (costoActual * incremento);

    montoaincrementar = montoaincrementar / factorconversion
    
    document.getElementById('ventaUpdate').value = montoaincrementar.toFixed(2)
}



function precioVenta(pincremento, valorCosto) {
    pincremento = pincremento.replace(',','.')
    valorCosto = valorCosto.replace(',','.')
    var conversion = 1
    var porc_iva = document.getElementById('pivaUpdate').value

    porc_iva = parseFloat(porc_iva.replace(',','.'))


    // Convertir a números
    let incremento = parseFloat(pincremento);
    let costo = parseFloat(valorCosto);
    const factorconversion = parseFloat(conversion)



    let montoaincrementar = costo + (costo * incremento);

    montoaincrementar = montoaincrementar / factorconversion

    let montoaincrementariva = montoaincrementar * (porc_iva/100)

    montoaincrementar = montoaincrementar + montoaincrementariva

    document.getElementById('ventaUpdate').value = montoaincrementar.toFixed(2)
}


function cambiarcantidadDeposito(idDepositouso, newCantidad) {
    const datos = {
        idDepositouso: idDepositouso,
        newCantidad: newCantidad,
    } 

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

   
    fetch('/DepositoUpdate/', {
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
        //refreshTableDeposito(idDepositouso)
        location.reload()
        
    })
    .catch(error => console.error('Error:', error));

    
}

function refreshTableDeposito(idDepositouso) {
    const idProducto = document.getElementById('idproducto').value
    $.ajax({
        type: 'GET',
        url: '/refresh_tableDepositoUso/' + '?idProducto=' + idProducto,
        dataType: 'html',
        success: function(data) {
            $('#tabla-deposito-uso').html(data);

            //$('#loaderModal').modal('hide');
            
        }
    });
}

function agregarUnidad() {
    $('#modalUnidadCompra').modal('show');
}

function guardarUnidad() {
    var nomunidadcompra = document.getElementById('nomunidadcompra').value
    if (nomunidadcompra.trim() === '') {

        alert('El nombre esta en blanco , debe colocar nombre valido');

    } else {

        const datos = {
            nomunidadcompra: nomunidadcompra,
          } 
    
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
       
        fetch('/agregarUnidadCompra/', {
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
            
        })
        .catch(error => console.error('Error:', error));
    
        
    }
}


