$(document).ready(function() {
    // Inicializa la DataTable y establece la longitud de página a 25
    var table = new DataTable('#tblnotacredito', {
        pageLength: 25 // Muestra los primeros 25 registros
    });
});

function eliminarNotaCredito(id_notacredito, autogenerada, aplicada) {
    console.log('autogenerada:', autogenerada)
    if (autogenerada === 'True' || aplicada === 'True') {
        Swal.fire({
            icon: "error",
            title: "CONDICION:AUTOGENERADA / PAGADA",
            text: "Para eliminar esta nota de credito (pagada ó autogenerada) , debe realizarlo por la opcion pendiente por cobrar! ",
            
            });
    } else {
        const datos = {
            id_notacredito: id_notacredito,
            };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/eliminar_nota_credito/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }, 
        body: JSON.stringify(datos)
        })
        .then(response => response.json())
        .then(data => {
           location.reload()
        
        })
        .catch(error => console.error(error)); 

    }
}

function verRecibo(idrecibo) {
    console.log('recibo: ', idrecibo)
}