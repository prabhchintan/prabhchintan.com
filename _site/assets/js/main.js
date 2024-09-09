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
    window.matchMedia('(prefers-color-scheme: dark)').addListener(updateColorScheme);
  }
  
  // Check for changes every second (as a fallback for some mobile devices)
  setInterval(updateColorScheme, 1000);