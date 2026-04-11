jQuery.fn.dataTableExt.oSort['date-eu-pre'] = function (date) {
    var dateParts = date.split('/');
    return (dateParts[2] + dateParts[1] + dateParts[0]) * 1; // Convertir a un número para ordenar
};

jQuery.fn.dataTableExt.oSort['date-eu-asc'] = function (a, b) {
    return ((a < b) ? -1 : ((a > b) ? 1 : 0));
};

jQuery.fn.dataTableExt.oSort['date-eu-desc'] = function (a, b) {
    return ((a < b) ? 1 : ((a > b) ? -1 : 0));
};


var table = $('#tblproductoproveedor').DataTable({
    displayLength: 25,
    columnDefs: [
        { type: 'date-eu', targets: 1 } // Especificar que la columna de fecha es del tipo 'date-eu'
    ],
    order: [[1, 'desc']]
   
})

