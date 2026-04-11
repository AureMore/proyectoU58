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