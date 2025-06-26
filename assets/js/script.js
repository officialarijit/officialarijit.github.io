// Modern Portfolio JavaScript
document.addEventListener("DOMContentLoaded", function() {
  // Initialize all components
  initScrollEffects();
  initContactForm();
  initAnimations();
  initTypingEffect();
  fetchGoogleScholarPublications();
  fetchGoogleScholarMetrics();
  
  // Initialize dark mode immediately and also after navbar loads
  initDarkMode();
  
  // Also initialize dark mode after a delay to catch any late-loading elements
  setTimeout(() => {
    if (typeof initDarkMode === 'function') {
      initDarkMode();
    }
  }, 500);
});

// Also initialize dark mode immediately if DOM is already loaded
if (document.readyState === 'loading') {
  // DOM is still loading, wait for DOMContentLoaded
} else {
  // DOM is already loaded, initialize immediately
  if (typeof initDarkMode === 'function') {
    initDarkMode();
  }
}

// Scroll effects and animations
function initScrollEffects() {
  const scrollToTopBtn = document.getElementById('scrollToTop');

  // Show/hide scroll to top button
  window.addEventListener('scroll', function() {
    if (window.scrollY > 300) {
      scrollToTopBtn.style.display = 'flex';
    } else {
      scrollToTopBtn.style.display = 'none';
    }
  });

  // Scroll to top functionality
  scrollToTopBtn.addEventListener('click', function() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  // Intersection Observer for animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
      }
    });
  }, observerOptions);

  // Observe elements for animation
  const animateElements = document.querySelectorAll('.skill-category, .project-card, .timeline-item, .education-card, .publication-item');
  animateElements.forEach(el => {
    observer.observe(el);
  });
}

// Contact form handling
function initContactForm() {
  const contactForm = document.getElementById('contactForm');
  const toggleBtn = document.getElementById('toggleContactForm');
  const cancelBtn = document.getElementById('cancelContactForm');
  const formElement = document.getElementById('contactFormElement');

  // Toggle contact form visibility
  if (toggleBtn && contactForm) {
    toggleBtn.addEventListener('click', function() {
      contactForm.style.display = 'block';
      setTimeout(() => {
        contactForm.classList.add('show');
      }, 10);
      toggleBtn.style.display = 'none';
    });
  }

  // Cancel button functionality
  if (cancelBtn && contactForm && toggleBtn) {
    cancelBtn.addEventListener('click', function() {
      contactForm.classList.remove('show');
      setTimeout(() => {
        contactForm.style.display = 'none';
        toggleBtn.style.display = 'inline-flex';
      }, 300);
      if (formElement) {
        formElement.reset();
      }
    });
  }

  // Form submission handling
  if (formElement) {
    formElement.addEventListener('submit', function(e) {
      e.preventDefault();

      // Get form data
      const formData = new FormData(this);
      const name = formData.get('name');
      const email = formData.get('email');
      const subject = formData.get('subject');
      const message = formData.get('message');

      // Basic validation
      if (!name || !email || !subject || !message) {
        showNotification('Please fill in all fields', 'error');
        return;
      }

      if (!isValidEmail(email)) {
        showNotification('Please enter a valid email address', 'error');
        return;
      }

      // Simulate form submission
      const submitBtn = this.querySelector('button[type="submit"]');
      const originalText = submitBtn.textContent;

      submitBtn.textContent = 'Sending...';
      submitBtn.disabled = true;

      // Simulate API call
      setTimeout(() => {
        showNotification('Message sent successfully! I\'ll get back to you soon.', 'success');
        this.reset();
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        
        // Hide form after successful submission
        if (contactForm && toggleBtn) {
          contactForm.classList.remove('show');
          setTimeout(() => {
            contactForm.style.display = 'none';
            toggleBtn.style.display = 'inline-flex';
          }, 300);
        }
      }, 2000);
    });
  }
}

