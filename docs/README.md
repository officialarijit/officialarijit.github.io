# Professional Portfolio Website

A modern, responsive portfolio website built with HTML, CSS, and JavaScript. This template is designed for professionals in tech, design, and creative fields to showcase their work, skills, and experience.

## 🚀 Features

- **Modern Design**: Clean, professional layout with smooth animations
- **Fully Responsive**: Works perfectly on desktop, tablet, and mobile devices
- **Interactive Elements**: Smooth scrolling, hover effects, and animations
- **Contact Form**: Functional contact form with validation
- **SEO Optimized**: Meta tags and semantic HTML structure
- **Fast Loading**: Optimized for performance
- **Accessible**: Built with accessibility in mind
- **Google Scholar Integration**: Automatic publication fetching and display
- **Modular Navigation**: Separate navbar component for easy maintenance
- **Image Lightbox**: Click any image to view it in full size with navigation

## 📁 File Structure

```
portfolio/
├── index.html              # Main HTML file
├── styles.css              # All CSS styles
├── navbar.css              # Navbar-specific styles
├── navbar.html             # Navbar component
├── navbar.js               # Navbar functionality
├── script.js               # JavaScript functionality
├── lightbox.css            # Image lightbox styles
├── lightbox.js             # Image lightbox functionality
├── test-lightbox.html      # Lightbox test page
├── publications.json       # Google Scholar publications data
├── update_publications.py  # Python script to update publications
├── photo.jpg               # Your profile photo
├── slide2.jpg              # About section image
├── slide3.jpg              # Project image
├── blog.html               # Blog page
├── blog-styles.css         # Blog-specific styles
├── blog.js                 # Blog functionality
├── manage_blog.py          # Blog management script
├── blog_posts.json         # Blog posts data
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 🔬 Google Scholar Integration

This portfolio includes automatic Google Scholar publication fetching and display, along with real-time citation metrics. Here's how to set it up:

### Automatic Setup

1. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the publications updater**:

   ```bash
   python update_publications.py
   ```

3. **Choose your option**:
   - **Option 1**: Try to fetch from Google Scholar (may not work due to anti-bot measures)
   - **Option 2**: Manual update (recommended)
   - **Option 3**: Fetch citation metrics only
   - **Option 4**: Exit

### Citation Metrics

The website automatically displays your Google Scholar citation metrics:

- **Total Citations**: Sum of all citations across your publications
- **h-index**: Measures both productivity and citation impact
- **i10-index**: Number of publications with at least 10 citations

These metrics are displayed in:

- **Hero Section**: As statistics cards
- **Dedicated Metrics Section**: Detailed breakdown with explanations
- **Dynamic Updates**: Automatically refreshed when you update the data

### Manual Update Process

The manual update option allows you to:

- **Add new publications**: Enter title, authors, journal, year, citations, and links
- **Update existing publications**: Modify any publication details
- **Remove publications**: Delete publications you no longer want to display
- **View all publications**: See your current publication list
- **Update citation metrics**: Manually update your citation statistics

### Publications JSON Structure

The `publications.json` file contains:

```json
{
  "profile": {
    "scholar_id": "4re6DoEAAAAJ",
    "scholar_url": "https://scholar.google.com/citations?hl=en&user=4re6DoEAAAAJ&view_op=list_works&sortby=pubdate",
    "last_updated": "2024-01-15"
  },
  "metrics": {
    "total_citations": 263,
    "h_index": 9,
    "i10_index": 9
  },
  "publications": [
    {
      "year": "2023",
      "title": "Your Publication Title",
      "authors": "Your Name, Co-author Name",
      "journal": "Journal Name",
      "citations": 15,
      "links": {
        "paper": "https://link-to-paper.com",
        "code": "https://github.com/your-repo"
      }
    }
  ]
}
```

### Updating Your Scholar ID

To use your own Google Scholar profile:

1. Find your Google Scholar ID in your profile URL
2. Update the `scholar_id` in `publications.json`
3. Update the `scholar_url` with your profile URL
4. Run the updater script to fetch your publications and metrics

### Troubleshooting

**If automatic fetching doesn't work:**

- Google Scholar has anti-bot measures that may block automated requests
- Use the manual update option instead
- The script will show a helpful error message with a direct link to your profile

**If publications don't display:**

- Check that `publications.json` exists and is valid JSON
- Ensure the file is in the same directory as `index.html`
- Check browser console for any JavaScript errors

**If citation metrics don't update:**

- Run the Python script and choose "Fetch citation metrics only"
- Clear browser cache and localStorage
- Verify your Google Scholar ID is correct

## 🖼️ Image Lightbox Feature

The portfolio includes a powerful image lightbox feature that allows visitors to click on any image to view it in full size with navigation controls.

### Features

- **Click to Zoom**: Click any image to open it in a full-screen lightbox
- **Navigation**: Use arrow keys, click navigation buttons, or swipe on mobile
- **Keyboard Controls**:
  - `Escape` to close
  - `Arrow Left/Right` to navigate
- **Touch Support**: Swipe left/right on mobile devices
- **Image Counter**: Shows current image position (e.g., "2 / 5")
- **Smooth Animations**: Elegant transitions and hover effects
- **Responsive Design**: Works perfectly on all screen sizes

### How It Works

The lightbox automatically makes all images on the page clickable, except for those explicitly excluded. When an image is clicked:

1. A full-screen overlay appears with a dark background
2. The image is displayed at its original size (or fit to screen)
3. Navigation controls appear if there are multiple images
4. The page scroll is disabled to prevent background scrolling

### Customization

#### Excluding Images

To prevent certain images from being clickable, add the `data-lightbox="false"` attribute:

```html
<img src="logo.png" alt="Logo" data-lightbox="false" />
```

Or use CSS classes to exclude multiple images:

```javascript
// In lightbox.js, the following images are automatically excluded:
window.imageLightbox.excludeImages(
  ".profile-photo, .nav-brand img, .social-links img, .footer img"
);
```

#### Including Specific Images Only

To make only specific images clickable:

```javascript
// Remove automatic image detection
// window.imageLightbox.makeImagesClickable();

