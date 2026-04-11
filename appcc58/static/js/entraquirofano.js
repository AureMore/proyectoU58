$(document).ready(function(){
  new DataTable('#tblinventario',{
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

// script.js
let segundos = 0;
let minutos = 0;
let horas = 0;
let milisegundos = 0;
let cronometroActivo = false;
let intervalo;
let horaEntrada;

function actualizarCronometro() {
milisegundos += 10
    if (milisegundos === 1000) {
        segundos++;
        milisegundos = 0;
    }
  if (segundos === 60) {
    minutos++;
    segundos = 0;
  }
  if (minutos === 60) {
    horas++;
    minutos = 0;
  }
  
  const cronometro = document.getElementById('cronometro');
  cronometro.innerText = `${horas.toString().padStart(2, '0')}:${minutos.toString().padStart(2, '0')}:${segundos.toString().padStart(2, '0')}.${milisegundos.toString().padStart(3, '0')}`; // Agrega los milisegundos al texto del cronómetro
}

document.getElementById('iniciar-cronometro').addEventListener('click', function() {
    if (!cronometroActivo) {
        cronometroActivo = true;
        const fecha = new Date();
        var hora = fecha.toLocaleTimeString();
        
        const hora_inicio = document.getElementById("hora_entrada").textContent
        if (hora_inicio == "::" ) {
          document.getElementById("hora_entrada").innerHTML = hora;
        } else {
          hora = hora_inicio
        }

        const currentTime =  fecha.toLocaleTimeString();;
        const diff =  hora - currentTime
        /// *******************
          const [h, m, s] = hora.split(':').map(Number);
          const fechaInicial = new Date(0, 0, 0, h, m, s);
          
          const [hf, mf, sf] = currentTime.split(':').map(Number);
          const fechaFinal = new Date(0, 0, 0, hf, mf, sf);
          
          const diferencia =  fechaFinal.getTime() - fechaInicial.getTime()
          
          const horasd = Math.floor(diferencia / (1000 * 60 * 60));
          const minutosd = Math.floor((diferencia % (1000 * 60 * 60)) / (1000 * 60));
          const segundosd = Math.floor((diferencia % (1000 * 60)) / 1000);

        ///************* */
    // Establece los valores iniciales para el temporizador
        horas = horasd;
        minutos = minutosd;
        segundos = segundosd;
        //milisegundos = diffMilliseconds;

        intervalo = setInterval(actualizarCronometro, 10); // Cambia el intervalo a 10 milisegundos
        document.getElementById('parar-cronometro').disabled = false; 
        document.getElementById('iniciar-cronometro').disabled = true; // Habilita el botón de parar
        cambiaStatusCirugia('4','IQ') // IQ=Ingreso Quirofano
    }
  });

  document.getElementById('parar-cronometro').addEventListener('click', function() {
        if (cronometroActivo) {
          cronometroActivo = false;
          clearInterval(intervalo);
          const fecha = new Date();
          const hora = fecha.toLocaleTimeString();
          document.getElementById("hora_salida").innerHTML = hora;
          document.getElementById('parar-cronometro').disabled = true; // Deshabilita el botón de parar
          cambiaStatusCirugia('5','SQ') //SQ=Salida Quirofano
          document.getElementById('btn-cerrar').classList.remove('activar');
          Swal.fire({
            title: "Bien!",
            text: "Cirugia Finalizada!",
            icon: "success"
          });

      }
  });

/////
  let segundos1 = 0;
  let minutos1 = 0;
  let horas1 = 0;
  let milisegundos1 = 0;
  let cronometroActivo1 = false;
  let intervalo1;
  
  function actualizarCronometro1() {
  milisegundos1 += 10
      if (milisegundos1 === 1000) {
            segundos1++;
          milisegundos1 = 0;
      }
    if (segundos1 === 60) {
      minutos1++;
      segundos1 = 0;
    }
    if (minutos1 === 60) {
      horas1++;
      minutos1 = 0;
    }
  
    const cronometro1 = document.getElementById('cronometro1');
    cronometro1.innerText = `${horas1.toString().padStart(2, '0')}:${minutos1.toString().padStart(2, '0')}:${segundos1.toString().padStart(2, '0')}.${milisegundos1.toString().padStart(3, '0')}`; // Agrega los milisegundos al texto del cronómetro
  }
  
  document.getElementById('iniciar-cronometro1').addEventListener('click', function() {
    const botonSeguridad = document.getElementById('parar-cronometro')
      if (!cronometroActivo1) {
        if (botonSeguridad.getAttribute('disabled') == null) {
          cronometroActivo1 = true;
          const fecha1 = new Date();
          var hora1 = fecha1.toLocaleTimeString();

          const hora_cirugia = document.getElementById("hora_cirugia").textContent
          if (hora_cirugia == "::" ) {
            document.getElementById("hora_cirugia").innerHTML = hora1;
          } else {
            hora1 = hora_cirugia
          }
 
          const currentTime1 =  fecha1.toLocaleTimeString();;
          const diff =  hora1 - currentTime1
          /// *******************
            const [h, m, s] = hora1.split(':').map(Number);
            const fechaInicial1 = new Date(0, 0, 0, h, m, s);
            
            const [hf, mf, sf] = currentTime1.split(':').map(Number);
            const fechaFinal1 = new Date(0, 0, 0, hf, mf, sf);
            
            const diferencia1 =  fechaFinal1.getTime() - fechaInicial1.getTime()
            
            const horasd1 = Math.floor(diferencia1 / (1000 * 60 * 60));
            const minutosd1 = Math.floor((diferencia1 % (1000 * 60 * 60)) / (1000 * 60));
            const segundosd1 = Math.floor((diferencia1 % (1000 * 60)) / 1000);

          ///************* */
      // Establece los valores iniciales para el temporizador
          horas1 = horasd1;
          minutos1 = minutosd1;
          segundos1 = segundosd1;
          //milisegundos = diffMilliseconds;
    
          intervalo1 = setInterval(actualizarCronometro1, 10); // Cambia el intervalo1 a 10 milisegundos
          document.getElementById('parar-cronometro1').disabled = false; // Habilita el botón de parar
          document.getElementById('iniciar-cronometro1').disabled = true;
          document.getElementById('parar-cronometro').disabled = true;
          cambiaStatusCirugia('4','IC') //IC = Inicio Cirugia
        } else {
            Swal.fire("Primero se activa la entrada a quirofano");
        }
    }
    });
  
    document.getElementById('parar-cronometro1').addEventListener('click', function() {
      if (cronometroActivo1) {
        cronometroActivo1 = false;
        clearInterval(intervalo1);
          const fecha = new Date();
          const hora = fecha.toLocaleTimeString();
          document.getElementById("salida_cirugia").innerHTML = hora;
        document.getElementById('parar-cronometro1').disabled = true; // Deshabilita el botón de parar
        document.getElementById('parar-cronometro').disabled = false;
        cambiaStatusCirugia('4','FC') //FC = Fin Cirugia
      }
    });
 

    $(document).ready(function() {
      $('#tblinventario').on('dblclick', 'tbody tr', function() {
        const idCirugia = document.getElementById('id_idCirugia').value;
        // Obtener la fila seleccionada
        var fila = $(this);
        // Agregar la fila a la tabla destino
        //agregarFilaSeleccionada(fila);
        var filaId = fila.attr('id').replace('fila-','');

        var cantidadInput = fila.find('input.cantidad_agregada');
        var cantidad = parseInt(cantidadInput.val());

        var ventaTd = fila.find('td:eq(4)');
        var venta = ventaTd.text();
        const checkbox = document.getElementById('idCheckFarmacia');
        var farmacia = 'False'
        if (checkbox.checked) {
          farmacia = 'True'
        }

        const datos = {
          filaId: filaId,
          cantidad: cantidad,
          idCirugia: idCirugia,
          venta: venta,
          farmacia:farmacia,
          nota: '',
          medico_entregado: ''
        };
  
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
        fetch('/guardar_consumo_cirugia/', {
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
          // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
          refreshTable();
        })
        .catch(error => console.error(error));

      });
    });

    function guardarTiempoCirugia() {
      
      const horaEntrada = document.getElementById('hora_entrada').textContent;
      const cronometro = document.getElementById('cronometro').textContent;
      const horaSalida = document.getElementById('hora_salida').textContent;
      const inicioCirugia = document.getElementById('hora_cirugia').textContent;
      const tiempoCirugia = document.getElementById('cronometro1').textContent;
      const finCirugia = document.getElementById('salida_cirugia').textContent;
      const idCirugia = document.getElementById('id_idCirugia').value;
      const horasfacturadas = document.getElementById('cronometro-factura').textContent
      const cronometroElement = document.getElementById("cronometro");
      const cronometroValue = cronometroElement.innerHTML ; // o también puedes usar textContent
      const horaInicioElement = document.getElementById("hora_entrada");
      const horaInicio = horaInicioElement.innerHTML ;  
      // Horas reales de Quirofano
      const [hours, minutes, seconds, milliseconds] = cronometroValue.match(/(\d+):(\d+):(\d+)\.(\d+)/).slice(1).map(Number);
      let hr_adicion =0 
      if (hours == 0) {
          hr_adicion = 1
      } else {
        if (minutes > 20) {
          hr_adicion = 1
        } 
      }
      const total_horas = hours + hr_adicion
      // Fin calculo Horas reales

      const datos = {
        total_horas: total_horas,
        cronometro: cronometro,
        cronometro1: tiempoCirugia,
        idCirugia: idCirugia,
        hora_entrada: horaEntrada,
        horasfacturadas: horasfacturadas
      };

      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      fetch('/guardar_datos_cirugia/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        }, 
        body: JSON.stringify(datos)
      })
      .then(response => response.json())
      .then(data => console.log(data))
      .catch(error => console.error(error));

     
            
    }


function verificarMedicos() {
  var farmacosMmq = false
  var asignarMedicos = false
  const tbody = document.getElementById('tbody-tblasignado');
  const rows = tbody.getElementsByTagName('tr');
  if (rows.length > 0) {
    farmacosMmq = true
  } else {
    Swal.fire({
      icon: "error",
      title: "Medicinas y MMQ",
      text: "Debe asignar antes de cerrar la cirugia",
    });
  }

 
  const selects = document.querySelectorAll('.nota_q_medicos');
  let total = 0
  // Recorre los select
  selects.forEach((select) => {
    if (select.value != '') {
      total += 1
    }
  });
  if (total > 0) {
    asignarMedicos = true
  } else {
    Swal.fire({
      icon: "error",
      title: "Personal Medico",
      text: "Debe seleccionar los medicos antes de cerrar la cirugia",
    });
  }

  if (asignarMedicos && farmacosMmq) {
    guardarTiempoCirugia()
    window.location.href = '/lista_cirugia_finish/'; 
    
  }


}


function cambiaStatusCirugia(newEstatus,tipoHora) {
  const idCirugia = document.getElementById('id_idCirugia').value;
  const datos = {
    idCirugia : idCirugia,
    estatus: newEstatus,
    tipoHora: tipoHora
  };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  fetch('/cambiar_estatus_cirugia/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    },
    body: JSON.stringify(datos)
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error(error));


}

function asignarKit(idKit) {
  const checkbox = document.getElementById('idCheckFarmacia');
  var farmacia = 'False'
  if (checkbox.checked) {
    farmacia = 'True'
  }

  const idCirugia = document.getElementById('id_idCirugia').value;
    const datos = {
      idKit : idKit,
      idCirugia: idCirugia,
      farmacia:farmacia,
    };
    
    
  //funcion asignar kit
    // Crear una solicitud AJAX
    //xhr.open('GET', '/filtrar_kits_cirugia/?idKit=' + idKit, true); // asumiendo que tu vista de Django está en /filtrar_kits/
  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/guardar_kit_cirugia/', {
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
      // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
      refreshTable();
      $('#modalInventario').modal('hide');
    })
    .catch(error => console.error(error));

}
  

  //fin funcion

function actualizarNotaqx(idNotaqx, idMedico) {

  const datos = {
    idNotaqx : idNotaqx,
    idMedico: idMedico,
  };

   const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  fetch('/guardar_medico_notaqx/', {
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
    // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
    refreshTableMedico()
    $('#modalInventario').modal('hide');
  })
  .catch(error => console.error(error));

}

function refreshTableMedico() {
  var id_filter = $('#id_idCirugia').val(); // Obtener el valor del input con id "id_filter"
  $.ajax({
      type: 'GET',
      url: '/refresh_table_medicos/' + '?id_filter=' + id_filter,
      dataType: 'html',
      success: function(data) {
          $('#my_tabla_medicos_qx').html(data);
      }
  });
}


function refreshTable() {
            selectedRows = [];
            console.log('banquear selectedrows')
            var id_filter = $('#id_idCirugia').val(); // Obtener el valor del input con id "id_filter"
            $.ajax({
                type: 'GET',
                url: '/refresh_table/' + '?id_filter=' + id_filter,
                dataType: 'html',
                success: function(data) {
                    $('#my_table').html(data);
                }
            });
}

//funcion para refrescar la tabla cuando abra la pagina html
$(document).ready(function() {

      const estatus_cirugia = document.getElementById('id_estatus_cirugia').value;
      if (estatus_cirugia > 4) {
        document.getElementById('parar-cronometro').disabled = true; 
        document.getElementById('iniciar-cronometro').disabled = true; 

      }
      var id_filter = $('#id_idCirugia').val(); // Obtener el valor del input con id "id_filter"
      $.ajax({
          type: 'GET',
          url: '/refresh_table/' + '?id_filter=' + id_filter,
          dataType: 'html',
          success: function(data) {
              $('#my_table').html(data);
          }
      });
});


function eliminarConsumoCirugia(idConsumo,whoElimina) {
console.log(whoElimina)
  const datos = {
    idConsumo : idConsumo,
    whoElimina : whoElimina,
  };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  fetch('/eliminar_consumo_cirugia/', {
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
    // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
    refreshTable();
  })
  .catch(error => console.error(error));

}

// funcion agregar por boton

function agregarxBoton(idInv,venta, cantidad) {
    const idCirugia = document.getElementById('id_idCirugia').value;
    // Obtener la fila seleccionada
    // Agregar la fila a la tabla destino
    //agregarFilaSeleccionada(fila);
    var filaId = idInv
    const farmacia = 'True'

    const datos = {
      filaId: filaId,
      cantidad: cantidad,
      idCirugia: idCirugia,
      venta: venta,
      farmacia:farmacia,
      nota: '',
      medico_entregado: ''
    };

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/guardar_consumo_cirugia/', {
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
      // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
      refreshTable();
    })
    .catch(error => console.error(error));

  }


