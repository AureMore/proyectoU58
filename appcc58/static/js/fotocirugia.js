"use strict";

const video = document.querySelector(".video");
const canvas = document.querySelector(".canvas");
const button = document.querySelector(".start-btn");
const switchCameraButton = document.querySelector(".switch-camera-btn");
const photo = document.querySelector(".photo");
const buttonCancel = document.querySelector(".buttonCancel");
let currentCamera = 0; // 0 para la cámara trasera, 1 para la cámara frontal
let stream;

// Constraints
const constraints = {
    audio: false,
    video: {
         width: { ideal: 1080 }, // Resolución ideal
         height: { ideal: 1080 }, // Resolución ideal 
         facingMode: { exact: "environment" }
         }, // Cámara trasera por defecto
};

// Acceso a la webcam
const init = async () => {
    try {
        if (stream) {
            stream.getTracks().forEach(track => track.stop()); // Detener el stream anterior
        }
        const newConstraints = { ...constraints };
        if (currentCamera === 0) {
            newConstraints.video.facingMode = { exact: "user" }; // Cámara frontal
        } else {
            newConstraints.video.facingMode = { exact: "environment" }; // Cámara trasera
        }
        stream = await navigator.mediaDevices.getUserMedia(newConstraints); // CORRECCIÓN AQUÍ
        handleSuccess(stream);
    } catch (error) {
        console.log(error);
    }
};

const handleSuccess = (stream) => {
    window.stream = stream;
    video.srcObject = stream;
    video.play();
};

init();

button.addEventListener("click", async () => {
    canvas.width = 800; // Ancho de la cámara
    canvas.height = 800; // Alto de la cámara
    let context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    let data = canvas.toDataURL("image/png",0.9);
    photo.setAttribute("src", data);
    const cedulaElement = document.getElementById('id_idCirugia').value;
    let cedula = cedulaElement.trim();
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Enviar la imagen al servidor
    const response = await fetch('/api/upload_photo_cirugia/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ image: data, cedula: cedula })
    });

    if (response.ok) {
        console.log('Foto guardada exitosamente');
        location.reload();
    } else {
        console.error('Error al guardar la foto');
    }
});

// Evento para cambiar la cámara
switchCameraButton.addEventListener("click", () => {
    currentCamera = (currentCamera + 1) % 2; // Cambiar entre 0 y 1
    init(); // Reiniciar la cámara
});

function muestraModalfoto() {
    let cirugia_id = document.getElementById('id_idCirugia').value;
    console.log(cirugia_id);
    $('#fotoModal').modal('show');
}
