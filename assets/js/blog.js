/**
 * Blog System JavaScript
 * Handles dynamic blog loading, filtering, and LaTeX rendering
 */

class BlogSystem {
    constructor() {
        this.blogPosts = [];
        this.currentCategory = 'all';
        this.currentPost = null;
        this.init();
    }

    async init() {
        console.log('Initializing blog system...');
        
        // Check if we're on the index page or blog page
        const isIndexPage = window.location.pathname.includes('index.html') || window.location.pathname === '/' || window.location.pathname === '';
        
        if (isIndexPage) {
            console.log('On index page - loading blog preview');
            await this.loadIndexBlogPosts();
        } else {
            console.log('On blog page - loading full blog system');
            await this.loadBlogPosts();
            this.setupEventListeners();
            this.renderBlogPosts();
            this.updateSidebar();
            this.setupMathJax();
            
            // Check if we should scroll to a specific post
            this.checkForScrollToPost();
        }
        
        console.log('Blog system initialized successfully');
        console.log('Total posts loaded:', this.blogPosts.length);
        console.log('Sidebar should be updated with recent posts');
    }

    async loadBlogPosts() {
        try {
            console.log('Loading blog posts...');
            const response = await fetch('data/blog_posts.json');
            if (!response.ok) {
                throw new Error(`Failed to load blog posts: ${response.status} ${response.statusText}`);
            }
            const data = await response.json();
            this.blogPosts = data.posts || [];
            console.log(`Loaded ${this.blogPosts.length} blog posts:`, this.blogPosts);
        } catch (error) {
            console.error('Error loading blog posts:', error);
            this.blogPosts = [];
            // Show error message on page
            const blogPostsContainer = document.getElementById('blog-posts');
            if (blogPostsContainer) {
                blogPostsContainer.innerHTML = `
                    <div class="no-posts">
                        <h3>Error Loading Blog Posts</h3>
                        <p>Unable to load blog posts. Please check the console for details.</p>
                        <p>Error: ${error.message}</p>
                    </div>
                `;
            }
        }
    }

