function reciclarProducto(nombre, nombrecomercial, codigo, id_inventario, max_quantity, id_deposito) {
    $('#staticBackdrop').modal('show')
    document.getElementById('cantidad-reciclar').value = 0
    document.getElementById('cantidad-no-reciclable').value = 0
    document.getElementById('producto-reciclar').innerHTML = codigo + ' - '+ nombre + ' - ' +nombrecomercial 
    document.getElementById('id_inventario').value = id_inventario
    document.getElementById('id_deposito').value = id_deposito
    document.getElementById('max_quantity').value = parseFloat(max_quantity)
}

function reciclar() {
    const id_inventario = document.getElementById('id_inventario').value
    const cantidad_ingresar = document.getElementById('cantidad-reciclar').value
    const cantidad_no_reciclar = document.getElementById('cantidad-no-reciclable').value
    const disponible = document.getElementById('max_quantity').value 
    const deposito_afectado = document.getElementById('id_deposito').value

    if ((parseFloat(cantidad_no_reciclar) + parseFloat(cantidad_ingresar)) <= 0 ) {
         alert('Debe especificar alguna cantidad para reciclar o no reciclar')
         return
    }

    if ((parseFloat(cantidad_no_reciclar) + parseFloat(cantidad_ingresar)) > parseFloat(disponible)  ) {
         alert('No puede reciclar y/o desincorporar una cantidad mayor al disponible')
         document.getElementById('cantidad-no-reciclable').value = 0
         document.getElementById('cantidad-reciclar').value = 0
         return
    }

    let max_quantity = document.getElementById('max_quantity').value
    if (parseFloat(cantidad_ingresar) > parseFloat(max_quantity)) {
        alert('No puede reusar cantidad mayor a la cantidad de salida del producto')
        document.getElementById('cantidad-reciclar').value = 0
        document.getElementById('cantidad-no-reciclable').value = 0
        return
    }
    if (parseFloat(cantidad_ingresar) > 0 || parseFloat(cantidad_no_reciclar)) {

            Swal.fire({
            title: "Esta seguro(a) ?",
            text: "Al reciclar, el producto vuelve al inventario de FARMACIA para su uso y al NO RECICLABLE lo desincorpora del inventario!",
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
                    cantidad_no_reciclar : cantidad_no_reciclar,
                    deposito_afectado : deposito_afectado
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

    } 
    
    
}

function cantidad_value(cantidad) {
    let max_quantity = document.getElementById('max_quantity').value
    console.log('max_quantity', max_quantity)
    if (parseFloat(cantidad) > parseFloat(max_quantity)) {
        alert('No puede reusar cantidad mayor a la cantidad de salida del producto')
        document.getElementById('cantidad-reciclar').value = 0
        document.getElementById('cantidad-no-reciclable').value = 0
    }
}

function cantidad_no_reciclar(cantidad) {
    let max_quantity = document.getElementById('max_quantity').value
    if (parseFloat(cantidad) > parseFloat(max_quantity)) {
        alert('No puede reusar cantidad mayor a la cantidad de salida del producto')
        document.getElementById('cantidad-reciclar').value = 0
        document.getElementById('cantidad-no-reciclable').value = 0
    }
}