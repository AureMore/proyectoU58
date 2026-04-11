var groupColumn = 1;
var table = $('#tblexistencia').DataTable({
    dom: 'Bfrtip',
    buttons: [
        {
            extend: 'excelHtml5',
            text: '<i class="fas fa-file-excel fa-lg"></i> Exportar a Excel',
            title: 'Inventario',
            exportOptions: {
                modifier: {
                    page: 'all' // Exporta todos los datos, no solo los de la página activa
                },
                columns: ':visible' ,
                format: {
                    body: function(data, row, column, node) {
                        // Verifica si la columna es la de cantidad (ajusta el índice según tu tabla)
                        if (column === 0 || column == 5) { // Cambia 2 por el índice real de tu columna de cantidad
                            // Reemplaza la coma por punto
                            return data.replace(',', '.');
                        }
                        return data; // Devuelve el dato sin cambios para otras columnas
                    }
                }
            }
        },
        
    ],
    columnDefs: [{ visible: false, targets: groupColumn }],
    order: [[groupColumn, 'asc']],
    pageLength : 50,

    drawCallback: function (settings) {
        var api = this.api();
        var rows = api.rows({ page: 'current' }).nodes();
        var last = null;
 
        api.column(groupColumn, { page: 'current' })
            .data()
            .each(function (group, i) {
                if (last !== group) {
                    $(rows)
                        .eq(i)
                        .before(
                            '<tr class="group"><td colspan="5" style="font-family: Impact, sans-serif;font-size: 14px;font-weight: 100;">' +
                                group +
                                '</td></tr>'
                        );
 
                    last = group;
                }
            });
    }
});
 
// Order by the grouping
$('#tblexistencia tbody').on('click', 'tr.group', function () {
    var currentOrder = table.order()[0];
    if (currentOrder[0] === groupColumn && currentOrder[1] === 'asc') {
        table.order([groupColumn, 'desc']).draw();
    }
    else {
        table.order([groupColumn, 'asc']).draw();
    }
});