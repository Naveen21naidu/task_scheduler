// Check if service workers and push are supported
if ('serviceWorker' in navigator && 'PushManager' in window) {
  window.addEventListener('load', async () => {
    try {
      // ✅ Register the service worker
      const registration = await navigator.serviceWorker.register('/static/service-worker.js');
      console.log('✅ Service Worker registered:', registration);

      // ✅ Request notification permission
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        console.warn('🚫 Notification permission denied');
        return;
      }

      // ✅ Subscribe to push notifications
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array('BBiVJi8--fMfDeRDHI4RRYzv_CFlzDFqL7o3ahnFH_hWDl0q-mxcLpWoWwKL3eyF4OwYPYV1YmDMg4lngmyLkNE=')
      });

      console.log('📬 Push subscription:', subscription);

      // ✅ Send subscription to Flask backend (optional)
      // await fetch('/subscribe', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(subscription)
      // });

    } catch (error) {
      console.error('❌ Error during service worker or push setup:', error);
    }
  });
} else {
  console.warn('🚫 Push messaging is not supported in this browser');
}

// ✅ Helper: Convert VAPID key to Uint8Array
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
