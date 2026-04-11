let dataTable;
let dataTableIsInitialized = false;

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

    let inventario_id = document.getElementById('inventario_id_producto').value
    await listProducts(inventario_id);

    dataTable=$('#datatable-productos').DataTable(dataTableOptions);
    dataTableIsInitialized = true
}



const listProducts = async (inventario_id) => {
     try {
        const response = await fetch(`/list_movimiento_producto/?inventario_id=${inventario_id}`)
        const data = await response.json()
        let content=``
        data.productos.forEach((producto, index) => {
            const fecha = new Date(producto.fecha_act);
            // Obtener día, mes y año con ceros a la izquierda si es necesario
            const dia = String(fecha.getDate()).padStart(2, '0');
            const mes = String(fecha.getMonth() + 1).padStart(2, '0'); // Los meses van de 0 a 11
            const anio = fecha.getFullYear();
            // Obtener hora y minutos con ceros a la izquierda
            const hora = String(fecha.getHours()).padStart(2, '0');
            const minutos = String(fecha.getMinutes()).padStart(2, '0');
            const iconHtml = producto.depositoentrada == null
                ? `<i class="fa-solid fa-file-export fa-lg" style="color:red;"></i>`
                : (producto.deposito == null
                    ? `<i class="fa-solid fa-file-import fa-xl" style="color: green;"></i>`
                    : `<i class="fa-solid fa-arrow-right-arrow-left fa-xl" style="color: blue;"></i>`
                );
            content+=`
                <tr>
                    <td>${index+1}</td>
                    <td style="text-align: center;">${iconHtml}</td>
                    <td>${dia}/${mes}/${anio} ${hora}:${minutos}</td>
                    <td>${producto.cirugia_id}</td>
                    <td>${producto.cantidad > 0 ? producto.cantidad : producto.cantidad_traslado}</td>
                    <td>${producto.tipodescarga__nombre}</td>
                    <td>${producto.nota}</td>
                    <td>${producto.deposito__nombre}</td>
                    <td>${producto.depositoentrada__nombre}</td>
                    <td>${producto.usuario__username}</td>

                    
                </tr>
            `
        });
        tableBody_productos.innerHTML = content
    } catch (ex) {
        alert(ex);
    }
}

window.addEventListener("load", async () => {
    //let inventario_id = document.getElementById('inventario_id_producto').value
    await initDataTable();
})