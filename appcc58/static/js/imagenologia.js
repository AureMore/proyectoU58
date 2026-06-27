let zoom = 1;

function abrirModal(imgUrl) {
    zoom = 1;
    const modal = document.getElementById("imageModal");
    const img = document.getElementById("modalImage");
    img.src = imgUrl;
    img.style.transform = "scale(1)";
    modal.style.display = "block";
}

function cerrarModal() {
    document.getElementById("imageModal").style.display = "none";
}

function zoomIn() {
    zoom += 0.1;
    document.getElementById("modalImage").style.transform = `scale(${zoom})`;
}

function zoomOut() {
    zoom = Math.max(0.5, zoom - 0.1);
    document.getElementById("modalImage").style.transform = `scale(${zoom})`;
}

let destinoCaptura = "archivo_pdf";
let cameraStream = null;
let currentCamera = "environment";

function abrirCamara(destino = "archivo_pdf") {

    destinoCaptura = destino;

    const modal = document.getElementById("cameraModal");
    const video = document.getElementById("cameraVideo");

    modal.style.display = "flex";

    navigator.mediaDevices.getUserMedia({
        video: {
            facingMode: currentCamera
        }
    })
    .then(function(stream){

        cameraStream = stream;
        video.srcObject = stream;

    })
    .catch(function(error){

        alert("No se pudo acceder a la cámara.");

    });
}

function cerrarCamara(){

    document.getElementById("cameraModal").style.display = "none";

    if(cameraStream){

        cameraStream.getTracks().forEach(track => track.stop());

        cameraStream = null;
    }
}

function cambiarCamara(){

    currentCamera =
        currentCamera === "environment"
        ? "user"
        : "environment";

    cerrarCamara();

    setTimeout(() => {
        abrirCamara();
    }, 200);
}

function capturarFoto(){

    const video = document.getElementById("cameraVideo");
    const canvas = document.getElementById("cameraCanvas");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");

    ctx.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );

    canvas.toBlob(function(blob){

        const archivo = new File(
            [blob],
            "captura.jpg",
            {type:"image/jpeg"}
        );

        const dt = new DataTransfer();

        dt.items.add(archivo);

        const input = document.querySelector(
            'input[name="' + destinoCaptura + '"]'
        );

        input.files = dt.files;

        cerrarCamara();

    }, "image/jpeg", 0.9);
}