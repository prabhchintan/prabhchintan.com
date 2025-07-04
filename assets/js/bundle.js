/**
 * Bundled JavaScript for Randhawa Inc. website
 * Includes theme toggle functionality and main application logic
 */

/**
 * Theme Management System
 */
class ThemeManager {
  constructor() {
    this.themeToggle = document.getElementById('theme-toggle');
    this.themeToggleIcon = this.themeToggle.querySelector('.theme-toggle-icon');
    this.mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Apply theme immediately before DOM content loads
    const savedTheme = localStorage.getItem('theme');
    const preferredTheme = savedTheme || (this.mediaQuery.matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', preferredTheme);
    
    // Add no-transition class immediately
    document.documentElement.classList.add('no-transition');
    
    this.initialize();
    
    // Remove no-transition class after a brief delay
    window.addEventListener('load', () => {
      setTimeout(() => {
        document.documentElement.classList.remove('no-transition');
      }, 1);
    });
  }

  initialize() {
    const savedTheme = localStorage.getItem('theme');
    const preferredTheme = savedTheme || (this.mediaQuery.matches ? 'dark' : 'light');
    this.setTheme(preferredTheme, false);

    this.themeToggle.addEventListener('click', (e) => {
      e.preventDefault(); // Prevent default button behavior
      this.toggleTheme();
    });

    // Add keyboard support
    this.themeToggle.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.toggleTheme();
      }
    });

    this.mediaQuery.addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) {
        this.setTheme(e.matches ? 'dark' : 'light', true);
      }
    });

    this.themeToggle.style.visibility = 'visible';
  }

  setTheme(theme, animate = true) {
    if (!animate) {
      document.documentElement.classList.add('no-transition');
    }
    
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    this.themeToggleIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    
    if (!animate) {
      // Force a reflow before removing the class
      document.documentElement.offsetHeight;
      document.documentElement.classList.remove('no-transition');
    }
  }

  toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    this.setTheme(newTheme, true);
  }
}

/**
 * Optimized Service Worker Registration
 */
function registerServiceWorker() {
  if ('serviceWorker' in navigator && !navigator.serviceWorker.controller) {
    navigator.serviceWorker.register('/service-worker.js')
      .then(registration => {
        if (process.env.NODE_ENV !== 'production') {
          console.log('Service Worker registered:', registration.scope);
        }
      })
      .catch(error => {
        if (process.env.NODE_ENV !== 'production') {
          console.error('Service Worker registration failed:', error);
        }
      });
  }
}

// MathJax code removed - not used on this site

/**
 * Initialize all components when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
  // Initialize theme manager
  new ThemeManager();
  
  // Register service worker (only on first visit)
  registerServiceWorker();
});