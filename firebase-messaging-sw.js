// Legacy Firebase Messaging service worker entrypoint.
// If an old registration still exists for /firebase-messaging-sw.js, this file forwards to the unified /sw.js worker.
importScripts('/sw.js');