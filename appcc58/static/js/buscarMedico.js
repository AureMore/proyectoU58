


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
});


