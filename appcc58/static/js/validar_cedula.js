function handleCedulaInput(input) {
    let value = input.value.toUpperCase();

    // Eliminar todo lo que no sea letra o número
    value = value.replace(/[^A-Z0-9]/g, '');

    if (value.length === 0) {
        input.value = '';
        return;
    }

    let firstChar = value.charAt(0);
    let numbers = '';

    // Si el primer carácter es número → colocar J por defecto
    if (/\d/.test(firstChar)) {
        numbers = value.replace(/\D/g, '');
        firstChar = 'V';
    } 
    // Si es letra válida
    else if (['V', 'E', 'P'].includes(firstChar)) {
        numbers = value.slice(1).replace(/\D/g, '');
    } 
    // Si es letra inválida → limpiar
    else {
        input.value = '';
        return;
    }

    // Limitar a 10 números
    numbers = numbers.substring(0, 10);

    // Construir formato
    if (numbers.length > 0) {
        input.value = firstChar + '-' + numbers;
    } else {
        input.value = firstChar;
    }
}