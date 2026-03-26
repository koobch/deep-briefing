// Deep-Briefing Whitepaper Interactivity

document.addEventListener('DOMContentLoaded', function() {
  initThemeToggle();
  initScrollTracking();
  initSmoothScroll();
});

// Theme Toggle (Light/Dark Mode)
function initThemeToggle() {
  const themeToggleBtn = document.getElementById('theme-toggle');
  const html = document.documentElement;

  // Check for saved preference or default to light mode
  const savedTheme = localStorage.getItem('theme') || 'light';
  applyTheme(savedTheme);

  themeToggleBtn.addEventListener('click', function() {
    const currentTheme = html.classList.contains('dark') ? 'dark' : 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  });

  function applyTheme(theme) {
    if (theme === 'dark') {
      html.classList.add('dark');
      themeToggleBtn.textContent = '☀️ Light';
    } else {
      html.classList.remove('dark');
      themeToggleBtn.textContent = '🌙 Dark';
    }
  }
}

// Scroll Tracking for Active Sidebar Item
function initScrollTracking() {
  const sections = document.querySelectorAll('h2[id]');
  const navLinks = document.querySelectorAll('.sidebar-toc a');

  window.addEventListener('scroll', function() {
    let currentSection = '';

    sections.forEach(section => {
      const rect = section.getBoundingClientRect();
      if (rect.top <= 100) {
        currentSection = section.id;
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === '#' + currentSection) {
        link.classList.add('active');
      }
    });
  });
}

// Smooth Scroll for Anchor Links
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href !== '#' && document.querySelector(href)) {
        e.preventDefault();
        document.querySelector(href).scrollIntoView({
          behavior: 'smooth'
        });
      }
    });
  });
}
