

/* ===============================
   ABRIR MODAL Y ENCENDER CÁMARA
================================ */
let paginas = [];
let cirugiaID = null;
let stream = null;

function abrirScanner(id) {
    cirugiaID = id;
    paginas = [];

    const modalEl = document.getElementById("scannerModal");
    const previewEl = document.getElementById("preview");
    const contadorEl = document.getElementById("contador");
    const videoEl = document.getElementById("video");

    // Seguridad: salir si alguno no existe
    if (!modalEl || !previewEl || !contadorEl || !videoEl) {
        console.error("Modal o elementos preview/contador/video no existen");
        return;
    }

    // Reset UI
    previewEl.innerHTML = "";
    contadorEl.innerText = "0 páginas";

    // Abrir modal
    const modal = new bootstrap.Modal(modalEl, {
        backdrop: 'static',
        keyboard: false
    });
    modal.show();

    // Encender cámara
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(s => {
            stream = s;
            videoEl.srcObject = stream;
        })
        .catch(() => alert("No se pudo acceder a la cámara"));
}

function detenerCamara() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
}

let zoom = 1; // zoom inicial

function ajustarZoom(cambio) {
    zoom += cambio;
    if (zoom < 0.5) zoom = 0.5;   // límite mínimo
    if (zoom > 3) zoom = 3;       // límite máximo

    const video = document.getElementById("video");
    video.style.transform = `scale(${zoom})`;
}


/* ===============================
   CAPTURAR IMAGEN CON AJUSTES
================================ */
function capturar() {
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");

    const brillo = parseInt(document.getElementById("brillo").value);
    const contraste = parseInt(document.getElementById("contraste").value);

    ctx.filter = `brightness(${100 + brillo}%) contrast(${100 + contraste}%)`;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imgData = canvas.toDataURL("image/jpeg", 0.95);
    if (paginas.length > 5 ) {
        alert('Ha alcanzado el maximo de capturas x documento')
    } else {
        paginas.push(imgData);
        // Actualizar contador
        document.getElementById("contador").innerText = paginas.length + " páginas";

        // Agregar preview
        actualizarPreview();
    }
    
    

    
}

/* ===============================
   MOSTRAR MINIATURAS
================================ */
function actualizarPreview() {
    const preview = document.getElementById("preview");
    preview.innerHTML = "";

    paginas.forEach((img, index) => {
        preview.innerHTML += `
        <div class="position-relative me-2 border p-1" style="width:130px">
            <img src="${img}" width="100%">
            <button class="btn btn-sm btn-danger position-absolute top-0 end-0"
                    onclick="eliminarPagina(${index})">
                    <i class="fa-regular fa-trash-can"></i>
            </button>
        </div>`;
    });
}

/* ===============================
   ELIMINAR PÁGINA DEL PREVIEW
================================ */
function eliminarPagina(index) {
    paginas.splice(index, 1);
    document.getElementById("contador").innerText = paginas.length + " páginas";
    actualizarPreview();
}

/* ===============================
   GUARDAR PDF EN EL SERVIDOR
================================ */
function guardarPDF() {
    if (!paginas.length) {
        alert("No hay páginas capturadas");
        return;
    }

    const csrf_token = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch("/cirugias/guardar-pdf/", {
        method: "POST",
        headers: {
            "X-CSRFToken": csrf_token,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            cirugia_id: cirugiaID,
            paginas: paginas
        })
    }).then(() => {
        // alert("PDF guardado correctamente");
        detenerCamara();
        location.reload();
    }).catch(() => alert("Error al guardar PDF"));
}

