function obtenerFacturasSeleccionadas(){

    return Array.from(facturasSeleccionadas)

}

function exportarExcel(){

    const ids = obtenerFacturasSeleccionadas()

    if(ids.length === 0){
        alert("Debe seleccionar al menos una factura")
        return
    }

    fetch('/exportar_facturas_excel/',{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            ids: ids
        })
    })
    .then(response => response.blob())
    .then(blob => {

        const url = window.URL.createObjectURL(blob)

        const a = document.createElement('a')
        a.href = url
        a.download = "facturas.xlsx"
        document.body.appendChild(a)
        a.click()
        a.remove()

    })

}

function getCookie(name) {

    let cookieValue = null

    if (document.cookie && document.cookie !== '') {

        const cookies = document.cookie.split(';')

        for (let i = 0; i < cookies.length; i++) {

            const cookie = cookies[i].trim()

            if (cookie.substring(0, name.length + 1) === (name + '=')) {

                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))

                break
            }
        }
    }

    return cookieValue
}