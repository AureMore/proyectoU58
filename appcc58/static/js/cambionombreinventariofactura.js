function cambioNombreInventario() {
    moneda_referencia = '2'
    const hoy = new Date();

    // Formatear la fecha en el formato YYYY-MM-DD
    const anio = hoy.getFullYear();
    const mes = String(hoy.getMonth() + 1).padStart(2, '0'); // Los meses son 0-indexados
    const dia = String(hoy.getDate()).padStart(2, '0');

    // Crear la cadena de fecha en el formato adecuado
    const fechaFormateada = `${anio}-${mes}-${dia}`
    let producto_id = document.getElementById('producto_id').value
    document.getElementById('lote').value = '';
    document.getElementById('categoria').value = '';
    document.getElementById('piva').value = 0;
    document.getElementById('costo').value = 0;
    document.getElementById('venta').value = 0;
    document.getElementById('laboratorio').value = '';
    //document.getElementById('presentacion_entrada').value ='';
    document.getElementById('presentacion_salida').value = '';  
    document.getElementById('cantidadcompra').value = 0;
    document.getElementById('nombrecomercial').value = '';
    document.getElementById('unidad_compra').value ='';
    //document.getElementById('conversion').value = 1;  
    document.getElementById('fechaelabora').value = fechaFormateada;
    document.getElementById('fechavence').value = fechaFormateada;
    document.getElementById('deposito_carga').value = '';

    if (producto_id != '') {
        const datos = {
            producto_id: producto_id,
          };
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch('/obtener_producto_inventario/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            }, 
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
            //$('#tabla-detalle-inventario').html(data);
            document.getElementById('codigo').value = data['codigo'];
            document.getElementById('lote').value =data['lote'];
            document.getElementById('categoria').value = data['categoria'];
            document.getElementById('piva').value = parseFloat(data['piva']).toFixed(2);
            if (moneda_referencia == '1') {
              document.getElementById("costo_moneda").innerText = "Costo en USD";
              document.getElementById("venta_moneda").innerText = "Venta en USD";
              document.getElementById('costo').value = data['costo'];
              document.getElementById('venta').value = parseFloat(data['venta']).toFixed(2);
            } else {
              document.getElementById("costo_moneda").innerText = "Costo en BS.";
              document.getElementById("venta_moneda").innerText = "Venta en BS.";
              document.getElementById('costo').value = parseFloat(data['costo_bs']).toFixed(2);
              document.getElementById('venta').value = parseFloat(data['venta_bs']).toFixed(2);
            }
            
            document.getElementById('laboratorio').value = data['laboratorio'];
            //document.getElementById('presentacion_entrada').value = data['presentacion'];
            document.getElementById('presentacion_salida').value = data['presentacion_salida'];
            document.getElementById('nombrecomercial').value = data['nombrecomercial'];
            document.getElementById('unidad_compra').value = data['unidad_compra'];
            //document.getElementById('conversion').value = data['conversion'];
            document.getElementById('fechaelabora').value = data['fecha_elaboracion'];
            document.getElementById('fechavence').value = data['fecha_vencimiento'];
            desactivarCamposNoModificables()
            // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
          })
          .catch(error => console.error(error));


  } else {
    
    activarCamposNoModificables()
    Swal.fire({
          title: '¡Atención!',
          text: 'Este producto no existe en el inventario, se creara automaticamente al guardar la factura',
          width: '400px',
          icon: 'warning',
          confirmButtonText: 'Continuar',
          background: '#f7f4f4',
          confirmButtonColor: '#198754',
        });
  }
}


function validarClasificacion() {
  const clasificacion = document.getElementById("clasificacion").value;

  if (!clasificacion) {
    alert("Primero debes seleccionar una clasificación");
    return false;
  }
  return true;
}

function filtrarPorClasificacion() {
  const clasificacion = document.getElementById("clasificacion").value;

  filtrarSelect("unidad_compra", clasificacion);
  filtrarSelect("presentacion_salida", clasificacion);
}


function filtrarSelect(selectId, clasificacion) {
  const select = document.getElementById(selectId);
  const options = select.querySelectorAll("option");

  options.forEach(option => {
    if (!option.value) return; // deja el "Seleccionar"

    const clasifOption = option.dataset.clasificacion;

    if (clasifOption === clasificacion) {
      option.style.display = "block";
    } else {
      option.style.display = "none";
    }
  });

  // reset selección
  select.value = "";
}


function totalCantidadCompra(select) {
  if (!validarClasificacion()) {
    select.value = ""; // reset
    return;
  }

  let cantidad_compra = parseFloat(document.getElementById('cantidadcompra').value).toFixed(2)
  const selectedOption = select.options[select.selectedIndex];
  
  const cantidad_bulto = parseFloat(selectedOption.dataset.cantidad).toFixed(2);
  const cantidad_unidad_bulto = parseFloat(selectedOption.dataset.cant_und_bulto).toFixed(2);


  document.getElementById('totalcantidad_compra').value = parseFloat(cantidad_compra * (cantidad_bulto * cantidad_unidad_bulto) ) .toFixed(2)

}

function totalCantidadSalida(select) {
  
  if (!validarClasificacion()) {
    select.value = ""; // reset
    return;
  }

}

function cambioCantidadCompra(cantidad_compra) {

  const select = document.getElementById("unidad_compra");
  const selectedOption = select.options[select.selectedIndex];
  let cantidad_bulto = parseFloat(selectedOption.dataset.cantidad || 0);
  let cantidad_unidad_bulto = parseFloat(selectedOption.dataset.cant_und_bulto || 0);
  
  let total_unidades_compra = parseFloat(cantidad_compra * (cantidad_bulto * cantidad_unidad_bulto)).toFixed(2)
  document.getElementById('totalcantidad_compra').value = total_unidades_compra

  
}

function verificarExento(categoria) {
  if (categoria == 1) {
    document.getElementById('piva').readOnly = true
    document.getElementById('piva').value = 0
    document.getElementById('piva').style.backgroundColor = "#e9ecef";
  } else {
    document.getElementById('piva').readOnly = false
    document.getElementById('piva').style.backgroundColor = "#ffffff";
  }
  
}

function desactivarCamposNoModificables() {
  document.getElementById('nombrecomercial').readOnly = true
  document.getElementById('categoria').disabled = true
  document.getElementById('nombrecomercial').style.backgroundColor = "#e9ecef";
  //document.getElementById('clasificacion').disabled = true

  document.getElementById('cantidad_critica').readOnly = true
  document.getElementById('cantidad_minima').readOnly = true
  document.getElementById('cantidad_critica').style.backgroundColor = "#e9ecef";
  document.getElementById('cantidad_minima').style.backgroundColor = "#e9ecef";
  id_categoria = document.getElementById('categoria').value
  verificarExento(id_categoria)
}

function activarCamposNoModificables() {
  document.getElementById('nombrecomercial').readOnly = false
  document.getElementById('categoria').disabled = false
  document.getElementById('nombrecomercial').style.backgroundColor = "#ffffff";
  document.getElementById('clasificacion').disabled = false

  document.getElementById('cantidad_critica').readOnly = false
  document.getElementById('cantidad_minima').readOnly = false
  document.getElementById('cantidad_critica').style.backgroundColor = "#ffffff";
  document.getElementById('cantidad_minima').style.backgroundColor = "#ffffff";
  id_categoria = document.getElementById('categoria').value
  verificarExento(id_categoria)
}





