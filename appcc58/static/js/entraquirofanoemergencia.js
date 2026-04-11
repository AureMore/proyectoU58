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
        const hora = fecha.toLocaleTimeString();
        document.getElementById("hora_entrada").innerHTML = hora;
        intervalo = setInterval(actualizarCronometro, 10); // Cambia el intervalo a 10 milisegundos
        document.getElementById('parar-cronometro').disabled = false; 
        document.getElementById('iniciar-cronometro').disabled = true; // Habilita el botón de parar
    }
  });

  document.getElementById('parar-cronometro').addEventListener('click', function(event) {
      if (!validar()) {
        const existePaciente = document.getElementById('id_paciente_emergencia').value
        const nombreProcedimiento = document.getElementById('idprocedimiento').value
        const errores = [];
        if (existePaciente=='') {
          errores.push('|Campo Pacientes es Requerido|');
        }
        if (nombreProcedimiento=='') {
          errores.push('|Campo Nombre de Procedimiento es Requerido|');
        }
        
        Swal.fire({
          title: "Campos Necesarios",
          text: errores.join(', '),
          icon: "question"
        });
        event.preventDefault();
      } else {
        if (cronometroActivo) {
          cronometroActivo = false;
          clearInterval(intervalo);
          const fecha = new Date();
          const hora = fecha.toLocaleTimeString();
          document.getElementById("hora_salida").innerHTML = hora;
          document.getElementById('parar-cronometro').disabled = true; // Deshabilita el botón de parar
          document.getElementById('btn-cerrar').classList.remove('activar');
          Swal.fire({
            position: "center",
            icon: "success",
            title: "Cirugia Finalizada ! ",
            showConfirmButton: true,
            timer: 1500
          });
      }
      }

      
      
  });

  function verificarDatos() {
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

    const tbodymed = document.getElementById('baremo-seleccionado');
    const rowsmed = tbodymed.getElementsByTagName('tr');
  
    if (rowsmed.length > 0) {
      asignarMedicos = true
    } else {
      Swal.fire({
        icon: "error",
        title: "Personal Medico",
        text: "Debe seleccionar los medicos antes de cerrar la cirugia",
      });
    }

    if (asignarMedicos && farmacosMmq) {
      guardarCiruguaEmergencia()
    }
  }

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
          const fecha = new Date();
          const hora = fecha.toLocaleTimeString();
          document.getElementById("hora_cirugia").innerHTML = hora;
  
          intervalo1 = setInterval(actualizarCronometro1, 10); // Cambia el intervalo1 a 10 milisegundos
          document.getElementById('parar-cronometro1').disabled = false; // Habilita el botón de parar
          document.getElementById('iniciar-cronometro1').disabled = true;
          document.getElementById('parar-cronometro').disabled = true;
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
      }
    });


    $(document).ready(function() {
        $('#tblinventario').on('dblclick', 'tbody tr', function() {
          // Obtener la fila seleccionada
          var fila = $(this);
          // Agregar la fila a la tabla destino
          agregarFilaSeleccionada(fila);
        });
    });
  
      function agregarFilaSeleccionada(fila) {
        // Clonar la fila seleccionada
        var filaClonada = fila.clone();
        //filaClonada.find('td:nth-child(4)').text('1');
        var cantidadInput = fila.find('input[name="cantidad_agregar"]');
        var cantidad = parseInt(cantidadInput.val());
        var precio = parseFloat(fila.find('td:nth-child(5)').text().replace(',','.'));
  
        var nuevoprecio = cantidad * precio
        filaClonada.find('td:nth-child(4)').html('<input type="text" value="' + cantidad + '" readonly class="readonly">');
        filaClonada.find('td:nth-child(5)').text(nuevoprecio.toFixed(2));
        var horaActual = new Date().toLocaleTimeString();
        filaClonada.append('<td>' + horaActual + '</td>');
        var botonEliminar = $('<td><button type="button" class="btn btn-outline-danger btn-sm btn-eliminar pb-0" ><i class="fa-solid fa-trash fa-xs" ></i></button></td>');
        filaClonada.append(botonEliminar);
        // Agregar la fila clonada a la tabla destino
        $('#tbody-tblasignado').append(filaClonada);
  
        calcularTotalPrecio();
        
      }
  
      $(document).on('click', '.btn-eliminar', function() {
        $(this).closest('tr').remove();
        calcularTotalPrecio();
      });
  
  
      function calcularTotalPrecio() {
        var total = 0;
        $('#tbody-tblasignado tr').each(function() {
          var precio = parseFloat($(this).find('td:nth-child(5)').text().replace(',', '.'));
          var cantidad = parseInt($(this).find('td:nth-child(4)').text());
          total += precio ;
        });
        $('#total-precio').text(total.toFixed(2));
      }


