function activarcompuesto(comportamiento) {
    console.log(comportamiento)
    if (comportamiento == '2') {
        document.getElementById('conversion').value = 1
        document.getElementById('ventaUpdate').value = 0.00
    }
}

$(document).ready(function(){
    let categoria = document.getElementById('updateCategoria').value
    verificarIva(categoria)
})

function verificarIva(categoria) {
    if (categoria == 1) {
        document.getElementById('pivaUpdate').value = 0
        document.getElementById('pivaUpdate').readOnly = true
        document.getElementById("pivaUpdate").style.backgroundColor = "#e9ecef";
    } else {
        document.getElementById('pivaUpdate').readOnly = false
        document.getElementById("pivaUpdate").style.backgroundColor = "white";
    }
    
}