#!/bin/bash

# Portfolio Deployment Script for GitHub Pages
# This script prepares and deploys the portfolio to GitHub Pages

set -e  # Exit on any error

echo "🚀 Starting portfolio deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "index.html" ]; then
    print_error "index.html not found. Please run this script from the portfolio root directory."
    exit 1
fi

print_status "Checking project structure..."

# Verify required files exist
required_files=(
    "index.html"
    "blog.html"
    "404.html"
    "assets/css/styles.css"
    "assets/css/navbar.css"
    "assets/css/blog-styles.css"
    "assets/css/lightbox.css"
    "assets/js/script.js"
    "assets/js/navbar.js"
    "assets/js/blog.js"
    "assets/js/lightbox.js"
    "components/navbar.html"
    "data/publications.json"
    "data/blog_posts.json"
    "CNAME"
    ".gitignore"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file missing: $file"
        exit 1
    fi
done

print_success "All required files found!"

# Check if Python is available for publication updates
if command -v python3 &> /dev/null; then
    print_status "Python found. Checking for publication updates..."
    
    if [ -f "scripts/update_publications.py" ]; then
        print_status "Updating publications from Google Scholar..."
        cd scripts
        python3 update_publications.py --auto || print_warning "Publication update failed, continuing with existing data"
        cd ..
    fi
else
    print_warning "Python not found. Skipping publication updates."
fi

# Check for Git repository
if [ ! -d ".git" ]; then
    print_error "Git repository not found. Please initialize Git first:"
    echo "  git init"
    echo "  git add ."
    echo "  git commit -m 'Initial commit'"
    exit 1
fi

# Check current branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
    print_warning "You're not on main/master branch. Current branch: $current_branch"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_warning "You have uncommitted changes:"
    git status --short
    
    read -p "Commit changes before deploying? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_warning "Deploying with uncommitted changes..."
    else
        print_status "Committing changes..."
        git add .
        git commit -m "Auto-commit before deployment $(date)"
    fi
fi

# Check remote repository
if ! git remote get-url origin &> /dev/null; then
    print_error "No remote repository configured. Please add your GitHub repository:"
    echo "  git remote add origin https://github.com/yourusername/officialarijit.github.io.git"
    exit 1
fi

print_status "Pushing to GitHub..."

# Push to GitHub
if git push origin "$current_branch"; then
    print_success "Successfully pushed to GitHub!"
else
    print_error "Failed to push to GitHub. Please check your credentials and try again."
    exit 1
fi

# Check if GitHub Pages is enabled
print_status "Checking GitHub Pages status..."
print_warning "Please ensure GitHub Pages is enabled in your repository settings:"
echo "  1. Go to your repository on GitHub"
echo "  2. Click Settings > Pages"
echo "  3. Set Source to 'Deploy from a branch'"
echo "  4. Select 'gh-pages' branch (or 'main' if using GitHub Actions)"
echo "  5. Click Save"

# Wait for deployment
print_status "Waiting for GitHub Pages deployment..."
print_warning "Deployment can take 5-10 minutes. You can check the status at:"
echo "  https://github.com/yourusername/officialarijit.github.io/actions"

# Check if we can detect the deployment
sleep 30
print_status "Checking if site is live..."

# Try to detect if the site is live (this is a basic check)
if curl -s -o /dev/null -w "%{http_code}" "https://officialarijit.github.io" | grep -q "200\|404"; then
    print_success "Site appears to be accessible!"
    echo "🌐 Your portfolio should be available at: https://officialarijit.github.io"
else
    print_warning "Site might still be deploying. Please check manually in a few minutes."
fi

print_success "Deployment process completed!"
echo ""
echo "📋 Next steps:"
echo "  1. Check GitHub Actions for deployment status"
echo "  2. Visit https://officialarijit.github.io to verify your site"
echo "  3. Test all features: navigation, blog, contact form, lightbox"
echo "  4. Update your social media profiles with the new URL"
echo ""
echo "🔧 For future updates:"
echo "  - Make your changes"
echo "  - Run: git add . && git commit -m 'Your message' && git push"
echo "  - GitHub Actions will automatically deploy your changes"
echo ""
print_success "🎉 Your portfolio is ready for the world!"
