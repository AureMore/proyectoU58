// Get the table body element
const tableBody = document.getElementById("items-recibo-proveedor").querySelector("tbody");

let rowCount = 1; // Initialize row count
// Create a function to add a new row
function addNewRow() {

    if (!funcionValidar()) {
        return
    }


    var porc_iva = document.getElementById('porc_iva').value
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
  precioUnitarioInput.className = "item-precio-unitario"
  precioUnitarioInput.name = "detalle_factura"
  cells[3].appendChild(precioUnitarioInput);

  const subtotalInput = document.createElement("input");
  subtotalInput.type = "number";
  subtotalInput.id = "subtotal";
  subtotalInput.className = "item-subtotal"
  subtotalInput.name = "detalle_factura"
  subtotalInput.readOnly = true;
  cells[4].appendChild(subtotalInput);

  const porcentajeInput = document.createElement("input");
  porcentajeInput.type = "number";
  porcentajeInput.id = "porcentaje";
  porcentajeInput.value = porc_iva;
  porcentajeInput.className = "item-iva"
  porcentajeInput.name = "detalle_factura"
  porcentajeInput.step = "0.01"
  cells[5].appendChild(porcentajeInput);

  const montovaInput = document.createElement("input");
  montovaInput.type = "number";
  montovaInput.id = "montoiva";
  montovaInput.value = 0;
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
    const precioUnitario = precioUnitarioInput.value.trim(); // Trim whitespace
    const pIva = porcentajeInput.value.trim()

    if (!cantidad || !precioUnitario) {
        subtotalInput.value = ""; // Clear subtotal if either input is empty
        return;
    }

    const cantidadNum = parseFloat(cantidad);
    const precioUnitarioNum = parseFloat(precioUnitario);

    if (isNaN(cantidadNum) || isNaN(precioUnitarioNum)) {
        subtotalInput.value = ""; // Clear subtotal if either input is not a number
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

function updateTotal() {
    const rows = document.querySelectorAll("table tbody tr ");

    let total = 0;
    let totaliva = 0
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

      total += subtotalValue;
      totaliva += ivasubtotalValue

    });
    let montonetoPagar = 0
    porcentajeRetener = parseFloat(document.getElementById('p_rentencion').value)
    let baseimponible = parseFloat(document.getElementById('baseimponible').value)
   document.getElementById('baseimponible').value = total.toFixed(2)
   document.getElementById('monto_iva').value = totaliva.toFixed(2)
   let montoRetener = 0
   montoRetener = total * (porcentajeRetener/100)
   montonetoPagar = (total - montoRetener) + totaliva
   
   document.getElementById('m_retencion').value = montoRetener.toFixed(2) 
   document.getElementById('monto_pagar_neto').value = montonetoPagar.toFixed(2)
    // Update the total amount element
    //totalAmountElement.textContent = total.toFixed(2); // Display with 2 decimal places
  }



// Add an event listener to the button to call the addNewRow function
const addButton = document.getElementById("add-button"); // Replace with the ID of your button
addButton.addEventListener("click", addNewRow);


function cambioConcepto(idConcepto, pNatural, pJuridico, pSustraendo, pTope){
    const idProveedor = document.getElementById('id_proveedor').value
    var typePerson = document.getElementById('id_tipopersona').value
    if (idProveedor == '') {
        Swal.fire("Debe Seleccionar un proveedor");
        return
    }

    if (typePerson == 'J' || typePerson == 'G') {
        var procentajeRetencion = pJuridico
    } else {
        var procentajeRetencion = pNatural
    }

    document.getElementById('p_rentencion').value = procentajeRetencion
    
}

function tipoPersona(nroRif) {
    var persona = nroRif.charAt(0)
    document.getElementById('id_tipopersona').value = persona
}


function funcionValidar() {
    const concepto = document.getElementById('retencion').value
    const tipoDocumento = document.getElementById('tipodocumento').value
    const proveedor = document.getElementById('id_proveedor').value
    const montoDocumento = document.getElementById('monto_total_documento').value
    const nrodocumento = document.getElementById('nrodocumento').value
    const nrocontrol = document.getElementById('nrocontrol').value
    var mensajeAdv = ''
 
    
    if (nrodocumento == 0 || nrodocumento == '' ) {
        mensajeAdv = 'Debe colocar el numero de documento para continuar'
    }

    if (nrocontrol == 0 || nrocontrol == '' ) {
        mensajeAdv = 'Debe colocar el numero de control de documento para continuar'
    }

    if (montoDocumento == 0 || montoDocumento == '' ) {
        mensajeAdv = 'Debe colocar el monto total de la factura a ingresar para continuar'
    }
    if (concepto == '') {
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
        console.log("Evita el prevent")
        event.preventDefault();
    }
});