// Add specific images
window.imageLightbox.addImages(".gallery img, .project-image img");
```

#### Customizing Styles

The lightbox styles are in `lightbox.css`. You can customize:

- **Background color**: Modify `.image-lightbox` background
- **Button styles**: Customize `.lightbox-close` and `.lightbox-nav`
- **Animation timing**: Adjust transition durations
- **Mobile responsiveness**: Modify media queries

### Testing

Use the included test page to verify the lightbox functionality:

1. Open `test-lightbox.html` in your browser
2. Click on different images to test the lightbox
3. Try keyboard navigation (arrow keys, escape)
4. Test on mobile devices for touch/swipe functionality

### Integration with Blog

The lightbox automatically works with blog posts:

- Images in blog content are clickable
- Lightbox reinitializes when new blog content is loaded
- Works seamlessly with the blog modal system

### Browser Compatibility

The lightbox works in all modern browsers:

- Chrome, Firefox, Safari, Edge
- Mobile browsers (iOS Safari, Chrome Mobile)
- Supports touch gestures and keyboard navigation

## 🎨 Customization Guide

### 1. Personal Information

Update the following in `index.html`:

#### Header Section

```html
<title>Your Name - Professional Portfolio</title>
<meta name="description" content="Your professional description" />
<meta name="keywords" content="your, keywords, here" />
```

#### Navigation

```html
<div class="nav-brand">
  <h1>Your Name</h1>
  <span class="nav-subtitle">Your Title</span>
</div>
```

#### Hero Section

```html
<h1 class="hero-title">Hi, I'm <span class="highlight">Your Name</span></h1>
<h2 class="hero-subtitle">Your Professional Title</h2>
<p class="hero-description">Your professional summary...</p>
```

#### Statistics

```html
<div class="hero-stats">
  <div class="stat">
    <span class="stat-number">5+</span>
    <span class="stat-label">Years Experience</span>
  </div>
  <!-- Add more stats as needed -->
</div>
```

### 2. About Section

Update the about content with your personal information:

```html
<div class="about-text">
  <p>Your professional story and background...</p>
  <p>Your expertise and focus areas...</p>

  <div class="about-highlights">
    <div class="highlight-item">
      <i class="fas fa-brain"></i>
      <span>Your Expertise 1</span>
    </div>
    <!-- Add more highlights -->
  </div>
