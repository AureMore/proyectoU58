const toggleBtn = document.getElementById('toggleQuestionsBtn');
    const questionsArea = document.getElementById('questionsArea');

    toggleBtn.addEventListener('click', () => {
        questionsArea.classList.toggle('show');
        toggleBtn.innerHTML  = questionsArea.classList.contains('show') ? '<i class="fa-solid fa-eye-slash"></i> Ocultar Cuestionario' : '<i class="fa-solid fa-eye"></i> Mostrar Cuestionario';
    });

    // Cambiar color de tarjeta según respuesta
document.querySelectorAll('.question-card').forEach(card => {
    const radios = card.querySelectorAll('input[type="radio"]');
    const detalle = card.querySelector('.detalle-si');

    radios.forEach(radio => {
        radio.addEventListener('change', () => {

            // Reset estilos
            card.classList.remove('si','no');

            if (radio.value === 'si') {
                card.classList.add('si');
                detalle.style.display = 'block';
            }

            if (radio.value === 'no') {
                card.classList.add('no');
                detalle.style.display = 'none';

                // Limpiar input si cambia a NO
                const input = detalle.querySelector('input');
                input.value = '';
            }
        });
    });
});



const maxChars = 1000;

document.querySelectorAll("textarea").forEach(textarea => {
    const contador = document.getElementById("count-" + textarea.id);

    textarea.addEventListener("input", () => {
        const restantes = maxChars - textarea.value.length;
        contador.textContent = restantes;

        if (restantes <= 100) {
            contador.style.color = "red";
            contador.style.backgroundColor = "#FFF"
        } else {
            contador.style.color = "#FFF";
        }
    });
});

function valoresDefecto() {
    var dtm_default = document.getElementById('dtm').value
    var ao_default = document.getElementById('ao').value
    var dem_default = document.getElementById('dem').value
    var rhmi_default = document.getElementById('rhmi').value
    var nota_default = document.getElementById('nota').value
    var aao_default = document.getElementById('aao').value

    var ekg_default = document.getElementById('ekg').value
    var rxtorax_default = document.getElementById('rxtorax').value

    if (dtm_default === '') {
        document.getElementById('dtm').value = '+ 6 cmt'
    }
    if (ao_default === '') {
        document.getElementById('ao').value = '+ 3 cmt'
    }
    if (dem_default === '') {
        document.getElementById('dem').value = '+ 12 cmt'
    }
    if (rhmi_default === '') {
        document.getElementById('rhmi').value = '+ 9 cmt'
    }
    if (nota_default === '') {
        document.getElementById('nota').value = 'Tiroide no visible ni palpable'
    }
    if (aao_default === '') {
        document.getElementById('aao').value = '+ 30°'
    }

    if (ekg_default === '') {
        document.getElementById('ekg').value = 'Trasado Normal'
    }
    if (rxtorax_default === '') {
        document.getElementById('rxtorax').value = 'Patron Normal'
    }
    
}


document.addEventListener("DOMContentLoaded", function() {
    valoresDefecto()
    const questionsArea = document.getElementById('questionsArea');
    questionsArea.classList.toggle('show');
    toggleBtn.innerHTML  = questionsArea.classList.contains('show') ? '<i class="fa-solid fa-eye-slash"></i> Ocultar Cuestionario' : '<i class="fa-solid fa-eye"></i> Mostrar Cuestionario';
    document.querySelectorAll('.question-card').forEach(card => {
        const radios = card.querySelectorAll('input[type="radio"]');
        const detalle = card.querySelector('.detalle-si');

        // Función para actualizar la visibilidad y el color
        function updateCard() {
            const siRadio = card.querySelector('input[value="si"]');
            const noRadio = card.querySelector('input[value="no"]');
            
            // Mostrar campo "Especifique"
            detalle.style.display = siRadio.checked ? 'block' : 'none';

            // Cambiar color según la respuesta
            card.classList.remove('si', 'no');
            if (siRadio.checked) {
                card.classList.add('si');  // verde
            } else if (noRadio.checked) {
                card.classList.add('no');  // rojo
            }
            // Si nada marcado, tarjeta normal
        }

        // Inicial al cargar la página
        updateCard();

        // Cambiar color y visibilidad al seleccionar radio
        radios.forEach(radio => {
            radio.addEventListener('change', updateCard);
        });
    });
});

function calcularIMC() {
    let peso = parseFloat(document.getElementById("peso").value) || 0;
    let talla = parseFloat(document.getElementById("talla").value) || 0;
    talla = (talla / 100)
    if (peso > 0 && talla > 0) {
        let imc = peso / (talla * talla);
        document.getElementById("imc").value = imc.toFixed(2);
    } else {
        document.getElementById("imc").value = '0.00';
    }
}


