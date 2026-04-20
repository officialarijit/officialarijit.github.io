// Simple zoom overlay — click image to zoom in, click overlay to close
class ImageLightbox {
  constructor() {
    this.isOpen = false;
    this.init();
  }

  init() {
    this.createOverlayHTML();
    this.bindEvents();
    this.makeImagesClickable();
  }

  createOverlayHTML() {
    const html = `
      <div class="image-lightbox" id="imageLightbox" role="dialog" aria-modal="true" aria-label="Image zoom overlay">
        <button class="lightbox-close" id="lightboxClose" aria-label="Close">&times;</button>
        <img class="lightbox-image" id="lightboxImage" src="" alt="">
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', html);
  }

  bindEvents() {
    const overlay = document.getElementById('imageLightbox');
    const closeBtn = document.getElementById('lightboxClose');

    // Click overlay backdrop to close
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay || e.target === document.getElementById('lightboxImage')) {
        this.close();
      }
    });

    closeBtn.addEventListener('click', () => this.close());

    // Escape key to close
    document.addEventListener('keydown', (e) => {
      if (this.isOpen && e.key === 'Escape') this.close();
    });
  }

  makeImagesClickable() {
    document.querySelectorAll('img').forEach((img) => {
      if (img.classList.contains('lightbox-image') || img.dataset.lightbox === 'false') return;
      img.classList.add('clickable-image');
      img.addEventListener('click', (e) => {
        e.preventDefault();
        this.open(img.src, img.alt);
      });
    });
  }

  open(src, alt) {
    this.isOpen = true;
    const overlay = document.getElementById('imageLightbox');
    const img = document.getElementById('lightboxImage');

    img.src = src;
    img.alt = alt || '';
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  close() {
    this.isOpen = false;
    const overlay = document.getElementById('imageLightbox');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
    // Clear src after transition so old image doesn't flash on next open
    setTimeout(() => {
      if (!this.isOpen) document.getElementById('lightboxImage').src = '';
    }, 300);
  }

  excludeImages(selector) {
    document.querySelectorAll(selector).forEach((img) => {
      img.classList.remove('clickable-image');
      img.dataset.lightbox = 'false';
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.imageLightbox = new ImageLightbox();
  window.imageLightbox.excludeImages('.profile-photo, .nav-brand img, .social-links img, .footer img');
});

function reinitializeLightbox() {
  if (window.imageLightbox) window.imageLightbox.makeImagesClickable();
}
window.reinitializeLightbox = reinitializeLightbox;

if (typeof module !== 'undefined' && module.exports) {
  module.exports = ImageLightbox;
}