    setupEventListeners() {
        // Filter buttons
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                const category = button.dataset.category;
                this.setCategory(category);
            });
        });

        // Modal close button
        const modalClose = document.getElementById('modal-close');
        if (modalClose) {
            modalClose.addEventListener('click', () => {
                this.closeModal();
            });
        }

        // Close modal when clicking outside
        const modal = document.getElementById('blog-modal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        }

        // Close modal with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.currentPost) {
                this.closeModal();
            }
        });

        // Category links in sidebar
        document.addEventListener('click', (e) => {
            if (e.target.matches('.category-list a')) {
                e.preventDefault();
                const category = e.target.dataset.category;
                this.setCategory(category);
            }
        });
    }

    setCategory(category) {
        console.log('Setting category to:', category);
        this.currentCategory = category;
        this.updateActiveFilter();
        this.renderBlogPosts();
    }

    updateActiveFilter() {
        // Update filter button states
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach(button => {
            button.classList.toggle('active', button.dataset.category === this.currentCategory);
        });
    }

    renderBlogPosts() {
        const blogPostsContainer = document.getElementById('blog-posts');
        if (!blogPostsContainer) {
            console.error('Blog posts container not found!');
            return;
        }

        const filteredPosts = this.getFilteredPosts();
        console.log('Rendering filtered posts:', filteredPosts);
        
        if (filteredPosts.length === 0) {
            blogPostsContainer.innerHTML = `
                <div class="no-posts">
                    <h3>No posts found</h3>
                    <p>No blog posts available for the selected category.</p>
                </div>
            `;
            return;
        }

        const postsHTML = filteredPosts.map(post => this.createPostCard(post)).join('');
        blogPostsContainer.innerHTML = postsHTML;

        // Add click listeners to post cards
        this.setupPostCardListeners();
        console.log('Blog posts rendered successfully');
    }

    getFilteredPosts() {
        console.log('Getting filtered posts. Current filter:', this.currentCategory);
        console.log('Available posts:', this.blogPosts);
        
        if (this.currentCategory === 'all') {
            return this.blogPosts;
        }
        
        const filtered = this.blogPosts.filter(post => {
            const postCategory = post.category.toLowerCase().replace(' ', '-');
            const matches = postCategory === this.currentCategory;
            console.log(`Post "${post.title}" category: "${postCategory}", filter: "${this.currentCategory}", matches: ${matches}`);
            return matches;
        });
        
        console.log('Filtered posts:', filtered);
        return filtered;
    }

    createPostCard(post) {
        const imageUrl = post.image || 'assets/images/slide2.jpg'; // Fallback image
        const date = new Date(post.date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        return `
            <article class="blog-post-card" data-category="${post.category.toLowerCase().replace(' ', '-')}" data-post-id="${post.id}">
                <div class="post-image">
                    <img src="${imageUrl}" alt="${post.title}" onerror="this.src='assets/images/slide2.jpg'; this.style.opacity='0.7';">
                </div>
                <div class="post-content">
                    <div class="post-meta">
                        <span class="post-category">${post.category}</span>
                        <span class="post-date">${date}</span>
                        <span class="post-read-time">${post.read_time}</span>
                    </div>
                    <h3 class="post-title">${post.title}</h3>
                    <p class="post-subtitle">${post.subtitle}</p>
                    <p class="post-excerpt">${post.excerpt}</p>
                    <div class="post-tags">
                        ${post.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                    </div>
                    <button class="read-more-btn">Read More</button>
                </div>
            </article>
        `;
    }

    setupPostCardListeners() {
        const postCards = document.querySelectorAll('.blog-post-card');
        postCards.forEach(card => {
            // Handle card click (excluding button clicks)
            card.addEventListener('click', (e) => {
                if (!e.target.closest('.read-more-btn')) {
                    const postId = card.dataset.postId;
                    this.openPost(postId);
                }
            });

            // Handle read more button click specifically
            const readMoreBtn = card.querySelector('.read-more-btn');
            if (readMoreBtn) {
                readMoreBtn.addEventListener('click', (e) => {
                    e.stopPropagation(); // Prevent card click event
                    const postId = card.dataset.postId;
                    console.log('Read more clicked for post:', postId);
                    this.openPost(postId);
                });
            }
        });
    }

    async openPost(postId) {
        console.log('Opening post with ID:', postId);
        const post = this.blogPosts.find(p => p.id === postId);
        if (!post) {
            console.error('Post not found with ID:', postId);
            return;
        }

        console.log('Found post:', post.title);
        this.currentPost = post;
        this.showModal(post);
    }

    showModal(post) {
        console.log('Showing modal for post:', post.title);
        const modal = document.getElementById('blog-modal');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');

        if (!modal || !modalTitle || !modalBody) {
            console.error('Modal elements not found:', { modal: !!modal, modalTitle: !!modalTitle, modalBody: !!modalBody });
            return;
        }

        modalTitle.textContent = post.title;
        
        // Create modal content
        const date = new Date(post.date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        const tagsHTML = post.tags.map(tag => `<span class="tag">${tag}</span>`).join('');

        modalBody.innerHTML = `
            <div class="modal-post-meta">
                <div class="post-meta-info">
                    <span class="post-date"><i class="far fa-calendar"></i> ${date}</span>
                    <span class="post-read-time"><i class="far fa-clock"></i> ${post.read_time}</span>
                    <span class="post-author"><i class="far fa-user"></i> ${post.author}</span>
                </div>
                <div class="post-tags">
                    ${tagsHTML}
                </div>
            </div>
            ${post.subtitle ? `<h3 class="post-subtitle">${post.subtitle}</h3>` : ''}
            <div class="post-content">
                ${post.content}
            </div>
        `;

        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        console.log('Modal should now be visible');

        // Wait for modal to be visible and content to be rendered, then render MathJax
        setTimeout(() => {
            console.log('Modal is visible, checking for LaTeX content...');
            const content = modalBody.innerHTML;
            if (content.includes('$$') || content.includes('$')) {
                console.log('LaTeX content detected, rendering MathJax...');
                this.renderMathJax();
            } else {
                console.log('No LaTeX content detected in modal');
            }
        }, 300);
    }

    closeModal() {
        const modal = document.getElementById('blog-modal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
        this.currentPost = null;
    }

    updateSidebar() {
        console.log('Updating sidebar with', this.blogPosts.length, 'posts');
        
        // Update category counts
        const categories = {};
        this.blogPosts.forEach(post => {
            const category = post.category;
            categories[category] = (categories[category] || 0) + 1;
        });

        console.log('Categories found:', categories);

        // Update category list
        const categoryList = document.querySelector('.category-list');
        if (categoryList) {
            const categoryHTML = Object.entries(categories).map(([category, count]) => {
                const categorySlug = category.toLowerCase().replace(/\s+/g, '-');
                return `<li><a href="#" data-category="${categorySlug}">${category} <span>(${count})</span></a></li>`;
            }).join('');
            categoryList.innerHTML = categoryHTML;
            console.log('Category list updated');
        } else {
            console.warn('Category list element not found');
        }

        // Update recent posts - sort by date (newest first) and take the latest 5
        const recentPosts = document.querySelector('.recent-posts');
        if (recentPosts) {
            // Sort posts by date (newest first)
            const sortedPosts = [...this.blogPosts].sort((a, b) => new Date(b.date) - new Date(a.date));
            const recentPostsHTML = sortedPosts.slice(0, 5).map(post => {
                const date = new Date(post.date).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });
                return `<li><a href="#" onclick="blogSystem.openPost('${post.id}')" title="${post.title}">${post.title}</a><span class="post-date-small">${date}</span></li>`;
            }).join('');
            
            if (recentPostsHTML) {
                recentPosts.innerHTML = recentPostsHTML;
                console.log('Recent posts updated with', sortedPosts.slice(0, 5).length, 'posts');
            } else {
                recentPosts.innerHTML = '<li><em>No posts available</em></li>';
                console.log('No recent posts to display');
            }
        } else {
            console.warn('Recent posts element not found');
        }
    }

    setupMathJax() {
        console.log('Setting up MathJax...');
        
        // Don't override MathJax if it's already configured
        if (!window.MathJax) {
            window.MathJax = {
                tex: {
                    inlineMath: [['$', '$'], ['\\(', '\\)']],
                    displayMath: [['$$', '$$'], ['\\[', '\\]']],
                    processEscapes: true,
                    processEnvironments: true
                },
                options: {
                    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
                    processHtmlClass: 'math-display'
                },
                startup: {
                    pageReady: () => {
                        console.log('MathJax startup complete');
                        return window.MathJax.startup.defaultPageReady();
                    }
                }
            };
        }
        
        // Wait for MathJax to be available
        this.waitForMathJax();
    }

    waitForMathJax() {
        if (window.MathJax && window.MathJax.typesetPromise) {
            console.log('MathJax is ready');
            return;
        }
        
        console.log('Waiting for MathJax to load...');
        setTimeout(() => this.waitForMathJax(), 100);
    }

    renderMathJax() {
        console.log('Rendering MathJax...');
        
        // Wait for MathJax to be ready
        const waitForMathJax = () => {
            if (window.MathJax && window.MathJax.typesetPromise) {
                console.log('MathJax is available, rendering...');
                return window.MathJax.typesetPromise().then(() => {
                    console.log('MathJax rendering completed');
                }).catch((error) => {
                    console.error('MathJax rendering error:', error);
                });
            } else {
                console.log('MathJax not ready yet, waiting...');
                setTimeout(waitForMathJax, 100);
            }
        };
        
        // Start the rendering process with a longer delay to ensure content is loaded
        setTimeout(waitForMathJax, 500);
    }

    async refreshBlogData() {
        console.log('Refreshing blog data...');
        
        // Add loading state to refresh button
        const refreshBtn = document.querySelector('.refresh-btn');
        if (refreshBtn) {
            const originalText = refreshBtn.innerHTML;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
            refreshBtn.disabled = true;
            
            try {
                await this.loadBlogPosts();
                this.renderBlogPosts();
                this.updateSidebar();
                console.log('Blog data refreshed successfully');
                
                // Show success feedback
                refreshBtn.innerHTML = '<i class="fas fa-check"></i> Refreshed!';
                setTimeout(() => {
                    refreshBtn.innerHTML = originalText;
                    refreshBtn.disabled = false;
                }, 2000);
            } catch (error) {
                console.error('Error refreshing blog data:', error);
                refreshBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error!';
                setTimeout(() => {
                    refreshBtn.innerHTML = originalText;
                    refreshBtn.disabled = false;
                }, 3000);
            }
        }
    }

    async loadIndexBlogPosts() {
        console.log('Loading blog posts for index page...');
        try {
            const response = await fetch('data/blog_posts.json');
            if (!response.ok) {
                throw new Error(`Failed to load blog posts: ${response.status} ${response.statusText}`);
            }
            const data = await response.json();
            const posts = data.posts || [];
            console.log(`Loaded ${posts.length} blog posts for index page`);
            
            this.renderIndexBlogPosts(posts);
        } catch (error) {
            console.error('Error loading blog posts for index page:', error);
            this.showIndexBlogError();
        }
    }

    renderIndexBlogPosts(posts) {
        const blogPreviewGrid = document.getElementById('blog-preview-grid');
        if (!blogPreviewGrid) {
            console.warn('Blog preview grid not found on index page');
            return;
        }

        // Sort posts by date (newest first) and take the latest 3
        const sortedPosts = [...posts].sort((a, b) => new Date(b.date) - new Date(a.date));
        const latestPosts = sortedPosts.slice(0, 3);

        if (latestPosts.length === 0) {
            blogPreviewGrid.innerHTML = `
                <div class="blog-preview-empty">
                    <p>No blog posts available yet.</p>
                    <a href="blog.html" class="btn btn-primary">Visit Blog</a>
                </div>
            `;
            return;
        }

        const postsHTML = latestPosts.map(post => this.createIndexBlogCard(post)).join('');
        blogPreviewGrid.innerHTML = postsHTML;
        
        console.log(`Rendered ${latestPosts.length} blog posts on index page`);
    }

    createIndexBlogCard(post) {
        const imageUrl = post.image || 'assets/images/slide2.jpg';
        const date = new Date(post.date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });

        return `
            <div class="blog-preview-card">
                <div class="blog-preview-image">
                    <img src="${imageUrl}" alt="${post.title}" onerror="this.src='assets/images/slide2.jpg'; this.style.opacity='0.7';">
                    <div class="blog-preview-overlay">
                        <span class="blog-category">${post.category}</span>
                    </div>
                </div>
                <div class="blog-preview-content">
                    <div class="blog-meta">
                        <span class="blog-date">${date}</span>
                        <span class="blog-read-time">${post.read_time}</span>
                    </div>
                    <h3>${post.title}</h3>
                    <p>${post.excerpt}</p>
                    <a href="blog.html" class="blog-read-more" onclick="sessionStorage.setItem('scrollToPost', '${post.id}')">Read More <i class="fas fa-arrow-right"></i></a>
                </div>
            </div>
        `;
    }

    showIndexBlogError() {
        const blogPreviewGrid = document.getElementById('blog-preview-grid');
        if (blogPreviewGrid) {
            blogPreviewGrid.innerHTML = `
                <div class="blog-preview-error">
                    <p>Unable to load blog posts at the moment.</p>
                    <a href="blog.html" class="btn btn-primary">Visit Blog</a>
                </div>
            `;
        }
    }

    checkForScrollToPost() {
        const scrollToPost = sessionStorage.getItem('scrollToPost');
        if (scrollToPost) {
            console.log('Scrolling to post:', scrollToPost);
            sessionStorage.removeItem('scrollToPost');
            
            // Wait a bit for the page to load, then scroll to the post
            setTimeout(() => {
                const postCard = document.querySelector(`[data-post-id="${scrollToPost}"]`);
                if (postCard) {
                    postCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    // Add a highlight effect
                    postCard.style.boxShadow = '0 0 20px rgba(61, 111, 182, 0.5)';
                    setTimeout(() => {
                        postCard.style.boxShadow = '';
                    }, 3000);
                }
            }, 1000);
        }
    }
}

// Initialize blog system when DOM is loaded
let blogSystem;
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM loaded, initializing blog system...');
    try {
        blogSystem = new BlogSystem();
        await blogSystem.init();
        console.log('Blog system initialized successfully');
        // Export for global access
        window.blogSystem = blogSystem;
    } catch (error) {
        console.error('Error initializing blog system:', error);
    }
});
