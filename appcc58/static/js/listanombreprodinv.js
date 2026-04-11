$(document).ready(function() {
  const boton = document.getElementById('btn-guardar-nuevo');
  boton.style.display = 'none';
    $('#id_datalistOptions').on('input', function() {
        var selectedOption = $(this).val();
        selectedOption = selectedOption.replace(/"/g, '')
        $(this).val(selectedOption);

        var selectedId = $('option[value="' + selectedOption + '"]').data('id');
        $('#producto_id').val(selectedId);
    });
});

function buscarInventarioProducto() {

    const hoy = new Date();

    // Formatear la fecha en el formato YYYY-MM-DD
    const anio = hoy.getFullYear();
    const mes = String(hoy.getMonth() + 1).padStart(2, '0'); // Los meses son 0-indexados
    const dia = String(hoy.getDate()).padStart(2, '0');

    // Crear la cadena de fecha en el formato adecuado
    const fechaFormateada = `${anio}-${mes}-${dia}`
    let producto_id = document.getElementById('producto_id').value
    document.getElementById('loteUpdate').value = '';
    document.getElementById('categoriaNew').value = '';
    document.getElementById('pivaUpdate').value = 0;
    document.getElementById('costoUpdate').value = 0;
    document.getElementById('ventaUpdate').value = 0;
    document.getElementById('laboratorioUpdate').value = '';
    document.getElementById('presentacion_entradaUpdate').value ='';
    document.getElementById('presentacion_salidaUpdate').value = '';  
    document.getElementById('nombreComercialUpdate').value = '';
    document.getElementById('unidad_compra').value ='';
    document.getElementById('conversion').value = 1;  
    document.getElementById('fechaelaboraUpdate').value = fechaFormateada;
    document.getElementById('fechavenceUpdate').value = fechaFormateada;

    document.getElementById('existencia').value = 0;
    document.getElementById('salida_total').value = 0;
    document.getElementById('cantidad_producidas').value = 0;


    if (producto_id != '') {
      const boton = document.getElementById('btn-guardar-nuevo');
      boton.style.display = 'none';
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
            campos_readonly(true)
            document.getElementById('codigoNew').value = data['codigo'];
            document.getElementById('loteUpdate').value =data['lote'];
            document.getElementById('categoriaNew').value = data['categoria'];
            document.getElementById('pivaUpdate').value =data['piva'];
            document.getElementById('costoUpdate').value = data['costo'];
            document.getElementById('ventaUpdate').value = parseFloat(data['venta']).toFixed(2);
            document.getElementById('laboratorioUpdate').value = data['laboratorio'];
            document.getElementById('presentacion_entradaUpdate').value = data['presentacion'];
            document.getElementById('presentacion_salidaUpdate').value = data['presentacion_salida'];
            document.getElementById('nombreComercialUpdate').value = data['nombrecomercial'];
            document.getElementById('unidad_compra').value = data['unidad_compra'];
            document.getElementById('conversion').value = data['conversion'];
            document.getElementById('fechaelaboraUpdate').value = data['fecha_elaboracion'];
            document.getElementById('fechavenceUpdate').value = data['fecha_vencimiento'];
            document.getElementById('existencia').value = data['existencia'];
            document.getElementById('salida_total').value = data['salida_producto'];
            document.getElementById('cantidad_producidas').value = data['cantidad_producidas'];

            ver_materia_prima(producto_id)

            // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
          })
          .catch(error => console.error(error));

        /////

    } else {
      ver_materia_prima(producto_id)
      campos_readonly(false)

      const boton = document.getElementById('btn-guardar-nuevo');
      boton.style.display = 'inline-block';


    }
}

function ver_materia_prima() {
    const idProducto = document.getElementById('producto_id').value;
    
        $.ajax({
            type: 'GET',
            url: '/refresh_materia_prima/' + '?idProducto=' + idProducto,
            dataType: 'json',  // Cambia a 'json'
            success: function(data) {
                // Inserta el HTML en la tabla
                $('#tabla-materia-prima').html(data.html);
                
                // Ahora puedes acceder al total_subtotal
                //console.log('total_subtotal', data.total_subtotal);
                
                // Ejemplo: Usa el valor en tu código (por ejemplo, mostrarlo en un elemento) montoincremento
                //$('#costoUpdate').value(data.total_subtotal);
                document.getElementById('costoUpdate').value = parseFloat(data.total_subtotal).toFixed(2)
                precioVenta(parseFloat(data.montoincremento).toFixed(2)  ,parseFloat(data.total_subtotal).toFixed(2))
                
                cambiarPrecioCostoMateriaPrima(idProducto, parseFloat(data.total_subtotal).toFixed(2))
                //$('#loaderModal').modal('hide');
            },
            error: function(xhr, status, error) {
                console.error('Error en AJAX:', error);
            }
        });
        
     
}



