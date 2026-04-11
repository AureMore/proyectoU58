document.addEventListener('DOMContentLoaded', function() {
    const fechaInput = document.getElementById('fecha_nac_paciente');
    const formulario = document.getElementById('formularioPaciente');
    
    // Configurar fecha máxima como hoy
    const today = new Date();
    const maxDate = today.toISOString().split('T')[0];
    fechaInput.setAttribute('max', maxDate);
    
    // Validación al salir del campo
    fechaInput.addEventListener('blur', function() {
        verificarFecha(this.value);
    });
    
    // Validación al enviar el formulario
    formulario.addEventListener('submit', function(e) {
        if (!verificarFecha(fechaInput.value)) {
            e.preventDefault();
            fechaInput.focus();
        }
    });
     // Función de verificación de fecha
    function verificarFecha(fecha) {
        const fechaInput = document.getElementById('fecha_nac_paciente');
        const fechaError = document.getElementById('fechaError');
        
        if (!fecha) {
            fechaInput.classList.add('is-invalid');
            fechaError.textContent = 'Por favor ingrese una fecha';
            return false;
        }
        
        const fechaSeleccionada = new Date(fecha);
        const hoy = new Date();
        
        if (fechaSeleccionada > hoy) {
            fechaInput.classList.add('is-invalid');
            fechaError.textContent = 'La fecha no puede ser mayor a la fecha actual';
            return false;
        }
        
        // Validación adicional para fechas muy antiguas
        const fechaMinima = new Date('1900-01-01');
        if (fechaSeleccionada < fechaMinima) {
            fechaInput.classList.add('is-invalid');
            fechaError.textContent = 'Por favor ingrese una fecha válida (después de 1900)';
            return false;
        }
        
        fechaInput.classList.remove('is-invalid');
        return true;
    }
    });