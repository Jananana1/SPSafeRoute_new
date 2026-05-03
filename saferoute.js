import { apiRequest } from './api.js';

let map = null;
let selectedDest = null;
let allRoutes = [];
let activeRouteIndex = 0;
let startLocation = null;

const CITY_BOUNDS = { south: 14.0400, west: 121.2000, north: 14.1100, east: 121.3800 };
const CITY_CENTER = { lat: 14.0700, lng: 121.3255 };

function initMap() {
    if (map) map.remove();
    map = L.map('map').setView([CITY_CENTER.lat, CITY_CENTER.lng], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap' }).addTo(map);
    map.setMaxBounds([[CITY_BOUNDS.south, CITY_BOUNDS.west], [CITY_BOUNDS.north, CITY_BOUNDS.east]]);
}
initMap();

// Helper: distance in meters
function getDistance(lat1, lng1, lat2, lng2) {
    const R = 6371000;
    const dLat = (lat2-lat1)*Math.PI/180;
    const dLon = (lng2-lng1)*Math.PI/180;
    const a = Math.sin(dLat/2)**2 + Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLon/2)**2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}

// Score route based on incidents from backend (already fetched)
async function scoreRoute(routeCoords) {
    const incidents = await apiRequest('/incidents/'); // get all incidents
    let incidentCount = 0;
    for (let i = 1; i < routeCoords.length; i++) {
        const p1 = routeCoords[i-1], p2 = routeCoords[i];
        const midLat = (p1.lat + p2.lat)/2, midLng = (p1.lng + p2.lng)/2;
        for (const inc of incidents) {
            const dist = getDistance(midLat, midLng, inc.lat, inc.lng);
            if (dist < 250) incidentCount++;
        }
    }
    return incidentCount;
}

async function fetchRouteAlternatives(start, dest) {
    const url = `https://router.project-osrm.org/route/v1/driving/${start.lng},${start.lat};${dest.lng},${dest.lat}?alternatives=true&overview=full&geometries=geojson`;
    const res = await fetch(url);
    const data = await res.json();
    if (data.code !== 'Ok') return null;
    const routes = [];
    for (const r of data.routes) {
        const coords = r.geometry.coordinates.map(c => ({ lat: c[1], lng: c[0] }));
        const incidentCount = await scoreRoute(coords);
        routes.push({ coords, duration: r.duration, distance: r.distance, incidentCount });
    }
    return routes;
}

async function classifyAndDisplay(routes, start, dest) {
    if (!routes.length) { alert('No routes found.'); return; }
    // Sort by incident count (lowest = safest)
    const sorted = [...routes].sort((a,b) => a.incidentCount - b.incidentCount);
    let safest = sorted[0], dangerous = sorted[sorted.length-1];
    let moderate = sorted[1] || dangerous;
    allRoutes = [safest, moderate, dangerous];
    
    const safestBtn = document.getElementById('safestBtn');
    const moderateBtn = document.getElementById('moderateBtn');
    const dangerousBtn = document.getElementById('dangerousBtn');
    safestBtn.onclick = () => displayRoute(0, '#10b981');
    moderateBtn.onclick = () => displayRoute(1, '#1A73E8');
    dangerousBtn.onclick = () => displayRoute(2, '#dc2626');
    
    function displayRoute(idx, color) {
        const route = allRoutes[idx];
        if (!route) return;
        if (window.currentPolyline) map.removeLayer(window.currentPolyline);
        window.currentPolyline = L.polyline(route.coords.map(c=>[c.lat,c.lng]), { color, weight:6 }).addTo(map);
        map.fitBounds(window.currentPolyline.getBounds());
        document.getElementById('infoMsg').innerHTML = `Incidents along route: ${route.incidentCount}`;
    }
    document.getElementById('routeButtons').style.display = 'flex';
    displayRoute(0, '#10b981'); // show safest initially
}

async function findRoute() {
    if (!selectedDest) { alert('Select a destination from suggestions'); return; }
    if (!navigator.geolocation) { alert('Geolocation not supported'); return; }
    navigator.geolocation.getCurrentPosition(async pos => {
        startLocation = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        const routes = await fetchRouteAlternatives(startLocation, selectedDest);
        if (routes) await classifyAndDisplay(routes, startLocation, selectedDest);
        else alert('No routes');
    }, () => alert('Location permission denied'));
}

// Destination search (Nominatim)
async function searchLocation(query) {
    const viewbox = `${CITY_BOUNDS.west},${CITY_BOUNDS.south},${CITY_BOUNDS.east},${CITY_BOUNDS.north}`;
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=5&viewbox=${viewbox}&bounded=1`;
    const res = await fetch(url, { headers: { 'User-Agent': 'SP-SafeRoute/1.0' } });
    const data = await res.json();
    return data.filter(i => i.lat >= CITY_BOUNDS.south && i.lat <= CITY_BOUNDS.north && i.lon >= CITY_BOUNDS.west && i.lon <= CITY_BOUNDS.east);
}

const destInput = document.getElementById('destinationSearch');
const suggestionsDiv = document.getElementById('suggestions');
let timeout;
destInput.addEventListener('input', (e) => {
    clearTimeout(timeout);
    if (e.target.value.length < 3) { suggestionsDiv.style.display = 'none'; return; }
    timeout = setTimeout(async () => {
        const suggestions = await searchLocation(e.target.value);
        suggestionsDiv.innerHTML = '';
        if (!suggestions.length) { suggestionsDiv.style.display = 'none'; return; }
        suggestionsDiv.style.display = 'block';
        suggestions.forEach(s => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.textContent = s.display_name;
            div.onclick = () => {
                destInput.value = s.display_name;
                selectedDest = { lat: parseFloat(s.lat), lng: parseFloat(s.lon) };
                suggestionsDiv.style.display = 'none';
            };
            suggestionsDiv.appendChild(div);
        });
    }, 500);
});

document.getElementById('findRouteBtn').addEventListener('click', findRoute);