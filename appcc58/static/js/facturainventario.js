function padZero(value, length = 2) {
    return String(value).padStart(length, '0');
}


function cambioTasa(fechaCambio) {

    const fecha_cambio_congelado = fechaCambio + ' 20:00:00.000'
    // Make an AJAX request to your Django backend
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `/buscar_cambio_desde_js/?fecha_cambio_congelado=${fecha_cambio_congelado}`, true);
    xhr.onload = function() {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        let monto = response.monto; // Assuming the Django backend returns a JSON response with a 'fecha' key
        document.getElementById('tasacambiofactura').value = parseFloat(monto).toFixed(4)
      }
    };
    xhr.send();
    
}
function guardarFacturaInventario() {
    const btn = document.getElementById("btnGuardar");

    if (!validacion_final()) {
        return
    }
    btn.disabled = true;
    Swal.fire({
    title: "Guardar y Actualizar",
    text: "Recuerde: al guardar el inventario se actualizara con las cantidades indicadas en la factura",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Si , Guardar"
    }).then((result) => {
    if (result.isConfirmed) {
        var numeroFactura = document.getElementById('numerofactura').value 
        let proveedorId = document.getElementById('proveedor').value 
        let concepto_id = document.getElementById('retencion').value 

        const datos = {
            numeroFactura: numeroFactura,
            proveedorId : proveedorId,
            concepto_id : concepto_id
        };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/guardarInventarioFactura/', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
            }, 
            body: JSON.stringify(datos)
        })
        .then(response => response.json())
        .then(data => {
            alert('Factura Guardada e Inventario Actualizado!')
            window.location.href = '/lista_factura_compra/';          
        })
        .catch(error => console.error(error));

    } else {
        btn.disabled = false;
    }
    });


}

function openModal() {
    $('#agregarProducto').modal('hide')
    $('#noinventarioModal').modal('show')
}


function calcular() {
    let cantidad = parseFloat(document.getElementById('cantidad').value) || 0;
    let precio = parseFloat(document.getElementById('precio').value) || 0;
    let iva = parseFloat(document.getElementById('iva').value) || 0;

    let subtotal = cantidad * precio;
    let montoIva = subtotal * (iva / 100);
    let total = subtotal + montoIva;

    document.getElementById('subtotal').value = subtotal.toFixed(2);
    document.getElementById('montoIva').value = montoIva.toFixed(2);
    document.getElementById('total').value = total.toFixed(2);
}

document.querySelectorAll('#cantidad, #precio, #iva')
    .forEach(el => el.addEventListener('input', calcular));


const input = document.getElementById("descripcion");
const datalist = document.getElementById("listaProductos");

// Cargar productos guardados
let productos = JSON.parse(localStorage.getItem("productos")) || [];

// Mostrar en datalist
function renderLista() {
    datalist.innerHTML = "";
    productos.forEach(p => {
        let option = document.createElement("option");
        option.value = p;
        datalist.appendChild(option);
    });
}

// Guardar nuevo producto
input.addEventListener("change", () => {
    let valor = input.value.trim();

    if (valor && !productos.includes(valor)) {
        productos.push(valor);
        localStorage.setItem("productos", JSON.stringify(productos));
        renderLista();
    }
});

renderLista();

function agregar_noinventario() {
    let cantidad = document.getElementById('cantidad').value 
    let precio = document.getElementById('precio').value 
    let descripcion = document.getElementById('descripcion').value 
    let iva = document.getElementById('iva').value
    if (cantidad == '') {
        alert('Debe colocar una cantidad')
        return
    }
    if (descripcion == '') {
        alert('Debe colocar descripcion')
        return
    }
    if (precio == '') {
        alert('Debe colocar el precio')
        return
    }

    var nroDocumento = document.getElementById('numeronota').value 
    var nroFactura = document.getElementById('numerofactura').value 
    let idProveedor = document.getElementById('proveedor').value 
    var fechaEntrega = document.getElementById('fechadocumento').value
    let idRetencion = document.getElementById('retencion').value
    let tasa_aplicable = document.getElementById('tasacambiofactura').value.replace(',','.')
    tasa_aplicable = parseFloat(tasa_aplicable).toFixed(4)



    const datos = {
        nroDocumento: nroDocumento,
        nroFactura: nroFactura,
        idProveedor: idProveedor,
        idRetencion : idRetencion,
        fechaEntrega: fechaEntrega,
        tasa_aplicable: tasa_aplicable,
        cantidad: cantidad,
        precio: precio,
        descripcion: descripcion,
        iva : iva,
        //detalles: data

      };

      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
      fetch('/agregarProductoNoInventario/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        }, 
        body: JSON.stringify(datos)
      })
      .then(response => response.json())
      .then(data => {

        refreshDetalleNota(data['idNota'])
        $('#noinventarioModal').modal('hide')
        // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
      })
      .catch(error => console.error(error));
    
}

function validacion_final() {

    var nroDocumento = document.getElementById('numeronota').value;
    var nroFactura = document.getElementById('numerofactura').value;
    var idProveedor = document.getElementById('proveedor').value;
    var retencion = document.getElementById('retencion').value 
    let monto_factura_input = parseFloat(document.getElementById('montofacturainput').value).toFixed(2)
    let total_operacion_bs = (document.getElementById('total_subtotal_operacion_bs').innerHTML).replace(',','.')

    console.log('monto_factura_input', monto_factura_input, total_operacion_bs )
    try {
        
        // Si no existe, validar los campos
        let msj = '';
        if (nroDocumento === '' || nroDocumento === '0') {
            msj = 'Indicar Numero de Control';
        }

        if (parseFloat(monto_factura_input).toFixed(2) != parseFloat(total_operacion_bs).toFixed(2)) {
            msj = 'Los montos de total factura y total a pagar no coinciden!';
        }
        
        if (nroFactura === '' || nroFactura === '0') {
            msj = 'Indicar Numero de Factura';
        }
        if (idProveedor === '') {
            msj = 'Seleccionar el Proveedor';
        }
        if (monto_factura_input == 0) {
            msj = 'Debe ingresar monto de factura';
        }
        if (retencion === '') {
            msj = 'Seleccionar el Concepto';
        }

        if (msj !== '') {
            Swal.fire({
                title: "Revise Datos Cargados!",
                text: msj,
                icon: "warning"
            });
            return false; // Detiene la validación si hay errores en los campos
        } else {
            return true
        }
    }
        catch (error) {
        console.error('Error al validar:', error);
        Swal.fire({
            title: "Error",
            text: 'Ocurrió un error al validar. Por favor, inténtalo de nuevo.',
            icon: "error"
        });
        return false; // La validación falla debido a un error
    }
    
}