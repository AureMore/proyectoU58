document.addEventListener('DOMContentLoaded', function() {
    const numberSpan = document.getElementById('formatted-number');
    const rawNumber = parseFloat(numberSpan.textContent.replace(',', '.'));
    const numberSpan1 = document.getElementById('formatted-number1');
    const rawNumber1 = parseFloat(numberSpan1.textContent.replace(',', '.'));
    const numberSpan2 = document.getElementById('formatted-number2');
    const rawNumber2 = parseFloat(numberSpan2.textContent.replace(',', '.'));

    const numberSpan3 = document.getElementById('formatted-number3');
    const rawNumber3 = parseFloat(numberSpan3.textContent.replace(',', '.'));
    const numberSpan4 = document.getElementById('formatted-number4');
    const rawNumber4 = parseFloat(numberSpan4.textContent.replace(',', '.'));
    
    // Formatear con separadores de miles (punto) y decimal (coma)
    // Opción 1: Formato en-US (1,234,567.89)
    const formattedNumber = rawNumber.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    const formattedNumber1 = rawNumber1.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    const formattedNumber2 = rawNumber2.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    const formattedNumber3 = rawNumber3.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    const formattedNumber4 = rawNumber4.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    
    // Opción 2: Formato personalizado (1.234.567,89)
    // const formattedNumber = rawNumber.toLocaleString('de-DE', {
    //    minimumFractionDigits: 2,
    //    maximumFractionDigits: 2
    // });
    
    numberSpan.textContent = formattedNumber;
    numberSpan1.textContent = formattedNumber1;
    numberSpan2.textContent = formattedNumber2;
    numberSpan3.textContent = formattedNumber3;
    numberSpan4.textContent = formattedNumber4;
});


//tblpagadorfrecuente
$(document).ready(function() {
    let table = new DataTable('#tblpagadorfrecuente', {
        order: [[1, 'desc']], // Suponiendo que "pagado" es la segunda columna (índice 1)
        language: {
            "sSearch": "Buscar:",
            "sLengthMenu": "Mostrar _MENU_ entradas",
            "sInfo": "Mostrando _START_ a _END_ de _TOTAL_ entradas",
            "sInfoEmpty": "Mostrando 0 a 0 de 0 entradas",
            "sInfoFiltered": "(filtrado de _MAX_ entradas totales)",
            "sZeroRecords": "No se encontraron resultados",
            "oPaginate": {
                "sFirst": "Primero",
                "sLast": "Último",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            }
        }
    });


    let table2 = new DataTable('#tbltopcirugia', {
        order: [[3, 'desc']], // Suponiendo que "pagado" es la segunda columna (índice 1)
        language: {
            "sSearch": "Buscar:",
            "sLengthMenu": "Mostrar _MENU_ entradas",
            "sInfo": "Mostrando _START_ a _END_ de _TOTAL_ entradas",
            "sInfoEmpty": "Mostrando 0 a 0 de 0 entradas",
            "sInfoFiltered": "(filtrado de _MAX_ entradas totales)",
            "sZeroRecords": "No se encontraron resultados",
            "oPaginate": {
                "sFirst": "Primero",
                "sLast": "Último",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            }
        }
    });

    let table3 = new DataTable('#tblnotacredito', {
        order: [[1, 'desc']], // Suponiendo que "pagado" es la segunda columna (índice 1)
        language: {
            "sSearch": "Buscar:",
            "sLengthMenu": "Mostrar _MENU_ entradas",
            "sInfo": "Mostrando _START_ a _END_ de _TOTAL_ entradas",
            "sInfoEmpty": "Mostrando 0 a 0 de 0 entradas",
            "sInfoFiltered": "(filtrado de _MAX_ entradas totales)",
            "sZeroRecords": "No se encontraron resultados",
            "oPaginate": {
                "sFirst": "Primero",
                "sLast": "Último",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            }
        }
    });

    let table4 = new DataTable('#tblcirugiapendiente', {
        order: [[2, 'desc']], // Suponiendo que "pagado" es la segunda columna (índice 1)
        language: {
            "sSearch": "Buscar:",
            "sLengthMenu": "Mostrar _MENU_ entradas",
            "sInfo": "Mostrando _START_ a _END_ de _TOTAL_ entradas",
            "sInfoEmpty": "Mostrando 0 a 0 de 0 entradas",
            "sInfoFiltered": "(filtrado de _MAX_ entradas totales)",
            "sZeroRecords": "No se encontraron resultados",
            "oPaginate": {
                "sFirst": "Primero",
                "sLast": "Último",
                "sNext": "Siguiente",
                "sPrevious": "Anterior"
            }
        }
    });

    

    
    
});




function pagadorFrecuente(input) {
    // Buscar la posición del carácter #
    const hashIndex = input.indexOf('#');
    
    // Si no se encuentra #, devolver el texto completo
    if (hashIndex === -1) {
        return input;
    } else {
        var cedula = input.substring(0, hashIndex).trim();
        // Extraer y devolver el texto antes del #
        console.log('cedula:',cedula) 
        muestracirugiaxpagadorFrecuente(cedula, input)

    }
    
}

