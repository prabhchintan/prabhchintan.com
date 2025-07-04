// Cache configuration
const CACHE_NAME = 'randhawa-inc-v5';
const STATIC_CACHE = 'static-v5';
const IMAGE_CACHE = 'images-v5';

// Static assets for cache-first strategy
const STATIC_ASSETS = [
  '/assets/css/style.css',
  '/assets/js/bundle.js',
  '/assets/fonts/FleurCornerCaps.woff2',
  '/manifest.json'
];

// Essential assets for immediate caching
const CORE_ASSETS = [
  '/',
  '/offline/',
  '/assets/images/og-image-small.webp',
  '/android-chrome-192x192.png',
  '/favicon-32x32.png'
];

// Image assets with WebP support
const IMAGE_ASSETS = [
  '/assets/images/og-image-small.webp',
  '/assets/images/og-image.webp',
  '/assets/images/og-image-optimized.webp'
];

/**
 * Install event: caches essential assets
 */
self.addEventListener('install', event => {
  event.waitUntil(
    Promise.all([
      caches.open(CACHE_NAME).then(cache => cache.addAll(CORE_ASSETS)),
      caches.open(STATIC_CACHE).then(cache => cache.addAll(STATIC_ASSETS)),
      caches.open(IMAGE_CACHE).then(cache => cache.addAll(IMAGE_ASSETS))
    ]).then(() => {
      self.skipWaiting(); // Activate immediately
    })
  );
});

/**
 * Activate event: clean up old caches
 */
self.addEventListener('activate', event => {
  const expectedCaches = [CACHE_NAME, STATIC_CACHE, IMAGE_CACHE];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (!expectedCaches.includes(cacheName)) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      self.clients.claim(); // Take control immediately
    })
  );
});

/**
 * Fetch event: optimized caching strategies
 */
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Cache-first for static assets
  if (STATIC_ASSETS.some(asset => url.pathname.includes(asset))) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }
  
  // Stale-while-revalidate for images
  if (request.destination === 'image' || url.pathname.includes('/assets/images/')) {
    event.respondWith(staleWhileRevalidate(request, IMAGE_CACHE));
    return;
  }
  
  // Network-first for pages
  event.respondWith(networkFirst(request));
});

// Cache-first strategy
function cacheFirst(request, cacheName) {
  return caches.open(cacheName).then(cache => {
    return cache.match(request).then(response => {
      return response || fetch(request).then(networkResponse => {
        cache.put(request, networkResponse.clone());
        return networkResponse;
      });
    });
  });
}

// Stale-while-revalidate strategy
function staleWhileRevalidate(request, cacheName) {
  return caches.open(cacheName).then(cache => {
    return cache.match(request).then(cachedResponse => {
      const fetchPromise = fetch(request).then(networkResponse => {
        cache.put(request, networkResponse.clone());
        return networkResponse;
      });
      return cachedResponse || fetchPromise;
    });
  });
}

// Network-first strategy
function networkFirst(request) {
  return fetch(request).then(response => {
    if (response.ok) {
      caches.open(CACHE_NAME).then(cache => {
        cache.put(request, response.clone());
      });
    }
    return response;
  }).catch(() => {
    return caches.match(request).then(cachedResponse => {
      return cachedResponse || caches.match('/offline/');
    });
  });
}

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