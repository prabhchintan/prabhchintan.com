/**
 * Register the service worker for PWA functionality
 */
function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/service-worker.js')
        .then(registration => {
          console.log('Service Worker registered successfully:', registration.scope);
        })
        .catch(error => {
          console.error('Service Worker registration failed:', error);
        });
    });
  }
}

// Register service worker
registerServiceWorker();

document.addEventListener('DOMContentLoaded', function() {
  document.body.classList.add('mathjax-loading');
  
  if (typeof MathJax !== 'undefined') {
    MathJax.Hub.Queue(function() {
      document.body.classList.remove('mathjax-loading');
      document.body.classList.add('mathjax-loaded');
    });
  } else {
    document.body.classList.remove('mathjax-loading');
  }
});