let seleccionadaFila = null;
let seleccionadaFilaOrigen = null;
let monedaOrigen = null
let monedaDestino = null


function aplicarPago(monedaCongelada) {
  
    var nrodocumento = document.getElementById('nrodocumento').value;
    var nrocontrol = document.getElementById('nrocontrol').value;
    
    //let netoPagar = document.getElementById('monto_id_usd').textContent;
    //let netoPagarBolivar = document.getElementById('monto_id_ved').textContent;
    //document.getElementById('neto_pago_usd').value = netoPagar
    //document.getElementById('neto_pago_ved').value = netoPagarBolivar


    if (monedaCongelada > 0) {
      document.getElementById('neto_pago_usd').value = 0
      
    }
     
    // Realizas la validación de los campos
    if (nrodocumento === '' || nrocontrol === '') {
      Swal.fire({
        title: "Campos Necesarios",
        text: "Numero de documento y numero de control deben completarse",
        icon: "error"
      });
      return ; // Si la validación falla, se cancela el envío del formulario
    } else {
        $('#myModalPago').modal('show');

    }

    
}


function resetearFilas() {
  // Seleccionamos todas las filas
  var filas = document.getElementById("destino-pago").getElementsByTagName("tr");
  
  // Resetamos el estilo de cada fila
  for (var i = 0; i < filas.length; i++) {
    var celdas = filas[i].getElementsByTagName("td");
    for (var j = 0; j < celdas.length; j++) {
      celdas[j].style.color = ""; // Resetamos el color de las letras
      celdas[j].style.fontWeight = "";
    }
  }
}

let fraccionaPagar = 1

function colocaMontoPago() {
  var moneda1 = document.getElementById('monedaOrigen').value
  var moneda2 = document.getElementById('monedaDestino').value
  document.getElementById('displaymoneda').textContent = 'Monto'
  if (moneda1 == moneda2) {
    if (moneda1 == 'Dolares') {
      fraccionaPagar = document.getElementById('neto_pago_usd').value 
      document.getElementById('montopago').value = fraccionaPagar
      document.getElementById('displaymoneda').textContent = moneda1
      
    }
    if (moneda1 == 'Bolivares') {
      fraccionaPagar = document.getElementById('neto_pago_ved').value 
      document.getElementById('montopago').value = fraccionaPagar
       document.getElementById('displaymoneda').textContent = moneda1
      
    }

  } else {

    document.getElementById('montopago').value = fraccionaPagar = 0

  }



}
let id_pago_medico

function seleccionarFila(radio) {
  resetearFilas();
  if (radio.checked) {
    seleccionadaFila = radio.value;
  } else {
    seleccionadaFila = null;
  }
  // Seleccionamos la fila correspondiente al radio button seleccionado
  var fila = document.getElementById("fila-" + radio.id.replace("flexRadioDefault", ""));
  
  // Seleccionamos todos los elementos <td> dentro de la fila
  var celdas = fila.getElementsByTagName("td");
  monedaDestino=celdas[5].textContent
  id_pago_medico = celdas[1].textContent
  document.getElementById('id_cuenta_beneficiara_medico').value = id_pago_medico
  
  var fila = radio.closest('tr');
  var monedaInput = fila.querySelector('td input[type="text"]');
  document.getElementById('monedaDestino').value = monedaInput.value
  
  // Cambiamos el estilo de cada celda
  for (var i = 0; i < celdas.length; i++) {
    celdas[i].style.color = "red"; // Cambiamos el color de las letras a azul
    celdas[i].style.fontWeight = "bold"; // Hacemos que la letra sea negrita
  }
  colocaMontoPago()
}


function resetearFilasOrigen() {
  // Seleccionamos todas las filas
  var filas = document.getElementById("origen-pago").getElementsByTagName("tr");
  
  // Resetamos el estilo de cada fila
  for (var i = 0; i < filas.length; i++) {
    var celdas = filas[i].getElementsByTagName("td");
    for (var j = 0; j < celdas.length; j++) {
      celdas[j].style.color = ""; // Resetamos el color de las letras
      celdas[j].style.fontWeight = "";
    }
  }
  
}

function seleccionarFilaOrigen(radio) {
  resetearFilasOrigen();
  if (radio.checked) {
    seleccionadaFilaOrigen = radio.value;
  } else {
    seleccionadaFilaOrigen = null;
  }
  // Seleccionamos la fila correspondiente al radio button seleccionado
  var filaorigen = document.getElementById("filaorigen-" + radio.id.replace("origenPago", ""));
  
  // Seleccionamos todos los elementos <td> dentro de la fila
  var celdas = filaorigen.getElementsByTagName("td");
  monedaOrigen = celdas[4].textContent
  id_pago_medico = celdas[1].textContent
  document.getElementById('id_cuenta_origen_fondos').value = id_pago_medico

  var fila = radio.closest('tr');
  var monedaInput = fila.querySelector('td input[type="text"]');
  document.getElementById('monedaOrigen').value = monedaInput.value

  // Cambiamos el estilo de cada celda
  for (var i = 0; i < celdas.length; i++) {
    celdas[i].style.color = "red"; // Cambiamos el color de las letras a azul
    celdas[i].style.fontWeight = "bold"; // Hacemos que la letra sea negrita
  }
  colocaMontoPago()
}


function validarFormulario() {
  let montoDolar = document.getElementById('neto_pago_usd').value
  var referencia = document.getElementById('referencia_pago').value
  var nomCampo = ''
  if (referencia === '') {
    nomCampo = 'Numero de referencia debe completarse' 
    Swal.fire({
      title: "Validando",
      text: nomCampo,
      icon: "error"
    });
  }
  if (seleccionadaFila === null) {
    nomCampo = 'Debe seleccionar un destino de pago'
    Swal.fire({
      title: "Validando",
      text: nomCampo,
      icon: "error"
    });
  }

  if (seleccionadaFilaOrigen === null) {
    nomCampo = 'Debe seleccionar un origen de fondos'
    Swal.fire({
      title: "Validando",
      text: nomCampo,
      icon: "error"
    });
  }

  if (monedaDestino != monedaOrigen) {
    nomCampo = 'Las monedas entre el origen de fondos y destino de pago no pueden ser diferentes'
    Swal.fire({
      title: "Validando",
      text: nomCampo,
      icon: "error"
    });
  }

  if ( montoDolar == 0 && monedaOrigen =='Dolares' ) {
    nomCampo = 'En los recibos hay cambio congelado y no puede pagar en Dolares escoja otra moneda'
    Swal.fire({
      title: "Validando",
      text: nomCampo,
      icon: "error"
    });

  }



  if (nomCampo === '') {
    $('#spinnerEsperar').modal('show')
    return true
  } else {
    return false
  }
 
}