let dataTable;
let dataTableIsInitialized = false;
let facturasSeleccionadas = new Set();

const dataTableOptions = {
    pageLength: 25,
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
    }

}

const initDataTable = async()=>{
    if (dataTableIsInitialized){
        dataTable.destroy()
    }

    //let inventario_id = document.getElementById('inventario_id_producto').value
    await listProducts();

    dataTable=$('#tbl-facturas-compra').DataTable(dataTableOptions);
    dataTableIsInitialized = true
}


$(document).on('change', '.row-check', function () {

    const id = this.dataset.id

    if (this.checked){
        facturasSeleccionadas.add(id)
    } else {
        facturasSeleccionadas.delete(id)
    }


})



function actualizarCheckHeader(){

    const total = document.querySelectorAll('#tbl-facturas-compra tbody .row-check').length
    const checked = document.querySelectorAll('#tbl-facturas-compra tbody .row-check:checked').length

    const header = document.getElementById('check-all')

    header.checked = total > 0 && total === checked

}

function actualizarCheckboxesVisibles(){

    document.querySelectorAll('.row-check').forEach(check=>{

        const id = check.dataset.id
        check.checked = facturasSeleccionadas.has(id)

    })

}


const listProducts = async () => {
    inventario_id = 0
     try {
        const response = await fetch(`/list_factura_producto/?inventario_id=${inventario_id}`)
        const data = await response.json()
        let content=``
        data.productos.forEach((producto, index) => {
            const fecha = new Date(producto.fecha_entrega);
            
            const dia = String(fecha.getDate()).padStart(2, '0');
            const mes = String(fecha.getMonth() + 1).padStart(2, '0'); // Los meses van de 0 a 11
            const anio = fecha.getFullYear();

            // Construir el HTML del dropdown
            let opcionesHtml = `
                <div class="dropdown">
                    <button class="dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false" style="border: none; width: 100%; background-color: aquamarine; border-radius: 4px;">
                        Opciones
                    </button>
                    <ul class="dropdown-menu dropdown-menu-info">
            `;
            
            // Opción condicional: Modificar Factura (solo si monto_abonado_factura_bs == 0)
            
                opcionesHtml += `
                    <li><a class="dropdown-item fuente-lista" href="/factura_compra_modificar/${producto.id}/"><i class="fa-solid fa-pen-to-square"></i> Modificar Factura</a></li>
                `;
   
            
            // Opción siempre visible: Pagar Factura
            opcionesHtml += `
                        <li><a class="dropdown-item fuente-lista" href="/factura_compra_pagar/${producto.id}/"><i class="fa-solid fa-credit-card"></i> Pagar Factura</a></li>
                       
                    
            `;

            // Opción siempre visible: Pagar Multiple Factura
            opcionesHtml += `
                        <li style="cursor:pointer;"><a class="dropdown-item fuente-lista" href="/pago_multiples_facturas/${producto.proveedor_compra_id}/" ><i class="fa-solid fa-list-check"></i> Pagar Multiple Facturas</a></li>
                         </ul>
                    </div>
                    
            `;
            
            content+=`
                <tr>
                    <td>${index+1}</td>
                    <td>${dia}/${mes}/${anio} </td>
                    <td>${producto.proveedor_compra__rif}</td>
                    <td>${producto.proveedor_compra__nombre}</td>
                    <td>${producto.notaentrega__numerodocumento}</td>
                    <td>${producto.numerodocumento}</td>
                    <td>${producto.numerocontrol}</td>
                    <td>${producto.concepto__nombre}</td>
                    <td style="${producto.tipodocumento_id == 3 ? 'color:blue;' : ''}">
                        ${producto.tipodocumento__nombre}
                    </td>
                    <td>${producto.porcentaje_retencion_islr}</td>
                    <td>${producto.proveedor_compra__porcentaje_retencion}</td>
                    <td>
                        ${
                            producto.comprobante_id
                            ? `<a type="button" target="_blank" href="/pdf_retencion/${producto.comprobante_id}/">${producto.comprobante__comprobante}</a>`
                            : "..."
                        }
                    </td>
                    <td>${opcionesHtml}</td>
                    <td style="text-align:center;">
                        <input 
                            type="checkbox" 
                            class="row-check"
                            data-id="${producto.id}"
                            ${facturasSeleccionadas.has(String(producto.id)) ? "checked" : ""}
                        >
                    </td>
                </tr>
            `
        });
        tableBody_facturas.innerHTML = content
    } catch (ex) {
        alert(ex);
    }
}

window.addEventListener("load", async () => {
    //let inventario_id = document.getElementById('inventario_id_producto').value
    await initDataTable();
})