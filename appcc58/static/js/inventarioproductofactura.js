
document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
    }
});

async function validarDatos() {
    var nroDocumento = document.getElementById('numeronota').value;
    var nroFactura = document.getElementById('numerofactura').value;
    var idProveedor = document.getElementById('proveedor').value;
    var retencion = document.getElementById('retencion').value 
    let monto_factura_input = parseFloat(document.getElementById('montofacturainput').value).toFixed(2)

    try {
        // Si no existe, validar los campos
        let msj = '';
        if (nroDocumento === '' || nroDocumento === '0') {
            msj = 'Indicar Numero de Control';
        }
        if (nroFactura === '' || nroFactura === '0') {
            msj = 'Indicar Numero de Factura';
        }
        if (idProveedor === '') {
            msj = 'Seleccionar el Proveedor';
        }
        if (retencion === '') {
            msj = 'Seleccionar el Concepto';
        }

        if (monto_factura_input == 0 || monto_factura_input == '' || isNaN(monto_factura_input)) {
             msj = 'Debe introducir el monto de la factura';
        }

        if (msj !== '') {
            Swal.fire({
                title: "Revise Datos Cargados!",
                text: msj,
                icon: "warning"
            });
            return false; // Detiene la validación si hay errores en los campos
        } else {
           
            const existeProducto = await buscarExiteProducto();
            
            if (existeProducto == 'true') {
                Swal.fire({  // Usando SweetAlert para la alerta
                    title: "Error",
                    text: 'Ya existe una factura con estos datos (Nro. Control/Nro. Factura)!.',
                    icon: "error"
                });
                return false; // Detiene la validación si ya existe
            }
        }

        // Si la validación pasa, inicializar los campos y abrir el modal
        inicializarCampos();
        $('#agregarProducto').modal('show');
        document.getElementById('montofacturainput').readOnly = true
        return true; // La validación es exitosa

    } catch (error) {
        Swal.fire({
            title: "Error",
            text: error,
            icon: "error"
        });
        return false; // La validación falla debido a un error
    }
}

function cambioformato(monto) {
    document.getElementById('montofacturainput').value = parseFloat(monto).toFixed(2)
}

function inicializarCampos() {
    const hoy = new Date();
    const anio = hoy.getFullYear();
    const mes = String(hoy.getMonth() + 1).padStart(2, '0');
    const dia = String(hoy.getDate()).padStart(2, '0');
    const fechaFormateada = `${anio}-${mes}-${dia}`;

    document.getElementById('lote').value = '';
    document.getElementById('categoria').value = '';
    document.getElementById('piva').value = '0';
    document.getElementById('costo').value = '0';
    document.getElementById('venta').value = '0';
    document.getElementById('laboratorio').value = '';
    //document.getElementById('presentacion_entrada').value = '';
    document.getElementById('presentacion_salida').value = '';
    document.getElementById('nombrecomercial').value = '';
    document.getElementById('exampleDataList').value = '';
    document.getElementById('unidad_compra').value = '';
    //document.getElementById('conversion').value = '1';
    document.getElementById('fechaelabora').value = fechaFormateada;
    document.getElementById('fechavence').value = fechaFormateada;
    document.getElementById('deposito_carga').value = '';
}


function agregarInventario() {
    var nroDocumento = document.getElementById('numeronota').value 
    var nroFactura = document.getElementById('numerofactura').value 
    let idProveedor = document.getElementById('proveedor').value 
    var fechaEntrega = document.getElementById('fechadocumento').value
    let idRetencion = document.getElementById('retencion').value
    let tasa_aplicable = document.getElementById('tasacambiofactura').value.replace(',','.')
    tasa_aplicable = parseFloat(tasa_aplicable).toFixed(4)

    if (!validarProducto()) {
        return
    }

    //var codigo = document.getElementById('codigo').value 
    let moneda_factura = '2' 
    let categoria = document.getElementById('categoria').value 
    let costo = document.getElementById('costo').value 
    let venta = document.getElementById('venta').value 
    let idInventario = document.getElementById('producto_id').value
    let clasificacion = document.getElementById('clasificacion').value 
    let laboratorio = document.getElementById('laboratorio').value 
    let presentacion_salida = document.getElementById('presentacion_salida').value 
    var lote = document.getElementById('lote').value 
    var fechaelabora = document.getElementById('fechaelabora').value 
    var fechavence = document.getElementById('fechavence').value 
    var piva = document.getElementById('piva').value 
    var nombreProducto = document.getElementById('exampleDataList').value 
    let cantidadcompra = document.getElementById('cantidadcompra').value;
    var nombrecomercial = document.getElementById('nombrecomercial').value;
    let unidad_compra = document.getElementById('unidad_compra').value ;
    //let conversion = document.getElementById('conversion').value;  
    let depositocarga = document.getElementById('deposito_carga').value;  
    let cantidad_minima = document.getElementById('cantidad_minima').value;  
    let cantidad_critica = document.getElementById('cantidad_critica').value;  
    let totalcantidad_compra = document.getElementById('totalcantidad_compra').value;

   

    const datos = {
        nroDocumento: nroDocumento,
        nroFactura: nroFactura,
        idProveedor: idProveedor,
        idRetencion : idRetencion,
        fechaEntrega: fechaEntrega,
        categoria: categoria,
        costo: costo,
        venta: venta,
        idInventario: idInventario,
        clasificacion : clasificacion,
        presentacion_salida : presentacion_salida,
        lote : lote,
        laboratorio : laboratorio,
        fechaelabora : fechaelabora,
        fechavence : fechavence,
        nombreProducto : nombreProducto,
        piva : piva,
        depositocarga : depositocarga,
        //conversion : conversion,
        unidad_compra : unidad_compra,
        nombrecomercial : nombrecomercial,
        cantidadcompra : cantidadcompra,
        tasa_aplicable : tasa_aplicable,
        moneda_factura : moneda_factura,
        cantidad_minima : cantidad_minima,
        cantidad_critica : cantidad_critica,
        totalcantidad_compra : totalcantidad_compra


        //detalles: data

      };

      

      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
      fetch('/agregarFacturaInventario/', {
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
            refreshDetalleNota(data['idNota'])
            $('#agregarProducto').modal('hide')
            // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
        })
        .catch(error => console.error(error));
}


