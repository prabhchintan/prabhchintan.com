// Name of the cache used by this service worker
const CACHE_NAME = 'randhawa-inc-v1';

// List of URLs to cache when the service worker is installed
const urlsToCache = [
  '/',
  '/assets/css/style.css',
  '/assets/js/main.js',
  '/assets/fonts/FleurCornerCaps.woff2',
  '/manifest.json',
  // Add other important assets here
];

// Install event: caches assets when the service worker is installed
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Activate event: cleans up old caches when a new service worker takes over
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (!cacheWhitelist.includes(cacheName)) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event: handles requests, attempting to serve from cache first
self.addEventListener('fetch', event => {
  if (event.request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        // First, try to use the navigation preload response if it's supported
        const preloadResponse = await event.preloadResponse;
        if (preloadResponse) {
          return preloadResponse;
        }

        // Next, try to get the resource from the network
        const networkResponse = await fetch(event.request);
        return networkResponse;
      } catch (error) {
        // If both preload and network fail, serve from cache
        const cache = await caches.open(CACHE_NAME);
        const cachedResponse = await cache.match('/');
        return cachedResponse;
      }
    })());
  }
});

// Optional: Add runtime caching
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }

        // Clone the request because it's a stream and can only be consumed once
        const fetchRequest = event.request.clone();

        return fetch(fetchRequest).then(response => {
          // Check if we received a valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clone the response because it's a stream and can only be consumed once
          const responseToCache = response.clone();

          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });

          return response;
        });
      })
  );
});