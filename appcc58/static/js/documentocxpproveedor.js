// Get the table body element
const tableBody = document.getElementById("items-recibo-proveedor").querySelector("tbody");

let rowCount = 1; // Initialize row count
// Create a function to add a new row
function addNewRow() {

    if (!funcionValidar()) {
        return
    }
 

    var porc_iva = document.getElementById('porc_iva').value
    porc_iva = parseFloat(porc_iva.replace(',','.')).toFixed(2)
    document.getElementById('porc_iva').value = porc_iva
    
  // Create a new table row element
  const newRow = document.createElement("tr");

  // Create the table cells for the new row
  const cells = [
    document.createElement("td"), // #
    document.createElement("td"), // CANTIDAD
    document.createElement("td"), // DESCRIPCION
    document.createElement("td"), // PRECIO UNITARIO
    document.createElement("td"), // SUBTOTAL
    document.createElement("td"), // % IVA
    document.createElement("td"), // MONTO IVA
    document.createElement("td"), // ... (hidden ID column)
  ];

  cells[0].innerHTML = rowCount;

  const cantidadInput = document.createElement("input");
  cantidadInput.type = "number";
  cantidadInput.id = "cantidad";
  cantidadInput.value = 0
  cantidadInput.className = "item-cantidad"
  cantidadInput.name = "detalle_factura"
  cells[1].appendChild(cantidadInput);

  const descripcionInput = document.createElement("input");
  descripcionInput.type = "text";
  descripcionInput.id = "descripcion";
  descripcionInput.className="item-descripcion"
  descripcionInput.name = "detalle_factura"
  cells[2].appendChild(descripcionInput);

  const precioUnitarioInput = document.createElement("input");
  precioUnitarioInput.type = "number";
  precioUnitarioInput.step = "0.01"
  precioUnitarioInput.id = "precio-unitario";
  precioUnitarioInput.value = 0
  precioUnitarioInput.className = "item-precio-unitario"
  precioUnitarioInput.name = "detalle_factura"
  cells[3].appendChild(precioUnitarioInput);

  const subtotalInput = document.createElement("input");
  subtotalInput.type = "number";
  subtotalInput.id = "subtotal";
  subtotalInput.value = 0
  subtotalInput.className = "item-subtotal"
  subtotalInput.name = "detalle_factura"
  subtotalInput.readOnly = true;
  cells[4].appendChild(subtotalInput); 

  const porcentajeInput = document.createElement("input");
  porcentajeInput.type = "number";
  porcentajeInput.id = "porcentaje";
  porcentajeInput.value = porc_iva;
  porcentajeInput.min = 0
  porcentajeInput.className = "item-iva"
  porcentajeInput.name = "detalle_factura"
  porcentajeInput.step = "0.01"
  cells[5].appendChild(porcentajeInput);

  const montovaInput = document.createElement("input");
  montovaInput.type = "number";
  montovaInput.id = "montoiva";
  montovaInput.value = 0;
  montovaInput.min = 0
  montovaInput.className = "item-monto-iva"
  montovaInput.name = "detalle_factura"
  montovaInput.step = "0.01"
  cells[6].appendChild(montovaInput);

    // Create a delete button for each row
    const deleteButton = document.createElement("button");
    deleteButton.textContent = "Quitar";
    deleteButton.className = "delete-button ms-2";
 

    deleteButton.addEventListener("click", (e) => {
        const row = e.target.parentNode.parentNode; // Get the parent row element
        row.remove(); // Remove the row
        updateTotal()
      });

   cells[6].appendChild(deleteButton); // Add the delete button to the last column

  // Add event listeners to update subtotal
  cantidadInput.addEventListener("input", updateSubtotal);
  precioUnitarioInput.addEventListener("input", updateSubtotal);
  porcentajeInput.addEventListener("input", updateSubtotal);

  // Function to update subtotal
function updateSubtotal() {
    const cantidad = cantidadInput.value.trim(); // Trim whitespace
    let precioUnitario = 0
    if (precioUnitarioInput.value.trim() == '') {
        precioUnitario = 0 
    } else {
        precioUnitario = precioUnitarioInput.value.trim(); // Trim whitespace
    }
    
    const pIva = porcentajeInput.value.trim()

    if (!cantidad || !precioUnitario) {
        subtotalInput.value = 0; // Clear subtotal if either input is empty
        return;
    }

    const cantidadNum = parseFloat(cantidad);
    const precioUnitarioNum = parseFloat(precioUnitario);

    if (isNaN(cantidadNum) || isNaN(precioUnitarioNum)) {
        subtotalInput.value = 0; // Clear subtotal if either input is not a number
        return;
    }

    const subtotal = cantidadNum * precioUnitarioNum;
    const montodeIva = subtotal * (pIva/100)
    subtotalInput.value = subtotal.toFixed(2);
    montovaInput.value = montodeIva.toFixed(2)
    updateTotal()
}

  // Add the cells to the new row
  cells.forEach((cell) => newRow.appendChild(cell));

  // Add the new row to the table body
  tableBody.appendChild(newRow);
  // Increment the row count
  rowCount++;
  updateTotal()
}

