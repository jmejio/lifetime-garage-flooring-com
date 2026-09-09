document.getElementById('year').textContent = new Date().getFullYear();

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
}
