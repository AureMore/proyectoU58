let table;

$(document).ready(function () {
    cargarDataTable();
});

function cargarDataTable() {

    table = $('#tbl-facturas-retencion').DataTable({
        pageLength: 50,
        language: {
            search: "Buscar:",
            lengthMenu: "Mostrar _MENU_ registros",
            info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
            infoEmpty: "Mostrando 0 a 0 de 0 registros",
            infoFiltered: "(filtrado de _MAX_ registros totales)",
            zeroRecords: "No se encontraron registros",
            emptyTable: "No hay datos disponibles",
            paginate: {
                first: "Primero",
                last: "Último",
                next: "Siguiente",
                previous: "Anterior"
            }
        }
        
    });

}
 

function advertenciaISLR(event) { 
    event.preventDefault();

    Swal.fire({
        title: "Seguro(a)?",
        text: "Operacion sin reverso al generar el comprobante de ISLR",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Si, Proceder!"
      }).then((result) => {
        if (result.isConfirmed) {
        //medicos diferentes

            const table = document.getElementById('tbl-facturas-retencion');
            const checkboxes = table.querySelectorAll('input[name="name_checkretencion"]');
            
            let selectedRows = [];
            let medicos = [];
            
            checkboxes.forEach((checkbox) => {
            if (checkbox.checked) {
                const row = checkbox.parentNode.parentNode;
                const medico = row.cells[2].textContent;
                selectedRows.push(row);
                medicos.push(medico);
            }
            });
            
            // Verificar si hay médicos diferentes
            const uniqueMedicos = [...new Set(medicos)];
            if (uniqueMedicos.length > 1) {
                
                Swal.fire({
                    title: "Seleccion errada!",
                    text: "No debe seleccionar beneficiarios diferentes, los comprobantes de retencion deben ser de un unico beneficiario ",
                    icon: "error"
                  });


            } else {
            event.target.submit();
            }
        


        //fin medicos diferentes
            // Envía el formulario manualmente
        } 
      });

}

document.getElementById('btnExportarDistribucion')
.addEventListener('click', exportarDistribucion);

function exportarDistribucion() {

    let datos = [];

    datos.push([
        'Fecha Emisión',
        'Beneficiario',
        'Tipo',
        'Documento',
        'Control',
        'Monto $',
        'Monto Bs'
    ]);

    table.rows().every(function () {

        const fila = this.node();

        const checkbox = $(fila).find(
            'input[name="name_distribucion"]'
        );

        if (checkbox.prop('checked')) {

            const celdas = $(fila).find('td');

            datos.push([
                celdas.eq(0).text().trim(), // Fecha
                celdas.eq(1).text().trim(), // Beneficiario
                celdas.eq(2).text().trim(), // Tipo
                celdas.eq(3).text().trim(), // Documento
                celdas.eq(4).text().trim(),  // Control
                celdas.eq(9).text().trim(), // Documento
                celdas.eq(10).text().trim(),  // Control
            ]);
        }
    });

    if (datos.length === 1) {

        Swal.fire({
            icon: 'warning',
            title: 'Sin selección',
            text: 'Debe seleccionar al menos una factura'
        });

        return;
    }

    const ws = XLSX.utils.aoa_to_sheet(datos);

    for (let i = 2; i <= datos.length; i++) {

        const celda = ws['F' + i];
        let celdaBs = ws['G' + i];

        if (celda) {
            celda.t = 'n';     // número
            celda.z = '#,##0.00';
        }

        if (celdaBs) {
            celdaBs.t = 'n';
            celdaBs.z = '#,##0.00';
        }
    }

    const wb = XLSX.utils.book_new();

    XLSX.utils.book_append_sheet(
        wb,
        ws,
        'Distribucion'
    );

    XLSX.writeFile(
        wb,
        'distribucion_moneda.xlsx'
    );
}