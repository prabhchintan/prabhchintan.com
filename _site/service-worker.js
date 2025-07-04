// Name of the cache used by this service worker
const CACHE_NAME = 'randhawa-inc-v4'; // Increment the version when making changes

// List of URLs to cache when the service worker is installed
const urlsToCache = [
  '/',
  '/index.html',
  '/offline/',
  '/assets/css/style.css',
  '/assets/js/bundle.js',
  '/assets/fonts/FleurCornerCaps.woff2',
  '/assets/images/og-image-small.jpg',
  '/android-chrome-192x192.png',
  '/android-chrome-384x384.png',
  '/apple-touch-icon.png',
  '/favicon-32x32.png',
  '/favicon-16x16.png',
  '/manifest.json',
  // Add other important assets here
];

/**
 * Install event: caches assets when the service worker is installed
 */
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .catch(error => {
        console.error('Error caching assets:', error);
      })
  );
});

/**
 * Activate event: cleans up old caches when a new service worker takes over
 */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

/**
 * Fetch event: handles requests, attempting to serve from network first, then cache
 */
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Check if we received a valid response
        if (!response || response.status !== 200 || response.type !== 'basic') {
          return response;
        }

        // Clone the response
        const responseToCache = response.clone();

        caches.open(CACHE_NAME)
          .then(cache => {
            cache.put(event.request, responseToCache);
          })
          .catch(error => {
            console.error('Error caching response:', error);
          });

        return response;
      })
      .catch(() => {
        // If the network request fails, try to serve from cache
        return caches.match(event.request)
          .then(cachedResponse => {
            if (cachedResponse) {
              return cachedResponse;
            }
            // If the resource is not in the cache, return the offline page
            return caches.match('/offline/');
          });
      })
  );
});

/**
 * Push event: handles push notifications (if implemented)
 */
self.addEventListener('push', event => {
  const title = 'Randhawa Inc';
  const options = {
    body: event.data.text(),
    icon: '/android-chrome-192x192.png',
    badge: '/android-chrome-192x192.png'
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

/**
 * Sync event: handles background sync (if implemented)
 */
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(
      // Implement background sync logic here
      console.log('Background sync event triggered')
    );
  }
});