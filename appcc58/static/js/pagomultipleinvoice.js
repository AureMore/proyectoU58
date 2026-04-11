document.addEventListener("DOMContentLoaded", function () {

  const checkTodos = document.getElementById("todas_factura");
  const checks = document.querySelectorAll(".factura-check");
  const totalP = document.getElementById("totalSeleccion");

  function actualizarTotal() {
    let total = 0;

    checks.forEach(check => {
        if (check.checked) {
            var saldo = check.dataset.saldo || 0.00;
                if (typeof saldo === 'string') {
                    saldo = parseFloat(saldo.replace(',','.')).toFixed(2)
                } else {
                    saldo = parseFloat(saldo).toFixed(2)
                }

            total += parseFloat(saldo);
        }
    });

    totalP.textContent = total.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}


  // ✔ Marcar / desmarcar todos
  checkTodos.addEventListener("change", function () {
    checks.forEach(check => {
      check.checked = checkTodos.checked;
    });
    actualizarTotal();
  });

  // ✔ Cuando se marca uno por uno
  checks.forEach(check => {
    check.addEventListener("change", function () {
      // Si uno se desmarca, desmarca el general
      if (!this.checked) {
        checkTodos.checked = false;
      }

      // Si todos están marcados, marca el general
      const todosMarcados = [...checks].every(c => c.checked);
      checkTodos.checked = todosMarcados;

      actualizarTotal();
    });
  });

  const form = document.querySelector("form");
    const contenedorHidden = document.getElementById("facturasHidden");

    form.addEventListener("submit", function () {
    contenedorHidden.innerHTML = "";
    
    checks.forEach(check => {
        if (check.checked) {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "facturas_ids";
        input.value = check.value;
        contenedorHidden.appendChild(input);
        }
    });
    
    });

});

function pagarSeleccion() {
    
    const checks = document.querySelectorAll(".factura-check");
    let monto_seleccionado = document.getElementById('totalSeleccion').textContent
    let numero_sin_coma = parseFloat(monto_seleccionado.replace(/,/g, ''));
    if (typeof numero_sin_coma === 'string') {
        numero_sin_coma = parseFloat(numero_sin_coma).toFixed(2)
        
    } else {
        numero_sin_coma = parseFloat(numero_sin_coma).toFixed(2)
    }
    if (numero_sin_coma <= 0) {
        alert('Debe seleccionar facturas a pagar !')
        return
    }
    
    document.getElementById('idmontopagarbs').value = numero_sin_coma
    $('#modalPago').modal('show')

    let tx_cambio = document.getElementById('tasacambio').value
    if (typeof tx_cambio === 'string') {
        tx_cambio = parseFloat(tx_cambio).toFixed(2)
        
    } else {
        tx_cambio = parseFloat(tx_cambio).toFixed(2)
    }
    
    document.getElementById('idmontopagarusd').value = parseFloat(numero_sin_coma / tx_cambio).toFixed(2)

    /* checks.forEach(check => {

        if (check.checked) {
            }

    }); */
}

function cambiartasa(fecha) {
    monto_usd = document.getElementById('idmontopagarbs').value
    if (typeof monto_usd === 'string') {
        monto_usd = parseFloat(monto_usd.replace(',','.')).toFixed(2)
    } else {
        monto_usd = parseFloat(monto_usd).toFixed(2)
    }

    const datos = {
        nfechaCambio : fecha,
    };

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/buscar_tasa_bcv_cxp/', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        console.log('data.congelar_cambio', data.congelar_cambio)
        document.getElementById('tasacambio').value = parseFloat(data.congelar_cambio).toFixed(4)
        if (parseFloat(data.congelar_cambio).toFixed(4) == 0.0000) {
            alert('No hay tasa de cambio de ese dia')
        }
        if (parseFloat(data.congelar_cambio).toFixed(4) > 0) {
            cambioMonto('B', monto_usd)
        } else {
            document.getElementById('idmontopagarusd').value = 0
        }
        
    })
    .catch(error => console.error(error));
  
}

function cambioMonto(moneda, monto) {
    var tasatx = document.getElementById('tasacambio').value
    if (typeof monto === 'string') {
        monto = parseFloat(monto.replace(',','.')).toFixed(2)
    } else {
        monto = parseFloat(monto).toFixed(2)
    }
        
    tasatx = parseFloat(tasatx.replace(',','.'))

    if (moneda == 'D') {
        document.getElementById('idmontopagarusd').value = monto
        let nuevo_monto = (monto * tasatx).toFixed(2)
        document.getElementById('idmontopagarbs').value = nuevo_monto
    } else {
        document.getElementById('idmontopagarbs').value = monto
        let nuevo_monto = (monto / tasatx).toFixed(2)
        document.getElementById('idmontopagarusd').value = nuevo_monto
    }
}

