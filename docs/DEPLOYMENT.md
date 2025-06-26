# GitHub Pages Deployment Guide

This guide will help you deploy your portfolio website to GitHub Pages.

## 🚀 Quick Start

### 1. Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right → "New repository"
3. Name your repository: `yourusername.github.io` (replace `yourusername` with your actual GitHub username)
4. Make it **Public** (required for free GitHub Pages)
5. Don't initialize with README (we already have one)
6. Click "Create repository"

### 2. Upload Your Files

#### Option A: Using Git (Recommended)

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial portfolio website"

# Add remote repository
git remote add origin https://github.com/yourusername/yourusername.github.io.git

# Push to GitHub
git branch -M main
git push -u origin main
```

#### Option B: Using GitHub Web Interface

1. Go to your repository on GitHub
2. Click "uploading an existing file"
3. Drag and drop all your portfolio files
4. Commit the changes

### 3. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click "Settings" tab
3. Scroll down to "Pages" section (in the left sidebar)
4. Under "Source", select "Deploy from a branch"
5. Under "Branch", select "main" and "/ (root)"
6. Click "Save"

### 4. Wait for Deployment

- GitHub will automatically build and deploy your site
- You'll see a green checkmark when deployment is complete
- Your site will be available at: `https://yourusername.github.io`

## 🔧 Configuration Files

### GitHub Actions Workflow (`.github/workflows/deploy.yml`)

This file automatically:

- Tests your portfolio when you push changes
- Validates HTML and file structure
- Deploys to GitHub Pages
- Runs on every push to main branch

### Custom 404 Page (`404.html`)

- Provides a user-friendly error page
- Includes navigation to popular sections
- Matches your portfolio's design

### CNAME File

For custom domain support:

1. Edit the `CNAME` file
2. Add your domain (e.g., `yourname.com`)
3. Configure DNS settings with your domain provider

## 📝 Customization

### Update Repository Name

If your repository is not named `yourusername.github.io`:

1. Update the deployment workflow in `.github/workflows/deploy.yml` if needed
2. Update any hardcoded URLs in your HTML files

### Update Personal Information

1. Edit `index.html` with your information
2. Update `publications.json` with your Google Scholar data
3. Replace placeholder images with your own

## 🔄 Updating Your Site

### Automatic Updates

1. Make changes to your files locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update portfolio"
   git push
   ```
3. GitHub Actions will automatically test and deploy

### Manual Updates

1. Go to your repository on GitHub
2. Edit files directly in the web interface
3. Commit changes
4. Site will automatically redeploy

## 🧪 Testing Before Deployment

Run the test suite locally:

```bash
# Test your portfolio
python test_publications.py

# Start local server
python -m http.server 8000
# Then visit http://localhost:8000
```

## 📊 Monitoring Deployment

### Check Deployment Status

1. Go to your repository on GitHub
2. Click "Actions" tab
3. View the latest workflow run
4. Green checkmark = successful deployment
5. Red X = deployment failed (check logs)

### Common Issues

**Build Fails:**

- Check that all required files exist
- Verify JSON syntax in `publications.json`
- Ensure no syntax errors in HTML/CSS/JS

**Site Not Loading:**

- Wait 5-10 minutes for deployment
- Check repository settings → Pages
- Verify repository is public

**Custom Domain Issues:**

- Check DNS settings
- Wait up to 24 hours for DNS propagation
- Verify CNAME file content

## 🌐 Custom Domain Setup

### 1. Purchase Domain

Buy a domain from providers like:

- Namecheap
- GoDaddy
- Google Domains
- Cloudflare

### 2. Configure DNS

Add these DNS records:

```
Type: CNAME
Name: www (or @)
Value: yourusername.github.io
```

### 3. Update CNAME File

Edit the `CNAME` file in your repository:

```
yourdomain.com
```

### 4. Enable HTTPS

GitHub Pages automatically provides SSL certificates for custom domains.

## 📱 Mobile Optimization

Your portfolio is already mobile-responsive, but test on:

- iPhone Safari
- Android Chrome
- iPad Safari
- Various screen sizes

## 🔍 SEO Optimization

### Meta Tags

Your `index.html` already includes:

- Title and description
- Open Graph tags
- Twitter Card tags
- Canonical URL

### Sitemap

GitHub Pages automatically generates a sitemap at:
`https://yourusername.github.io/sitemap.xml`

### Google Analytics

To add Google Analytics:

1. Get your tracking ID from Google Analytics
2. Add this to your `index.html` head section:
   ```html
   <!-- Google Analytics -->
   <script
     async
     src="https://www.googletagmanager.com/gtag/js?id=GA_TRACKING_ID"
   ></script>
   <script>
     window.dataLayer = window.dataLayer || [];
     function gtag() {
       dataLayer.push(arguments);
     }
     gtag("js", new Date());
     gtag("config", "GA_TRACKING_ID");
   </script>
   ```

## 🚀 Performance Tips

### Optimize Images

- Use WebP format when possible
- Compress images before uploading
- Use appropriate sizes for different devices

### Minify Assets

Use the VS Code tasks to minify:

```bash
# Minify CSS and JS
Ctrl+Shift+P → "Tasks: Run Task" → "Build for Production"
```

### Enable Compression

GitHub Pages automatically enables gzip compression.

## 📞 Support

If you encounter issues:

1. Check GitHub Pages documentation
2. Review GitHub Actions logs
3. Test locally first
4. Verify all files are committed

## 🎉 Success!

Once deployed, your portfolio will be available at:
`https://yourusername.github.io`

Share this URL with:

- Potential employers
- Research collaborators
- Professional networks
- Social media profiles

---

**Remember:** GitHub Pages is free for public repositories. For private repositories, you'll need GitHub Pro or higher.