function refreshTablaCirugiasPendiente(parametro1, callback) {
    $.ajax({
        type: 'GET',
        url: '/refresh_table_cirugia_pendiente/' + '?parametro1=' + parametro1 ,
        dataType: 'json',
        success: function(response) {
            // Actualizar el HTML de la tabla
            $('#tabla-cirugia-pendiente-cobro').html(response.html);
            // Leer el valor de total_subtotal
            // Ejecutamos el callback cuando todo está listo
            if (callback) callback();
           
        },
        error: function() {
            // Manejo de errores (opcional)
            alert('Error al cargar los datos. Inténtalo de nuevo.');
            $('#cargandoModal').modal('hide'); // Asegúrate de ocultar el modal en caso de error
        }


    }); 
}



function muestraPentiente(dias, tituloModal) {
    const titulo = document.getElementById('detalleCirugiaLabel')
    titulo.textContent = tituloModal;
    
    $('#cargandoModal').modal('show')
    
    // Refrescar la tabla y ejecutar acciones cuando la operación termine
    refreshTablaCirugiasPendiente(dias, function() {
        // Primero ocultar el modal de carga
        $('#cargandoModal').modal('hide');
        
        // Luego mostrar el modal de detalle (solo cuando todo esté listo)
        $('#detalleCirugia').modal('show');
    });
   
}


function refreshTablaCirugiasPagadorFrecuente(parametro1, callback) {
    $.ajax({
        type: 'GET',
        url: '/refresh_table_cirugia_pagador_frecuente/' + '?parametro1=' + parametro1 ,
        dataType: 'json',
        success: function(response) {
            // Actualizar el HTML de la tabla
            $('#tabla-cirugia-pagador-frecuente').html(response.html);
            // Leer el valor de total_subtotal
            // Ejecutamos el callback cuando todo está listo
            if (callback) callback();
           
        },
        error: function() {
            // Manejo de errores (opcional)
            alert('Error al cargar los datos. Inténtalo de nuevo.');
            $('#cargandoModal').modal('hide'); // Asegúrate de ocultar el modal en caso de error
        }


    }); 
}


function muestracirugiaxpagadorFrecuente(cedulapagador, nombrepagador) {
    const titulo = document.getElementById('detallecirugiaPagadorLabel')
    titulo.textContent = nombrepagador;
    
    $('#cargandoModal').modal('show')
    
    // Refrescar la tabla y ejecutar acciones cuando la operación termine
    refreshTablaCirugiasPagadorFrecuente(cedulapagador, function() {
        // Agregar un pequeño retraso antes de ocultar el modal de carga
        setTimeout(function() {
            $('#cargandoModal').modal('hide');
            // Luego mostrar el modal de detalle (solo cuando todo esté listo)
            $('#detallecirugiaPagador').modal('show');
        }, 1000); // Retraso de 500 ms (ajusta según sea necesario)
    });
   
}

function buscarCuentaxCobrar(cuentacobrar_id) {
    window.open(`/cirugia_porcobrar/${cuentacobrar_id}/`, '_blank');
}


function refreshTablaCirugiasPagadorNC(parametro1, callback) {
    $.ajax({
        type: 'GET',
        url: '/refresh_table_cirugia_pagador_notacredito/' + '?parametro1=' + parametro1 ,
        dataType: 'json',
        success: function(response) {
            // Actualizar el HTML de la tabla
            $('#tabla-cirugia-pagador-notacredito').html(response.html);
            // Leer el valor de total_subtotal
            // Ejecutamos el callback cuando todo está listo
            if (callback) callback();
           
        },
        error: function() {
            // Manejo de errores (opcional)
            alert('Error al cargar los datos. Inténtalo de nuevo.');
            $('#cargandoModal').modal('hide'); // Asegúrate de ocultar el modal en caso de error
        }


    }); 
}


function muestracirugiaxpagadorNC(cedulapagador, nombrepagador) {
    const titulo = document.getElementById('notacreditoPagadorLabel')
    titulo.textContent = nombrepagador;
    
    $('#cargandoModal').modal('show')
    
    // Refrescar la tabla y ejecutar acciones cuando la operación termine
    refreshTablaCirugiasPagadorNC(cedulapagador, function() {
        // Agregar un pequeño retraso antes de ocultar el modal de carga
        setTimeout(function() {
            $('#cargandoModal').modal('hide');
            // Luego mostrar el modal de detalle (solo cuando todo esté listo)
            $('#notacreditoPagador').modal('show');
        }, 1000); // Retraso de 500 ms (ajusta según sea necesario)
    });
   
}



function pagadorNotaCredito(input) {
    // Buscar la posición del carácter #
    const hashIndex = input.indexOf('#');
    
    // Si no se encuentra #, devolver el texto completo
    if (hashIndex === -1) {
        return input;
    } else {
        var cedula = input.substring(0, hashIndex).trim();
        // Extraer y devolver el texto antes del #
        muestracirugiaxpagadorNC(cedula, input)

    }
    
}