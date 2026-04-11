function agregarFraccionPago() {
    let fraccionPagar = document.getElementById('montopago').value 
    let fraccionReferencia = document.getElementById('idreferencia').value 
    let fraccionNota = document.getElementById('idnota').value 
    let topeBs = document.getElementById('neto_pago_ved').value 
    let topeUsd = document.getElementById('neto_pago_usd').value
    
    topeUsd = parseFloat(topeUsd.replace(',','.'))
    topeBs = parseFloat(topeBs.replace(',','.'))
    fraccionPagar = parseFloat(fraccionPagar.replace(',','.'))

    var id_pago_medico = document.getElementById('tipo_moneda_pago').textContent
    var id_origen_fondos = document.getElementById('tipo_moneda_destino').textContent

    if (id_pago_medico == '' || id_origen_fondos == '' ) {
        alert('Seleccione ambas cuentas de pago')
        return 
    }

    if (id_pago_medico != id_origen_fondos) {
        alert('Las monedas de origen de pago y destino de pago deben ser iguales')
        return 
    }

    
    if (fraccionPagar == 0 || fraccionPagar == '') {
        alert('colocar Monto del Pago')
        return
    }
    if (fraccionReferencia == 0 || fraccionReferencia == '') {
        alert('colocar Referencia del Pago')
        return
    }
    if (id_origen_fondos == 'Bolivares' & fraccionPagar > topeBs ) {
        alert('No puede pagar monto mayor a deuda')
        return
    }

    if (id_origen_fondos == 'Dolares' & fraccionPagar > topeUsd ) {
        alert('No puede pagar monto mayor a deuda')
        return
    }


    id_destino = document.getElementById('cuenta_destino_pago').value
    id_origen = document.getElementById('cuenta_origen_pago').value

    // Crear el tbody
    let tablaBody = document.getElementById('tbodypagos');
    

    let fila = tablaBody.insertRow();
    
            
    // Crear celdas con inputs
    let celdas = [
        `<input type="text" readonly style="text-align:right; display:none;" name="mul_pago_cuenta_medico" value="${id_destino}" />`,
        `<input type="text" readonly style="text-align:right; display:none;" name="mul_pago_origen_fondos" value="${id_origen}" />`,
        `<input type="text" readonly style="text-align:right;" name="mul_montofraccion" value="${fraccionPagar.toFixed(2)}" />`,
        `<input type="text" readonly name="mul_monedapago" value="${id_pago_medico}" />`,
        `<input type="text" readonly name="mul_referencia" value="${fraccionReferencia}" />`,
        `<input type="text" readonly name="mul_nota" value="${fraccionNota}" />`,
        `<button type="button" class="btn btn-danger btn-sm" onclick="eliminarFila(this, ${fraccionPagar}, '${id_pago_medico}')">Quitar</button>`,
       
    ];
    
    fila.dataset.monto = fraccionPagar;
    fila.dataset.moneda = id_pago_medico;

    celdas.forEach(celda => {
        let td = document.createElement('td');
        td.innerHTML = celda; // Usar innerHTML para agregar el input
        fila.appendChild(td);
    });
    saldoCuentas(fraccionPagar,id_pago_medico )
    // Sumar el monto según la moneda

}
var topemonedaUsd = parseFloat(document.getElementById('neto_pago_usd') .value.replace(',','.'))
var topemonedaBs = parseFloat(document.getElementById('neto_pago_ved') .value.replace(',','.'))
let saldoUsd = 0
let saldoBs = 0
const tasa_bcv_calculo = parseFloat(document.getElementById('tasa_bcv_calculo') .value.replace(',','.'))


function saldoCuentas(monto, tipomoneda) {
    
    if (tipomoneda == 'Dolares') {
        saldoUsd = topemonedaUsd - monto
        saldoBs = saldoUsd * tasa_bcv_calculo
        if (parseFloat(saldoUsd) < 0 ) {
            saldoUsd = 0
        }
        document.getElementById('idsaldo').value = saldoUsd.toFixed(2)
    } else {
        saldoBs = topemonedaBs - monto
        saldoUsd = saldoBs / tasa_bcv_calculo
        if (parseFloat(saldoBs) < 0 ) {
            saldoBs = 0
        }
        document.getElementById('idsaldo').value = saldoBs.toFixed(2)
    }
    
    
    
    document.getElementById('neto_pago_usd').value = saldoUsd.toFixed(2)
    document.getElementById('neto_pago_ved').value = saldoBs.toFixed(2)
    topemonedaUsd = saldoUsd
    topemonedaBs = saldoBs

    
}

function eliminarFila(boton, monto, moneda) {
    // 1. Identificar la fila a eliminar
    let fila = boton.parentNode.parentNode;
    
    // 2. Revertir el saldo (Sumar de nuevo a la deuda)
    if (moneda === 'Dolares') {
        topemonedaUsd += monto;
        topemonedaBs = topemonedaUsd * tasa_bcv_calculo;
    } else {
        topemonedaBs += monto;
        topemonedaUsd = topemonedaBs / tasa_bcv_calculo;
    }

    // 3. Actualizar los inputs de la interfaz
    document.getElementById('neto_pago_usd').value = topemonedaUsd.toFixed(2);
    document.getElementById('neto_pago_ved').value = topemonedaBs.toFixed(2);
    
    // Actualizar el saldo visual (puedes elegir cuál mostrar)
    document.getElementById('idsaldo').value = (moneda === 'Dolares' ? topemonedaUsd : topemonedaBs).toFixed(2);

    // 4. Eliminar la fila físicamente
    fila.remove();
}

