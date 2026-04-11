function mostrarImagen(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            var img = document.getElementById('imagen-preview');
            img.src = e.target.result;
            img.width = 300;
            img.height = 200;
        };
        reader.readAsDataURL(input.files[0]);
    }
}


function presupuestoActivado(radioButton) {
    if (radioButton.checked) {
        // Aquí puedes obtener el valor del radio button seleccionado
        var selectedId = radioButton.value;
        document.getElementById('id_idpresupuesto').value = selectedId

        $.ajax({
            type: "GET",
            url: "/buscar-convenio/",
            data: {
                selected_Id: selectedId
            },
            success: function(data) {
                
                // Aquí puedes procesar las variables devueltas por Django
                var nombre_convenio = data.nombre_convenio;
                var medicoId = data.medicoId;
                var pacienteNombre = data.pacienteNombre;
                var pacienteCedula = data.pacienteCedula;
                var procedimiento = data.procedimiento;
                var horaCirugia = data.horaCirugia;
                var fecha_procedimiento = data.fecha_procedimiento;
                const fecha = new Date(fecha_procedimiento);
                const meses = [
                    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
                  ];
                const dia = fecha.getDate()+1;
                const mes = meses[fecha.getMonth()];
                const anio = fecha.getFullYear();

                document.getElementById('id_nombre_convenio').innerHTML = `<b>${nombre_convenio}</b>`;
                let selectMedico = document.getElementById('medico');
                selectMedico.value = medicoId;
                const textoConsentimiento = document.getElementById('texto-consentimiento');
                textoConsentimiento.innerHTML = `
                    Yo <b><u>${pacienteNombre}</u></b>, con cedula de identidad <b> <u>${pacienteCedula}</u></b>  
                    acepto ser hospitalizado(a) y/o intervenido(a) quirúrgicamente en Unidad Quirúrgica Vizcaya CA. Después de ser informado(a) de la naturaleza, 
                    necesidad y posibles complicaciones del procedimiento quirúrgico, <u><b>${procedimiento}</b></u> manifiesto mi aceptación a su realización. 
                    He recibido respuesta a mis preguntas y duda. He tomado la decisión de aceptar el procedimiento de manera libre y voluntaria.
                    He comprendido el contenido de este consentimiento, por lo que dejo la presente constancia a las <u><b>${horaCirugia}</b></u> horas
                    del día <b>${dia} de ${mes} del año ${anio}</b> . He aceptado las normas de la institución y me comprometo a cumplirlas ,
                    he sido informado(a) que las instalaciones de la unidad no se debe generar, realizar, ni publicar material audiovisual , sin la autorización de la directiva o personal responsable.
                `;
                // ...
              }
            });
    }
}


function cambioCongelado(checkbox, presupuestoId) {
    var cambio_congelado = 'False'
    if (checkbox.checked) {
      $('#cambioCongeladoCambiar').modal('show')
        cambio_congelado = 'True'
      // realizar acción cuando el checkbox está seleccionado
    } 

    const datos = {
        cambio_congelado : cambio_congelado,
        presupuestoId : presupuestoId,
      };
    
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
      fetch('/congelar_cambio/', {
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
      })
      .catch(error => console.error(error));



  }

function buscarCambio() {
  const fecha_cambio_congelado = document.getElementById('fecha_cambio_congelado').value
 
  const date = new Date(fecha_cambio_congelado);
  const fechaFormatted = `${date.getFullYear()}-${padZero(date.getMonth() + 1)}-${padZero(date.getDate() + 1)} ${padZero(date.getHours())}:${padZero(date.getMinutes())}:${padZero(date.getSeconds())}.${padZero(date.getMilliseconds(), 6)}`;
  console.log("Fecha")
  console.log(fechaFormatted)
  // Make an AJAX request to your Django backend
  const xhr = new XMLHttpRequest();
  xhr.open('GET', `/buscar_cambio_desde_js/?fecha_cambio_congelado=${fechaFormatted}`, true);
  xhr.onload = function() {
    if (xhr.status === 200) {
      const response = JSON.parse(xhr.responseText);
      const monto = response.monto; // Assuming the Django backend returns a JSON response with a 'fecha' key
      document.getElementById('monto_cambio_congelado').value = monto; // Update the input field with the retrieved date
    }
  };
  xhr.send();

}

function padZero(value, length = 2) {
  return String(value).padStart(length, '0');
}