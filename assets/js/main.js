function setColorScheme(scheme) {
  document.documentElement.setAttribute('data-theme', scheme);
  const themeColor = scheme === 'dark' ? '#1a1410' : '#f8f4e9';
  document.querySelector('meta[name="theme-color"]').setAttribute('content', themeColor);
}

function updateColorScheme() {
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    setColorScheme('dark');
  } else {
    setColorScheme('light');
  }
}

// Initial setup
updateColorScheme();

// Listen for changes
if (window.matchMedia) {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', updateColorScheme);
}

// Register service worker for PWA functionality
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {
        console.log('Service Worker registered successfully:', registration.scope);
      })
      .catch(error => {
        console.log('Service Worker registration failed:', error);
      });
  });
}