function seleccionarOrigen(idOrigen, usoCuenta, monedaCuenta) {
    document.getElementById('idusocuenta').value = usoCuenta
    document.getElementById('idmonedacuenta').value =monedaCuenta
    
}


function seleccionarDestino(idDestino,formaPago,bancoPago,monedaProveedor, idformapago) {
    document.getElementById('id_mediodepago').value = idformapago
    document.getElementById('idformapago').value = formaPago
    document.getElementById('idbancopago').value =bancoPago
    document.getElementById('monedaProveedor').value = monedaProveedor
   
}

function agregarFraccionPago() {
    
    var idOrigenFondos = document.getElementById('idOrigenFondos').value
    var idDestinoFondos = document.getElementById('idDestinoFondos').value

    var idmonedacuenta = document.getElementById('idmonedacuenta').value
    var monedaProveedor = document.getElementById('monedaProveedor').value

    var idreferenciapago = document.getElementById('idreferenciapago').value

    let tope_pagar_bs = document.getElementById('idmontopagarbs').value
    if (typeof tope_pagar_bs === 'string') {
        tope_pagar_bs = parseFloat(tope_pagar_bs.replace(',','.')).toFixed(2)
    } else {
        tope_pagar_bs = parseFloat(tope_pagar_bs).toFixed(2)
    }

    let fraccion_pagar_bs = document.getElementById('fraccion_pagar_bs').value
    if (typeof fraccion_pagar_bs === 'string') {
        fraccion_pagar_bs = parseFloat(fraccion_pagar_bs.replace(',','.')).toFixed(2)
    } else {
        fraccion_pagar_bs = parseFloat(fraccion_pagar_bs).toFixed(2)
    }

    if (fraccion_pagar_bs == 0 || parseFloat(fraccion_pagar_bs) > parseFloat(tope_pagar_bs)) {
        console.log('montos', fraccion_pagar_bs, tope_pagar_bs )
        alert('Debe colocar el monto a pagar y no puede ser superior al total a pagar')
    } else if ( idOrigenFondos == '' || idDestinoFondos == '' ) {
        alert('Debe seleccionar origen y destino de fondos')
    } else if ( monedaProveedor != idmonedacuenta) {
        alert('La moneda de origen y destino del pago deben ser iguales')
    } else if ( idreferenciapago == '' ) {
        alert('Debe indicar referencia del pago')
    } else {
        agregar_en_tabla_html()
    }

    
}

function actualizarcambio(monto_nuevo, moneda) {
    var tasacambio = document.getElementById('tasacambio').value

    if (typeof tasacambio === 'string') {
        tasacambio = parseFloat(tasacambio.replace(',','.')).toFixed(4)
    } else {
        tasacambio = parseFloat(tasacambio).toFixed(4)
    }
    if (typeof monto_nuevo === 'string') {
        monto_nuevo = parseFloat(monto_nuevo.replace(',','.')).toFixed(4)
    } else {
        monto_nuevo = parseFloat(monto_nuevo).toFixed(4)
    }

    if (moneda === 'B') {
        let monto_nuevo_dl = monto_nuevo / tasacambio
        document.getElementById('fraccion_pagar_dl').value = monto_nuevo_dl.toFixed(2)
    } else {
        let monto_nuevo_bs = monto_nuevo * tasacambio
        document.getElementById('fraccion_pagar_bs').value = monto_nuevo_bs.toFixed(2)
    }
    
    
}

