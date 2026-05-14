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

messaging.onBackgroundMessage((payload) => {
    console.log('[firebase-messaging-sw.js] Background message received:', payload);
    const notificationTitle = payload.notification?.title || 'SPSafeRoute Alert';
    const notificationBody = payload.notification?.body || '';
    const notificationOptions = {
        body: notificationBody,
        icon: '/static/icons/android-chrome-192x192.png',
        badge: '/static/icons/favicon-32x32.png',
        vibrate: [200, 100, 200],
        data: payload.data || {},
        requireInteraction: false
    };
    self.registration.showNotification(notificationTitle, notificationOptions);
});