function validar() {
  const existePaciente = document.getElementById('id_paciente_emergencia').value
  const nombreProcedimiento = document.getElementById('idprocedimiento').value
  
  if (existePaciente=='') {
    return false 
  }
  if (nombreProcedimiento=='') {
    return false 
  }
  
  return true

}

function guardarCiruguaEmergencia() {
  const cronometroElement = document.getElementById("cronometro");
  const cronometroValue = cronometroElement.innerHTML ; // o también puedes usar textContent
  const horaInicioElement = document.getElementById("hora_entrada");
  const horaInicio = horaInicioElement.innerHTML ;  

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
  var datosTabla1 = [];
    $('#baremo-seleccionado tr').each(function() {
        var fila = {};

            fila['hora_entrada'] = document.getElementById('hora_entrada').textContent;
            fila['cronometro'] = document.getElementById('cronometro').textContent;
            fila['hora_salida'] = document.getElementById('hora_salida').textContent;
            fila['hora_cirugia'] = document.getElementById('hora_cirugia').textContent;
            fila['cronometro1'] = document.getElementById('cronometro1').textContent;
            fila['salida_cirugia'] = document.getElementById('salida_cirugia').textContent;

            fila['horasQx'] = total_horas
            fila['horaInicio'] = horaInicio 
            fila['nroQuirofano'] = document.getElementById('idnroQuirofano').value
            fila['convenio'] = document.getElementById('idconvenio').value
            fila['idPaciente'] = document.getElementById('id_paciente_emergencia').value
            fila['nombreProcedimiento'] = document.getElementById('idprocedimiento').value
            fila['notasProcedimiento'] = document.getElementById('idnotaprocedmiento').value
            fila['id_baremo'] = $(this).find('td:nth-child(1)').text();
            fila['descripcion'] = $(this).find('td:nth-child(2)').text();
            fila['id_medico'] = $(this).find('td:nth-child(3)').text();
            fila['descripcion_medico'] = $(this).find('td:nth-child(4)').text();
            fila['hora_actual'] = $(this).find('td:nth-child(5)').text();

            if (fila['id_medico']=='true' || fila['id_medico']=='True') {
              fila['id_medico'] = $(this).find('td:nth-child(4) select').val();
            } else {
              fila['id_medico'] =''
            }
            
            datosTabla1.push(fila);
      
    });

    var datosTabla2 = []
    $('#tbody-tblasignado tr').each(function() {
        var fila = {};
        var fila = $(this);
        fila['idInv'] = parseInt(fila.attr('id').replace("fila-", ""));
        fila['codigo'] = fila.find('td:nth-child(1)').text().replace(',', '.');
        fila['cantidad'] = fila.find('td:nth-child(4) input').val();
        fila['precio'] = fila.find('td:nth-child(5)').text().replace(',', '.');
        fila['hora_actual'] = fila.find('td:nth-child(6)').text();
        datosTabla2.push(fila);
    });
  

    const datos = {
      tabla1: datosTabla1,
      tabla2: datosTabla2
    }

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var datosJson = {};
        try {
            datosJson = JSON.stringify({ datos: datos });
        } catch (e) {
            console.error('Error al serializar datos:', e);
            return;
        }

    $.ajax({
      type: 'POST',
      url: '/guardar_baremo_seleccionado/',
      data: datosJson,
      headers: {
        'X-CSRFToken': csrfToken
      },
      contentType: 'application/json',
      
      success: function(data) {
          console.log(data.mensaje);
          window.location.href = '/lista_cirugia_finish/';
      },
      error: function(xhr, status, error) {
          console.log('Error al guardar datos');
      }
  });
    
}