function muestraTablaDisponibleFarmacia(idAtencion) {
        
    let depositoId = document.getElementById('depositonew').value
    let producto_id = document.getElementById('producto_id').value
    if (depositoId == '') {
        alert('Seleccionar Deposito de Medicamentos')
        
    } else {
        if (producto_id == '') {
          alert('Debe Seleccionar el producto que sera el producto terminado')
        } else {
           $.ajax({
            type: 'GET',
            url: '/refresh_tabla_disponible_pt/' + '?depositoId=' + depositoId ,
            dataType: 'html',
            success: function(data) {
                $('#tabla-producto-mt').html(data);
                $('#existenciaDepositos').modal('show')
            }
        }); 

        }
        
    }
}

function agregar_a_producto_terminado(inventario_id, nCantidad, existencia, deposito_id) {
  existencia = parseFloat(existencia)
  let producto_id = document.getElementById('producto_id').value
  if (nCantidad > existencia) {
      alert('No hay existencia disponble en este producto')
  } else {
    const datos = {
            nCantidad: nCantidad,
            inventario_id: inventario_id,
            deposito_id: deposito_id,
            producto_terminado_id: producto_id
          };
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch('/agregar_producto_bd_terminado/', {
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
            //document.getElementById('cantidad_producidas').value = data['cantidad_producidas'];
            ver_materia_prima(producto_id)

            // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
          })
          .catch(error => console.error(error));

  }

}


function eliminarMateriaPrima(id_materia_prima) {
  let producto_id = document.getElementById('producto_id').value
  const datos = {
            id_materia_prima: id_materia_prima,
          };
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch('/eliminar_materia_prima/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            }, 
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
           
            ver_materia_prima(producto_id)

            
          })
          .catch(error => console.error(error));
  
}


function agregarProductoTerminadoInventario() {
  let producto_id = document.getElementById('producto_id').value
  let depositonew = document.getElementById('depositonew').value
  if (depositonew == '') {
    alert('Debe seleccionar el deposito donde se cargara el producto terminado')
    return
  }
  
  let cantidad_agregar = document.getElementById('cantidad_agregar_producto_terminado').value
  cantidad_agregar = parseFloat(cantidad_agregar.replace(',','.'))
  if (cantidad_agregar > 0) {
    if (producto_id != '') {

      const datos = {
        producto_id: producto_id,
        cantidad_agregar: cantidad_agregar,
        depositonew : depositonew,
      };
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      fetch('/agregar_producto_terminado_a_inventario/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            }, 
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
            if (data.existe == 'NO') {
              alert('El producto terminado debe tener compuestos para poder agregar al inventario!')
            } else {
              console.log('data existencia', data.existencias)
              if (data.existencias == false) {
                alert("No hay existencia en los productos de materia prima para generar el producto terminado, Revise la existencia de la materia prima");
              } else {
                alert("Producto Terminado Agregado al Inventario");
                window.location.href = '/create_producto_inventario/';
              }
              
            }
            
          })
          .catch(error => console.error(error));

    } else {
      alert('Debe seleccionar un producto')
    }
  } else {
    alert('La cantidad agregar del producto terminado debe ser mayor a cero (0)')
  }
  
}

function cambiarPrecioCostoMateriaPrima(inventario_id , nuevo_precio_costo) {
  const nuevo_precio_venta =  document.getElementById('ventaUpdate').value
  const datos = {
        inventario_id: inventario_id,
        nuevo_precio_costo: nuevo_precio_costo,
        nuevo_precio_venta: nuevo_precio_venta
      };
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      fetch('/cambio_precio_costo_inventario/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            }, 
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
            
            
          })
          .catch(error => console.error(error));

  
}