// Email validation
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Notification system
function showNotification(message, type = 'info') {
  // Remove existing notifications
  const existingNotification = document.querySelector('.notification');
  if (existingNotification) {
    existingNotification.remove();
  }

  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.innerHTML = `
    <div class="notification-content">
      <span class="notification-message">${message}</span>
      <button class="notification-close">&times;</button>
    </div>
  `;

  // Add styles
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    z-index: 10000;
    transform: translateX(100%);
    transition: transform 0.3s ease;
    max-width: 400px;
  `;

  // Add to page
  document.body.appendChild(notification);

  // Animate in
  setTimeout(() => {
    notification.style.transform = 'translateX(0)';
  }, 100);

  // Close button functionality
  const closeBtn = notification.querySelector('.notification-close');
  closeBtn.addEventListener('click', () => {
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => notification.remove(), 300);
  });

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (notification.parentNode) {
      notification.style.transform = 'translateX(100%)';
      setTimeout(() => notification.remove(), 300);
    }
  }, 5000);
}

// Animations
function initAnimations() {
  // Add CSS for animations
  const style = document.createElement('style');
  style.textContent = `
    .animate-in {
      animation: fadeInUp 0.6s ease forwards;
    }

    @keyframes fadeInUp {
      from {
        opacity: 0;
        transform: translateY(30px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .skill-category,
    .project-card,
    .timeline-item,
    .education-card,
    .publication-item {
      opacity: 0;
      transform: translateY(30px);
    }

    .skill-category.animate-in,
    .project-card.animate-in,
    .timeline-item.animate-in,
    .education-card.animate-in,
    .publication-item.animate-in {
      opacity: 1;
      transform: translateY(0);
    }

    .notification-content {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
    }

    .notification-close {
      background: none;
      border: none;
      color: white;
      font-size: 1.5rem;
      cursor: pointer;
      padding: 0;
      line-height: 1;
    }

    .notification-close:hover {
      opacity: 0.8;
    }
  `;
  document.head.appendChild(style);
}

// Typing effect for hero title
function initTypingEffect() {
  const heroTitle = document.querySelector('.hero-title');
  if (!heroTitle) return;

  const originalText = heroTitle.textContent;
  const highlightSpan = heroTitle.querySelector('.highlight');

  if (highlightSpan) {
    const highlightText = highlightSpan.textContent;
    highlightSpan.textContent = '';

    let i = 0;
    const typeWriter = () => {
      if (i < highlightText.length) {
        highlightSpan.textContent += highlightText.charAt(i);
        i++;
        setTimeout(typeWriter, 100);
      }
    };

    // Start typing effect after a delay
    setTimeout(typeWriter, 1000);
  }
}

// Progress bar animation
function animateProgressBars() {
  const progressBars = document.querySelectorAll('.progress-filled');

  const progressObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const progressBar = entry.target;
        const width = progressBar.style.width;
        progressBar.style.width = '0%';

        setTimeout(() => {
          progressBar.style.width = width;
        }, 200);
      }
    });
  }, { threshold: 0.5 });

  progressBars.forEach(bar => {
    progressObserver.observe(bar);
  });
}

// Initialize progress bar animations
document.addEventListener('DOMContentLoaded', function() {
  animateProgressBars();
});

// Parallax effect for hero section
function initParallax() {
  const heroSection = document.querySelector('.hero-section');
  if (!heroSection) return;

  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const rate = scrolled * -0.5;

    heroSection.style.transform = `translateY(${rate}px)`;
  });
}

// Initialize parallax
document.addEventListener('DOMContentLoaded', function() {
  initParallax();
});

// Smooth reveal animations for sections
function initRevealAnimations() {
  const sections = document.querySelectorAll('.section');

  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('section-visible');
      }
    });
  }, { threshold: 0.1 });

  sections.forEach(section => {
    sectionObserver.observe(section);
  });
}

// Add reveal animation styles
const revealStyles = document.createElement('style');
revealStyles.textContent = `
  .section {
    opacity: 0;
    transform: translateY(50px);
    transition: opacity 0.8s ease, transform 0.8s ease;
  }

  .section.section-visible {
    opacity: 1;
    transform: translateY(0);
  }

  .hero-section {
    opacity: 1;
    transform: none;
  }
`;
document.head.appendChild(revealStyles);

// Initialize reveal animations
document.addEventListener('DOMContentLoaded', function() {
  initRevealAnimations();
});

// Add loading animation
window.addEventListener('load', function() {
  document.body.classList.add('loaded');
});

// Add loading styles
const loadingStyles = document.createElement('style');
loadingStyles.textContent = `
  body {
    opacity: 0;
    transition: opacity 0.5s ease;
  }

  body.loaded {
    opacity: 1;
  }
`;
document.head.appendChild(loadingStyles);

  // Fetch Google Scholar citation metrics from a local JSON file (scholar.json)
  fetch('scholar.json')
    .then(response => response.json())
    .then(data => {
      const metricsDiv = document.getElementById('scholar-metrics');
      metricsDiv.innerHTML = `
        <p><strong>Total Citations:</strong> ${data.total_citations}</p>
        <p><strong>h-index:</strong> ${data.h_index}</p>
        <p><strong>i10-index:</strong> ${data.i10_index}</p>
      `;
    })
    .catch(error => {
      console.error('Error loading Google Scholar metrics:', error);
      const metricsDiv = document.getElementById('scholar-metrics');
      metricsDiv.innerHTML = `<p>Unable to load citation metrics.</p>`;
    });

// Add loading styles for publications
const loadingStyles = document.createElement('style');
loadingStyles.textContent = `
  .loading-publications {
    text-align: center;
    padding: 3rem 1rem;
  }

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid var(--border-color);
    border-top: 4px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .loading-publications p {
    color: var(--text-secondary);
    font-size: 1.125rem;
  }

  .error-message,
  .no-publications {
    text-align: center;
    padding: 3rem 1rem;
    background-color: var(--bg-secondary);
    border-radius: var(--border-radius-lg);
    border: 2px dashed var(--border-color);
  }

  .error-message p,
  .no-publications p {
    color: var(--text-secondary);
    font-size: 1.125rem;
    margin-bottom: 1rem;
  }

  .error-message a {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 500;
    transition: var(--transition);
  }

  .error-message a:hover {
    color: var(--accent-color);
    text-decoration: underline;
  }
`;
document.head.appendChild(loadingStyles);

// Fetch Google Scholar Publications
async function fetchGoogleScholarPublications() {
  const publicationsContainer = document.querySelector('.publications-list');
  if (!publicationsContainer) return;

  // Show loading state
  publicationsContainer.innerHTML = `
    <div class="loading-publications">
      <div class="loading-spinner"></div>
      <p>Loading publications from Google Scholar...</p>
    </div>
  `;

  try {
    // Since direct CORS access to Google Scholar is restricted,
    // we'll use a proxy service or fetch from a local JSON file
    // For now, let's create a more comprehensive local data structure

    const publications = await getPublicationsData();
    displayPublications(publications);
  } catch (error) {
    console.error('Error fetching publications:', error);
    publicationsContainer.innerHTML = `
      <div class="error-message">
        <p>Unable to load publications automatically. Please check the <a href="https://scholar.google.com/citations?hl=en&user=4re6DoEAAAAJ&view_op=list_works&sortby=pubdate" target="_blank">Google Scholar profile</a> directly.</p>
      </div>
    `;
  }
}

// Get publications data (you can update this with your actual publications)
async function getPublicationsData() {
  try {
    // Fetch from the local JSON file
    const response = await fetch('../data/publications.json');
    if (!response.ok) {
      throw new Error('Failed to fetch publications data');
    }

    const data = await response.json();
    return data.publications;
  } catch (error) {
    console.error('Error loading publications.json:', error);

    // Fallback to hardcoded data if JSON file is not available
    const publications = [
      {
        year: "2023",
        title: "A docker-based federated learning framework design and deployment for multi-modal data stream classification",
        authors: "Arijit Nandi, Fatos Xhafa, Rohit Kumar",
        journal: "Computing, Springer",
        citations: 15,
        links: {
          paper: "https://link.springer.com/article/10.1007/s00607-023-01195-5",
          code: "https://github.com/officialarijit/dfl"
        }
      },
      {
        year: "2022",
        title: "A federated learning method for real-time emotion state classification from multi-modal streaming",
        authors: "Arijit Nandi, Fatos Xhafa",
        journal: "Methods, Volume 204",
        citations: 12,
        links: {
          paper: "https://www.sciencedirect.com/science/article/abs/pii/S1046202322000894",
          code: "https://github.com/officialarijit/Fed-ReMECS-mqtt"
        }
      },
      {
        year: "2022",
        title: "Reward-penalty weighted ensemble for emotion state classification from multi-modal data streams",
        authors: "Arijit Nandi, Fatos Xhafa, Laia Subirats, Santi Fort",
        journal: "International Journal of Neural Systems",
        citations: 8,
        links: {
          paper: "https://www.worldscientific.com/doi/abs/10.1142/S0129065722500018",
          code: null
        }
      }
    ];

    return publications;
  }
}

// Display publications in the UI
function displayPublications(publications) {
  const publicationsContainer = document.querySelector('.publications-list');
  if (!publicationsContainer) return;

  if (publications.length === 0) {
    publicationsContainer.innerHTML = `
      <div class="no-publications">
        <p>No publications found. Please check your Google Scholar profile.</p>
      </div>
    `;
    return;
  }

  const publicationsHTML = publications.map(pub => `
    <div class="publication-item">
      <div class="publication-year">${pub.year}</div>
      <div class="publication-content">
        <h3>"${pub.title}"</h3>
        <p class="publication-authors">${pub.authors}</p>
        <p class="publication-journal">${pub.journal}</p>
        <div class="publication-metrics">
          <span class="citation-count">
            <i class="fas fa-quote-left"></i> ${pub.citations} citations
          </span>
        </div>
        <div class="publication-links">
          ${pub.links.paper ? `<a href="${pub.links.paper}" target="_blank"><i class="fas fa-external-link-alt"></i> View Paper</a>` : ''}
          ${pub.links.code ? `<a href="${pub.links.code}" target="_blank"><i class="fas fa-code"></i> Code</a>` : ''}
        </div>
      </div>
    </div>
  `).join('');

  publicationsContainer.innerHTML = publicationsHTML;
}

// Alternative: Use a CORS proxy to fetch from Google Scholar
// Note: This requires a CORS proxy service
async function fetchFromGoogleScholarWithProxy() {
  const scholarUrl = 'https://scholar.google.com/citations?hl=en&user=4re6DoEAAAAJ&view_op=list_works&sortby=pubdate';

  try {
    // You can use a CORS proxy service like:
    // const proxyUrl = 'https://cors-anywhere.herokuapp.com/';
    // const response = await fetch(proxyUrl + scholarUrl);

    // For now, we'll use the local data approach
    throw new Error('Direct CORS access not available');
  } catch (error) {
    console.error('CORS proxy fetch failed:', error);
    throw error;
  }
}

// Fetch Google Scholar Citation Metrics
async function fetchGoogleScholarMetrics() {
  try {
    // First try to fetch from the local JSON file
    const response = await fetch('../data/publications.json');
    if (response.ok) {
      const data = await response.json();
      if (data.metrics) {
        displayCitationMetrics(data.metrics);
        return;
      }
    }
  } catch (error) {
    console.log('No local metrics found, trying to fetch from Google Scholar...');
  }

  // If local data not available, try to fetch from Google Scholar
  try {
    const metrics = await fetchMetricsFromGoogleScholar();
    if (metrics) {
      displayCitationMetrics(metrics);
      // Save the metrics to local storage for future use
      localStorage.setItem('googleScholarMetrics', JSON.stringify(metrics));
    } else {
      // Fallback to default metrics
      displayCitationMetrics({
        total_citations: 263,
        h_index: 9,
        i10_index: 9
      });
    }
  } catch (error) {
    console.error('Error fetching Google Scholar metrics:', error);
    // Use cached metrics if available
    const cachedMetrics = localStorage.getItem('googleScholarMetrics');
    if (cachedMetrics) {
      displayCitationMetrics(JSON.parse(cachedMetrics));
    } else {
      // Final fallback
      displayCitationMetrics({
        total_citations: 263,
        h_index: 9,
        i10_index: 9
      });
    }
  }
}

// Attempt to fetch metrics from Google Scholar
async function fetchMetricsFromGoogleScholar() {
  const scholarId = '4re6DoEAAAAJ';
  const url = `https://scholar.google.com/citations?hl=en&user=${scholarId}&view_op=homepage`;

  try {
    // Note: This will likely fail due to CORS restrictions
    // In a real implementation, you'd need a backend proxy
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Failed to fetch from Google Scholar');
    }

    const html = await response.text();
    return parseMetricsFromHTML(html);
  } catch (error) {
    console.log('Direct fetch failed, trying alternative methods...');
    return null;
  }
}

// Parse metrics from Google Scholar HTML
function parseMetricsFromHTML(html) {
  try {
    // This is a simplified parser - you'd need to adjust based on actual HTML structure
    const totalCitationsMatch = html.match(/Citations\s*(\d+)/i);
    const hIndexMatch = html.match(/h-index\s*(\d+)/i);
    const i10IndexMatch = html.match(/i10-index\s*(\d+)/i);

    if (totalCitationsMatch || hIndexMatch || i10IndexMatch) {
      return {
        total_citations: totalCitationsMatch ? parseInt(totalCitationsMatch[1]) : 0,
        h_index: hIndexMatch ? parseInt(hIndexMatch[1]) : 0,
        i10_index: i10IndexMatch ? parseInt(i10IndexMatch[1]) : 0
      };
    }
    return null;
  } catch (error) {
    console.error('Error parsing metrics from HTML:', error);
    return null;
  }
}

// Display citation metrics in the UI
function displayCitationMetrics(metrics) {
  // Update hero section stats
  updateHeroStats(metrics);

  // Update or create metrics section
  updateMetricsSection(metrics);
}

// Update hero section statistics
function updateHeroStats(metrics) {
  const heroStats = document.querySelector('.hero-stats');
  if (heroStats) {
    // Update existing stats or create new ones
    const statsHTML = `
      <div class="stat">
        <span class="stat-number">${metrics.total_citations}+</span>
        <span class="stat-label">Total Citations</span>
      </div>
      <div class="stat">
        <span class="stat-number">${metrics.h_index}</span>
        <span class="stat-label">h-index</span>
      </div>
      <div class="stat">
        <span class="stat-number">${metrics.i10_index}</span>
        <span class="stat-label">i10-index</span>
      </div>
    `;
    heroStats.innerHTML = statsHTML;
  }
}

// Update or create metrics section
function updateMetricsSection(metrics) {
  let metricsSection = document.getElementById('metrics');

  if (!metricsSection) {
    // Create metrics section if it doesn't exist
    const publicationsSection = document.getElementById('publications');
    if (publicationsSection) {
      metricsSection = document.createElement('section');
      metricsSection.id = 'metrics';
      metricsSection.className = 'section';
      publicationsSection.parentNode.insertBefore(metricsSection, publicationsSection);
    }
  }

  if (metricsSection) {
    metricsSection.innerHTML = `
      <div class="container">
        <div class="section-header">
          <h2>Research Impact</h2>
          <p class="section-subtitle">Google Scholar Citation Metrics</p>
        </div>
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-icon">
              <i class="fas fa-quote-left"></i>
            </div>
            <div class="metric-content">
              <h3>Total Citations</h3>
              <div class="metric-value">${metrics.total_citations}</div>
              <p>Total citations across all publications</p>
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-icon">
              <i class="fas fa-chart-line"></i>
            </div>
            <div class="metric-content">
              <h3>h-index</h3>
              <div class="metric-value">${metrics.h_index}</div>
              <p>h-index measures both productivity and citation impact</p>
            </div>
          </div>
          <div class="metric-card">
            <div class="metric-icon">
              <i class="fas fa-star"></i>
            </div>
            <div class="metric-content">
              <h3>i10-index</h3>
              <div class="metric-value">${metrics.i10_index}</div>
              <p>Number of publications with at least 10 citations</p>
            </div>
          </div>
        </div>
        <div class="metrics-footer">
          <p>
            <i class="fas fa-info-circle"></i>
            Metrics are automatically updated from
            <a href="https://scholar.google.com/citations?hl=en&user=4re6DoEAAAAJ" target="_blank">
              Google Scholar
            </a>
          </p>
        </div>
      </div>
    `;
  }
}

function setDarkMode(enabled) {
  console.log('Setting dark mode:', enabled);
  
  try {
    if (enabled) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('darkMode', 'true');
      
      // Update all dark mode toggle buttons
      const toggleButtons = document.querySelectorAll('.dark-mode-toggle i');
      toggleButtons.forEach(i => {
        i.classList.remove('fa-moon');
        i.classList.add('fa-sun');
      });
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('darkMode', 'false');
      
      // Update all dark mode toggle buttons
      const toggleButtons = document.querySelectorAll('.dark-mode-toggle i');
      toggleButtons.forEach(i => {
        i.classList.remove('fa-sun');
        i.classList.add('fa-moon');
      });
    }
    
    console.log('Dark mode set successfully. Body classes:', document.body.classList.toString());
  } catch (error) {
    console.error('Error setting dark mode:', error);
  }
}

function initDarkMode() {
  console.log('Initializing dark mode...');
  
  try {
    // Get saved preference or system preference
    const saved = localStorage.getItem('darkMode');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Determine if dark mode should be enabled
    let enabled = false;
    if (saved !== null) {
      enabled = saved === 'true';
    } else {
      enabled = prefersDark;
    }
    
    console.log('Dark mode preferences:', { 
      saved, 
      prefersDark, 
      enabled,
      bodyClasses: document.body.classList.toString() 
    });
    
    // Set initial state
    setDarkMode(enabled);
    
    // Add event listeners to all dark mode toggle buttons
    const toggleButtons = document.querySelectorAll('.dark-mode-toggle');
    console.log('Found dark mode toggle buttons:', toggleButtons.length);
    
    toggleButtons.forEach((btn, index) => {
      console.log(`Setting up toggle button ${index + 1}`);
      
      // Remove any existing listeners
      btn.replaceWith(btn.cloneNode(true));
      
      // Get the new button reference
      const newBtn = document.querySelectorAll('.dark-mode-toggle')[index];
      
      newBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Dark mode toggle clicked');
        const currentDarkMode = document.body.classList.contains('dark-mode');
        setDarkMode(!currentDarkMode);
      });
    });
    
    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      const saved = localStorage.getItem('darkMode');
      if (saved === null) {
        // Only auto-switch if user hasn't manually set a preference
        setDarkMode(e.matches);
      }
    });
    
    console.log('Dark mode initialization completed');
  } catch (error) {
    console.error('Error initializing dark mode:', error);
  }
}
