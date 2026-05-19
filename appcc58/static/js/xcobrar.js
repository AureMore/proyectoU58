function cambioConcepto(idConcepto, pNatural, pJuridico, pSustraendo, pTope){
    const idProveedor = document.getElementById('cedula-pagador').value.trim()
    let montoaRetener = parseFloat(document.getElementById('monto-pago-bs').value.replace(',','.'))
    let tasaCambio = parseFloat(document.getElementById('tasa-cambio').value.replace(',','.'))

    if (typeof pNatural === 'string') {
        pNatural = parseFloat(pNatural.replace(',','.')).toFixed(2)
    } else {
        pNatural = parseFloat(pNatural).toFixed(2)
    }

    if (typeof pJuridico === 'string') {
        pJuridico = parseFloat(pJuridico.replace(',','.')).toFixed(2)
    } else {
        pJuridico = parseFloat(pJuridico).toFixed(2)
    }



    if (idProveedor == '') {
        document.getElementById('concepto-retencion').value = ''
        Swal.fire("Debe indicar los datos del pagador");
        return

    }

    if (idConcepto == '') {
        pNatural = 0
        pJuridico = 0
        pSustraendo = 0

    }


    if (montoaRetener == 0) {
        document.getElementById('concepto-retencion').value = ''
        Swal.fire("Debe indicar el monto a cobrar");
        return
    }
    var typePerson = idProveedor.charAt(0);
    let procentajeRetencion = 0
    if (typePerson == 'J' || typePerson == 'G') {
        procentajeRetencion = pJuridico
    } else {
        procentajeRetencion = pNatural
    }
    let porcentaje_reverso = (100 - procentajeRetencion)/100
    
    
    procentajeRetencion = parseFloat(procentajeRetencion)
    document.getElementById('porc-retencion').value = procentajeRetencion
    if (procentajeRetencion > 0) {
        /* let monto_con_retencion_dl = parseFloat(document.getElementById('monto_con_retencion_dl').value.replace(',','.'))
        let monto_sin_retencion_dl = parseFloat(document.getElementById('monto_sin_retencion_dl').value.replace(',','.'))
        let total_general_monto_dl = parseFloat(document.getElementById('total_general_monto_dl').value.replace(',','.'))
        let tasa_usar = parseFloat(document.getElementById('tasa-cambio').value.replace(',','.'))

        document.getElementById('monto_con_retencion_dl').value =( monto_con_retencion_dl * tasa_usar).toFixed(2)
        document.getElementById('monto_sin_retencion_dl').value =( monto_sin_retencion_dl * tasa_usar).toFixed(2)
        document.getElementById('total_general_monto_dl').value =  ((monto_con_retencion_dl * tasa_usar) + ( monto_sin_retencion_dl * tasa_usar)).toFixed(2)

        $('#idmontossobreRetencion').modal('show') */
        CuadroRetenciones()
    } else {

        let monto_bruto_calculado = montoaRetener / porcentaje_reverso
        let netoRetenido = monto_bruto_calculado - montoaRetener
        let netoCobrado = montoaRetener
        let netoDolar = netoCobrado / tasaCambio

        
        document.getElementById('monto-retencion').value = netoRetenido.toFixed(2)
        document.getElementById('neto-cobrado-bs').value = netoCobrado.toFixed(2)
        document.getElementById('neto-cobrado-usd').value = netoDolar.toFixed(2)

    }
   
    
    //recalcularMontos()
} 

function recalcularMontos() {
    console.log('monto')
    let tasaCambio = parseFloat(document.getElementById('tasa-cambio').value.replace(',','.'))
    let montoaRetener = parseFloat(document.getElementById('monto-pago-bs').value.replace(',','.'))
    let porcentajeRetencion = document.getElementById('porc-retencion').value
    let porcentaje_reverso = (100 - porcentajeRetencion)/100
    let monto_bruto_calculado = montoaRetener / porcentaje_reverso
    let netoRetenido = monto_bruto_calculado - montoaRetener
    let netoDolar = montoaRetener / tasaCambio
    document.getElementById('monto-retencion').value = netoRetenido.toFixed(2)
    document.getElementById('neto-cobrado-usd').value = netoDolar.toFixed(2)
    document.getElementById('neto-cobrado-bs').value = montoaRetener.toFixed(2)

    //let montobrutoUsd = parseFloat(document.getElementById('monto-cobrado').value.replace(',','.'))
    
    //let montoRetenidoBs = parseFloat(document.getElementById('monto-retencion').value.replace(',','.'))
    //let netoCobrado = montobrutoBs - montoRetenidoBs
    
}