function retencion_iva(proveedor_id) {
    if (proveedor_id != "") {
        $.ajax({
        type: 'GET',
        url: '/extraer_retencion_iva/' + '?proveedor_id=' + proveedor_id ,
        dataType: 'json', // Cambiar a 'json'
        success: function(response) {
            let porcentaje_retener = response.porcentaje_retener
            document.getElementById('p_retencion_iva').value = porcentaje_retener
        },
        error: function() {
            // Manejo de errores
            alert('Error al refrescar la tabla. Inténtalo de nuevo.');
            $('#modalSubBaremito').modal('hide');
        }
    }); 

    } else {
        document.getElementById('p_retencion_iva').value = 0 
       document.getElementById('m_retencion_iva').value = 0 
    }


} 


function updateTotal() {
    const rows = document.getElementById("items-recibo-proveedor").querySelectorAll("tbody tr");
    //const rows = document.querySelectorAll("table tbody tr ");

    let total = 0;
    let totaliva = 0
    let total_base_imponible = 0
    let total_exento = 0
    // Loop through each row and sum up the subtotals
    rows.forEach((row) => {
        const subtotalInput = row.querySelector("input.item-subtotal"); // Select the input element with class "item-subtotal"
        var subtotalValue = parseFloat(subtotalInput.value); // Get the value of the input element  
        const montoIvasubtotal = row.querySelector("input.item-monto-iva"); // Select the input element with class "item-subtotal"
        var ivasubtotalValue = parseFloat(montoIvasubtotal.value); // Get the value of the input element  

        if (isNaN(subtotalValue)) {
            subtotalValue = 0
        }
        if (isNaN(ivasubtotalValue)) {
            ivasubtotalValue = 0
        }
        if (ivasubtotalValue > 0) {
            total_base_imponible += subtotalValue
        } else {
            total_exento += subtotalValue
        }

      totaliva += ivasubtotalValue

    });
    let montonetoPagar = 0
    porcentajeRetener = parseFloat(document.getElementById('p_rentencion').value)
    let por_retencion = document.getElementById('p_retencion_iva').value
    let monto_retener_iva = ((totaliva * (por_retencion/100))).toFixed(2)
    let monto_sustraendo = document.getElementById('monto_sustraendo').value

    if (typeof monto_sustraendo === 'string') {
        monto_sustraendo = parseFloat(monto_sustraendo.replace(',','.')).toFixed(2)
    } else {
        monto_sustraendo = parseFloat(monto_sustraendo).toFixed(2)
    }

    // monto_sustraendo = parseFloat(monto_sustraendo).toFixed(2)
    document.getElementById('m_retencion_iva').value = monto_retener_iva
    document.getElementById('baseimponible').value = total_base_imponible.toFixed(2)
    document.getElementById('monto_iva').value = totaliva.toFixed(2)
    document.getElementById('montoexento').value = total_exento.toFixed(2)
    let montoRetener = 0
    montoRetener = (((total_base_imponible + total_exento) ) * (porcentajeRetener/100)) - monto_sustraendo
    if ((total_base_imponible + total_exento) > 0)  {
        montoRetener = parseFloat(montoRetener)
    } else {
        montoRetener = 0
    }
    
    monto_retener_iva = parseFloat(monto_retener_iva)
    montonetoPagar = total_base_imponible + total_exento + totaliva - (montoRetener + monto_retener_iva)
   
    document.getElementById('m_retencion').value = montoRetener.toFixed(2)
    document.getElementById('neto_a_pagar').value = montonetoPagar.toFixed(2)
    // Update the total amount element
    //totalAmountElement.textContent = total.toFixed(2); // Display with 2 decimal places
  }



// Add an event listener to the button to call the addNewRow function
const addButton = document.getElementById("add-button"); // Replace with the ID of your button
addButton.addEventListener("click", addNewRow);


