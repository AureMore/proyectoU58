function cambiarDescripcion(id_tipoproveedor, nombrenuevo) {
    if (nombrenuevo != '') {
       const datos = {
            id_tipoproveedor : id_tipoproveedor,
            nombrenuevo : nombrenuevo
          };
        
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/cambiar_nombre_tipo_proveedor/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(datos)
          })
          .then(response => response.json())
          .then(data => {
            location.reload()
          })
          .catch(error => console.error(error)); 
    }
}