function generarNotaCredito(detalle_factura_id) {

    const checkboxes = document.querySelectorAll('input[name="input_chek"]:checked');

    if (checkboxes.length === 0) {
        Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Debe seleccionar al menos un item",
            width: '300px'
        });
        return;
    }

    Swal.fire({
        title: "Seguro(a) de seguir?, este proceso no tiene reverso!",
        text: "Ingrese el número de la nota de crédito",
        icon: "warning",
        input: "text",
        inputPlaceholder: "Ej: 000123",
        showCancelButton: true,
        confirmButtonText: "Si continuar!",
        cancelButtonText: "Cancelar",
        width: '400px',
        customClass: {
            confirmButton: 'btn-grande',
            cancelButton: 'btn-grande',
            title: 'txt-sw',
            },

        // 🔥 Validación del input
        inputValidator: (value) => {
            if (!value) {
                return "Debe ingresar el número de la nota de crédito";
            }
        }

    }).then((result) => {
        if (result.isConfirmed) {

            let numeroNotaCredito = result.value;

            console.log("Número NC:", numeroNotaCredito);

            // Obtener IDs seleccionados
            let ids = [];
            checkboxes.forEach((checkbox) => {
                let id = checkbox.id.replace('input_check_', '');
                ids.push(id);
            });

            // Enviar a Django 👇
            fetch('/generar_nota_credito/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    factura_id: detalle_factura_id,
                    items: ids,
                    numero_nc: numeroNotaCredito
                })
            })
            .then(response => response.json())
            .then(data => {
                Swal.fire({
                    icon: "success",
                    title: "Listo",
                    text: "Nota de crédito generada",
                    timer: 2000,              // ⏱ 2 segundos
                    timerProgressBar: true,   // barra de progreso (opcional)
                    showConfirmButton: false  // oculta el botón
                }).then(() => {
                    location.reload();
                });
            });

        }
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}