$(document).ready(function() {
    $('#exampleDataList').on('input', function() {
        var selectedOption = $(this).val();
        selectedOption = selectedOption.replace(/"/g, '')
        $(this).val(selectedOption);

        var selectedId = $('option[value="' + selectedOption + '"]').data('id');
        $('#producto_id').val(selectedId);
    });
});


function validarProducto() {
    var advertencia = ''
    let categoria = document.getElementById('categoria').value 
    let costo = document.getElementById('costo').value 
    let clasificacion = document.getElementById('clasificacion').value 
    let presentacion_salida = document.getElementById('presentacion_salida').value 
    let unidad_compra = document.getElementById('unidad_compra').value 
    let cantidadcompra = parseFloat(document.getElementById('cantidadcompra').value) 
    var deposito_carga = document.getElementById('deposito_carga').value 
    let lote = document.getElementById('lote').value 
    let laboratorio = document.getElementById('laboratorio').value 

    if (categoria == 1) {
        if (lote.trim() == '' || laboratorio.trim() == '') {
            advertencia = 'Para medicinas debe incluir lote y laboratorio'
        }
    }

    if (unidad_compra.trim() == '') {
            advertencia = 'Seleccione la unidad de compra del producto'
        }
    
    if (cantidadcompra == 0 ) {
        advertencia = 'Coloque la cantidad del producto'
    }
    if (clasificacion == '' ) {
        advertencia = 'Seleccione la clasificacion del producto'
    }
    if (presentacion_salida == '' ) {
        advertencia = 'Seleccione la presentacion de salida del producto'
    }
    if (deposito_carga == '' ) {
        advertencia = 'Introduzca el deposito del producto'
    }
    if (costo == 0 ) {
        advertencia = 'Coloque el costo del producto'
    }
    if (categoria == '' ) {
        advertencia = 'Seleccione la categoria del producto'
    }
   


    if (advertencia == '' ) {
        return true
    } else {
        Swal.fire({
            title: "Faltan Datos!",
            text: advertencia,
            icon: "warning"
          });
        return false
    }

    
}


function refreshDetalleNota(idNota) {
    $.ajax({
        type: 'GET',
        url: '/refresh_table_detalle_factura/' + '?idNota=' + idNota,
        dataType: 'html',
        success: function(data) {
            $('#tabla-detalle-inventario').html(data);
        }
    });
}

function montoVenta() {
    let porcentajeIncremento = (document.getElementById('porc_incremento').value).replace(',','.')
    let montoIncremento = (document.getElementById('montoIncremento').value ).replace(',','.')
    let montocosto = (document.getElementById('costo').value ).replace(',','.')
    let montoVenta = 0
    let montoAdicional = 0
    montocosto = Number(montocosto)
    montoIncremento = Number(montoIncremento)
    porcentajeIncremento = Number(porcentajeIncremento)
    if (montoIncremento == 0){
        porcentajeIncremento = (porcentajeIncremento/100)
        montoAdicional = montocosto * porcentajeIncremento
        montoVenta = (montocosto) + (montoAdicional)
    } else {
        montoVenta = (montocosto) + (montoIncremento)
    }
    document.getElementById('venta').value = montoVenta.toFixed(2)


   // 
}



function montoVentaUpdate() {
    let porcentajeIncremento = (document.getElementById('porc_incremento').value).replace(',','.')
    let montoIncremento = (document.getElementById('montoIncremento').value ).replace(',','.')
    let montocosto = (document.getElementById('costoUpdate').value ).replace(',','.')
    let montoVenta = 0
    let montoAdicional = 0
    montocosto = Number(montocosto)
    montoIncremento = Number(montoIncremento)
    porcentajeIncremento = Number(porcentajeIncremento)
    if (montoIncremento == 0){
        porcentajeIncremento = (porcentajeIncremento/100)
        montoAdicional = montocosto * porcentajeIncremento
        montoVenta = (montocosto) + (montoAdicional)
    } else {
        montoVenta = (montocosto) + (montoIncremento)
    }
    document.getElementById('ventaUpdate').value = montoVenta.toFixed(2) 


   // 
}



function modificarItemNota(codigo, categoria, piva, costo, venta, nombre, laboratorio, presentacion, presentacionsalida,lote, fechaelabora, fechavence, producto_id,idDetalle,
    unidad_conversion, unidadcompra, cantidad, cantidad_min, cantidad_cri, deposito_carga, nombrecomercial  ) {

    const fechaParts = fechaelabora.match(/(\d+) de (\w+) de (\d+)/);
    const day = fechaParts[1];
    const month = fechaParts[2];
    const year = fechaParts[3];

    const months = {
    'enero': '01',
    'febrero': '02',
    'marzo': '03',
    'abril': '04',
    'mayo': '05',
    'junio': '06',
    'julio': '07',
    'agosto': '08',
    'septiembre': '09',
    'octubre': '10',
    'noviembre': '11',
    'diciembre': '12'
    };

    const fechaFormateada = `${year}-${months[month]}-${String(day).padStart(2, '0')}`;

    const fechaParts2 = fechavence.match(/(\d+) de (\w+) de (\d+)/);
    const day2 = fechaParts2[1];
    const month2 = fechaParts2[2];
    const year2 = fechaParts2[3];

    const months2 = {
    'enero': '01',
    'febrero': '02',
    'marzo': '03',
    'abril': '04',
    'mayo': '05',
    'junio': '06',
    'julio': '07',
    'agosto': '08',
    'septiembre': '09',
    'octubre': '10',
    'noviembre': '11',
    'diciembre': '12'
    };

    const fechaFormateada2 = `${year2}-${months2[month2]}-${String(day2).padStart(2, '0')}`;
    
``
    costo = parseFloat(costo.replace(',','.'))
    venta = parseFloat(venta.replace(',','.'))
    document.getElementById('idDetalle').value = idDetalle
    document.getElementById('codigoUpdate').value = codigo
    document.getElementById('categoriaUpdate').value = categoria
    document.getElementById('pivaUpdate').value = piva.replace(',','.')
    document.getElementById('costoUpdate').value = costo.toFixed(2)
    document.getElementById('ventaUpdate').value = venta.toFixed(2)
    document.getElementById('exampleDataListUpdate').value =nombre
    document.getElementById('producto_id_update').value =producto_id
    document.getElementById('laboratorioUpdate').value = laboratorio
    document.getElementById('presentacion_entradaUpdate').value =presentacion
    document.getElementById('presentacion_salidaUpdate').value =presentacionsalida
    document.getElementById('loteUpdate').value =lote
    document.getElementById('fechaelaboraUpdate').value =fechaFormateada
    document.getElementById('fechavenceUpdate').value =fechaFormateada2
    document.getElementById('conversionUpdate').value = unidad_conversion
    document.getElementById('unidad_compraUpdate').value = unidadcompra
    document.getElementById('cantidadcompraUpdate').value = cantidad
    document.getElementById('cantidad_minimaUpdate').value = cantidad_min
    document.getElementById('cantidad_criticaUpdate').value = cantidad_cri
    document.getElementById('depositoUpdate').value = deposito_carga
    document.getElementById('nombrecomercialUpdate').value = nombrecomercial
    
    
/* 
        $.ajax({
            type: 'GET',
            url: '/refresh_table_deposito/' + '?idDetalle=' + idDetalle,
            dataType: 'html',
            success: function(data) {
                $('#tabla-deposito-transito').html(data);
            }
        });

 */

    $('#updateProducto').modal('show')
}


function eliminarProducto(producto_id) {

    const datos = {
        producto_id: producto_id,
      };
    
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
      fetch('/eliminarProductoFactura/', {
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
        refreshDetalleNota(data['idNota'])
        // Llama a la función que deseas ejecutar después de recibir la respuesta de éxito
      })
      .catch(error => console.error(error));
}


const inputMoneda = document.getElementById('tasacambiofactura');
const div = document.getElementById('muestratasa');
// Agrega un evento change al inputMoneda
inputMoneda.addEventListener('change', function() {
    // Agrega la clase 'oculta' al div
    div.classList.remove('oculta');
});

/* const selectMoneda = document.getElementById('moneda_factura');
const divmoneda = document.getElementById('muestramoneda');
// Agrega un evento change al selectMoneda */


async function buscarExiteProducto() {
    var nroDocumento = document.getElementById('numerofactura').value;
    var nroControl = document.getElementById('numeronota').value;
    var idProveedor = document.getElementById('proveedor').value;
    const datos = {
        nroDocumento: nroDocumento,
        nroControl: nroControl,
        idProveedor: idProveedor,
    };
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    try {
        const response = await fetch('/buscar_existe_factura_inventario/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`); //Manejo de errores de HTTP
        }
        const data = await response.json();
        var existe = data['existe'];
        return existe; // Retorna el valor booleano
    } catch (error) {
        throw error; // Re-lanza el error para que `validarDatos` lo capture
    }
}

function cambioConcepto() {

}
