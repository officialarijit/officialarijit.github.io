/**
 * Dossier sidebar: mobile drawer, desktop collapse, and section scroll spy.
 */
document.addEventListener('DOMContentLoaded', () => {
  const panel = document.querySelector('.dossier-panel');
  const toggle = document.querySelector('.dossier-panel__toggle');
  const topbarMenu = document.querySelector('.dossier-topbar__menu');
  const overlay = document.querySelector('.dossier-mobile-overlay');
  const navWrap = document.getElementById('dossier-panel-nav');
  const collapseBtn = document.querySelector('.dossier-panel-collapse');
  const revealBtn = document.querySelector('.dossier-sidebar-reveal');
  const sectionLinks = Array.from(
    document.querySelectorAll('.dossier-panel__nav a[data-section]')
  );

  const PANEL_STORAGE_KEY = 'dossierPanelCollapsed';
  const mobileQuery = window.matchMedia('(max-width: 900px)');
  const desktopQuery = window.matchMedia('(min-width: 901px)');

  function isMobile() {
    return mobileQuery.matches;
  }

  function isDesktop() {
    return desktopQuery.matches;
  }

  function setMobileNavOpen(open) {
    document.body.classList.toggle('dossier-mobile-nav-open', open);

    if (topbarMenu) {
      topbarMenu.setAttribute('aria-expanded', String(open));
      topbarMenu.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      const icon = topbarMenu.querySelector('i');
      if (icon) {
        icon.classList.toggle('fa-bars', !open);
        icon.classList.toggle('fa-times', open);
      }
    }

    if (overlay) {
      overlay.setAttribute('aria-hidden', String(!open));
    }

    document.body.style.overflow = open ? 'hidden' : '';
  }

  function closeMobileNav() {
    if (isMobile()) setMobileNavOpen(false);
  }

  function setPanelCollapsed(collapsed, persist) {
    document.body.classList.toggle('dossier-panel-collapsed', collapsed);

    if (collapseBtn) {
      collapseBtn.setAttribute('aria-label', collapsed ? 'Sidebar hidden' : 'Hide sidebar');
      collapseBtn.setAttribute('title', collapsed ? 'Sidebar hidden' : 'Hide sidebar');
    }

    if (revealBtn) {
      revealBtn.hidden = !collapsed || !isDesktop();
      revealBtn.setAttribute('aria-hidden', String(!collapsed || !isDesktop()));
    }

    if (persist) {
      try {
        localStorage.setItem(PANEL_STORAGE_KEY, collapsed ? 'true' : 'false');
      } catch (e) {}
    }
  }

  function loadPanelPreference() {
    if (!isDesktop()) {
      setPanelCollapsed(false, false);
      return;
    }

    try {
      const saved = localStorage.getItem(PANEL_STORAGE_KEY);
      setPanelCollapsed(saved === 'true', false);
    } catch (e) {
      setPanelCollapsed(false, false);
    }
  }

  if (topbarMenu) {
    topbarMenu.addEventListener('click', () => {
      if (!isMobile()) return;
      setMobileNavOpen(!document.body.classList.contains('dossier-mobile-nav-open'));
    });
  }

  if (overlay) {
    overlay.addEventListener('click', closeMobileNav);
  }

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeMobileNav();
  });

  if (collapseBtn) {
    collapseBtn.addEventListener('click', () => {
      if (!isDesktop()) return;
      setPanelCollapsed(true, true);
    });
  }

  if (revealBtn) {
    revealBtn.addEventListener('click', () => {
      if (!isDesktop()) return;
      setPanelCollapsed(false, true);
    });
  }

  const onViewportChange = () => {
    closeMobileNav();

    if (!isDesktop()) {
      setPanelCollapsed(false, false);
      return;
    }

    try {
      const saved = localStorage.getItem(PANEL_STORAGE_KEY);
      setPanelCollapsed(saved === 'true', false);
    } catch (e) {
      setPanelCollapsed(false, false);
    }
  };

  if (mobileQuery.addEventListener) {
    mobileQuery.addEventListener('change', onViewportChange);
  } else if (mobileQuery.addListener) {
    mobileQuery.addListener(onViewportChange);
  }

  if (desktopQuery.addEventListener) {
    desktopQuery.addEventListener('change', onViewportChange);
  } else if (desktopQuery.addListener) {
    desktopQuery.addListener(onViewportChange);
  }

  loadPanelPreference();

  if (toggle && panel && navWrap) {
    const toggleIcon = toggle.querySelector('i');

    toggle.addEventListener('click', () => {
      if (!isMobile()) return;
      const isOpen = panel.classList.toggle('is-nav-open');
      toggle.setAttribute('aria-expanded', String(isOpen));
      if (toggleIcon) {
        toggleIcon.classList.toggle('fa-bars', !isOpen);
        toggleIcon.classList.toggle('fa-times', isOpen);
      }
    });
  }

  if (navWrap) {
    navWrap.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', closeMobileNav);
    });
  }

  if (sectionLinks.length === 0) return;

  const sectionIds = sectionLinks.map((link) => link.dataset.section);
  const sections = sectionIds
    .map((id) => document.getElementById(id))
    .filter(Boolean);

  if (sections.length === 0) return;

  const setActive = (id) => {
    sectionLinks.forEach((link) => {
      link.classList.toggle('is-active', link.dataset.section === id);
    });

    const breadcrumb = document.getElementById('dossier-breadcrumb-current');
    const activeLink = sectionLinks.find((link) => link.dataset.section === id);
    if (breadcrumb && activeLink) {
      breadcrumb.textContent = activeLink.textContent.trim();
    }
  };

  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio);

      if (visible.length > 0) {
        setActive(visible[0].target.id);
      }
    },
    {
      root: null,
      rootMargin: '-20% 0px -65% 0px',
      threshold: [0, 0.15, 0.35, 0.55],
    }
  );

  sections.forEach((section) => observer.observe(section));

  const syncInitial = () => {
    const scrollY = window.scrollY + 120;
    let current = sections[0].id;

    sections.forEach((section) => {
      if (section.offsetTop <= scrollY) {
        current = section.id;
      }
    });

    setActive(current);
  };

  syncInitial();
  window.addEventListener('scroll', syncInitial, { passive: true });
});