</div>
```

### 3. Skills Section

Customize your skills by editing the skills grid:

```html
<div class="skill-category">
  <h3><i class="fas fa-code"></i> Programming Languages</h3>
  <div class="skill-list">
    <div class="skill-item">
      <div class="skill-info">
        <span class="skill-name">Python</span>
        <span class="skill-level">Advanced</span>
      </div>
      <div class="progress">
        <div class="progress-filled" style="width: 90%;"></div>
      </div>
    </div>
    <!-- Add more skills -->
  </div>
</div>
```

**Available Icons:**

- `fas fa-code` - Programming
- `fas fa-brain` - AI/ML
- `fas fa-chart-bar` - Data Science
- `fas fa-tools` - Tools & Technologies
- `fas fa-database` - Databases
- `fas fa-cloud` - Cloud Services

### 4. Experience Section

Update your work experience:

```html
<div class="timeline-item">
  <div class="timeline-marker"></div>
  <div class="timeline-content">
    <div class="timeline-header">
      <h3>Your Job Title</h3>
      <span class="company">Company Name</span>
      <span class="period">2023 - Present</span>
    </div>
    <p>Brief description of your role...</p>
    <ul>
      <li>Key achievement 1</li>
      <li>Key achievement 2</li>
      <li>Key achievement 3</li>
    </ul>
  </div>
</div>
```

### 5. Projects Section

Showcase your projects:

```html
<div class="project-card">
  <div class="project-image">
    <img src="project-image.jpg" alt="Project Name" />
    <div class="project-overlay">
      <div class="project-links">
        <a href="live-link" target="_blank"
          ><i class="fas fa-external-link-alt"></i
        ></a>
        <a href="github-link" target="_blank"><i class="fab fa-github"></i></a>
      </div>
    </div>
  </div>
  <div class="project-content">
    <h3>Project Name</h3>
    <p>Project description...</p>
    <div class="project-tech">
      <span class="tech-tag">Technology 1</span>
      <span class="tech-tag">Technology 2</span>
    </div>
  </div>
</div>
```

### 6. Education Section

Update your educational background:

```html
<div class="education-card">
  <div class="education-icon">
    <i class="fas fa-graduation-cap"></i>
  </div>
  <div class="education-content">
    <h3>Degree Name</h3>
    <span class="institution">University Name</span>
    <span class="period">2019 - 2021</span>
    <p>Additional details about your education...</p>
  </div>
</div>
```

### 7. Publications Section

The publications section is now automatically populated from your Google Scholar profile. To update:

1. Run `python update_publications.py`
2. Choose manual update
3. Add, edit, or remove publications as needed

### 8. Contact Information

Update your contact details:

```html
<div class="contact-item">
  <i class="fas fa-envelope"></i>
  <div>
    <h3>Email</h3>
    <p>your.email@example.com</p>
  </div>
</div>
```

### 9. Social Links

Update social media links in the hero section and footer:

```html
<div class="social-links">
  <a href="linkedin-url" target="_blank"><i class="fab fa-linkedin"></i></a>
  <a href="github-url" target="_blank"><i class="fab fa-github"></i></a>
  <a href="twitter-url" target="_blank"><i class="fab fa-twitter"></i></a>
</div>
```

## 🎨 Styling Customization

### Colors

Update the CSS variables in `styles.css`:

```css
:root {
  --primary-color: #2563eb; /* Main brand color */
  --primary-dark: #1d4ed8; /* Darker shade for hover */
  --secondary-color: #64748b; /* Secondary text color */
  --accent-color: #f59e0b; /* Accent color for highlights */
  --text-primary: #1e293b; /* Primary text color */
  --text-secondary: #64748b; /* Secondary text color */
  --bg-primary: #ffffff; /* Primary background */
  --bg-secondary: #f8fafc; /* Secondary background */
}
```

### Fonts

Change the font by updating the Google Fonts import:

```css
@import url("https://fonts.googleapis.com/css2?family=Your-Font:wght@300;400;500;600;700&display=swap");
```

Then update the font-family in the body:

```css
body {
  font-family: "Your-Font", sans-serif;
}
```

## 📱 Responsive Design

The website is fully responsive with breakpoints at:

- **Desktop**: 1024px and above
- **Tablet**: 768px - 1023px
- **Mobile**: Below 768px

## 🚀 Deployment

### GitHub Pages

1. Push your code to a GitHub repository
2. Go to Settings > Pages
3. Select your branch and save
4. Your site will be available at `https://username.github.io/repository-name`

