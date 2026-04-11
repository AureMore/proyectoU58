let saveTimeout = null; 
let refreshInterval = null; 


$(document).ready(function() {
    

    $('#tbl-medico-ht').DataTable({
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
        "pageLength": 10 // Establecer la paginación en 25 elementos por página
    });
    // console.log("escucho aqui1");
    const textarea = document.getElementById("texto");
    if (textarea) {
        textarea.addEventListener("input", () => {
            console.log("escucho aqui");
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(autoGuardarNota, 800);
        });
    }
    const cirugiaId = document
                .getElementById("historia_clinica")
                .dataset.cirugiaId;

    /* refreshInterval = setInterval(function () {
        refreshNotaEnfermeria(cirugiaId);
    }, 5000); */
    
  
});



const cronometros = {
  1: { inicio: null, intervalo: null, activo: false, tiempoAcumulado: 0 },
  2: { inicio: null, intervalo: null, activo: false, tiempoAcumulado: 0 },
  3: { inicio: null, intervalo: null, activo: false, tiempoAcumulado: 0 }
};

function toggleCronometro(id) {

if (CIRUGIA_FINALIZADA) {
    alert('⛔ La cirugía está finalizada. No se pueden modificar cronómetros.');
    return;
  }

  const c = cronometros[id];
  const boton = event.currentTarget;
  const historiaId = document.getElementById('historia_id').value;
  const nombre = document.getElementById(`name${id}`).value;

  if (!c.activo) {
    // ▶ INICIAR
    c.inicio = Date.now() - c.tiempoAcumulado;

    c.intervalo = setInterval(() => {
      const transcurrido = Date.now() - c.inicio;
      document.getElementById(`time${id}`).innerText =
        formatearTiempo(transcurrido);
    }, 10);

    boton.innerHTML = `<i class="fa-solid fa-pause" style="color:red;"></i> Detener`;
    c.activo = true;

    fetch('/guardar-cronometro/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        historia_id: historiaId,
        cronometro: id,
        accion: 'iniciar',
        nombre: nombre
      })
    });

  } else {
    // ⏹ DETENER
    clearInterval(c.intervalo);
    c.tiempoAcumulado = Date.now() - c.inicio;

    boton.innerHTML = `<i class="fa-solid fa-play" style="color:green;"></i> Iniciar`;
    c.activo = false;

    fetch('/guardar-cronometro/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        historia_id: historiaId,
        cronometro: id,
        accion: 'detener',
        tiempo_ms: c.tiempoAcumulado
      })
    });
  }
}

function formatearTiempo(ms) {
  const h = Math.floor(ms / 3600000);
  const m = Math.floor((ms % 3600000) / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  const ms2 = ms % 1000;

  return (
    String(h).padStart(2, '0') + ':' +
    String(m).padStart(2, '0') + ':' +
    String(s).padStart(2, '0') + ':' +
    String(ms2).padStart(3, '0')
  );
}

function refreshNotaEnfermeria(id_cirugia) {

    $.ajax({
        type: 'GET',
        url: '/refresh_nota_enfermeria/' + '?id_cirugia=' + id_cirugia ,
        dataType: 'json', // Cambiar a 'json'
        success: function(response) {
            if (response.cambio === 1) {
                console.log('cambio')
                $('#div-nota-enfermeria').html(response.html);
            } else {
                console.log('no cambio')
            }
            
           
        },
        error: function() {
            // Manejo de errores
            alert('Error al refrescar la tabla. Inténtalo de nuevo.');
        }
    }); 
}


  // reconocimiento de voz

let recognition = null;
let escuchando = false;
let textoBase = "";

function toggleListening() {
    const boton = document.getElementById("botonVoz");
    const textarea = document.getElementById("texto");

    if (!escuchando) {
        const SpeechRecognition =
            window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            alert("Reconocimiento de voz no soportado");
            return;
        }

        recognition = new SpeechRecognition();
        recognition.lang = "es-ES";
        recognition.continuous = true;
        recognition.interimResults = true;

        // Guardamos lo que el usuario ya escribió
        textoBase = textarea.value.trim();
        if (textoBase !== "") textoBase += " ";

        recognition.onstart = () => {
            escuchando = true;
            boton.innerHTML = '<i class="fa-solid fa-microphone-slash" style="color:red;"></i> Pausar (Notas enfermeria)';
        };

        recognition.onresult = (event) => {
            let textoTemporal = "";

            for (let i = event.resultIndex; i < event.results.length; i++) {
                textoTemporal += event.results[i][0].transcript;
            }

            textarea.value = textoBase + textoTemporal;
            textarea.dispatchEvent(new Event("input"));
        };

        recognition.onend = () => {
            escuchando = false;
            boton.innerHTML = '<i class="fa-solid fa-microphone" style="color:green;"></i> Hablar (Notas enfermeria)';
            // Se guarda lo dictado
            textoBase = textarea.value;
            autoGuardarNota();
            
        };

        recognition.onerror = (e) => {
            alert('Existe un problema con el microfono, Revise configuracion del microfono en este equipo')
            console.error("Error de voz:", e.error);
        };

        recognition.start();
    } else {
        recognition.stop();
    }
}


