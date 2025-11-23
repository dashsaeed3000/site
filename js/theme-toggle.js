// Theme Toggle Script
(function() {
  // Wait for DOM to be ready
  function initThemeToggle() {
    const toggleButton = document.getElementById('theme-toggle');
    if (!toggleButton) {
      // Retry after a short delay if button not found
      setTimeout(initThemeToggle, 100);
      return;
    }

    const html = document.documentElement;
    // Check saved theme
    let theme = localStorage.getItem('site-theme') || 'dark';

    function setTheme(mode) {
      if(mode === 'bright') {
        html.classList.add('theme-bright');
        html.classList.remove('theme-dark');
        toggleButton.textContent = '🌙';
      } else {
        html.classList.remove('theme-bright');
        html.classList.add('theme-dark');
        toggleButton.textContent = '☀️';
      }
      localStorage.setItem('site-theme', mode);
    }

    // Set initial theme
    setTheme(theme);

    toggleButton.addEventListener('click', function() {
      theme = (theme === 'dark') ? 'bright' : 'dark';
      setTheme(theme);
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initThemeToggle);
  } else {
    initThemeToggle();
  }
})();
