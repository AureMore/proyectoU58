// Obtener el elemento hora_entrada

// Obtener el elemento cronometro
const cronometroElement = document.getElementById('cronometro-factura');
let horas_facturables = 0
// Obtener el valor de hora_entrada
let total_horasx = 0
// Establecer un intervalo para actualizar el cronometro cada segundo
setInterval(() => {
    const horaEntradaElement = document.getElementById('hora_entrada');
    const horaEntradaString = horaEntradaElement.textContent.trim();

    const horaSalidaElement = document.getElementById('hora_salida');
    const horaSalidaString = horaSalidaElement.textContent.trim();

    if (horaEntradaString == '::') {
        console.log("NO HA INICIADO RELOJ DE QUIROFANO")
    } else {
            const horaEntradaParts = horaEntradaString.split(':');
            const horaEntradaHours = parseInt(horaEntradaParts[0]);
            const horaEntradaMinutes = parseInt(horaEntradaParts[1]);
            const horaEntradaSeconds = parseInt(horaEntradaParts[2]);
            const horaSalidaParts = horaSalidaString.split(':');
            const horaSalidaHours = parseInt(horaSalidaParts[0]);
            const horaSalidaMinutes = parseInt(horaSalidaParts[1]);
            const horaSalidaSeconds = parseInt(horaSalidaParts[2]);


              // Obtener la hora actual
            var hora_actual = new Date();
            
            if (horaSalidaString == '::') {
              var currentTimeqx = hora_actual
            } else {
              var currentTimeqx = new Date(hora_actual.getFullYear(), hora_actual.getMonth(), hora_actual.getDate(), horaSalidaHours, horaSalidaMinutes, horaSalidaSeconds);
              const horaEntradaqx = new Date(currentTimeqx.getFullYear(), currentTimeqx.getMonth(), currentTimeqx.getDate(), horaEntradaHours, horaEntradaMinutes, horaEntradaSeconds);
            }

            const horaEntradaqx = new Date(currentTimeqx.getFullYear(), currentTimeqx.getMonth(), currentTimeqx.getDate(), horaEntradaHours, horaEntradaMinutes, horaEntradaSeconds);
            // Calcular el tiempo transcurrido
            const elapsedTime = currentTimeqx - horaEntradaqx;

            // Formatear el tiempo transcurrido como HH:MM:SS
            const hoursqx = Math.floor(elapsedTime / 3600000);
            const minutesqx = Math.floor((elapsedTime % 3600000) / 60000);
            const secondsqx = Math.floor((elapsedTime % 60000) / 1000);

            let htra = hoursqx.toString().padStart(2, '0');
            let mtra = minutesqx.toString().padStart(2, '0');
            let stra = secondsqx.toString().padStart(2, '0');
            let mstra = '000'
            const tiempoTranscurrido = `${htra}:${mtra}:${stra}.${mstra}`;
            // Actualizar el elemento cronometro
            if (hoursqx == NaN) {
                horas_facturables = 0
            }
            
            if (hoursqx == 0) {
                horas_facturables = 1
            } else {
                if (hoursqx > 0 && minutesqx > 19 ) {
                    horas_facturables = hoursqx 
                }
            }
            const [hourx, minutex, secondx, millisecondx] = tiempoTranscurrido.match(/(\d+):(\d+):(\d+)\.(\d+)/).slice(1).map(Number);
            let hr_adicion =0 
            if (hourx == 0) {
                hr_adicion = 1
            } else {
              if (minutex > 20) {
                hr_adicion = 1
              } 
            }
            total_horasx = hourx + hr_adicion
           
    }
    console.log("REFRESCA")
 

  cronometroElement.textContent = `${total_horasx}`;
}, 2000);


/* function refreshTable() {
  console.log('refrescando tabla')
  var id_filter = $('#id_idCirugia').val(); // Obtener el valor del input con id "id_filter"
  $.ajax({
      type: 'GET',
      url: '/refresh_table/' + '?id_filter=' + id_filter,
      dataType: 'html',
      success: function(data) {
          $('#my_table').html(data);
      }
  });
} */