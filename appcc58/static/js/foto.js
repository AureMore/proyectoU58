"use strict";

 const video = document.querySelector(".video");
 const canvas = document.querySelector(".canvas");
 const button = document.querySelector(".start-btn");
 const photo = document.querySelector(".photo");
 const buttonCancel = document.querySelector(".buttonCancel");
 let takePhoto;
 //constrains
 /*
 Aquí enviamos las caracteristicas del video y
 audio que solicitamos
 */
 const constraints = {
    audio: false,
    video: {width:420, height:340},
 };
 //acceso a la webcam
 /*
 Aquí recibimos la respuesta del navegador, es una promesa
 */
 const init = async () => {
 try {
     const stream = await navigator.mediaDevices.getUserMedia(constraints);
     console.log(stream);
     handleSucces(stream);
 } catch (error) {
     console.log(error);
 }
 };
 //
 const handleSucces = (stream) => {
    window.stream = stream;
    video.srcObject = stream;
    video.play();
 };
 //
 init();
 //
 button.addEventListener("click", async () => {
    let context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, 420, 340);
    let data = canvas.toDataURL("image/png");
    photo.setAttribute("src", data);
    const cedulaElement = document.querySelector('#cedula_file strong');
    let cedula = cedulaElement.textContent;
    cedula = cedula.trim();
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
     // Enviar la imagen al servidor
     const response = await fetch('/api/upload-photo/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,// Asegúrate de incluir el token CSRF
        },
        body: JSON.stringify({ image: data, cedula : cedula })
    });

    if (response.ok) {
        console.log('Foto guardada exitosamente');
         // Aquí puedes actualizar el src de la imagen en el HTML
         const imagenPreview = document.getElementById('imagen-preview');
         // Suponiendo que el servidor devuelve la URL de la imagen guardada
         const imagenUrl = `${window.location.origin}/media/${cedula}.png` ; // Cambia esto según tu lógica
         imagenPreview.setAttribute('src', `${imagenUrl}?t=${new Date().getTime()}`); // Evita caché


    } else {
        console.error('Error al guardar la foto');
    }


 });

