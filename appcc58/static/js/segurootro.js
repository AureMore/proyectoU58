window.onload = function() {
    document.getElementById("id_grupo").value = 'S';
    document.querySelector("label[for='id_cedula']").innerHTML = "RIF (Gxxxxxxxx)";
    document.querySelector("label[for='id_nombre']").innerHTML = "Nombre / Razon Social";

    document.querySelector("label[for='id_tipopersonal']").innerHTML = "Relacion";

};