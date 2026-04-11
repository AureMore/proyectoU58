let timeout;

 // Función para cerrar sesión
 function logOut() {
     // Redirigir a la URL de cierre de sesión
     window.location.href = '/salir/';  // Cambia esto a la URL de tu vista de logout
 }
 // Función para reiniciar el temporizador
 function resetTimer() {
     clearTimeout(timeout);
     timeout = setTimeout(logOut, 1200000); // 20minutos en milisegundos
 }
 // Eventos para detectar actividad del usuario
 window.onload = resetTimer;
 window.onmousemove = resetTimer;
 window.onkeydown = resetTimer;  // Cambiado de onkeypress a onkeydown
 window.onscroll = resetTimer;