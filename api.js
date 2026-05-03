const API_BASE = '';
let TOKEN = localStorage.getItem('token');

async function apiRequest(endpoint, method = 'GET', body = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (TOKEN) headers['Authorization'] = `Bearer ${TOKEN}`;
    const response = await fetch(`${API_BASE}${endpoint}`, {
        method,
        headers,
        body: body ? JSON.stringify(body) : null,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Request failed');
    return data;
}

function setToken(token) {
    TOKEN = token;
    if (token) localStorage.setItem('token', token);
    else localStorage.removeItem('token');
}

function getToken() { return TOKEN; }