function inputNetoCobradoBs() {
    let tasaCambio = parseFloat(document.getElementById('tasa-cambio').value.replace(',','.'))
    let inputNetoBs = document.getElementById('neto-cobrado-bs').value
    let montobrutoBs = parseFloat(document.getElementById('monto-pago-bs').value.replace(',','.'))
    let montoRetenidoBs = montobrutoBs - inputNetoBs
    let netoDolar = inputNetoBs / tasaCambio
    document.getElementById('monto-retencion').value = montoRetenidoBs.toFixed(2)
    document.getElementById('neto-cobrado-usd').value = netoDolar.toFixed(2)

}


function validarCampos() {
    var msjValidacion = ''
    const monDol = document.getElementById('monto-cobrado').value
    const cedPag = document.getElementById('cedula-pagador').value
    const nomPag = document.getElementById('nombre-pagador').value
    const forPag = document.getElementById('forma-pago').value
    const moneda_recibo =  document.getElementById('moneda_recibo').value
    var moneda_pago = '2'
    if (forPag == '5' || forPag == '6' || forPag == '9' || forPag == '10' || forPag == '12' || forPag == '16' ) {
        moneda_pago = '1'
    }

    if (moneda_pago != moneda_recibo) {
        msjValidacion = 'Tipo de Moneda de pago y cuenta receptora de fondos es distinta, revise!'
        Swal.fire({
        title: "Validando",
        text: msjValidacion,
        icon: "error"
        });
    }

    //const banPag = document.getElementById('banco-pago').value
    const refPag = document.getElementById('referencia-pago').value
    if (monDol == '' || monDol == 0){
        msjValidacion = 'Indicar el monto a cobrar'
        Swal.fire({
        title: "Validando",
        text: msjValidacion,
        icon: "error"
        });
    }
    if (cedPag == '' || nomPag == '' ){
        msjValidacion = 'Indicar datos cedula y nombre pagador'
        Swal.fire({
            title: "Validando",
            text: msjValidacion,
            icon: "error"
            });
    }
    if (forPag == ''  ){
        msjValidacion = 'Indicar forma de pago'
        Swal.fire({
            title: "Validando",
            text: msjValidacion,
            icon: "error"
            });
    }
    if (refPag == '' ){
        msjValidacion = 'Indicar referencia del pago'
        Swal.fire({
            title: "Validando",
            text: msjValidacion,
            icon: "error"
            });
    }

    if (msjValidacion == '') {
        $('#spinnerEsperar').modal('show')
        //event.target.submit();
        return true
    } else {
        //Swal.fire(msjValidacion);
        return false
    }
}

var montoInputDl = document.getElementById('monto-cobrado');
let montoTransformadoDl = 0

montoInputDl.addEventListener('input', function() {
    if (typeof montoInputDl.value === 'string') {
        montoTransformadoDl = montoInputDl.value.replace(',','.')
    } else {
        montoTransformadoDl = montoInputDl.value
    }
    const montoCambioBcv = parseFloat(document.getElementById('tasa-cambio').value.replace(',','.')).toFixed(4)
    let montoBolivares = parseFloat(montoTransformadoDl).toFixed(2) * montoCambioBcv

    document.getElementById('monto-pago-bs').value = montoBolivares.toFixed(2)
});


const montoInputBs = document.getElementById('monto-pago-bs');

montoInputBs.addEventListener('input', function() {

    const montoCambioBcv = parseFloat(document.getElementById('tasa-cambio').value.replace(',','.')).toFixed(4)
    let montoDolares = parseFloat(montoInputBs.value).toFixed(2) / montoCambioBcv

    document.getElementById('monto-cobrado').value = montoDolares.toFixed(2)
});

