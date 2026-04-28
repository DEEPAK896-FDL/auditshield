/* AuditShield — main.js */

document.addEventListener('DOMContentLoaded', function () {

  // ── Auto-dismiss flash messages after 4 seconds ──────────────────────────
  const alerts = document.querySelectorAll('.alert-auto-dismiss');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = 'opacity 0.5s ease';
      alert.style.opacity = '0';
      setTimeout(function () { alert.remove(); }, 500);
    }, 4000);
  });

  // ── Sidebar active link detection ────────────────────────────────────────
  const currentPath = window.location.pathname;
  const sidebarLinks = document.querySelectorAll('.sidebar-link');
  sidebarLinks.forEach(function (link) {
    const href = link.getAttribute('href');
    if (href && href !== '/' && currentPath.startsWith(href)) {
      link.classList.add('active');
    }
  });

  // ── Bootstrap Tooltip initialization ─────────────────────────────────────
  const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipEls.forEach(function (el) {
    bootstrap.Tooltip.getOrCreateInstance(el);
  });

  // ── Overdue row highlighting ──────────────────────────────────────────────
  const overdueRows = document.querySelectorAll('tr[data-overdue="true"]');
  overdueRows.forEach(function (row) {
    row.classList.add('finding-overdue-row');
  });

  // ── Confirm dialogs for destructive actions ───────────────────────────────
  const confirmForms = document.querySelectorAll('form[data-confirm]');
  confirmForms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      const msg = form.getAttribute('data-confirm') || 'Are you sure?';
      if (!confirm(msg)) {
        e.preventDefault();
      }
    });
  });

  const confirmLinks = document.querySelectorAll('a[data-confirm]');
  confirmLinks.forEach(function (link) {
    link.addEventListener('click', function (e) {
      const msg = link.getAttribute('data-confirm') || 'Are you sure?';
      if (!confirm(msg)) {
        e.preventDefault();
      }
    });
  });

  // ── Smooth scroll for anchor links ───────────────────────────────────────
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  anchorLinks.forEach(function (link) {
    link.addEventListener('click', function (e) {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── Mobile sidebar toggle ─────────────────────────────────────────────────
  const menuToggle = document.getElementById('menuToggle');
  const sidebar = document.querySelector('.sidebar');
  if (menuToggle && sidebar) {
    menuToggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
  }

});
