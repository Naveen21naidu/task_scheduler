const CACHE_NAME = 'task-scheduler-cache-v1';
const OFFLINE_URL = '/static/offline.html'; // Make sure this file exists in static/

// ✅ Install event: Pre-cache essential assets
self.addEventListener('install', event => {
  console.log('✅ Service Worker installed');
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll([
        '/',
        '/static/index.html',
        '/static/styles.css',
        '/static/app.js',
        OFFLINE_URL,
        '/static/icons/icon-192.png',
        '/static/icons/icon-512.png',
        '/static/manifest.json'
      ]);
    }).then(() => self.skipWaiting())
  );
});

// ✅ Activate event: Clean old caches
self.addEventListener('activate', event => {
  console.log('✅ Service Worker activated');
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      )
    )
  );
  return self.clients.claim();
});

// ✅ Fetch event: Cache-first strategy with fallback
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      return (
        cachedResponse ||
        fetch(event.request).catch(() => caches.match(OFFLINE_URL))
      );
    })
  );
});

// ✅ Notification click: Redirect to homepage or task list
self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/') // You can change this to '/tasks' or any route
  );
});

// ✅ Push event: Show notification when push is received
self.addEventListener('push', event => {
  console.log('📨 Push received:', event.data?.text() || event.data?.json());

  let data = {
    title: '🔔 Task Reminder',
    body: 'You have a pending task!',
    icon: '/static/icons/icon-192.png'
  };

  try {
    const payload = event.data?.json();
    if (payload) {
      data = { ...data, ...payload };
    }
  } catch (e) {
    const text = event.data?.text();
    if (text) {
      data.body = text;
    }
  }

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: data.icon,
      badge: '/static/icons/icon-192.png',
      data: { url: '/' }
    })
  );
});
