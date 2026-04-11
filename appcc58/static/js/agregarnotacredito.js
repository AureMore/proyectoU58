function refreshNotasCreditosClientes(pagador_id) {
    return new Promise((resolve, reject) => {
        $.ajax({
            type: 'GET',
            url: '/obtener_notascredito/' + '?pagador_id=' + pagador_id,
            dataType: 'json',
            success: function(response) {
                // Actualizar el HTML de la tabla
                $('#tabla-nota-credito-cliente').html(response.html);
                resolve(); // Resolvemos la promesa cuando la llamada es exitosa
            },
            error: function(xhr, status, error) {
                console.error('Error en la llamada AJAX:', error);
                reject(error); // Rechazamos la promesa en caso de error
            }
        });
    });
}

function buscarCuentaxCobrar(cuentacobrar_id) {
    window.open(`/cirugia_porcobrar/${cuentacobrar_id}/`, '_blank');
}


function buscarDatos(vcedulapagador) {
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
            const apellido = data.apellido;
            const direccion = data.direccion;
            const pagador = data.pagador_id;
            var total_saldo = data.total_saldo
            document.getElementById('cedulapagadornotacrediro').value = vcedulapagador;
            document.getElementById('nombrepagadornotacredito').value = nombre;
            document.getElementById('telpagadornotacredito').value = telefono;
            document.getElementById('dirpagadornotacredito').value = direccion;
            console.log('pagador:'+ pagador)
            refreshNotasCreditosClientes(pagador)


        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

function cambioMonto(moneda, monto) {
    var tasatx = document.getElementById('tasa-cambio').value
    if (typeof monto === 'string') {
        monto = parseFloat(monto.replace(',','.')).toFixed(2)
    } else {
        monto = parseFloat(monto).toFixed(2)
    }
        
    tasatx = parseFloat(tasatx.replace(',','.'))

    if (moneda == 'D') {
        document.getElementById('monto-cobrado-dolares').value = monto
        let nuevo_monto = (monto * tasatx).toFixed(2)
        document.getElementById('monto-cobrado-bolivares').value = nuevo_monto
    } else {
        document.getElementById('monto-cobrado-bolivares').value = monto
        let nuevo_monto = (monto / tasatx).toFixed(2)
        document.getElementById('monto-cobrado-dolares').value = nuevo_monto
    }
}

function cambioTx(new_tasa) {
    let monto_dolares = document.getElementById('monto-cobrado-dolares').value
    monto_dolares = parseFloat(monto_dolares.replace(',','.'))
    new_tasa = parseFloat(new_tasa.replace(',','.'))
    let nuevo_monto = (monto_dolares * new_tasa).toFixed(2)
    document.getElementById('monto-cobrado-bolivares').value = nuevo_monto
}

async function comprarMonedas(formapago,recepcion_fondos) {
     try {
        const response = await fetch(`/buscar_monedas_notacredito/?formapago=${formapago}&recepcion_fondos=${recepcion_fondos}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        const monedaIgual = data.monedaIgual; // Asumiendo que el backend de Django devuelve una respuesta JSON con una clave 'monedaIgual'
        
        return monedaIgual === 'true'; // Devuelve true o false
    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
        return false; // En caso de error, puedes devolver false o manejarlo de otra manera
    }
}


async function guardar_pago() {
    let monto_dolares = document.getElementById('monto-cobrado-dolares').value
    var tasatx = document.getElementById('tasa-cambio').value
    var formapago = document.getElementById('forma-pago').value
    var recepcion_fondos = document.getElementById('destino_cobro').value
    var cedulapagador = document.getElementById('cedulapagadornotacrediro').value
    var nombrepagador = document.getElementById('nombrepagadornotacredito').value
    

    var mensaje = ''
    //comprar monedas
    if (formapago != '' && recepcion_fondos != '') {
       var valor = await comprarMonedas(formapago,recepcion_fondos)
       console.log('valor:', valor)
       if (valor) {
        mensaje = ''
       } else {
        mensaje = 'Forma de pago y cuenta receptora de fondos deben ser monedas iguales!'
       }
       
    }
        //fin comprar monedas
    console.log('mensaje:'+mensaje)
    
    if (monto_dolares <= 0 || monto_dolares == '') {
        mensaje = 'Montos no pueden estar en 0 , revise e intente de nuevo !'
    }
    if (tasatx <= 0 || tasatx == '') {
        mensaje = 'Debe colocar tasa de cambio, revise e intente de nuevo !'
    }
    if (formapago == '') {
        mensaje = 'Debe colocar forma de pago, revise e intente de nuevo !'
    }
    if (recepcion_fondos == '') {
        mensaje = 'Debe colocar la cuenta receptora de los fondos, revise e intente de nuevo !'
    }
    if (cedulapagador == '') {
        mensaje = 'Debe colocar la cedula de la persona que realizara el pago !'
    }
    if (nombrepagador == '') {
        mensaje = 'Debe colocar el nombre y apellido de la persona que realizara el pago !'
    }
    

    if (mensaje != '') {
       Swal.fire({
        title: 'Atención',
        html: '<p style="font-size: 18px; font-family: monospace;">'+mensaje+'</p>',
        icon: 'error',
        customClass: {
            popup: 'my-swal-popup',
            title: 'my-swal-title',
            htmlContainer: 'my-swal-html'
        }
        });
    } else {
        guardarPagoCliente()
        

    }
}
function guardarPagoCliente() {
    let monto_dolares = document.getElementById('monto-cobrado-dolares').value
    let monto_bolivares = document.getElementById('monto-cobrado-bolivares').value
    var tasatx = document.getElementById('tasa-cambio').value
    var formapago = document.getElementById('forma-pago').value
    var recepcion_fondos = document.getElementById('destino_cobro').value
    var cedulapagador = document.getElementById('cedulapagadornotacrediro').value
    var nombrepagador = document.getElementById('nombrepagadornotacredito').value
    var telefonopagador = document.getElementById('telpagadornotacredito').value
    var direccionpagador = document.getElementById('dirpagadornotacredito').value
    var desnotacredito = document.getElementById('desnotacredito').value
    var presupuesto_referencia = document.getElementById('presupuesto_referencia').value
    var bancos_origen_fondos = document.getElementById('bancos').value
    var referencia_pago = document.getElementById('referencia-pago').value
    var fecha_pago = document.getElementById('fecha-pago').value

    const datos = {
            monto_dolares: monto_dolares,
            monto_bolivares: monto_bolivares,
            tasatx: tasatx,
            formapago: formapago,
            recepcion_fondos: recepcion_fondos,
            cedulapagador: cedulapagador,
            nombrepagador: nombrepagador,
            telefonopagador: telefonopagador,
            direccionpagador: direccionpagador,
            desnotacredito: desnotacredito,
            presupuesto_referencia: presupuesto_referencia,
            bancos_origen_fondos: bancos_origen_fondos,
            referencia_pago: referencia_pago,
            fecha_pago: fecha_pago
            };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/aplicar_nota_credito/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }, 
        body: JSON.stringify(datos)
        })
        .then(response => response.json())
        .then(data => {
            buscarDatos(cedulapagador)
            document.getElementById('monto-cobrado-dolares').value = 0
            document.getElementById('monto-cobrado-bolivares').value = 0
            document.getElementById('forma-pago').value = ''
        
        })
        .catch(error => console.error(error));
    
}

function cerrar_lista() {
    window.location.href = `/notas_credito_cuentacobrar/`;
    
}

function cambiartasa(fecha) {
    monto_usd = document.getElementById('monto-cobrado-dolares').value
    if (typeof monto_usd === 'string') {
        monto_usd = parseFloat(monto_usd.replace(',','.')).toFixed(2)
    } else {
        monto_usd = parseFloat(monto_usd).toFixed(2)
    }

    const datos = {
        nfechaCambio : fecha,
    };

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/buscar_tasa_bcv_nc/', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('tasa-cambio').value = data.congelar_cambio
        if (monto_usd > 0) {
            cambioMonto('D', monto_usd)
        }
        
    })
    .catch(error => console.error(error));
  
}

function padZero(value, length = 2) {
    return String(value).padStart(length, '0');
}
