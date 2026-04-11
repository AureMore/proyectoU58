function desactivarMedioPagoProveedor(id_mediopago) {
    const datos = {
            id_mediopago : id_mediopago,
          };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/desactivar_medio_pago_proveedor/', {
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

/* document.addEventListener("DOMContentLoaded", function () {
    const rifInput = document.querySelector("#id_rif");

    rifInput.addEventListener("input", function () {
        let value = rifInput.value.toUpperCase();

        // Quitar espacios
        value = value.replace(/\s+/g, "");

        // Si escribe solo la letra, validamos que sea permitida
        if (/^[VJGPE]$/i.test(value)) {
            value = value + "-";
        }

        // Evitar que escriba letras inválidas
        if (!/^[VJGPE]-?\d*$/.test(value)) {
            // Si no cumple el patrón, lo recortamos al último válido
            value = value.slice(0, -1);
        }

        // Asegurar que el guion siempre se mantenga después de la letra
        if (/^[VJGPE]/.test(value) && !/^[VJGPE]-/.test(value)) {
            value = value[0] + "-";
        }

        rifInput.value = value;
    });

    // Evitar borrar el guion
    rifInput.addEventListener("keydown", function (e) {
        const cursorPos = rifInput.selectionStart;
        if ((e.key === "Backspace" || e.key === "Delete") && cursorPos === 2) {
            e.preventDefault();
        }
    });
}); */