// reconocimiento de voz

let recognitioncirugia = null;
let escuchandocirugia = false;
let textoBaseCirugia = "";

function toggleListeningCirugia() {
    const boton = document.getElementById("botonVozCirugia");
    const textarea = document.getElementById("textocirugia");

    if (!escuchandocirugia) {
        const SpeechRecognition =
            window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            alert("Reconocimiento de voz no soportado");
            return;
        }

        recognitioncirugia = new SpeechRecognition();
        recognitioncirugia.lang = "es-ES";
        recognitioncirugia.continuous = true;
        recognitioncirugia.interimResults = true;

        // Guardamos lo que el usuario ya escribió
        textoBaseCirugia = textarea.value.trim();
        if (textoBaseCirugia !== "") textoBaseCirugia += " ";

        recognitioncirugia.onstart = () => {
            escuchandocirugia = true;
            boton.innerHTML = '<i class="fa-solid fa-microphone-slash" style="color:red;"></i> Pausar (Notas cirugia)';
        };

        recognitioncirugia.onresult = (event) => {
            let textoTemporal = "";

            for (let i = event.resultIndex; i < event.results.length; i++) {
                textoTemporal += event.results[i][0].transcript;
            }

            textarea.value = textoBaseCirugia + textoTemporal;
        };

        recognitioncirugia.onend = () => {
            escuchandocirugia = false;
            boton.innerHTML = '<i class="fa-solid fa-microphone" style="color:green;"></i> Hablar (Notas cirugia)';
            // Se guarda lo dictado
            textoBaseCirugia = textarea.value;
        };

        recognitioncirugia.onerror = (e) => {
            alert('Existe un problema con el microfono, Revise configuracion del microfono en este equipo')
            console.error("Error de voz:", e.error);
        };

        recognitioncirugia.start();
    } else {
        recognitioncirugia.stop();
    }
}


function pantallaCompleta() {

    let elem = document.documentElement; // toda la página
    if (document.fullscreenElement) {
        document.exitFullscreen();
    } else {
        if (elem.requestFullscreen) {
            elem.requestFullscreen();
        } else if (elem.webkitRequestFullscreen) { // Safari
            elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) { // IE11
            elem.msRequestFullscreen();
        }

    }

    
}


let ultimoTextoGuardado = "";

function autoGuardarNota(force = false) {
    const textarea = document.getElementById("texto");
    if (!textarea) return;

    const textoActual = textarea.value;
    const historiaId = textarea.dataset.historiaId;

    if (!historiaId) {
        console.warn("⚠️ No hay historia_id");
        return;
    }

    if (!force && textoActual === ultimoTextoGuardado) return;

    ultimoTextoGuardado = textoActual;

    fetch("/guardar-nota-enfermeria/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
            historia_id: historiaId,
            nota: textoActual
        })
    })
    .then(response => {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return response.json();
    })
    .then(data => {
        if (data.ok) {
            console.log("✅ Nota de enfermería guardada correctamente");
        } else {
            console.warn("⚠️ Backend respondió pero no guardó");
        }
    })
    .catch(err => {
        console.error("❌ Error guardando nota:", err);
    });
}


/* // Detecta cambios por escritura o dictado
document.getElementById("texto").addEventListener("input", () => {
    console.log('escucho aqui')
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(autoGuardarNota, 800); // guarda 0.8s después de parar
}); */

function getCSRFToken() {
    return document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="))
        ?.split("=")[1];
}


const textarea = document.getElementById("texto");

function autoResizeTextarea(el) {
    el.style.height = "auto";            // Resetear altura
    el.style.height = el.scrollHeight + "px"; // Ajustar al contenido
}

// Ejecutar al escribir o al dictar
textarea.addEventListener("input", () => {
    autoResizeTextarea(textarea);
});

// También ejecutar al cargar la página para inicializar con el contenido actual
window.addEventListener("load", () => {
    autoResizeTextarea(textarea);
});

