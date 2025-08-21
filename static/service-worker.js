self.addEventListener('install', event => {
  console.log('✅ Service Worker installed');
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  console.log('✅ Service Worker activated');
});

self.addEventListener('fetch', event => {
  event.respondWith(fetch(event.request));
});
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/') // Redirect to homepage or task list
    );
});
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

registration.pushManager.subscribe({
  userVisibleOnly: true,
  applicationServerKey: convertedKey
}).then(subscription => {
  return fetch('/save-subscription', {
    method: 'POST',
    body: JSON.stringify(subscription),
    headers: {
      'Content-Type': 'application/json'
    }
  });
});

