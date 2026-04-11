let dataTable;
let dataTableIsInitialized = false;

const dataTableOptions = {
    pageLength: 500,
    destroy: true,
    language: {
        search: "Buscar:",
        lengthMenu: "Mostrar _MENU_ registros",
        info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
        infoEmpty: "Mostrando 0 a 0 de 0 registros",
        infoFiltered: "(filtrado de _MAX_ registros totales)",
        zeroRecords: "No se encontraron registros coincidentes",
        paginate: {
            first: "Primero",
            last: "Último",
            next: "Siguiente",
            previous: "Anterior"
        },
        loadingRecords: "Cargando...",
        processing: "Procesando..."
    },
    dom: 'Bfrtip',
    buttons: [
        {
            extend: 'excelHtml5',  // Botón para exportar a Excel
            text: 'Exportar a Excel',  // Texto del botón (puedes cambiarlo)
            className: 'btn btn-success',  // Clase CSS opcional para estilo (usa Bootstrap si lo tienes)
            filename: 'productos_export',  // Nombre base del archivo (se agrega fecha automáticamente)
            exportOptions: {
                modifier: {
                    // Opcional: exporta solo columnas visibles (útil si ocultas columnas)
                    page: 'current',  // 'all' para todas las páginas, 'current' para página actual
                    search: 'applied'  // Respeta filtros aplicados
                },
                columns: ':visible' ,  // Opcional: especifica qué columnas exportar (ajusta según tu tabla)
            }
        },
    ]

}

const initDataTable = async()=>{
    if (dataTableIsInitialized){
        dataTable.destroy()
    }

    await listProducts();

    dataTable=$('#datatable-productos').DataTable(dataTableOptions);
    dataTableIsInitialized = true
}



const listProducts = async () => {
    var fecha_tope = document.getElementById('id_fecha_tope').value
    var fecha_inicio = document.getElementById('id_fecha_inicio').value 
    var categoria_filtro = document.getElementById('categoria_filtro').value

     try {
        const response = await fetch(`/refrescar_tabla_inventario_contable/?fecha_tope=${fecha_tope}&categoria_filtro=${categoria_filtro}&fecha_inicio=${fecha_inicio}`)
        const data = await response.json()
        let content=``
        data.productos.forEach((producto, index) => {
            const sin_soporte = (parseFloat(producto.total_entrada) || 0)- (parseFloat(producto.total_entrada_nota_entrega) || 0)
            const estiloNotaEntrega = sin_soporte != 0 ? 'style="color: red; font-weight:bold;"' : '';
            const estiloNotaEntregBlue = 'style="color: blue; font-weight:bold; text-align:right;"' ;
            const estiloNotaEntregGreen = 'style="color: green; font-weight: 900;"' ;
            const existencia = (parseFloat(producto.total_entrada_nota_entrega) || 0)  - (parseFloat(producto.total_descarga) || 0)
            
            let monto_iva = (parseFloat(producto.costo) || 0) * ((parseFloat(producto.piva) || 0) / 100)
            let costo_total = (monto_iva) + (parseFloat(producto.costo) || 0)
            


            content+=`
                <tr>
                    <td>${index+1}</td>
                    <td>${producto.codigo}</td>
                    <td>${producto.nombre}</td>
                    <td>${producto.nombre_comercial}</td>
                    <td ${estiloNotaEntregGreen}>${costo_total.toFixed(2)}</td>
                    <td style="text-align:right;">
                        ${(parseFloat(producto.total_descarga).toFixed(2) || 0)}
                     </td>
                    <td style="text-align:center;">${producto.presentacion_salida__nombre}</td>
                    <td style="text-align:right;">${producto.unidad_conversion}</td>
                    <td style="text-align:right;">${(parseFloat(producto.total_entrada_nota_entrega) || 0).toFixed(2)} </td>
                    <td style="text-align:center;">${producto.unidadcompra__nombre}</td>
                    <td ${estiloNotaEntregBlue}>${existencia.toFixed(2)}</td>
                    <td style="text-align:center;">${producto.presentacion_salida__nombre}</td>
                    
                </tr>
            `
        });
        tableBody_inventario.innerHTML = content
    } catch (ex) {
        alert(ex);
    }
}

window.addEventListener("load", async () => {
     //let inventario_id = document.getElementById('inventario_id_producto').value
    await initDataTable();
})

async function seleccion_fechas() {
    await initDataTable();
}