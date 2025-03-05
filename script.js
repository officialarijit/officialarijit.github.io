// Smooth scrolling for navigation links and dynamic features
document.addEventListener("DOMContentLoaded", function() {
  // Smooth scrolling for nav links
  const navLinks = document.querySelectorAll("nav ul li a");
  navLinks.forEach(link => {
    link.addEventListener("click", function(e) {
      e.preventDefault();
      // Close mobile menu if open
      if (document.querySelector('.nav-menu').classList.contains('active')) {
        document.querySelector('.nav-menu').classList.remove('active');
      }
      const targetId = this.getAttribute("href").substring(1);
      const targetSection = document.getElementById(targetId);
      if (targetSection) {
        window.scrollTo({
          top: targetSection.offsetTop - 60,
          behavior: "smooth"
        });
      }
    });
  });

  // Mobile hamburger menu toggle
  const menuToggle = document.getElementById("menu-toggle");
  menuToggle.addEventListener("click", function() {
    document.querySelector(".nav-menu").classList.toggle("active");
  });



document.getElementById("menu-toggle").addEventListener("click", function() {
  document.querySelector(".nav-menu").classList.toggle("active");
});


  // Slider functionality
  let slideIndex = 0;
  const slides = document.querySelectorAll(".slide");
  const prev = document.querySelector(".prev");
  const next = document.querySelector(".next");

  function showSlide(index) {
    slides.forEach((slide, i) => {
      slide.classList.remove("active");
      if (i === index) {
        slide.classList.add("active");
      }
    });
  }

  function nextSlide() {
    slideIndex = (slideIndex + 1) % slides.length;
    showSlide(slideIndex);
  }

  function prevSlide() {
    slideIndex = (slideIndex - 1 + slides.length) % slides.length;
    showSlide(slideIndex);
  }

  // Auto-slide every 5 seconds
  let slideInterval = setInterval(nextSlide, 5000);

  // Manual control for slider
  next.addEventListener("click", function() {
    nextSlide();
    clearInterval(slideInterval);
    slideInterval = setInterval(nextSlide, 5000);
  });

  prev.addEventListener("click", function() {
    prevSlide();
    clearInterval(slideInterval);
    slideInterval = setInterval(nextSlide, 5000);
  });

  // Scroll To Top Button functionality
  const scrollToTopBtn = document.getElementById("scrollToTop");
  window.addEventListener("scroll", function() {
    if (window.scrollY > 300) {
      scrollToTopBtn.style.display = "block";
    } else {
      scrollToTopBtn.style.display = "none";
    }
  });

  scrollToTopBtn.addEventListener("click", function() {
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  });

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
});

