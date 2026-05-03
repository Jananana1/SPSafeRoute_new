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
    const title = payload.notification.title;
    const options = { body: payload.notification.body, icon: '/static/icon.png' };
    self.registration.showNotification(title, options);
});