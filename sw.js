// ============================================================
//  SP SafeRoute – Caching + Firebase Messaging Service Worker  (sw.js)
//  Place this file at the ROOT of your project (same level as index.html)
// ============================================================

importScripts('https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.22.0/firebase-messaging-compat.js');

const firebaseConfig = {
    apiKey: "AIzaSyBv92XnzznnO-e7q-F7n8IqiyABvj2fhwU",
    authDomain: "spsaferoute.firebaseapp.com",
    projectId: "spsaferoute",
    storageBucket: "spsaferoute.firebasestorage.app",
    messagingSenderId: "328821048277",
    appId: "1:328821048277:web:e5ea508b9b90180ec0b35c"
};

firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

const CACHE_NAME = 'spsaferoute-v1';
const OFFLINE_URL = '/index.html';

// Static assets to precache on install
const PRECACHE_ASSETS = [
    '/',
    '/index.html',
    '/map.html',
    '/report.html',
    '/saferoute.html',
    '/activealerts.html',
    '/sos.html',
    '/profile.html',
    '/verify-account.html',
    '/style.css',
    '/app.js',
    '/api.js',
    '/saferoute.js',
    '/manifest.json',
    '/static/icons/android-chrome-192x192.png',
    '/static/icons/android-chrome-512x512.png',
    '/static/icons/apple-touch-icon.png',
    '/static/icons/favicon-32x32.png',
    '/static/icons/favicon-16x16.png',
];

// API routes — never cache these (always network)
const NETWORK_ONLY_PATTERNS = [
    /\/auth\//,
    /\/users\//,
    /\/incidents\//,
    /\/sos\//,
    /\/admin\//,
    /\/uploads\//,
];

// ── INSTALL: precache all static assets ──────────────────────
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            console.log('[SW] Precaching static assets');
            return cache.addAll(PRECACHE_ASSETS);
        }).then(() => self.skipWaiting())
    );
});

// ── ACTIVATE: clean up old caches ────────────────────────────
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys
                    .filter(key => key !== CACHE_NAME)
                    .map(key => {
                        console.log('[SW] Deleting old cache:', key);
                        return caches.delete(key);
                    })
            )
        ).then(() => self.clients.claim())
    );
});

// ── FETCH: smart caching strategy ────────────────────────────
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Only handle same-origin requests
    if (url.origin !== self.location.origin) return;

    // API calls — network only, never cache
    const isApiCall = NETWORK_ONLY_PATTERNS.some(pattern => pattern.test(url.pathname));
    if (isApiCall) {
        event.respondWith(
            fetch(request).catch(() =>
                new Response(
                    JSON.stringify({ detail: 'You are offline. Please check your connection.' }),
                    { status: 503, headers: { 'Content-Type': 'application/json' } }
                )
            )
        );
        return;
    }

    // HTML pages — Network first, fall back to cache, then offline page
    if (request.destination === 'document') {
        event.respondWith(
            fetch(request)
                .then(response => {
                    // Cache a fresh copy
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
                    return response;
                })
                .catch(() =>
                    caches.match(request).then(cached =>
                        cached || caches.match(OFFLINE_URL)
                    )
                )
        );
        return;
    }

    // CSS / JS / Images — Cache first, fall back to network then cache update
    event.respondWith(
        caches.match(request).then(cached => {
            if (cached) return cached;

            return fetch(request).then(response => {
                if (!response || response.status !== 200 || response.type !== 'basic') {
                    return response;
                }
                const clone = response.clone();
                caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
                return response;
            }).catch(() => {
                // For images, return a simple SVG placeholder if offline
                if (request.destination === 'image') {
                    return new Response(
                        `<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
                            <rect width="100" height="100" fill="#e2e8f0"/>
                            <text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" fill="#94a3b8" font-size="12">Offline</text>
                        </svg>`,
                        { headers: { 'Content-Type': 'image/svg+xml' } }
                    );
                }
            });
        })
    );
});

// ── PUSH: handled by the merged Firebase messaging integration ──
messaging.onBackgroundMessage((payload) => {
    console.log('[sw.js] Background message received:', payload);

    // Firebase SDK automatically displays notifications if the payload contains 'notification'.
    // We only need to manually show it if it's a data-only message.
    if (payload.notification) {
        return;
    }

    const notificationTitle = 'SPSafeRoute Alert';
    const notificationBody = payload.data?.message || 'New update from SafeRoute';
    const notificationOptions = {
        body: notificationBody,
        icon: '/static/icons/android-chrome-192x192.png',
        badge: '/static/icons/android-chrome-192x192.png',
        vibrate: [200, 100, 200],
        data: payload.data || {},
        requireInteraction: false,
        tag: 'spsaferoute-alert',
        renotify: true
    };
    self.registration.showNotification(notificationTitle, notificationOptions);
});

// ── NOTIFICATION CLICK: open app when notification tapped ────
self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(clientList => {
            for (const client of clientList) {
                if (client.url.includes(self.location.origin) && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) return clients.openWindow('/');
        })
    );
});