function guardarFechaI(fechaIF, tipo, historiaId ) {

    fetch("/guardar_fecha_transoperatoria/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
            historia_id: historiaId,
            fechaIF: fechaIF,
            tipo: tipo
        })
    })
    .then(response => {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return response.json();
    })
    .then(data => {
        if (data.ok) {
            console.log("✅  correctamente");
        } else {
            console.warn("⚠️ Backend respondió pero no guardó");
        }
    })
    .catch(err => {
        console.error("❌ Error guardando nota:", err);
    });
    
}

window.onload = () => {
    final = document.getElementById('finalizada').value
    if (final == 'True') {
        document.getElementById('cronometro1').disabled = true;
        document.getElementById('name1').disabled = true;
        document.getElementById('cronometro2').disabled = true;
        document.getElementById('name2').disabled = true;
        document.getElementById('cronometro3').disabled = true;
        document.getElementById('name3').disabled = true;
        document.getElementById('botonVoz').disabled = true;
        document.getElementById('botonVozCirugia').disabled = true;
        document.getElementById('texto').disabled = true;
        document.getElementById('textocirugia').disabled = true;
        document.getElementById('fecha').disabled = true;
        document.getElementById('fechafinal').disabled = true;

        
    } 


  for (let i = 1; i <= 3; i++) {
    const c = cronometros[i];
    const data = datosBackend[i];

    c.tiempoAcumulado = data.tiempo || 0;

    if (data.nombre) {
      document.getElementById(`name${i}`).value = data.nombre;
    }

    // 🟢 estaba corriendo
    if (data.inicio && data.inicio > 0) {
      c.inicio = data.inicio;
      c.activo = true;

      c.intervalo = setInterval(() => {
        const transcurrido =
          Date.now() - c.inicio + c.tiempoAcumulado;

        document.getElementById(`time${i}`).innerText =
          formatearTiempo(transcurrido);
      }, 10);

      document.querySelector(
        `button[onclick="toggleCronometro(${i})"]`
      ).innerHTML =
        `<i class="fa-solid fa-pause" style="color:red;"></i> Detener`;
    } 
    // 🟡 estaba pausado
    else {
      document.getElementById(`time${i}`).innerText =
        formatearTiempo(c.tiempoAcumulado);
    }
  }
};

function guardaNombreCronometro(nombre_cronometro, historiaId, numero) {
    fetch("/guardar_nombre_cronometro/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
            historia_id: historiaId,
            nombre_cronometro: nombre_cronometro,
            numero: numero
        })
    })
    .then(response => {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return response.json();
    })
    .then(data => {
        if (data.ok) {
            console.log("✅  correctamente");
        } else {
            console.warn("⚠️ Backend respondió pero no guardó");
        }
    })
    .catch(err => {
        console.error("❌ Error guardando nota:", err);
    });
    
}

function finalizarTodo(id_historia) {
    const btn1 = document.getElementById('cronometro1');
    const texto1 = btn1.textContent.trim();
    const btn2 = document.getElementById('cronometro2');
    const texto2 = btn2.textContent.trim();
    const btn3 = document.getElementById('cronometro3');
    const texto3 = btn3.textContent.trim();

    const inputFecha = document.getElementById('fecha');
    const inputFechafinal = document.getElementById('fechafinal');

    var activo = false

    if (texto1.includes('Detener')) {
        activo = true
    } 
    if (texto2.includes('Detener')) {
        activo = true
    }
    if (texto3.includes('Detener')) {
        activo = true
    }

    if (activo) {
        alert('Debe detener los cronometros para finalizar')
    } else {
        if (inputFecha.value && inputFecha.value.trim() !== '') {
            if (inputFechafinal.value && inputFechafinal.value.trim() !== '') {
                console.log('✅ Todos los campos ok para guardar');

                fetch("/guardar_finalizacion_transoperatorio/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken()
                    },
                    body: JSON.stringify({
                        historia_id: id_historia,
                    })
                })
                .then(response => {
                    if (!response.ok) throw new Error("HTTP " + response.status);
                    return response.json();
                })
                .then(data => {
                    if (data.ok) {
                        console.log("✅  correctamente");
                        location.reload()
                    } else {
                        console.warn("⚠️ Backend respondió pero no guardó");
                    }
                })
                .catch(err => {
                    console.error("❌ Error guardando nota:", err);
                });


            } else {
                alert('Debe colocar fecha final')
            }

        } else {
            alert('Debe colocar fecha de inicio')
        }
    }

}