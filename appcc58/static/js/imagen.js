var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
document.getElementById('generateJpgFromHtml').addEventListener('click', function() {
    id_nombre_jpg = document.getElementById('id_nombre_jpg').value
    html2canvas(document.querySelector('#contenido_jpg')).then(function(canvas) {
        var image = canvas.toDataURL('image/jpeg').split(',')[1];
        var byteString = atob(image);
        var arrayBuffer = new ArrayBuffer(byteString.length);
        var int8Array = new Uint8Array(arrayBuffer);
        for (var i = 0; i < byteString.length; i++) {
            int8Array[i] = byteString.charCodeAt(i);
        }
        var blob = new Blob([int8Array], { type: 'image/jpeg' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a'); 
        a.href = url;
        a.download = 'archivo_' + id_nombre_jpg + '.jpg';
        a.click();

        // enviar archivo para que lo ejecute el servidoral servidor
        html2canvas(document.querySelector('#contenido_jpg')).then(function(canvas) {
            var image = canvas.toDataURL('image/jpeg');
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/save-image/', true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.setRequestHeader('X-CSRFToken', csrftoken); // Agregar el token CSRF
            xhr.onload = function() {
              if (this.status === 200 ) {
                console.log("Guardado en server")
              } else {
                // Error al guardar la imagen
              }
            };
           
            var filename = 'archivo_' + id_nombre_jpg  +'.jpg' ; // Agregar el valor de clientId al nombre del archivo
            xhr.send('image=' + encodeURIComponent(image) + '&filename=' + encodeURIComponent(filename) );
      
          }); 

        // fin 
    }); 

});