function agregar_en_tabla_html() {

    const montoBs = parseFloat(document.getElementById("fraccion_pagar_bs").value) || 0;
    const montoUsd = parseFloat(document.getElementById("fraccion_pagar_dl").value) || 0;
    const referencia = document.getElementById("idreferenciapago").value.trim();
    const nota = document.getElementById("idnotapago").value.trim();
    let tasa = document.getElementById("tasacambio").value;
    let medio_pago = document.getElementById("id_mediodepago").value;

    const idOrigenFondos = document.getElementById("idOrigenFondos").value;
    const idDestinoFondos = document.getElementById("idDestinoFondos").value;

    // Normalizar tasa
    tasa = parseFloat(tasa.toString().replace(',', '.')) || 0;
    tasa = tasa.toFixed(4);

    // 🔴 Validaciones
    if (montoBs <= 0 && montoUsd <= 0) {
        alert("Debe ingresar un monto en Bs o USD");
        return;
    }

    if (!referencia) {
        alert("La referencia es obligatoria");
        return;
    }

    const tbody = document.getElementById("fracciones-pagos");
    const hidden = document.getElementById("fraccionesHidden"); // 👈 NUEVO
    const tr = document.createElement("tr");

    const fecha = document.getElementById("fecha-pago").value;
    const index = Date.now(); // ID único

    tr.dataset.index = index;

    const totalSeleccionado = obtenerTotalSeleccionado();
    const totalFraccionesActual = obtenerTotalFraccionesBs();

    if ((totalFraccionesActual + montoBs) > totalSeleccionado) {
        alert(
            "El monto de las fracciones excede el total seleccionado.\n" +
            "Total seleccionado: " + totalSeleccionado.toLocaleString('en-US', { minimumFractionDigits: 2 }) + "\n" +
            "Total fracciones: " + totalFraccionesActual.toLocaleString('en-US', { minimumFractionDigits: 2 })
        );
    return;
    }

    

    /* if ((totalFraccionesActual + montoBs) == totalSeleccionado) {

    } */


    tr.innerHTML = `
        <td>${fecha}</td>
        <td style="text-align:right;">${tasa}</td>
        <td style="text-align:right;">${montoBs.toFixed(2)}</td>
        <td style="text-align:right;">${montoUsd.toFixed(2)}</td>
        <td style="text-align:center;">${referencia}</td>
        <td>${idOrigenFondos}</td>
        <td>${idDestinoFondos}</td>
        <td>${nota}</td>
        <td style="text-align:center;">
            <button type="button" class="btn btn-sm btn-outline-danger"
                onclick="eliminar_fraccion(${index})">
                <i class="fa-solid fa-trash"></i>
            </button>
        </td>
        <td>${medio_pago}</td>
    `;

    tbody.appendChild(tr);

    // 👉 INPUTS HIDDEN (lo que va a Django)
    hidden.insertAdjacentHTML("beforeend", `
        <div id="hidden-${index}">
            <input type="hidden" name="fracciones_fecha[]" value="${fecha}">
            <input type="hidden" name="fracciones_tasa[]" value="${tasa}">
            <input type="hidden" name="fracciones_bs[]" value="${montoBs}">
            <input type="hidden" name="fracciones_usd[]" value="${montoUsd}">
            <input type="hidden" name="fracciones_ref[]" value="${referencia}">
            <input type="hidden" name="fracciones_origen[]" value="${idOrigenFondos}">
            <input type="hidden" name="fracciones_destino[]" value="${idDestinoFondos}">
            <input type="hidden" name="fracciones_nota[]" value="${nota}">
            <input type="hidden" name="fracciones_mediopago[]" value="${medio_pago}">
        </div>
    `);

    // 🔄 Limpiar campos
    document.getElementById("fraccion_pagar_bs").value = 0;
    document.getElementById("fraccion_pagar_dl").value = 0;
    document.getElementById("idreferenciapago").value = "";
    document.getElementById("idnotapago").value = "";
    validarBotonAgregar()
}

function eliminar_fraccion(index) {
    document.querySelector(`tr[data-index="${index}"]`)?.remove();
    document.getElementById(`hidden-${index}`)?.remove();
    validarBotonAgregar()
}

function obtenerTotalSeleccionado() {
    const texto = document.getElementById("totalSeleccion").textContent || "0";
    return parseFloat(texto.replace(/,/g, '')) || 0;
}

function obtenerTotalFraccionesBs() {
    let total = 0;

    document.querySelectorAll("#fracciones-pagos tr").forEach(tr => {
        const montoTexto = tr.children[2].textContent; // columna Monto Bs
        total += parseFloat(montoTexto.replace(/,/g, '')) || 0;
    });

    return total;
}

function validarBotonAgregar() {
    const totalSeleccionado = obtenerTotalSeleccionado();
    const totalFracciones = obtenerTotalFraccionesBs();

    const boton = document.getElementById('boton_mas');
    const boton_django_post = document.getElementById('guardar-django');
    boton.disabled = totalFracciones >= totalSeleccionado;
    console.log('totalFracciones',totalFracciones.toFixed(2), totalSeleccionado.toFixed(2)  )

    if (totalFracciones.toFixed(2) >= totalSeleccionado.toFixed(2)) {
        boton_django_post.disabled = false
    } else {
        boton_django_post.disabled = true
    }
    
}








