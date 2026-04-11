// por aqui pasa atencion medica inmediata y tambien PREINGRESOS NEW
function buscarPaciente(cedula) {
  const boton_historias = document.getElementById('boton_historias_anteriores');
    const datos = {
        cedula : cedula,
      };
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch('/buscar_paciente_existe/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('nombrepaciente').value = data.nombre
        document.getElementById('apellidopaciente').value = data.apellido
        document.getElementById('fecha_nac_paciente').value = data.fecha_nac
        document.getElementById('idPaciente').value = data.idPaciente
        if (data.cirugias_activas > 0) {
            alert('No puede hacer un preingreso de un paciente con una admision en proceso')
            
            document.getElementById('cedula_atencion_inmediata').value = ''
            document.getElementById('nombrepaciente').value = ''
            document.getElementById('fecha_nac_paciente').value = ''
            document.getElementById('idPaciente').value = 0
            return
        }
        if (data.amis_activas > 0) {
            alert('Ya el paciente tiene una (AMI) admision en proceso, Revise')
            
            document.getElementById('cedula_atencion_inmediata').value = ''
            document.getElementById('nombrepaciente').value = ''
            document.getElementById('fecha_nac_paciente').value = ''
            document.getElementById('idPaciente').value = 0
            return
        } 
        
        if (data.amis_cortesia_activas > 0) {
            alert('Ya el paciente tiene una (AMC) admision cortesia en proceso, Revise')
            
            document.getElementById('cedula_atencion_inmediata').value = ''
            document.getElementById('nombrepaciente').value = ''
            document.getElementById('fecha_nac_paciente').value = ''
            document.getElementById('idPaciente').value = 0
            return
        } 

        if (data.historial == 'True') {
          boton_historias.style.display = 'block';

          if (data.cirugias_anteriores && data.cirugias_anteriores.length > 0) {
            // Por ejemplo, mostrar las cirugías en una lista
            const cirugiasList = document.getElementById('cirugiasList'); // Asegúrate de tener un elemento con este ID
            cirugiasList.innerHTML = ''; // Limpiar la lista antes de agregar nuevos elementos

            data.cirugias_anteriores.forEach(cirugia => {
                const fechaAct = new Date(cirugia.fecha_act); // Convertir la fecha a un objeto Date
                const dia = String(fechaAct.getDate()).padStart(2, '0'); // Obtener el día y agregar un cero a la izquierda si es necesario
                const mes = String(fechaAct.getMonth() + 1).padStart(2, '0'); // Obtener el mes (0-11) y agregar un cero a la izquierda
                const anio = fechaAct.getFullYear(); // Obtener el año

                const fechaFormateada = `${dia}/${mes}/${anio}`; // Formato d/m/y
                const listItem = document.createElement('li');

               // Crear un enlace que actúe como botón
               const link = document.createElement('a');
               link.textContent =`CIRUGÍA: ${cirugia.id} -`; // Mostrar el ID de la cirugía
               link.href = `/entrada_quirofano/${cirugia.id}/`; // Ajusta la URL según tu ruta
               link.target = '_blank'; // Abrir en una nueva pestaña
               link.style.display = 'inline-block'; // Para que se vea como un botón

               // Agregar el enlace y la fecha al elemento de lista
               listItem.appendChild(link);
               listItem.appendChild(document.createTextNode(`- Fecha: ${fechaFormateada} - Procedimiento: ${cirugia.nombre_procedimiento}`)); // Agregar texto adicional
               cirugiasList.appendChild(listItem);
            });
          }

        } else {
          boton_historias.style.display = 'none';
        }
        
        if (data.presupuestos_activos && data.presupuestos_activos.length > 0) {

           // Crear el selector HTML
                let selectHTML = '<select id="presupuestoSeleccionado" class="presupuesto-selector">';
                
                // Agregar opción por defecto
                selectHTML += '<option value="" disabled selected>-- Seleccione un presupuesto --</option>';
                
                // Agregar cada presupuesto como opción
                data.presupuestos_activos.forEach(presupuesto => {
                    selectHTML += `<option value="${presupuesto.id}">${presupuesto.id} - ${presupuesto.nombre_procedimiento} </option>`;
                });

              //selectHTML += '</select>';
                    //        data.presupuestos_activos.forEach(presupuesto => {
                    //selectHTML += `<option value="${presupuesto.id}">${presupuesto.id} - ${presupuesto.nombre_procedimiento} </option>`;
                //});
                
                selectHTML += '</select>';
                
                Swal.fire({
                    title: "Presupuesto a Vincular",
                    text: "Cliente con varios presupuestos debe seleccionar el presupuesto a vincular al PreIngreso",
                    html: selectHTML,
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#3085d6",
                    cancelButtonColor: "#d33",
                    confirmButtonText: "Continuar",
                    allowOutsideClick: false,
                    preConfirm: () => {
                        const seleccionado = document.getElementById('presupuestoSeleccionado').value;
                        if (!seleccionado) {
                            Swal.showValidationMessage('Debe seleccionar un presupuesto');
                            return false;
                        }
                        return seleccionado;
                    }
                }).then((result) => {
                    if (result.isConfirmed) {
                        const presupuestoId = result.value;
                        const presupuestoSeleccionado = data.presupuestos_activos.find(p => p.id == presupuestoId);
                        
                        // Aquí puedes hacer lo que necesites con el presupuesto seleccionado
                        console.log('presupuesto seleccionado:'+presupuestoId)
                        document.getElementById('id_presupuesto_vinculado').value = presupuestoId
                        //mostrarResultado(presupuestoSeleccionado);
                    } else {
                        window.location.href = `/listado_preingresos/`;
                    }
                });
          
        }

    })
    .catch(error => console.error(error));

     
}