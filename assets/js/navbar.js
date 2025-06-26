// Navbar loader and manager
class NavbarManager {
    constructor() {
        this.navbarContainer = null;
        this.currentPage = this.getCurrentPage();
    }

    getCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('blog.html')) {
            return 'blog';
        }
        return 'home';
    }

    async loadNavbar() {
        try {
            const response = await fetch('components/navbar.html');

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const navbarHtml = await response.text();

            // Create a temporary container to parse the HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = navbarHtml;

            // Find the nav element
            const navElement = tempDiv.querySelector('nav');

            if (navElement) {
                // Insert the navbar at the beginning of the body
                document.body.insertBefore(navElement, document.body.firstChild);

                // Update active states based on current page
                this.updateActiveStates();

                // Initialize mobile menu functionality
                this.initializeMobileMenu();

                // Initialize smooth scrolling
                this.initializeSmoothScrolling();

                // Initialize navbar background effects
                this.initializeNavbarEffects();

                // Initialize dark mode after navbar is loaded with a small delay
                setTimeout(() => {
                    if (typeof initDarkMode === 'function') {
                        console.log('Initializing dark mode from navbar manager...');
                        initDarkMode();
                    } else {
                        console.warn('initDarkMode function not found');
                    }
                }, 100);

                // Retry dropdown initialization with a delay to ensure DOM is ready
                setTimeout(() => {
                    this.initializeDropdown();
                }, 50);

                console.log('Navbar loaded successfully');
            } else {
                console.error('Nav element not found in navbar.html');
                this.createFallbackNavbar();
            }
        } catch (error) {
            console.error('Error loading navbar:', error);
            this.createFallbackNavbar();
        }
    }

    createFallbackNavbar() {
        console.log('Creating fallback navbar');
        const fallbackNav = document.createElement('nav');
        fallbackNav.innerHTML = `
            <div class="container nav-container">
                <div class="nav-brand">
                    <h1><a href="index.html">Arijit Nandi, Ph.D.</a></h1>
                    <span class="nav-subtitle">AI/ML Engineer & Researcher</span>
                </div>
                <button class="menu-toggle" id="menu-toggle" aria-label="Toggle Navigation">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
                <ul class="nav-menu">
                    <li><a href="index.html#hero">Home</a></li>
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle">About <i class="fas fa-chevron-down"></i></a>
                        <ul class="dropdown-menu">
                            <li><a href="index.html#about">About Me</a></li>
                            <li><a href="index.html#skills">Skills</a></li>
                            <li><a href="index.html#experience">Experience</a></li>
                            <li><a href="index.html#projects">Projects</a></li>
                            <li><a href="index.html#education">Education</a></li>
                            <li><a href="index.html#publications">Publications</a></li>
                        </ul>
                    </li>
                    <li><a href="blog.html">Blog</a></li>
                    <li><a href="index.html#social-media">Connect</a></li>
                    <li><a href="index.html#contact">Contact</a></li>
                    <li>
                        <button id="darkModeToggle" class="dark-mode-toggle" title="Toggle dark mode">
                            <i class="fas fa-moon"></i>
                        </button>
                    </li>
                </ul>
            </div>
        `;

        document.body.insertBefore(fallbackNav, document.body.firstChild);

        // Initialize functionality
        this.updateActiveStates();
        this.initializeMobileMenu();
        this.initializeSmoothScrolling();
        this.initializeNavbarEffects();
        
        // Initialize dark mode after navbar is loaded with a small delay
        setTimeout(() => {
            if (typeof initDarkMode === 'function') {
                console.log('Initializing dark mode from fallback navbar...');
                initDarkMode();
            } else {
                console.warn('initDarkMode function not found in fallback');
            }
        }, 100);
    }

    updateActiveStates() {
        const navLinks = document.querySelectorAll('.nav-menu a');

        navLinks.forEach(link => {
            // Remove any existing active class
            link.classList.remove('active');

            const href = link.getAttribute('href');

            // Check if this link should be active
            if (this.currentPage === 'blog' && href === 'blog.html') {
                link.classList.add('active');
            } else if (this.currentPage === 'home') {
                // For home page, check if we're on a specific section
                const currentHash = window.location.hash;
                if (currentHash && href === `index.html${currentHash}`) {
                    link.classList.add('active');

                    // If this is a dropdown item, also highlight the dropdown toggle
                    const dropdownItem = link.closest('.dropdown-menu');
                    if (dropdownItem) {
                        const dropdown = dropdownItem.closest('.dropdown');
                        if (dropdown) {
                            dropdown.classList.add('active');
                        }
                    }
                } else if (!currentHash && (href === 'index.html#hero' || href === '#hero')) {
                    link.classList.add('active');
                }
            }
        });
    }

    initializeMobileMenu() {
        const menuToggle = document.getElementById('menu-toggle');
        const navMenu = document.querySelector('.nav-menu');

        if (menuToggle && navMenu) {
            menuToggle.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();

                navMenu.classList.toggle('active');
                menuToggle.classList.toggle('active');

                // Close any open dropdowns when toggling mobile menu
                const dropdowns = document.querySelectorAll('.dropdown');
                dropdowns.forEach(dropdown => {
                    dropdown.classList.remove('active');
                });
            });

            // Close mobile menu when clicking on a regular link (not dropdown toggle)
            const navLinks = document.querySelectorAll('.nav-menu > li > a:not(.dropdown-toggle)');
            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    navMenu.classList.remove('active');
                    menuToggle.classList.remove('active');
                });
            });

            // Close mobile menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!menuToggle.contains(e.target) && !navMenu.contains(e.target)) {
                    navMenu.classList.remove('active');
                    menuToggle.classList.remove('active');

                    // Also close any open dropdowns
                    const dropdowns = document.querySelectorAll('.dropdown');
                    dropdowns.forEach(dropdown => {
                        dropdown.classList.remove('active');
                    });
                }
            });
        }

        // Initialize dropdown functionality
        this.initializeDropdown();
    }

    initializeDropdown() {
        const dropdowns = document.querySelectorAll('.dropdown');

        dropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.dropdown-toggle');

            if (toggle) {
                // Remove any existing event listeners to prevent duplicates
                toggle.removeEventListener('click', this.handleDropdownToggle);
                
                // Add new event listener
                toggle.addEventListener('click', this.handleDropdownToggle.bind(this));
            }
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown')) {
                dropdowns.forEach(dropdown => {
                    dropdown.classList.remove('active');
                });
            }
        });

        // Close dropdowns on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                dropdowns.forEach(dropdown => {
                    dropdown.classList.remove('active');
                });
            }
        });

        // Handle dropdown item clicks (both desktop and mobile)
        this.initializeDropdownItemClicks();
        
        console.log(`Initialized ${dropdowns.length} dropdowns`);
    }

    handleDropdownToggle(e) {
        e.preventDefault();
        e.stopPropagation();

        const dropdown = e.target.closest('.dropdown');
        const allDropdowns = document.querySelectorAll('.dropdown');

        // Close other dropdowns
        allDropdowns.forEach(other => {
            if (other !== dropdown) {
                other.classList.remove('active');
            }
        });

        // Toggle current dropdown
        dropdown.classList.toggle('active');
        
        console.log(`Dropdown toggled: ${dropdown.classList.contains('active') ? 'opened' : 'closed'}`);
    }

    initializeDropdownItemClicks() {
        const dropdowns = document.querySelectorAll('.dropdown');

        dropdowns.forEach(dropdown => {
            const dropdownLinks = dropdown.querySelectorAll('.dropdown-menu a');

            dropdownLinks.forEach(link => {
                link.addEventListener('click', () => {
                    // Close the dropdown
                    dropdown.classList.remove('active');

                    // Close the mobile menu if on mobile
                    const navMenu = document.querySelector('.nav-menu');
                    const menuToggle = document.getElementById('menu-toggle');

                    if (navMenu && menuToggle && window.innerWidth <= 768) {
                        navMenu.classList.remove('active');
                        menuToggle.classList.remove('active');
                    }
                });
            });
        });
    }

    initializeSmoothScrolling() {
        const navLinks = document.querySelectorAll('.nav-menu a');
        const nav = document.querySelector('nav');

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');

                // Handle blog link
                if (href === 'blog.html') {
                    // If we're already on blog page, don't prevent default
                    if (this.currentPage === 'blog') {
                        return;
                    }
                    // Otherwise, let it navigate normally
                    return;
                }

                // Handle links to index.html with hash
                if (href.startsWith('index.html#')) {
                    // If we're already on index.html, prevent default and scroll smoothly
                    if (this.currentPage === 'home') {
                        e.preventDefault();

                        const targetId = href.split('#')[1];
                        const targetSection = document.getElementById(targetId);

                        if (targetSection) {
                            const navHeight = nav.offsetHeight;
                            const targetPosition = targetSection.offsetTop - navHeight - 20;

                            console.log(`Scrolling to ${targetId} at position ${targetPosition}`);

                            window.scrollTo({
                                top: targetPosition,
                                behavior: 'smooth'
                            });

                            // Update URL hash after scrolling
                            setTimeout(() => {
                                window.location.hash = targetId;
                            }, 500);
                        } else {
                            console.warn(`Target section with id '${targetId}' not found`);
                        }
                    }
                    // If we're on blog page, let it navigate normally to index.html
                    return;
                }
            });
        });
    }

    initializeNavbarEffects() {
        const nav = document.querySelector('nav');

        if (nav) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 100) {
                    nav.style.background = 'rgba(255, 255, 255, 0.98)';
                    nav.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
                } else {
                    nav.style.background = 'rgba(255, 255, 255, 0.95)';
                    nav.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
                }
            });
        }

        // Initialize section tracking for active states
        this.initializeSectionTracking();
    }

    initializeSectionTracking() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-menu a[href^="index.html#"]');
        
        console.log(`Found ${sections.length} sections with IDs:`, Array.from(sections).map(s => s.id));
        console.log(`Found ${navLinks.length} nav links:`, Array.from(navLinks).map(l => l.getAttribute('href')));
        
        if (sections.length === 0 || navLinks.length === 0) {
            console.warn('No sections or nav links found for tracking');
            return;
        }

        const observerOptions = {
            threshold: 0.3,
            rootMargin: '-20% 0px -20% 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const currentSectionId = entry.target.id;
                    console.log(`Section ${currentSectionId} is now active`);
                    this.updateActiveStateForSection(currentSectionId);
                }
            });
        }, observerOptions);

        // Observe all sections
        sections.forEach(section => {
            observer.observe(section);
            console.log(`Observing section: ${section.id}`);
        });
    }

    updateActiveStateForSection(sectionId) {
        const navLinks = document.querySelectorAll('.nav-menu a');
        
        console.log(`Updating active state for section: ${sectionId}`);
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            
            const href = link.getAttribute('href');
            if (href === `index.html#${sectionId}` || href === `#${sectionId}`) {
                link.classList.add('active');
                console.log(`Made link active: ${href}`);
                
                // Note: Removed dropdown container active state to prevent dropdown from opening on scroll
                // The dropdown toggle will still be highlighted through CSS if needed
            }
        });
    }

    // Method to update active state when hash changes (for single page navigation)
    handleHashChange() {
        if (this.currentPage === 'home') {
            this.updateActiveStates();
        }
    }
}

// Initialize navbar when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const navbarManager = new NavbarManager();
    navbarManager.loadNavbar();

    // Handle hash changes for single page navigation
    window.addEventListener('hashchange', () => {
        navbarManager.handleHashChange();
    });
});