function cambioConcepto(idConcepto, pNatural, pJuridico, pSustraendoN, pTopeN, pTopeJ, pSustraendoJ){
    const idProveedor = document.getElementById('id_proveedor').value
    var typePerson = document.getElementById('id_tipopersona').value
    if (idProveedor == '') {
        Swal.fire("Debe Seleccionar un proveedor");
        return
    }

    if (typePerson == 'J' || typePerson == 'G') {
        var procentajeRetencion = pJuridico
        var pSustraendo = pSustraendoJ
    } else {
        var procentajeRetencion = pNatural
        var pSustraendo = pSustraendoN
    }

    document.getElementById('p_rentencion').value = procentajeRetencion
    document.getElementById('monto_sustraendo').value = pSustraendo
    /* document.getElementById('m-sustraendo').value = pSustraendo */
    
    updateTotal()
}

function tipoPersona(nroRif) {
    if (nroRif == '' || nroRif == null ) {
        return
    } else {
        var persona = nroRif.charAt(0)
        document.getElementById('id_tipopersona').value = persona
        retencion_iva(document.getElementById('id_proveedor').value)
    }
    
}


function funcionValidar() {
    const concepto = document.getElementById('retencion').value
    const tipoDocumento = document.getElementById('tipodocumento').value
    const proveedor = document.getElementById('id_proveedor').value
    const montoDocumento = document.getElementById('monto_total_documento').value
    const nrodocumento = document.getElementById('nrodocumento').value
    const nrocontrol = document.getElementById('nrocontrol').value
    const centrocosto = document.getElementById('centrocosto').value
    var mensajeAdv = ''
 
    
    if (nrodocumento == 0 || nrodocumento == '' ) {
        mensajeAdv = 'Debe colocar el numero de documento para continuar'
    }

    if (nrocontrol == 0 || nrocontrol == '' ) {
        mensajeAdv = 'Debe colocar el numero de control de documento para continuar'
    }

    if (centrocosto == '' ) {
        mensajeAdv = 'Debe colocar el centro de costo de documento para continuar'
    }

    if (montoDocumento == 0 || montoDocumento == '' ) {
        mensajeAdv = 'Debe colocar el monto total de la factura a ingresar para continuar'
    }
    if (concepto == '' && tipoDocumento == 1  ) {
        mensajeAdv = 'Debe seleccionar un concepto para continuar'
    }
    if (tipoDocumento == '') {
        mensajeAdv = 'Debe seleccionar un tipo de documento para continuar'
    }
    if (proveedor == '') {
        mensajeAdv = 'Debe seleccionar un proveedor para continuar'
    }
   
   
    if (mensajeAdv != '') {
        Swal.fire(mensajeAdv);
        return false
    } else {
        return true
    }


}

 
function mostrarMoneda(tipoDoc) {
    const mostrar = document.getElementById('moneda_caja');
    if (tipoDoc > 1) {
        mostrar.classList.remove('ocultar');
    } else {
        mostrar.classList.add('ocultar');
    }

}


document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
    }
});


function cambioNumero(numero, tipo_nro) {
  proveedor_id = document.getElementById("id_proveedor").value;

  const datos = {
    numero: numero,
    tipo_nro: tipo_nro,
    proveedor_id: proveedor_id
  };

  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

  fetch('/revisar_existe_factura_control/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    }, 
    body: JSON.stringify(datos)
  })
  .then(response => response.json())
  .then(data => {
      if (data.existe) {
        if (tipo_nro == 'NF') {
          document.getElementById("nrodocumento").value = ''
          numero_descripcion = 'FACTURA'
        } else {
          document.getElementById("nrocontrol").value = ''
          numero_descripcion = 'CONTROL'
        }
          
        
        Swal.fire({
          icon: "error",
          title: "Numero de "+numero_descripcion+" Ya existe",
          text: "No puede incluir numeros iguales de factura / control al mismo proveedor!",
        });
        
      }
    //location.reload()    
  })
  .catch(error => console.error(error)); 

  
}

function validarCampos() {
    let monto_pagar_input = parseFloat(document.getElementById('monto_total_documento').value).toFixed(2)

    let baseimponible = parseFloat(document.getElementById('baseimponible').value).toFixed(2)
    let montoexento = parseFloat(document.getElementById('montoexento').value).toFixed(2)
    let monto_iva = parseFloat(document.getElementById('monto_iva').value).toFixed(2)

    let neto_a_pagar = parseFloat(baseimponible) + parseFloat(montoexento) + parseFloat(monto_iva)
    neto_a_pagar = neto_a_pagar.toFixed(2)

    if (neto_a_pagar <= 0) {
        alert('No puede guardar facturas en cero(0)')
        return false
    } else if ( neto_a_pagar != monto_pagar_input ) {
        alert('El monto del documento es diferente al total a pagar, Revise!')
        return false
    } else {
        document.getElementById('guardar_factura').hidden = true
        return true
    }
    
}

function formatermonto(monto) {
    document.getElementById('monto_total_documento').value = parseFloat(monto).toFixed(2)
}
