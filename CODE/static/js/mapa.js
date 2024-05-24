// Crea el mapa
var map = L.map('mapa').setView([39.47943785905445, -0.3555432220290346], 13);

// Añade capa de mapa base
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Función que va a ir añadiendo los puntos
function addMarker(lat, lon, tooltip) {
    L.marker([lat, lon]).addTo(map)
        .bindPopup(tooltip)
        .openPopup();
}

// Solicita los datos del servidor
fetch('/data')
    .then(response => response.json())
    .then(responseData => {
        const data = responseData.data;
        const clavesMapa = responseData.clavesMapa;

        data.forEach(function (punto) {
            // Construir el contenido del tooltip
            var tooltip = '';
            clavesMapa.forEach(function (key) {
                if (punto.hasOwnProperty(key)) {
                    tooltip += `<strong>${key}:</strong> ${punto[key]}<br>`;
                }
            });
            // Extrae la latitud, longitud y nombre para añadir el punto en el mapa
            
            addMarker(punto.localizacion.lat, punto.localizacion.lon, tooltip);
        });
    })
    .catch(error => console.error('Error al cargar los datos:', error));

// Cuando el usuario hace click en cualquier punto del mapa le dice la latitud y longitud de ese punto
map.on('click', seleccion)
function seleccion(e) {
    alert("Posición: " + e.latlng)
}
