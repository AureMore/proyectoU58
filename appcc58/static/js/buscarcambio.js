function cambioTasa(){
    const fecha_cambio_congelado = document.getElementById('fecha_cambio_buscar').value
   
    const date = new Date(fecha_cambio_congelado);
    const fechaFormatted = `${date.getFullYear()}-${padZero(date.getMonth() + 1)}-${padZero(date.getDate() + 1)} ${padZero(date.getHours())}:${padZero(date.getMinutes())}:${padZero(date.getSeconds())}.${padZero(date.getMilliseconds(), 6)}`;
    // Make an AJAX request to your Django backend
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `/buscar_cambio_desde_js/?fecha_cambio_congelado=${fechaFormatted}`, true);
    xhr.onload = function() {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        let monto = response.monto; // Assuming the Django backend returns a JSON response with a 'fecha' key
        monto = Math.floor(monto * 100) / 100;
        document.getElementById('tasa-cambio').value = monto; // Update the input field with the retrieved date
        const montoInputDl = parseFloat(document.getElementById('monto-cobrado').value);

        document.getElementById('monto-pago-bs').value = (montoInputDl * monto).toFixed(2)
        document.getElementById('neto-cobrado-usd').value = (montoInputDl).toFixed(2)
        document.getElementById('neto-cobrado-bs').value = (montoInputDl * monto).toFixed(2)

      }
    };
    xhr.send();

  
}

function padZero(value, length = 2) {
    return String(value).padStart(length, '0');
}

function cambioTasaMonto(montoTasa) {
        const montoInputDl = parseFloat(document.getElementById('monto-cobrado').value);
        document.getElementById('monto-pago-bs').value = (montoInputDl * montoTasa).toFixed(2)

}

