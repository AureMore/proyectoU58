


function cambio_moneda_factura(moneda) {
  if (moneda == '1') {
    document.getElementById("costo_moneda").innerText = "Costo en USD";
    document.getElementById("venta_moneda").innerText = "Venta en USD";
  } else {
    document.getElementById("costo_moneda").innerText = "Costo en BS.";
    document.getElementById("venta_moneda").innerText = "Venta en BS.";
  }
  
}


$(document).ready(function() {
    $('#exampleDataList').on('input', function() {
        var selectedOption = $(this).val();
        selectedOption = selectedOption.replace(/"/g, '')
        $(this).val(selectedOption);

        var selectedId = $('option[value="' + selectedOption + '"]').data('id');
        $('#medico_id').val(selectedId);
    });

   new DataTable('#tbl-pag-medico', {
    pageLength: 25,
    language: {
        decimal: "",
        emptyTable: "No hay datos disponibles",
        info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
        infoEmpty: "Mostrando 0 a 0 de 0 registros",
        infoFiltered: "(filtrado de _MAX_ registros totales)",
        lengthMenu: "Mostrar _MENU_ registros",
        loadingRecords: "Cargando...",
        processing: "Procesando...",
        search: "Buscar:",
        zeroRecords: "No se encontraron resultados",
        paginate: {
            first: "Primero",
            last: "Último",
            next: "Siguiente",
            previous: "Anterior"
        }
    }

   }); 
});


