# Arijit Nandi - Professional Portfolio

A modern, responsive portfolio website showcasing AI/ML research, projects, and professional experience with automated citation updates.

## 🌐 Live Site

**Visit the live portfolio:** [https://officialarijit.github.io](https://officialarijit.github.io)

## 🆕 Recent Updates

### **Latest Features Added:**
- 🎯 **Citation Metrics Display**: Real-time publication metrics (citations, h-index, i10-index) in About section
- 🌍 **Flag Counter**: Visitor statistics from different countries
- 📧 **Enhanced Contact Options**: Direct email link alongside contact form
- 🤖 **Automated Publications Update**: GitHub Actions workflow for automatic citation updates
- ✨ **Improved UI/UX**: Enhanced styling and animations throughout

## 📁 Project Structure

```
portfolio/
├── 📄 HTML Files
│   ├── index.html              # Main portfolio page
│   ├── blog.html               # Blog page
│   └── 404.html                # Error page
├── 🎨 Assets
│   ├── css/
│   │   ├── styles.css          # Main styles (enhanced with metrics display)
│   │   ├── navbar.css          # Navbar styles
│   │   ├── blog-styles.css     # Blog styles
│   │   └── lightbox.css        # Lightbox styles
│   ├── js/
│   │   ├── script.js           # Main functionality
│   │   ├── navbar.js           # Navbar functionality
│   │   ├── blog.js             # Blog functionality
│   │   ├── publications.js     # Publications display
│   │   └── lightbox.js         # Lightbox functionality
│   └── images/
│       ├── photo.jpg           # Profile photo
│       ├── slide2.jpg          # About section image
│       └── slide3.jpg          # Project image
├── 🧩 Components
│   └── navbar.html             # Navbar component
├── 📊 Data
│   ├── blog_posts.json         # Blog posts data (auto-generated)
│   └── publications.json       # Publications data (auto-updated)
├── 📝 Blogs
│   ├── blog1.md               # Blog post 1
│   ├── blog2.md               # Blog post 2
│   └── ...                    # More blog posts
├── 🐍 Scripts
│   ├── process_blogs.py       # Process Markdown blogs to JSON
│   ├── add_blog_post.py       # Create new blog post template
│   ├── update_publications.py # Google Scholar integration (enhanced)
│   └── test_publications.py   # Testing script
├── 📚 Documentation
│   ├── README.md               # Detailed documentation
│   ├── DEPLOYMENT.md           # Deployment guide
│   └── GITHUB_ACTIONS.md       # GitHub Actions documentation
├── ⚙️ Configuration
│   ├── CNAME                   # Domain configuration
│   ├── deploy.sh               # Deployment script
│   ├── requirements.txt        # Python dependencies
│   └── .gitignore              # Git ignore rules
└── 🔄 GitHub Actions
    └── .github/workflows/
        ├── deploy.yml          # Automatic deployment workflow
        └── update-publications.yml # Automated publications update
```

## 🎯 Features

- **Modern Design**: Clean, professional layout with smooth animations
- **Fully Responsive**: Works perfectly on desktop, tablet, and mobile devices
- **Interactive Elements**: Smooth scrolling, hover effects, and animations
- **Image Lightbox**: Click any image to view it in full size with navigation
- **Blog System**: Markdown files with LaTeX math support, automatic processing
- **Google Scholar Integration**: Automatic publication fetching and display
- **Citation Metrics Display**: Real-time publication statistics in About section
- **Flag Counter**: Visitor statistics from different countries
- **Enhanced Contact Options**: Direct email link and contact form
- **Automated Updates**: GitHub Actions workflow for citation updates
- **Modular Navigation**: Separate navbar component for easy maintenance
- **Contact Form**: Functional contact form with validation
- **SEO Optimized**: Meta tags and semantic HTML structure
- **GitHub Pages Ready**: Optimized for hosting on GitHub Pages

## 🚀 Quick Deployment

### Option 1: Automatic Deployment (Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial portfolio deployment"
   git push origin main
   ```

2. **Enable GitHub Pages**:
   - Go to your repository settings
   - Navigate to Pages section
   - Set source to "GitHub Actions"
   - Your site will be automatically deployed

3. **Enable Automated Updates**:
   - Go to Settings → Actions → General
   - Enable "Read and write permissions"
   - The publications will update automatically daily

### Option 2: Manual Deployment

1. **Run the deployment script**:
   ```bash
   ./deploy.sh
   ```

2. **Follow the prompts** to complete deployment

## 🤖 Automated Publications Update

### **GitHub Actions Workflow**

The portfolio now includes an automated workflow that:

- **Daily Updates**: Runs every day at 6 AM UTC
- **Fetches Citations**: Gets latest publication data from Google Scholar
- **Updates Metrics**: Refreshes citation counts, h-index, and i10-index
- **Auto-Deploys**: Commits changes and updates the live website

### **Setup Instructions**

1. **Enable Actions**: Go to your repository's Actions tab
2. **Configure Permissions**: Settings → Actions → General → "Read and write permissions"
3. **Update Scholar ID**: Edit `scripts/update_publications.py` with your Google Scholar ID
4. **Test**: Run the workflow manually from Actions tab

### **Manual Execution**

```bash
# Interactive mode
python scripts/update_publications.py

# Automated mode (same as GitHub Actions)
python scripts/update_publications.py --auto-update
```

📖 **Full Documentation**: See [docs/GITHUB_ACTIONS.md](docs/GITHUB_ACTIONS.md) for detailed setup instructions.

## 🛠️ Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/officialarijit/officialarijit.github.io.git
cd officialarijit.github.io
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Update Publications
```bash
cd scripts
python update_publications.py
```

### 4. Manage Blog Posts
```bash
# Create a new blog post
python scripts/add_blog_post.py

# Process all blog posts to update the website
python scripts/process_blogs.py
```

### 5. Test Locally
```bash
python -m http.server 8000
# Visit http://localhost:8000
```

## 📊 Citation Metrics Display

### **New Features in About Section**

The About section now includes:

- **Publication Metrics**: Total citations, h-index, and i10-index
- **Real-time Updates**: Automatically updated via GitHub Actions
- **Beautiful Design**: Gradient background with hover animations
- **Responsive Layout**: Works perfectly on all devices
- **Flag Counter**: Visitor statistics from different countries

### **Metrics Display Features**

- ✅ **Automatic Updates**: Fetched from Google Scholar daily
- ✅ **Visual Appeal**: Gradient design with shimmer effects
- ✅ **Interactive**: Hover animations and scaling effects
- ✅ **Mobile Friendly**: Responsive design for all screen sizes
- ✅ **Dark Mode Support**: Consistent styling in both themes

## 📝 Blog System

### Creating New Blog Posts

The blog system uses Markdown files with YAML frontmatter for metadata. Each week, you can easily add new blog posts:

1. **Create a new blog post**:
   ```bash
   python scripts/add_blog_post.py
   ```

2. **Edit the generated Markdown file** in the `blogs/` folder

3. **Process all blogs** to update the website:
   ```bash
   python scripts/process_blogs.py
   ```

### Blog Post Features

- **Markdown Support**: Write content in Markdown format
- **LaTeX Math**: Include mathematical formulas with `$...$` (inline) and `$$...$$` (display)
- **Code Syntax Highlighting**: Automatic syntax highlighting for code blocks
- **Frontmatter Metadata**: Title, subtitle, author, date, category, tags, and excerpt
- **Automatic Processing**: Converts Markdown to HTML and generates JSON data

### Blog Post Structure

Each blog post (`blog1.md`, `blog2.md`, etc.) contains:

```yaml
---
title: "Your Blog Title"
subtitle: "Optional subtitle"
author: "Arijit Nandi"
date: "2024-01-15"
read_time: "8 min read"
category: "Machine Learning"
tags: ["ML", "AI", "Python"]
image: "assets/images/your-image.jpg"
excerpt: "Brief description of the blog post"
---

# Your Blog Title

Your content here with Markdown formatting...
```

## 📖 Documentation

- **[Detailed Documentation](docs/README.md)**: Comprehensive guide with customization instructions
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Step-by-step deployment instructions
- **[GitHub Actions Guide](docs/GITHUB_ACTIONS.md)**: Automated publications update setup

## 🎨 Customization

### Personal Information
Update these files with your information:
- `index.html` - Main content and personal details
- `components/navbar.html` - Navigation and branding
- `data/publications.json` - Your publications and metrics (auto-updated)
- `blogs/*.md` - Your blog posts (Markdown files)

### Styling
- `assets/css/styles.css` - Main styles and layout (includes metrics display)
- `assets/css/navbar.css` - Navigation styling
- `assets/css/blog-styles.css` - Blog-specific styles
- `assets/css/lightbox.css` - Image lightbox styling

### Functionality
- `assets/js/script.js` - Main JavaScript functionality
- `assets/js/navbar.js` - Navigation behavior
- `assets/js/blog.js` - Blog system
- `assets/js/publications.js` - Publications display
- `assets/js/lightbox.js` - Image lightbox

## 🔧 Development Workflow

### File Organization
The project follows a logical directory structure:
- **HTML files** in root for easy access
- **Assets** organized by type (CSS, JS, images)
- **Components** for reusable elements
- **Data** for JSON files and content
- **Blogs** for Markdown blog posts
- **Scripts** for Python utilities
- **Documentation** for guides and READMEs
- **GitHub Actions** for automated workflows

### Adding New Features
1. **CSS**: Add to appropriate file in `assets/css/`
2. **JavaScript**: Add to appropriate file in `assets/js/`
3. **Images**: Place in `assets/images/`
4. **Data**: Update files in `data/`
5. **Components**: Add to `components/`
6. **Blog Posts**: Add Markdown files to `blogs/`
7. **Automation**: Add workflows to `.github/workflows/`

### Git Workflow
```bash
# Make your changes
git add .
git commit -m "Description of changes"
git push origin main
# GitHub Actions will automatically deploy and update publications
```

## 🌐 Hosting

### GitHub Pages
- **URL**: https://officialarijit.github.io
- **Automatic Deployment**: Enabled via GitHub Actions
- **Automated Updates**: Publications update daily via GitHub Actions
- **Custom Domain**: Configured via CNAME file

### Performance Optimizations
- ✅ Minified CSS and JavaScript
- ✅ Optimized images
- ✅ Efficient asset loading
- ✅ SEO best practices
- ✅ Mobile-first responsive design
- ✅ Automated content updates

## 📊 Analytics & SEO

The portfolio includes:
- **Meta tags** for social media sharing
- **Structured data** for search engines
- **Sitemap** for better indexing
- **Performance optimizations** for fast loading
- **Flag counter** for visitor analytics
- **Citation metrics** for academic impact

## 🔒 Security

- **HTTPS**: Enabled by GitHub Pages
- **Content Security Policy**: Configured for security
- **No sensitive data**: All content is public-facing
- **Rate limiting**: Respectful API calls to Google Scholar

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Contact

- **Portfolio**: [https://officialarijit.github.io](https://officialarijit.github.io)
- **Email**: ai4arijit@gmail.com
- **LinkedIn**: [Your LinkedIn]
- **GitHub**: [Your GitHub]

---

**Built with ❤️ using HTML, CSS, JavaScript, and Python**

**Hosted on GitHub Pages with Automated Updates** 🌐🤖