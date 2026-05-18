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

// ========== VALIDATION FUNCTIONS ==========
function validateLoginForm(email, password) {
    if (authMessage) {
        authMessage.innerText = '';
        authMessage.classList.add('hidden');
    }
    
    if (!email || email.trim() === '') {
        if (authMessage) {
            authMessage.innerText = 'Email address is required';
            authMessage.classList.remove('hidden');
        }
        return false;
    }
    
    if (!password || password.trim() === '') {
        if (authMessage) {
            authMessage.innerText = 'Password is required';
            authMessage.classList.remove('hidden');
        }
        return false;
    }
    
    return true;
}

function validateEmailFormat(email) {
    const emailRegex = /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/;
    return emailRegex.test(email);
}

function validateRegistrationForm(full_name, email, password, confirm_password, captcha_answer) {
    if (regMessage) {
        regMessage.innerText = '';
        regMessage.classList.add('hidden');
    }
    
    if (!full_name || full_name.trim() === '') {
        if (regMessage) {
            regMessage.innerText = 'Full name is required';
            regMessage.classList.remove('hidden');
        }
        return false;
    }
    
    if (!email || email.trim() === '') {
        if (regMessage) {
            regMessage.innerText = 'Email address is required';
            regMessage.classList.remove('hidden');
        }
        return false;
    }
    
    if (!validateEmailFormat(email)) {
        if (regMessage) {
            regMessage.innerText = 'Please enter a valid email address (e.g., name@domain.com)';
            regMessage.classList.remove('hidden');
        }
        return false;
    }
    
    if (!password || password.trim() === '') {
        if (regMessage) {
            regMessage.innerText = 'Password is required';
            regMessage.classList.remove('hidden');
        }
        return false;
    }
    
    if (password.length < 8) {
        if (regMessage) {
            regMessage.innerText = 'Password must be at least 8 characters long';
            regMessage.classList.remove('hidden');
        }
        return false;
    }
    
    if (password !== confirm_password) {
        if (regMessage) {
            regMessage.innerText = 'Passwords do not match';
            regMessage.classList.remove('hidden');
        }
        return false;
    }
    
    if (!captcha_answer || captcha_answer.trim() === '') {
        if (regMessage) {
            regMessage.innerText = 'Please answer the security question';
            regMessage.classList.remove('hidden');
        }
        return false;
    }
    
    return true;
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
const authMessage = document.getElementById('loginMessage');
const regMessage = document.getElementById('registerMessage');

// ========== USER LOAD ==========
async function loadUser() {
    try {
        const user = await apiRequest('/users/me');
        document.getElementById('userName').innerText = user.full_name || user.email;
        const adminBtn = document.getElementById('adminBtn');
        if (adminBtn) adminBtn.style.display = user.is_admin ? 'flex' : 'none';
    } catch (e) { logout(); }
}

// ========== LOGIN ==========
async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    // Add validation
    if (!validateLoginForm(email, password)) {
        return;
    }
    
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

        if (data.mfa_required) {
            window.tempMfaToken = data.access_token;
            loginPanel.classList.add('hidden');
            document.getElementById('mfaPanel')?.classList.remove('hidden');
        } else {
            setToken(data.access_token);
            loginPanel.classList.add('hidden');
            mainPanel.classList.remove('hidden');
            await loadUser();
            if (typeof registerFCMToken === 'function') {
                registerFCMToken();
            }
        }
    } catch (err) {
        if (authMessage) {
            authMessage.innerText = err.message;
            authMessage.classList.remove('hidden');
        }
    }
}

// ========== REGISTER ==========
async function register() {
    const full_name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const confirm_password = document.getElementById('regConfirmPassword')?.value || password;
    const captcha_id = document.getElementById('captchaId')?.value || "";
    const captcha_answer = document.getElementById('captchaAnswer')?.value || "";

    // Add validation
    if (!validateRegistrationForm(full_name, email, password, confirm_password, captcha_answer)) {
        // Clear sensitive fields
        if (document.getElementById('regPassword')) document.getElementById('regPassword').value = '';
        if (document.getElementById('regConfirmPassword')) document.getElementById('regConfirmPassword').value = '';
        return;
    }

    try {
        const res = await fetch('/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, confirm_password, full_name, captcha_id, captcha_answer })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        if (data.mfa_required) {
            window.tempMfaToken = data.access_token;
            registerPanel.classList.add('hidden');
            document.getElementById('mfaPanel').classList.remove('hidden');
            document.getElementById('mfaMessage').innerText = '';
        } else {
            setToken(data.access_token);
            registerPanel.classList.add('hidden');
            mainPanel.classList.remove('hidden');
            await loadUser();
            if (typeof registerFCMToken === 'function') {
                registerFCMToken();
            }
        }
    } catch (err) {
        if (regMessage) {
            regMessage.innerText = err.message;
            regMessage.classList.remove('hidden');
        }
        // Reload captcha on error
        if (typeof loadCaptcha === 'function') {
            loadCaptcha();
        }
    }
}

// ========== LOGOUT ==========
function logout() {
    setToken(null);
    mainPanel.classList.add('hidden');
    loginPanel.classList.remove('hidden');
    registerPanel.classList.add('hidden');
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
        // Auto-register push token if permission already granted (no prompt)
        if (typeof registerFCMToken === 'function' && Notification.permission === 'granted') {
            registerFCMToken();
        }
    }).catch(() => logout());
} else {
    loginPanel.classList.remove('hidden');
}