### Netlify

1. Drag and drop your project folder to Netlify
2. Your site will be deployed instantly
3. You can connect your GitHub repository for automatic deployments

### Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in your project directory
3. Follow the prompts to deploy

## 🔧 Advanced Customization

### Adding New Sections

1. Add the HTML structure in `index.html`
2. Add corresponding styles in `styles.css`
3. Add any JavaScript functionality in `script.js`

### Custom Animations

Add custom CSS animations:

```css
@keyframes yourAnimation {
  from {
    /* initial state */
  }
  to {
    /* final state */
  }
}

.your-element {
  animation: yourAnimation 1s ease;
}
```

### Form Backend Integration

To connect the contact form to a backend:

1. Update the form action in `index.html`
2. Modify the form handling in `script.js`
3. Add your backend endpoint

## 📊 Performance Optimization

- Optimize images before uploading
- Use WebP format when possible
- Compress CSS and JavaScript files
- Enable gzip compression on your server

## 🔍 SEO Optimization

- Update meta tags with your information
- Add structured data for better search results
- Optimize image alt texts
- Use semantic HTML elements

## 🛠️ Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Internet Explorer 11+

## 📄 License

This template is free to use for personal and commercial projects.

## 🤝 Support

If you need help customizing this portfolio:

1. Check this README for common customization tasks
2. Review the code comments for guidance
3. Test changes in a local environment first

## 🎯 Quick Start

1. Download or clone this repository
2. Install Python dependencies: `pip install -r requirements.txt`
3. Update your publications: `python update_publications.py`
4. Open `index.html` in a text editor
5. Replace "Your Name" with your actual name
6. Update the content with your information
7. Customize colors and styling as needed
8. Deploy to your preferred hosting platform

## 📝 Blog System

This portfolio includes a comprehensive blog system with Markdown and LaTeX support, allowing you to share your thoughts on AI, ML, and technology topics.

### Features

- **Markdown Support**: Write posts using standard Markdown syntax
- **LaTeX Math Rendering**: Display mathematical equations beautifully
- **Category Filtering**: Organize posts by categories (ML, Data Science, AI Ethics, etc.)
- **Responsive Design**: Blog works perfectly on all devices
- **Search and Filter**: Easy navigation through posts
- **Modal Reading**: Clean, distraction-free reading experience
- **Auto-generated Excerpts**: Automatic post summaries
- **Tag System**: Automatic tag extraction from content

### Blog Management

The blog system includes a Python management script for easy post creation and editing:

#### Quick Start

1. **Create a new post**:

   ```bash
   python manage_blog.py create --title "Your Post Title" --category "machine-learning" --content-file "your_post.md"
   ```

2. **List all posts**:

   ```bash
   python manage_blog.py list
   ```

3. **Edit a post**:

   ```bash
   python manage_blog.py edit --post-id "post-1"
   ```

4. **Delete a post**:

   ```bash
   python manage_blog.py delete --post-id "post-1"
   ```

5. **Create a template**:

   ```bash
   python manage_blog.py template --template-file "new_post.md"
   ```

6. **Export to JavaScript**:
   ```bash
   python manage_blog.py export --output "blog_posts.js"
   ```

#### Writing Blog Posts

1. **Create a markdown template**:

   ```bash
   python manage_blog.py template
   ```

2. **Edit the template** (`new_post.md`):

   ````markdown
   # Your Blog Post Title

   Write your content here with full Markdown support.

   ## LaTeX Math Examples

   Inline math: $E = mc^2$

   Display math:
   $$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$

   ## Code Examples

   ```python
   def hello_world():
       print("Hello, World!")
   ```
   ````