function buscarPagador(vcedulapagador, saldo_deudor) {

    if (typeof saldo_deudor === 'string' ) {
                saldo_deudor = saldo_deudor.replace(',','.')
            }
    saldo_deudor = parseFloat(saldo_deudor).toFixed(2)
    document.getElementById('concepto-retencion').value = ''
    // Make a fetch request to your Django backend
    fetch(`/buscar_pagador_notacredito/?vcedulapagador=${vcedulapagador}`)
        .then(response => { 
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const nombre = data.nombre; // Assuming the Django backend returns a JSON response with a 'nombre' key
            const telefono = data.telefono;
            var total_saldo = data.total_saldo
            let cantidad_notacredito = data.cantidad_existe_notacredito
            if (typeof total_saldo === 'string' ) {
                total_saldo = total_saldo.replace(',','.')
            }
            
            total_saldo = parseFloat(total_saldo).toFixed(2)
            cantidad_notacredito = parseFloat(cantidad_notacredito)
            document.getElementById('cedula-pagador').value = vcedulapagador;
            document.getElementById('nombre-pagador').value = nombre;
            document.getElementById('telefono-pagador').value = telefono;
            
                // modal de notas de credito cuando tiene + de 1 pendiente
                if (total_saldo > 0 ) {
                    console.log('total_saldo:' + total_saldo)
                    muestraModalNotasCredito()
                }
                
                //fin modal de notas de credito cuando tiene + de 1 pendiente
            
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}


function monedaRecibo(moneda_id) {
    console.log('moneda recibo:'+moneda_id)
    document.getElementById('moneda_recibo').value = moneda_id
}

function mostrarModalDetalle(id_ctacobrar) {
    document.getElementById('id_detallectaxcobrar').value = id_ctacobrar
    $('#pedirDetalle').modal('show')
}

function imprimirRecibo() {
  let id_ctacobrar =  document.getElementById('id_detallectaxcobrar').value
  var checkbox = document.getElementById("flexCheckDefault");
  if (checkbox.checked) {
      window.open(`/pdf_recibocxc_detalle/${id_ctacobrar}/`, '_blank', 'noopener,noreferrer');
  } else {
        window.open(`/pdf_recibocxc/${id_ctacobrar}/`, '_blank', 'noopener,noreferrer');
        //window.location.href = `/pdf_recibocxc/${id_ctacobrar}/`;

  }

}

function refreshTablaCirugiasPagadorNC(parametro1) {
    $.ajax({
        type: 'GET',
        url: '/refresh_table_cirugia_pagador_notacredito_seleccion/' + '?parametro1=' + parametro1 ,
        dataType: 'json',
        success: function(response) {
            // Actualizar el HTML de la tabla
            $('#tabla-nc-pendiente').html(response.html);
            // Leer el valor de total_subtotal
            // Ejecutamos el callback cuando todo está listo
            
        },
        error: function() {
            // Manejo de errores (opcional)
            alert('Error al cargar los datos. Inténtalo de nuevo.');
            $('#notaCreditoPagador').modal('hide'); // Asegúrate de ocultar el modal en caso de error
        }


    }); 
}


function muestraModalNotasCredito() {
    const cedula_pagador = document.getElementById('cedula-pagador').value
    refreshTablaCirugiasPagadorNC(cedula_pagador)
    $('#notaCreditoPagador').modal('show')
    console.log('pagador:'+cedula_pagador)
    
}

function validarMontoNC(saldo_disponible_nc_dl, nuevo_monto_dl, bcr_id) {
    if (parseFloat(nuevo_monto_dl) > parseFloat(saldo_disponible_nc_dl)) {
        alert('No puede aplicar un monto superior al saldo actual de la nota de credito!')
        document.getElementById('saldo_actual_'+ bcr_id).value = parseFloat(saldo_disponible_nc_dl).toFixed(2)
        document.getElementById('saldo_actual_'+ bcr_id).focus()
        return
    }
}

function aplicar_nc_seleccion() {
    
    const saldo_actual = parseFloat(document.getElementById('monto-cobrado').value.replace(',','.'))
    

    let seleccionados = [];
    let total_seleccionado = 0
    const cuentacobrar_id = document.getElementById('id_cuentaxcobrar').value
    // Buscar todas las filas con checkbox marcado
    document.querySelectorAll("#tblnotacreditoseleccion tr").forEach(function(row) {
        let checkbox = row.querySelector(".fila-check");
        if (checkbox && checkbox.checked) {
            let filaData = {
                id: row.cells[0].innerText.trim(),
                fecha: row.cells[1].innerText.trim(),
                descripcion: row.cells[2].innerText.trim(),
                saldo: row.cells[3].innerText.trim().replace(',','.'),
                aplicar: (row.cells[4].querySelector('input').value).replace(',','.'),
                usuario: row.cells[5].innerText.trim(),
                cuentacobrar_id: cuentacobrar_id
            };
            total_seleccionado += parseFloat(filaData.aplicar)
            seleccionados.push(filaData);
        }
    });
    if (seleccionados.length === 0) {
        alert("No seleccionaste ninguna nota de credito.");
        return;
    }

    if (parseFloat(saldo_actual) < parseFloat(total_seleccionado) ) {
        alert('El monto aplicar de nota de credito es superior al saldo del paciente!')
        return;
    }
        

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/procesar_ncr_seleccionada_v2/', {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            'X-CSRFToken': csrftoken  // importante en Django
        },
        body: JSON.stringify({ datos: seleccionados }),
    })
    .then((res) => res.json())
    .then((data) => {
        console.log("Respuesta del servidor:", data);
        alert("Se Aplicaron " + data.procesados + " notas de credito al cliente.");
        location.reload()
    })
    .catch((err) => console.error("Error:", err));

}

