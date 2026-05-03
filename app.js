// ========== TOKEN MANAGEMENT ==========
let TOKEN = localStorage.getItem('token');

function setToken(token) {
    TOKEN = token;
    if (token) localStorage.setItem('token', token);
    else localStorage.removeItem('token');
}

function getToken() {
    return TOKEN;
}

// ========== API REQUEST HELPER ==========
async function apiRequest(endpoint, method = 'GET', body = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (TOKEN) headers['Authorization'] = `Bearer ${TOKEN}`;
    const response = await fetch(endpoint, {
        method,
        headers,
        body: body ? JSON.stringify(body) : null,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Request failed');
    return data;
}

// ========== DOM ELEMENTS ==========
const loginPanel = document.getElementById('loginPanel');
const registerPanel = document.getElementById('registerPanel');
const mainPanel = document.getElementById('mainPanel');
const authMessage = document.getElementById('loginMessage');   // corrected ID
const regMessage = document.getElementById('registerMessage'); // corrected ID

// ========== USER LOAD ==========
async function loadUser() {
    try {
        const user = await apiRequest('/users/me');
        document.getElementById('userName').innerText = user.full_name || user.email;
        const adminBtn = document.getElementById('adminBtn');
        if (adminBtn) adminBtn.style.display = user.is_admin ? 'flex' : 'none';
        // After successful load, if push notifications are available, re‑enable button state
        const pushStatusDiv = document.getElementById('pushStatus');
        if (pushStatusDiv && pushStatusDiv.innerHTML.includes('✅')) {
            // already enabled, do nothing
        }
    } catch (e) { logout(); }
}

// ========== LOGIN ==========
async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    try {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: params
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail);
        setToken(data.access_token);
        loginPanel.classList.add('hidden');
        mainPanel.classList.remove('hidden');
        await loadUser();
    } catch (err) {
        authMessage.innerText = err.message;
        authMessage.classList.remove('hidden');
    }
}

// ========== REGISTER ==========
async function register() {
    const full_name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    try {
        const res = await fetch('/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        setToken(data.access_token);
        registerPanel.classList.add('hidden');
        mainPanel.classList.remove('hidden');
        await loadUser();
    } catch (err) {
        regMessage.innerText = err.message;
        regMessage.classList.remove('hidden');
    }
}

// ========== LOGOUT ==========
function logout() {
    setToken(null);
    mainPanel.classList.add('hidden');
    loginPanel.classList.remove('hidden');
    registerPanel.classList.add('hidden');
    // Reset push status text when logged out
    const pushStatus = document.getElementById('pushStatus');
    if (pushStatus) pushStatus.innerHTML = '🔔 Enable notifications to get updates';
}

// ========== PUSH NOTIFICATIONS (FIREBASE) ==========
// (only if Firebase is already loaded from index.html)
function initPushNotifications() {
    const enableBtn = document.getElementById('enablePushBtn');
    if (!enableBtn) return;

    enableBtn.addEventListener('click', async () => {
        if (!TOKEN) {
            alert('Please login first');
            return;
        }
        // Firebase is assumed to be already initialized in the global scope
        if (typeof firebase === 'undefined') {
            alert('Firebase not loaded. Please refresh the page.');
            return;
        }
        try {
            const messaging = firebase.messaging();
            await messaging.requestPermission();
            const fcmToken = await messaging.getToken({
                vapidKey: "BKnT_hLfIL2DlonLwZrXY4kwjBEjlp6BaJIr6_ESnVT_K4R985hNmpftY7A9YA9HWSNjCNEeEcTuN8v6VBFDHeI"
            });
            if (fcmToken) {
                const resp = await fetch('/user/fcm-token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${TOKEN}`
                    },
                    body: JSON.stringify({ token: fcmToken })
                });
                if (resp.ok) {
                    document.getElementById('pushStatus').innerHTML = '✅ Notifications enabled';
                } else {
                    document.getElementById('pushStatus').innerHTML = '⚠️ Failed to save token';
                }
            } else {
                document.getElementById('pushStatus').innerHTML = '❌ Unable to get token';
            }
        } catch (err) {
            console.error(err);
            document.getElementById('pushStatus').innerHTML = '❌ Permission denied or error';
        }
    });
}

// ========== NAVIGATION ==========
document.getElementById('mapBtn')?.addEventListener('click', () => location.href = 'map.html');
document.getElementById('reportBtn')?.addEventListener('click', () => location.href = 'report.html');
document.getElementById('routeBtn')?.addEventListener('click', () => location.href = 'saferoute.html');
document.getElementById('alertsBtn')?.addEventListener('click', () => location.href = 'activealerts.html');
document.getElementById('sosBtn')?.addEventListener('click', () => location.href = 'sos.html');
document.getElementById('adminBtn')?.addEventListener('click', () => location.href = 'admin.html');
document.getElementById('loginBtn')?.addEventListener('click', login);
document.getElementById('registerBtn')?.addEventListener('click', register);
document.getElementById('logoutBtn')?.addEventListener('click', logout);
document.getElementById('showRegisterBtn')?.addEventListener('click', () => {
    loginPanel.classList.add('hidden');
    registerPanel.classList.remove('hidden');
});
document.getElementById('showLoginBtn')?.addEventListener('click', () => {
    registerPanel.classList.add('hidden');
    loginPanel.classList.remove('hidden');
});

// ========== INITIAL CHECK ==========
if (getToken()) {
    loadUser().then(() => {
        loginPanel.classList.add('hidden');
        mainPanel.classList.remove('hidden');
        initPushNotifications();  // enable push button only after login
    }).catch(() => logout());
} else {
    loginPanel.classList.remove('hidden');
}