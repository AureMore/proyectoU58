function handleCedulaInput(input) {
    const value = input.value.trim();
    var firts_letter = value
    if (/[^A-Za-z]/.test(value.charAt(0))) {
        input.value = 'V' +  firts_letter + value.slice(1).replace(/\D/g, '');
    } else {
        input.value = value.charAt(0).toUpperCase() + value.slice(1).replace(/\D/g, '');
    }
}