function handleRifInput(input) {
    // Convertir a mayúsculas
    let value = input.value.toUpperCase();

    // Eliminar todo lo que no sea letra o número
    value = value.replace(/[^A-Z0-9]/g, '');

    // Validar que la primera letra sea G, J o P
    if (value.length > 0) {
        let firstLetter = value.charAt(0);

        if (!['G', 'J', 'P'].includes(firstLetter)) {
            value = ''; // Limpia si no es válida
            input.value = value;
            return;
        }

        // Separar letra y números
        let numbers = value.slice(1).replace(/\D/g, '');

        // Limitar a 10 números máximo
        numbers = numbers.substring(0, 13);

        // Construir formato final
        if (numbers.length > 0) {
            value = firstLetter + '-' + numbers;
        } else {
            value = firstLetter;
        }
    }

    input.value = value;
}