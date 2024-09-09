// Define color scheme values
const LIGHT_SCHEME = 'light';
const DARK_SCHEME = 'dark';
const THEME_COLOR_LIGHT = '#f8f4e9';
const THEME_COLOR_DARK = '#1a1410';

/**
 * Set the color scheme for the document and update the theme-color meta tag
 * @param {string} scheme - The color scheme to set ('light' or 'dark')
 */
function setColorScheme(scheme) {
  console.log('Setting color scheme:', scheme);
  document.documentElement.setAttribute('data-theme', scheme);
  const themeColor = scheme === DARK_SCHEME ? THEME_COLOR_DARK : THEME_COLOR_LIGHT;
  document.querySelector('meta[name="theme-color"]').setAttribute('content', themeColor);
}

/**
 * Update the color scheme based on the user's system preference
 */
function updateColorScheme() {
  const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
  setColorScheme(prefersDarkScheme.matches ? DARK_SCHEME : LIGHT_SCHEME);
}

/**
 * Initialize color scheme functionality
 */
function initColorScheme() {
  // Initial setup
  updateColorScheme();

  // Listen for changes in system color scheme preference
  const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
  prefersDarkScheme.addListener(updateColorScheme);
}

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

// Initialize color scheme functionality
initColorScheme();

// Register service worker
registerServiceWorker();