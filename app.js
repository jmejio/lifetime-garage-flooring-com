document.getElementById('year').textContent = new Date().getFullYear();

// The logo always links to "/" (a plain link so it still works without JS —
// landing on a fresh page load always starts at the true scrollTop 0, no
// anchor/sticky-header math needed). On the home page itself that's the
// current URL, so clicking it wouldn't otherwise do anything; intercept it
// there to just scroll the current page back to the top instead.
const logoLink = document.querySelector('.navbar-brand');
if (logoLink && (location.pathname === '/' || location.pathname === '/index.html')) {
  logoLink.addEventListener('click', (event) => {
    event.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

const navMenu = document.getElementById('navMenu');
const navToggle = document.querySelector('[data-bs-target="#navMenu"]');

if (navMenu && navToggle) {
  const navCollapse = bootstrap.Collapse.getOrCreateInstance(navMenu, { toggle: false });

  navMenu.querySelectorAll('.nav-link:not(.dropdown-toggle), .dropdown-item, .btn').forEach((link) => {
    link.addEventListener('click', () => navCollapse.hide());
  });

  document.addEventListener('click', (event) => {
    const isOpen = navMenu.classList.contains('show');
    const clickedInsideMenu = navMenu.contains(event.target);
    const clickedToggle = navToggle.contains(event.target);

    if (isOpen && !clickedInsideMenu && !clickedToggle) {
      navCollapse.hide();
    }
  });

  // Desktop-only: open Services/Locations dropdowns on hover (with a short
  // close delay) in addition to the default click/keyboard behavior. Guarded
  // to real pointer devices so touchscreens (e.g. wide tablets) keep
  // click-only behavior.
  if (window.matchMedia('(hover: hover) and (pointer: fine) and (min-width: 768px)').matches) {
    navMenu.querySelectorAll('.nav-item.dropdown').forEach((dropdown) => {
      const toggle = dropdown.querySelector('[data-bs-toggle="dropdown"]');
      const instance = bootstrap.Dropdown.getOrCreateInstance(toggle);
      let closeTimer;

      dropdown.addEventListener('mouseenter', () => {
        clearTimeout(closeTimer);
        instance.show();
      });
      dropdown.addEventListener('mouseleave', () => {
        closeTimer = setTimeout(() => instance.hide(), 200);
      });
    });
  }
}
