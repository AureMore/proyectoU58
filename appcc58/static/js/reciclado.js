function reciclarProducto(nombre, nombrecomercial, codigo, id_inventario, max_quantity) {
    $('#staticBackdrop').modal('show')
    document.getElementById('producto-reciclar').innerHTML = codigo + ' - '+ nombre + ' - ' +nombrecomercial 
    document.getElementById('id_inventario').value = id_inventario
    document.getElementById('max_quantity').value = parseFloat(max_quantity)
}

function reciclar() {
    const id_inventario = document.getElementById('id_inventario').value
    const cantidad_ingresar = document.getElementById('cantidad-reciclar').value
    let max_quantity = document.getElementById('max_quantity').value
    if (parseFloat(cantidad_ingresar) > parseFloat(max_quantity)) {
        alert('No puede reusar cantidad mayor a la cantidad de salida del producto')
        document.getElementById('cantidad-reciclar').value = 0
        return
    }
    if (parseFloat(cantidad_ingresar) > 0) {

            Swal.fire({
            title: "Esta seguro(a) ?",
            text: "Al reciclar, el producto vuelve al inventario de FARMACIA para su uso!",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Si, Continuar!"
        }).then((result) => {
            if (result.isConfirmed) {
            // a ingresar el producto al inventario
                const datos = {
                    id_inventario: id_inventario,
                    cantidad_ingresar: cantidad_ingresar,
                };


                fetch('/ingresar_reciclado_inventario/', {
                    method: 'POST',
                    headers: {
                    'Content-Type': 'application/json',
                    }, 
                    body: JSON.stringify(datos)
                })
                .then(response => response.json())
                .then(data => {
                    location.reload()    
                })
                .catch(error => console.error(error));

            // fin de ingresar en django
            }
        });

    } else {
        alert('Debe colocar la cantidad')
    }
    
    
}

function cantidad_value(cantidad) {
    let max_quantity = document.getElementById('max_quantity').value
    if (parseFloat(cantidad) > parseFloat(max_quantity)) {
        alert('No puede reusar cantidad mayor a la cantidad de salida del producto')
        document.getElementById('cantidad-reciclar').value = 0
    }
}