function verificaCuentareceptora(nforma_pago) {
    if (nforma_pago == '16') {
        document.getElementById('destino_cobro').value = 14
        document.getElementById('moneda_recibo').value = 1
    }
}

function aplicacionNotaCredito() {
    let monto_notas_pendiente = document.getElementById('id_total_nc_pendientes').value
    let saldo_actual = document.getElementById('id_saldo_total').value

    if (typeof saldo_actual === 'string') {
        saldo_actual = parseFloat(saldo_actual.replace(',','.')).toFixed(2)
    } else {
        saldo_actual = parseFloat(saldo_actual).toFixed(2)
    }
    
    if (typeof monto_notas_pendiente === 'string') {
        monto_notas_pendiente = parseFloat(monto_notas_pendiente.replace(',','.')).toFixed(2)
    } else {
        monto_notas_pendiente = parseFloat(monto_notas_pendiente).toFixed(2)
    }
    if (monto_notas_pendiente > 0 && saldo_actual > 0) {
        $('#notaCreditoMismaCuenta').modal('show')
    }
    
    
}

function aplicar_nc_misma_cuenta() {
    let seleccionados = [];
    const cuentacobrar_id = document.getElementById('id_cuentaxcobrar').value
    // Buscar todas las filas con checkbox marcado
    document.querySelectorAll("#tblnotacreditoseleccion tr").forEach(function(row) {
        let checkbox = row.querySelector(".fila-check");
        if (checkbox && checkbox.checked) {
            let filaData = {
                id: row.cells[0].innerText.trim(),
                fecha: row.cells[1].innerText.trim(),
                descripcion: row.cells[2].innerText.trim(),
                saldo: row.cells[3].innerText.trim().replace(',','.'),
                usuario: row.cells[4].innerText.trim(),
                cuentacobrar_id: cuentacobrar_id
            };
            seleccionados.push(filaData);
        }
    });
    if (seleccionados.length === 0) {
        alert("No seleccionaste ninguna nota de credito.");
        return;
    }
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/procesar_ncr_seleccionada_misma_cuenta/', {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            'X-CSRFToken': csrftoken  // importante en Django
        },
        body: JSON.stringify({ datos: seleccionados }),
    })
    .then((res) => res.json())
    .then((data) => {
        console.log("Respuesta del servidor:", data);
        alert("Se Aplicaron " + data.procesados + " notas de credito al cliente.");
        location.reload()
    })
    .catch((err) => console.error("Error:", err));

}

