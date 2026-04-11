let panelVisible = true;

function togglePanel() {
    const panel = document.getElementById("panelSeleccion");
    const buttonIcon = panel.querySelector(".btn-toggle-panel i");

    if (panelVisible) {
        panel.classList.add("panel-oculto");
        buttonIcon.classList.remove("fa-chevron-up");
        buttonIcon.classList.add("fa-chevron-down");
    } else {
        panel.classList.remove("panel-oculto");
        buttonIcon.classList.remove("fa-chevron-down");
        buttonIcon.classList.add("fa-chevron-up");
    }

    panelVisible = !panelVisible;
}

let panelVisible3 = true;

function togglePanelHc3() {
    const panel = document.getElementById("panelHistoria3");
    const buttonIcon = panel.querySelector(".btn-toggle-panel i");

    if (panelVisible3) {
        panel.classList.add("panel-oculto");
        buttonIcon.classList.remove("fa-chevron-up");
        buttonIcon.classList.add("fa-chevron-down");
    } else {
        panel.classList.remove("panel-oculto");
        buttonIcon.classList.remove("fa-chevron-down");
        buttonIcon.classList.add("fa-chevron-up");
    }

    panelVisible3 = !panelVisible3;
}

function eliminarEvolucion(evolucion_id) {

    const datos = {
            evolucion_id : evolucion_id,
          };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/eliminar_evolucion_hc/', {
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

function calcularIMC() {
    let peso = parseFloat(document.getElementById("peso").value) || 0;
    let talla = parseFloat(document.getElementById("talla").value) || 0;
    talla = (talla / 100)
    console.log('talla', talla)
    if (peso > 0 && talla > 0) {
        let imc = peso / (talla * talla);
        document.getElementById("imc").value = imc.toFixed(2);
    } else {
        document.getElementById("imc").value = '0.00';
    }
}