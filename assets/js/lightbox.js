// Image Lightbox Functionality
class ImageLightbox {
  constructor() {
    this.currentIndex = 0;
    this.images = [];
    this.isOpen = false;
    this.init();
  }

  init() {
    this.createLightboxHTML();
    this.bindEvents();
    this.makeImagesClickable();
  }

  createLightboxHTML() {
    const lightboxHTML = `
      <div class="image-lightbox" id="imageLightbox">
        <div class="lightbox-content">
          <img class="lightbox-image" id="lightboxImage" src="" alt="">
          <button class="lightbox-close" id="lightboxClose">&times;</button>
          <button class="lightbox-nav lightbox-prev" id="lightboxPrev">‹</button>
          <button class="lightbox-nav lightbox-next" id="lightboxNext">›</button>
          <div class="lightbox-counter" id="lightboxCounter"></div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', lightboxHTML);
  }

  bindEvents() {
    const lightbox = document.getElementById('imageLightbox');
    const closeBtn = document.getElementById('lightboxClose');
    const prevBtn = document.getElementById('lightboxPrev');
    const nextBtn = document.getElementById('lightboxNext');

    // Close lightbox
    closeBtn.addEventListener('click', () => this.close());
    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox) this.close();
    });

    // Navigation
    prevBtn.addEventListener('click', () => this.prev());
    nextBtn.addEventListener('click', () => this.next());

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (!this.isOpen) return;

      switch(e.key) {
        case 'Escape':
          this.close();
          break;
        case 'ArrowLeft':
          this.prev();
          break;
        case 'ArrowRight':
          this.next();
          break;
      }
    });

    // Touch/swipe support for mobile
    let startX = 0;
    let endX = 0;

    lightbox.addEventListener('touchstart', (e) => {
      startX = e.changedTouches[0].screenX;
    });

    lightbox.addEventListener('touchend', (e) => {
      endX = e.changedTouches[0].screenX;
      this.handleSwipe();
    });
  }

  handleSwipe() {
    const swipeThreshold = 50;
    const diff = startX - endX;

    if (Math.abs(diff) > swipeThreshold) {
      if (diff > 0) {
        this.next();
      } else {
        this.prev();
      }
    }
  }

  makeImagesClickable() {
    // Make all images clickable by default
    const images = document.querySelectorAll('img');
    images.forEach((img, index) => {
      // Skip if already has click handler or is in lightbox
      if (img.classList.contains('lightbox-image') || img.dataset.lightbox === 'false') {
        return;
      }

      img.classList.add('clickable-image');
      img.addEventListener('click', (e) => {
        e.preventDefault();
        this.openImage(img.src, img.alt, index);
      });
    });
  }

  openImage(src, alt, index = 0) {
    this.currentIndex = index;
    this.isOpen = true;

    const lightbox = document.getElementById('imageLightbox');
    const lightboxImage = document.getElementById('lightboxImage');
    const counter = document.getElementById('lightboxCounter');

    // Show loading state
    lightboxImage.style.display = 'none';
    lightbox.classList.add('active');

    // Load image
    const img = new Image();
    img.onload = () => {
      lightboxImage.src = src;
      lightboxImage.alt = alt;
      lightboxImage.style.display = 'block';
      this.updateCounter();
    };
    img.onerror = () => {
      lightboxImage.style.display = 'block';
      lightboxImage.src = src;
      lightboxImage.alt = alt;
      this.updateCounter();
    };
    img.src = src;

    // Prevent body scroll
    document.body.style.overflow = 'hidden';
  }

  close() {
    this.isOpen = false;
    const lightbox = document.getElementById('imageLightbox');
    lightbox.classList.remove('active');
    document.body.style.overflow = '';
  }

  prev() {
    const images = document.querySelectorAll('.clickable-image');
    if (images.length === 0) return;

    this.currentIndex = (this.currentIndex - 1 + images.length) % images.length;
    const prevImage = images[this.currentIndex];
    this.openImage(prevImage.src, prevImage.alt, this.currentIndex);
  }

  next() {
    const images = document.querySelectorAll('.clickable-image');
    if (images.length === 0) return;

    this.currentIndex = (this.currentIndex + 1) % images.length;
    const nextImage = images[this.currentIndex];
    this.openImage(nextImage.src, nextImage.alt, this.currentIndex);
  }

  updateCounter() {
    const images = document.querySelectorAll('.clickable-image');
    const counter = document.getElementById('lightboxCounter');

    if (images.length > 1) {
      counter.textContent = `${this.currentIndex + 1} / ${images.length}`;
      counter.style.display = 'block';
    } else {
      counter.style.display = 'none';
    }
  }

  // Method to add specific images to lightbox
  addImages(imageSelectors) {
    const images = document.querySelectorAll(imageSelectors);
    images.forEach((img, index) => {
      img.classList.add('clickable-image');
      img.addEventListener('click', (e) => {
        e.preventDefault();
        this.openImage(img.src, img.alt, index);
      });
    });
  }

  // Method to exclude specific images from lightbox
  excludeImages(imageSelectors) {
    const images = document.querySelectorAll(imageSelectors);
    images.forEach(img => {
      img.classList.remove('clickable-image');
      img.dataset.lightbox = 'false';
    });
  }
}

// Initialize lightbox when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.imageLightbox = new ImageLightbox();

  // Exclude specific images (like logos, icons, etc.)
  window.imageLightbox.excludeImages('.profile-photo, .nav-brand img, .social-links img, .footer img');

  // Optional: Add specific images only
  // window.imageLightbox.addImages('.gallery img, .project-image img');
});

// Re-initialize for dynamically loaded content
function reinitializeLightbox() {
  if (window.imageLightbox) {
    window.imageLightbox.makeImagesClickable();
  }
}

// Make function globally available
window.reinitializeLightbox = reinitializeLightbox;

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ImageLightbox;
}