function abrimodalCobro(saldo_actual) {
    document.getElementById('monto-cobrado').value = parseFloat(saldo_actual).toFixed(2)
    let tasaCambio = parseFloat(document.getElementById('tasa-cambio').value.replace(',','.'))
    document.getElementById('monto-pago-bs').value = (parseFloat(saldo_actual) * tasaCambio).toFixed(2)
    recalcularMontos()
    $('#registroCobro').modal('show')
    
}

function CuadroRetenciones() {
    var concepto_retencion_valido = document.getElementById('concepto-retencion').value
    let monto_ingresado_manual = document.getElementById('monto-pago-bs').value
    if (typeof monto_ingresado_manual === 'string') {
        monto_ingresado_manual = parseFloat(monto_ingresado_manual.replace(',','.')).toFixed(2)
    } else {
        monto_ingresado_manual = parseFloat(monto_ingresado_manual).toFixed(2)
    }

    

    if (concepto_retencion_valido != '' ) {
        let monto_con_retencion_dl = parseFloat(document.getElementById('monto_con_retencion_dl').value.replace(',','.'))
        let monto_sin_retencion_dl = parseFloat(document.getElementById('monto_sin_retencion_dl').value.replace(',','.'))
        let total_general_monto_dl = parseFloat(document.getElementById('total_general_monto_dl').value.replace(',','.'))
        let tasa_usar = parseFloat(document.getElementById('tasa-cambio').value.replace(',','.'))
        const div = document.getElementById("monto_actuar_retencion");

        document.getElementById('monto_con_retencion_bs').value =( monto_con_retencion_dl * tasa_usar).toFixed(2)
        document.getElementById('monto_sin_retencion_bs').value =( monto_sin_retencion_dl * tasa_usar).toFixed(2)
        document.getElementById('total_general_monto_bs').value =  ((monto_con_retencion_dl * tasa_usar) + ( monto_sin_retencion_dl * tasa_usar)).toFixed(2)
        let total_general_monto_bs = ((monto_con_retencion_dl * tasa_usar) + ( monto_sin_retencion_dl * tasa_usar)).toFixed(2)
        document.getElementById('monto_ingreso_manual').value = monto_ingresado_manual
        if(monto_ingresado_manual != total_general_monto_bs ) {
            
            div.style.display = "block";

        } else {
            div.style.display = "none";
        }

        let monto_cobrado_fechas_anteriores = parseFloat(document.getElementById('monto_cobrado_anteriores_bs').value.replace(',','.'))
        let monto_cobrado_fechas_anteriores_dl = parseFloat(document.getElementById('monto_cobrado_anteriores_dl').value.replace(',','.'))
        
        let monto_real_con_pagos_anteriores = parseFloat(monto_ingresado_manual) + parseFloat(monto_cobrado_fechas_anteriores)

        if (monto_cobrado_fechas_anteriores > 0) {
            let monto_dl_recalculado_por_dif_tx =  (total_general_monto_dl - ((monto_cobrado_fechas_anteriores / tasa_usar))).toFixed(2)
            let monto_bs_recalculado_por_dif_tx = (monto_dl_recalculado_por_dif_tx * tasa_usar).toFixed(2)
            document.getElementById('monto-cobrado').value = parseFloat(monto_dl_recalculado_por_dif_tx).toFixed(2)
            document.getElementById('monto-pago-bs').value = parseFloat(monto_bs_recalculado_por_dif_tx).toFixed(2)

            /* let diferencia_cambiaria_dl = (monto_cobrado_fechas_anteriores_dl - monto_dl_recalculado_por_dif_tx ).toFixed(2)
            let saldo_actual_bolivares = monto_cobrado_fechas_anteriores - total_general_monto_bs */


            console.log('monto_dl_recalculado_por_dif_tx', monto_dl_recalculado_por_dif_tx)
            /* document.getElementById("monto_factura_id").innerHTML = "<b>Total con diferencial cambiario aplicado</b>"
            document.querySelector("#monto_factura_id b").style.color = "red";
            document.getElementById('total_general_monto_bs').value = monto_real_con_pagos_anteriores.toFixed(2) */
        }

        $('#idmontossobreRetencion').modal('show')

    } else {
        alert('Debe seleccionar un concepto')
    }
    
    
}