function guardaCantReal(nCant, idConsumo,ntope) {
  //validar las cantidades
  nCant = parseFloat(nCant.replace(',','.'))
  ntope = parseFloat(ntope.replace(',','.'))
  if (nCant > ntope) {
    alert('Cantidad superior a lo entregado Negado Asignacion!')
    return
  }
    const datos = {
      nCant: nCant,
      idConsumo: idConsumo,
    
    };
    


    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/guardar_consumo_cantidad_real/', {
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
      const primerosCincoCaracteres = data.mensaje.substring(0, 5)
      if (primerosCincoCaracteres == 'MAYOR') {
        alert('Cantidad Excede lo disponible. Negado!')
      } else {
        refreshTable()
      }
      $('#modalInventario').modal('hide')
      // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
    })
    .catch(error => console.error(error));

}


function actualizarDisponibleQx() {
  var id_filter = $('#id_idCirugia').val(); // Obtener el valor del input con id "id_filter"
            $.ajax({
                type: 'GET',
                url: '/refresh_table_asignado_qx/' + '?id_filter=' + id_filter,
                dataType: 'html',
                success: function(data) {
                    $('#my_table_asignado_farmacia').html(data);
                    $('#modalInventario').modal('show')
                }
            }); 
}


function checkCheckbox(inputField) {
  const checkboxId = `checkbox-${inputField.id.split('-')[1]}`;
  const checkbox = document.getElementById(checkboxId);
  checkbox.checked = true;
}

var selectedRows = [];

function rowCheckBoxSelection() {
  $('#tblfarmaciaselected tbody input[name="check_fila"]').on('change', function() {
      var id = $(this).attr('id').replace('checkbox-', '');
      var quantity = $(this).closest('tr').find('input[name="real_usado"]').val();
      if ($(this).is(':checked')) {
          var exists = selectedRows.some(record => record.id === id);
          if (!exists) {
            selectedRows.push({ id: id, quantity: quantity });
            console.log('marcado para agregar')
          }
          
      } else {
          selectedRows = selectedRows.filter(record => record.id !== id);
      }
  });
}

 
function guardarFarmaciaSeleccionados() {
 
  $.ajax({
    type: 'POST',
    url: '/save_selected_rows/',
    data: JSON.stringify(selectedRows),
    contentType: 'application/json',
    success: function(data) {
        // Maneja la respuesta de tu vista de Django
        refreshTable()
    }
  });

}