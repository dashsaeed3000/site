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
    // Check saved theme preference
    let currentTheme = localStorage.getItem('site-theme') || 'dark';

    function setTheme(mode) {
      if(mode === 'bright') {
        html.classList.add('theme-bright');
        html.classList.remove('theme-dark');
        toggleButton.textContent = '🌙';
        toggleButton.setAttribute('title', 'Switch to dark mode');
      } else {
        html.classList.remove('theme-bright');
        html.classList.add('theme-dark');
        toggleButton.textContent = '☀️';
        toggleButton.setAttribute('title', 'Switch to light mode');
      }
      localStorage.setItem('site-theme', mode);
      currentTheme = mode;
    }

    // Set initial theme
    setTheme(currentTheme);

    // Add click event listener
    toggleButton.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      const newTheme = (currentTheme === 'dark') ? 'bright' : 'dark';
      setTheme(newTheme);
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initThemeToggle);
  } else {
    initThemeToggle();
  }
})();