function marcadocheck(numero_check) {
    const chk0 = document.getElementById("check-retencion") 
    const chk1 = document.getElementById("monto_retencion_segun_factura") 
    const chk2 = document.getElementById("monto_total_segun_factura") 
    const porcentaje_a_retener = document.getElementById('porc-retencion').value
    let monto_aplicar_retencion = 0

    let monto_de_retencion_bs = 0
    if (numero_check == 0 && chk0.checked) {
        document.getElementById("monto_total_segun_factura").checked = false
        document.getElementById("monto_retencion_segun_factura").checked = false
        monto_aplicar_retencion =  document.getElementById("monto_ingreso_manual").value
       
    }
    if (numero_check == 1 && chk1.checked) {
        document.getElementById("monto_total_segun_factura").checked = false
        document.getElementById("check-retencion").checked = false
        monto_aplicar_retencion =  document.getElementById("monto_con_retencion_bs").value
    }
    if (numero_check == 2 && chk2.checked) {
        document.getElementById("monto_retencion_segun_factura").checked = false
        document.getElementById("check-retencion").checked = false
        monto_aplicar_retencion =  document.getElementById("total_general_monto_bs").value
    } 

    monto_de_retencion_bs = monto_aplicar_retencion * (porcentaje_a_retener/100)
    document.getElementById('monto_a_retener').innerHTML = 'Monto BS de la retencion : '+ monto_de_retencion_bs.toFixed(2)

    
}

function aplicarRetencionSeleccionada() {
    const chk0 = document.getElementById("check-retencion") 
    const chk1 = document.getElementById("monto_retencion_segun_factura") 
    const chk2 = document.getElementById("monto_total_segun_factura")
    let tx = document.getElementById("tasa-cambio").value
    if (typeof tx === 'string') {
        tx = parseFloat(tx.replace(',','.')).toFixed(2)
    } else {
        tx = parseFloat(tx).toFixed(2)
    }


    const porcentaje_a_retener = document.getElementById('porc-retencion').value 
    let monto_aplicar_retencion = 0
    let monto_de_retencion_bs = 0
    let neto_cobrado_bolivares = 0
    let neto_cobrado_usd= 0
    let monto_sin_retencion = 0


    if (chk0.checked) {
        monto_aplicar_retencion =  document.getElementById("monto_ingreso_manual").value

    }
    if (chk1.checked) {
        monto_aplicar_retencion =  document.getElementById("monto_con_retencion_bs").value
        monto_sin_retencion = document.getElementById("monto_sin_retencion_bs").value
    }
    if (chk2.checked) {
        monto_aplicar_retencion =  document.getElementById("total_general_monto_bs").value
    }

    monto_de_retencion_bs = (monto_aplicar_retencion * (porcentaje_a_retener/100)).toFixed(2)
    document.getElementById("monto-retencion").value = monto_de_retencion_bs

    

    saldo_monto_dl = document.getElementById("neto-cobrado-bs").value
    saldo_monto_bs = document.getElementById("monto-pago-bs").value
    if (typeof saldo_monto_dl === 'string') {
        saldo_monto_dl = parseFloat(saldo_monto_dl.replace(',','.')).toFixed(2)
    } else {
        saldo_monto_dl = parseFloat(saldo_monto_dl).toFixed(2)
    }

    if (typeof saldo_monto_bs === 'string') {
        saldo_monto_bs = parseFloat(saldo_monto_bs.replace(',','.')).toFixed(2)
    } else {
        saldo_monto_bs = parseFloat(saldo_monto_bs).toFixed(2)
    }

    neto_cobrado_bolivares = parseFloat(saldo_monto_bs - monto_de_retencion_bs)
    neto_cobrado_usd = (neto_cobrado_bolivares) / tx


    document.getElementById("neto-cobrado-bs").value = neto_cobrado_bolivares.toFixed(2)
    document.getElementById("neto-cobrado-usd").value = neto_cobrado_usd.toFixed(2)
    
    

    $('#idmontossobreRetencion').modal('hide')
    
}