function construirBaremo() {
    convenio = document.getElementById('convenio').value
    plantilla = document.getElementById('plantilla').value
    horaqx = document.getElementById('id_horasqx').value
    let horaho = document.getElementById('id_hospital').value
    let total_venta = 0
    const bloque = document.getElementById('mostrar_incremento');
    bloque.style.display = 'flex'

    if (plantilla == null || plantilla === "") {
        console.log("El valor de plantilla es nulo o vacío");
        return
    }

    fetch(`/filtro-baremo-presupuesto/?convenio=${convenio}&plantilla=${plantilla}&horaqx=${horaqx}&horaho=${horaho}`, {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        // Create an HTML table with the results
        let tableHtml = '';
        data.forEach(item => {
            tableHtml += '<tr data-id="${item.id}" style="font-size:8pt;">';
            tableHtml += `<td class="grupo oculto" >${item.grupo__nombre}</td>`;
            tableHtml += `<td>${item.detalle__nombre}</td>`;
            if (horaqx>1 && item.haymas==1) {
                tableHtml += `<td>
        </div>
        </div>
                        <input type="number" name="baremo_fila" value="${parseFloat(horaqx).toFixed(2)}"  style="border:none;" onchange="cambioCantidad(${item.id})" required >
                        </td>`;
            } else {
                tableHtml += `<td>
                
                        <input type="number" name="baremo_fila" value="${item.cantidad}" style="border:none;" onchange="cambioCantidad(${item.id})" required>
                        </td>`;
            }
           
            tableHtml += `<td><input class="cantidad-derecha precio-venta" type="text" name="baremo_fila" value="${parseFloat(item.venta).toFixed(2)}"  style="border:none;" onchange="cambioPrecioVenta(${item.id})"></input></td>`;
            total_venta = total_venta +  parseFloat(item.venta)    
            tableHtml += `<td style="text-align:center;"><input type="text" name="baremo_fila" value="${item.unidad__nombre}"  style="border:none;"></input></td>`;

            tableHtml += `<td> <button type="button" style="background-color:red;color:white;border:none; padding:5px 10px" onclick="eliminarFila(this)"><i class="fas fa-trash" ></i></button> </td>`;
            tableHtml += `<td style="text-align:center;"><input class="" type="checkbox" name="baremo_check" onchange="actualizarPrecio(this, ${item.id})" style="border:none;"></input></td>`;
            tableHtml += `<td style="text-align:center;"><input class="baremo_porcentaje" type="text" name="baremo_porcentaje" readonly style="border:none;  background-color:transparent; text-align:right;"></input></td>`;
            tableHtml += `<td style="text-align:center;"><input class="grupo oculto" type="text" name="baremo_fila" value="${item.convenio}"  style="border:none;"></input></td>`;
            tableHtml += `<td style="text-align:center;"><input class="grupo oculto" type="text" name="baremo_fila" value="${item.grupo}"  style="border:none;"></input></td>`;
            tableHtml += `<td style="text-align:center;"><input class="grupo oculto" type="text" name="baremo_fila" value="${item.detalle}"  style="border:none;"></input></td>`;
            tableHtml += `<td style="text-align:center;"><input class="grupo oculto" type="text" name="baremo_fila" value="${item.ntqx}"  style="border:none;"></input></td>`;
            
            tableHtml += '</tr>';
        });

        // Append the table to your HTML element
        const tabla = document.getElementById('tblplantilla');
        tabla.innerHTML = '';
        // Crear el encabezado de la tabla
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr style="text-align:center; font-family: 'Arial Narrow', Arial, sans-serif;">
                <th>Detalle del Item</th>
                <th style="text-align:left;">Cantidad</th>
                <th>Venta</th>
                <th>Unidad</th>
                <th></th>
                <th></th>
                <th>% Incremento</th>
                <th></th>
                <th></th>
                <th></th>
                <th></th>

            </tr>
        `;


        tabla.appendChild(thead);
        const tbody = document.createElement('tbody');
        tbody.innerHTML = tableHtml;
        tabla.appendChild(tbody);
        const tfoot = document.createElement('tfoot');
        tfoot.innerHTML = `
            <tr style="text-align:center; font-family: 'Arial Narrow', Arial, sans-serif;">
                <td> </td>
                <td>Total general Presupuesto</td>
                <td id="id_total_venta"><strong> ${parseFloat(total_venta).toFixed(2)}$</strong></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
             

            </tr>
        `;
        tabla.appendChild(tfoot);
        // Agrupar las filas
        const grupos = {};
        tabla.querySelectorAll('tbody tr').forEach((fila) => {
            const valorGrupo = fila.querySelector('.grupo').textContent;
            if (!grupos[valorGrupo]) {
                grupos[valorGrupo] = [];
            }
            grupos[valorGrupo].push(fila);
        });

        // Recorremos los grupos y los mostramos en la tabla
        Object.keys(grupos).forEach((grupo) => {
            const filasGrupo = grupos[grupo];
            const tituloGrupo = document.createElement('tr');
            tituloGrupo.innerHTML = `<th colspan="3">${grupo}</th>`;
            tabla.appendChild(tituloGrupo);

            const tbodyGrupo = document.createElement('tbody');
            filasGrupo.forEach((fila) => {
                tbodyGrupo.appendChild(fila);
            });
            tabla.appendChild(tbodyGrupo);
        });
    })
    .catch(error => console.error('Error:', error));
}

function recalcularTotal() {
    const filas = document.querySelectorAll('#tblplantilla tbody tr');
    let total = 0;
    filas.forEach(fila => {
      const precioVenta = parseFloat(fila.querySelector('.precio-venta').value);
      total += precioVenta;
    });
    document.getElementById('id_total_venta').innerHTML = `<strong> ${parseFloat(total).toFixed(2)}$</strong>`;
  }

function eliminarFila(boton) {
    const fila = boton.closest('tr');
    fila.remove();
    recalcularTotal();
  }




function cambioCantidad(itemId) {

    // Get the input field that triggered the event
    const inputField = event.target;
  
    // Get the row that contains the input field
    const row = inputField.closest('tr');
  
    // Get the quantity and price elements in the row
    const quantityInput = row.querySelector('input[name="baremo_fila"][type="number"]');
    const priceInput = row.querySelector('input[name="baremo_fila"][type="text"]');
  
    // Get the new quantity value
    const newQuantity = parseFloat(quantityInput.value);
  
    // Calculate the new price (you'll need to implement the pricing logic here)
    //const newPrice = calculateNewPrice(newQuantity, itemId);
    idBaremo1 = itemId
    cantidad1 = newQuantity

    //nueva
    $.ajax({
        type: "GET",
        url: "/actualizar-precio/",  
        data: {
            idBaremo1: idBaremo1,
            cantidad1: cantidad1,
        },
        success: function(data) {
            const precioventa = data.precio ;
            priceInput.value = precioventa;
            recalcularTotal();
          
        }
    })
    //nueva fin
  }


//cambio de Precio de venta



function cambioPrecioVenta(itemId) {
  

  const inputFieldPrecio = event.target;
  
  // Get the row that contains the input field
  const rowSeleccionada = inputFieldPrecio.closest('tr');

  // Get the quantity and price elements in the row
  const cantidadInput = rowSeleccionada.querySelector('input[name="baremo_fila"][type="number"]');
  const precioInput = rowSeleccionada.querySelector('input[name="baremo_fila"][type="text"]');

  const cantidad = parseFloat(cantidadInput.value);
  const newPrecio = parseFloat(precioInput.value)
  precioInput.value = newPrecio.toFixed(2)
  let valor = 1
  if (cantidad == 0 ) {
    cantidadInput.value = valor.toFixed(2)
  }
  recalcularTotal();
  // Get the new quantity value

  // Calculate the new price (you'll need to implement the pricing logic here)
  //const newPrice = calculateNewPrice(newQuantity, itemId);


}



//fin cambio Precio Venta



  

  document.getElementById("myBaremoAdicional").addEventListener("click", function(event) {
    event.preventDefault(); // Evita que se active el modal por defecto

    plantilla = document.getElementById('plantilla').value
 
    if (plantilla == null || plantilla === "") {
        Swal.fire({
            icon: "error",
            title: "Error",
            text: "Debe seleccionar una plantilla primero",
            width: '250px', // ancho del recuadro
            heightAuto: true,
            customClass: {
                title: 'swal2-title-large',
                text: 'swal2-text-large'
              }
          });
    } else {
        var modal = new bootstrap.Modal(document.getElementById("exampleModal"));
        modal.show();
    }

});


function checkCedulaExistence(input) {
    var cedula = input.value;
    if (cedula !== '') {
      $.ajax({
        type: 'GET',
        url: "/check_cedula_existance/" ,
        data: {
          'cedula': cedula
        },
        success: function(data) {
          nombre = data.nombre
          apellido = data.apellido
          telefono = data.telefono
          direccion = data.direccion
          
          document.getElementById('new_paciente_nombre').value = nombre
          document.getElementById('new_paciente_apellido').value = apellido
          document.getElementById('new_paciente_telefono').value = telefono
          document.getElementById('new_paciente_direccion').value = direccion
        }
      });
    }
  }


  function checkCedulaExistenceResp(input) {
    var cedula = input.value;
    if (cedula !== '') {
      $.ajax({
        type: 'GET',
        url: "/check_cedula_existance_rep/" ,
        data: {
          'cedula': cedula
        },
        success: function(data) {
          nombre = data.nombre
          apellido = data.apellido
          telefono = data.telefono

          
          document.getElementById('id_resp_nombre').value = nombre
          document.getElementById('id_resp_apellido').value = apellido
          document.getElementById('id_resp_telefono').value = telefono
          
        }
      });
    }
  }


  function actualizarPrecio(checkbox, itemId) {
    // Obtener el porcentaje del input
    const porcentaje = parseFloat(document.getElementById('porcentaje').value) || 0;

    // Obtener la fila del checkbox
    const row = checkbox.closest('tr');

    // Obtener el input de precio-venta en la misma fila
    const precioVentaInput = row.querySelector('.precio-venta');
    const por_aumento = row.querySelector('.baremo_porcentaje');

    // Obtener el precio original
    const porcentajeAumento =  parseFloat(por_aumento.value);
    const precioOriginal = parseFloat(precioVentaInput.value);

    // Calcular el nuevo precio si el checkbox está marcado
    if (checkbox.checked) {
        const incremento = (precioOriginal * porcentaje) / 100;
        const nuevoPrecio = precioOriginal + incremento;
        precioVentaInput.value = nuevoPrecio.toFixed(2);
        por_aumento.value = porcentaje.toFixed(2)
    } else {
      const porcientoRestar = (porcentajeAumento / 100) + 1
      const montoOriginal = precioOriginal / porcientoRestar
      precioVentaInput.value = montoOriginal.toFixed(2);
      por_aumento.value = ''
        // Si el checkbox no está marcado, puedes decidir si revertir el precio o no
        // Aquí simplemente no hacemos nada, pero podrías guardar el precio original en otro lugar
    }
    cambioPrecioVenta(itemId)
   
}