function guardar_nuevo_producto() {

  const conversion = document.getElementById('conversion').value
  const categoria = document.getElementById('categoriaNew').value
  const loteUpdate =  document.getElementById('loteUpdate').value
  const pivaUpdate =  document.getElementById('pivaUpdate').value
  const costoUpdate =  document.getElementById('costoUpdate').value
  const ventaUpdate =  document.getElementById('ventaUpdate').value
  const laboratorioUpdate =  document.getElementById('laboratorioUpdate').value
  const presentacion_entradaUpdate =  document.getElementById('presentacion_entradaUpdate').value
  const presentacion_salidaUpdate =  document.getElementById('presentacion_salidaUpdate').value
  const nombreComercialUpdate =  document.getElementById('nombreComercialUpdate').value
  const unidad_compra =  document.getElementById('unidad_compra').value
  const fechaelaboraUpdate =  document.getElementById('fechaelaboraUpdate').value
  const fechavenceUpdate =  document.getElementById('fechavenceUpdate').value
  const cantidad_minima =  document.getElementById('cantidad_minima').value
  const cantidad_critica =  document.getElementById('cantidad_critica').value
  const nombreUpdate =  document.getElementById('id_datalistOptions').value

 
  if ( unidad_compra == '') {
    mensaje = 'Debe seleccionar unidad de compra'
  } else if ( presentacion_entradaUpdate == '') {
    mensaje = 'Debe Presentacion'
  } else if ( presentacion_salidaUpdate == '') {
    mensaje = 'Debe Unidad de venta'
  } else if ( categoria == '') {
    mensaje = 'Debe seleccionar categoria'
  } else if ( laboratorioUpdate == '') {
    mensaje = 'Debe seleccionar laboratorio / fabricante'
  }else if ( nombreUpdate == '') {
    mensaje = 'Debe colocar nombre'
  } else {
    mensaje = ''
  }
  
  if ( mensaje != '' ) {
    alert('Revise: ' + mensaje )
    return
  }

  const datos = {
      conversion : conversion,
      categoria : categoria,
      loteUpdate : loteUpdate,
      pivaUpdate : pivaUpdate,
      costoUpdate : costoUpdate,
      ventaUpdate : ventaUpdate,
      laboratorioUpdate : laboratorioUpdate,
      presentacion_entradaUpdate : presentacion_entradaUpdate,
      presentacion_salidaUpdate : presentacion_salidaUpdate,
      nombreComercialUpdate : nombreComercialUpdate,
      unidad_compra : unidad_compra,
      fechaelaboraUpdate : fechaelaboraUpdate,
      fechavenceUpdate : fechavenceUpdate,
      cantidad_minima : cantidad_minima,
      cantidad_critica : cantidad_critica,
      nombreUpdate: nombreUpdate

     };
   const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
   fetch('/guardar_nuevo_producto_inventario/', {
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
       document.getElementById('producto_id').value = data.producto_id
       document.getElementById('codigoNew').value =  data.codigo
       buscarInventarioProducto()

       // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
     })
     .catch(error => console.error(error));
  
}


function campos_readonly(isReadOnly) {

  const conversion = document.getElementById('conversion');
  const categoria = document.getElementById('categoriaNew')
  const loteUpdate =  document.getElementById('loteUpdate')
  const pivaUpdate =  document.getElementById('pivaUpdate')
  const costoUpdate =  document.getElementById('costoUpdate')
  const ventaUpdate =  document.getElementById('ventaUpdate')
  const laboratorioUpdate =  document.getElementById('laboratorioUpdate')
  const presentacion_entradaUpdate =  document.getElementById('presentacion_entradaUpdate')
  const presentacion_salidaUpdate =  document.getElementById('presentacion_salidaUpdate')
  const nombreComercialUpdate =  document.getElementById('nombreComercialUpdate')
  const unidad_compra =  document.getElementById('unidad_compra')
  const fechaelaboraUpdate =  document.getElementById('fechaelaboraUpdate')
  const fechavenceUpdate =  document.getElementById('fechavenceUpdate')
  const cantidad_minima =  document.getElementById('cantidad_minima')
  const cantidad_critica =  document.getElementById('cantidad_critica')

  conversion.disabled = isReadOnly; 
  categoria.disabled  = isReadOnly;
  loteUpdate.disabled = isReadOnly; 
  pivaUpdate.disabled = isReadOnly; 
  costoUpdate.disabled = isReadOnly; 
  ventaUpdate.disabled = isReadOnly; 
  laboratorioUpdate.disabled  = isReadOnly;
  presentacion_entradaUpdate.disabled  = isReadOnly;
  presentacion_salidaUpdate.disabled  = isReadOnly;
  nombreComercialUpdate.disabled = isReadOnly; 
  unidad_compra.disabled  = isReadOnly;
  fechaelaboraUpdate.disabled  = isReadOnly
  fechavenceUpdate.disabled  = isReadOnly
  cantidad_minima.disabled  = isReadOnly
  cantidad_critica.disabled  = isReadOnly

   
}