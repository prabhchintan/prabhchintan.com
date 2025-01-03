class ThemeManager {
    constructor() {
      this.themeToggle = document.getElementById('theme-toggle');
      this.themeToggleIcon = this.themeToggle.querySelector('.theme-toggle-icon');
      this.mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      console.log('ThemeManager initialized'); // Debug log
      this.initialize();
    }
  
    initialize() {
      const savedTheme = localStorage.getItem('theme');
      const preferredTheme = savedTheme || (this.mediaQuery.matches ? 'dark' : 'light');
      console.log('Initial theme:', preferredTheme); // Debug log
      this.setTheme(preferredTheme, false);
  
      this.themeToggle.addEventListener('click', () => this.toggleTheme());
      this.mediaQuery.addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
          this.setTheme(e.matches ? 'dark' : 'light', true);
        }
      });
  
      this.themeToggle.style.visibility = 'visible';
    }
  
    setTheme(theme, animate = true) {
      console.log('Setting theme to:', theme); // Debug log
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('theme', theme);
      this.themeToggleIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
      
      // Force a repaint to ensure theme changes are applied
      document.body.style.display = 'none';
      document.body.offsetHeight; // Trigger reflow
      document.body.style.display = '';
    }
  
    toggleTheme() {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      console.log('Toggling theme from', currentTheme, 'to', newTheme); // Debug log
      this.setTheme(newTheme);
    }
  }
  
  // Initialize theme manager
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new ThemeManager());
  } else {
    new ThemeManager();
  }