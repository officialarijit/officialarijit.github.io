#!/usr/bin/env python3
"""
Blog Processing Script
Scans the blogs folder for Markdown files and generates blog data for the website.
Supports frontmatter metadata, LaTeX math, and code syntax highlighting.
"""

import os
import json
import re
# import yaml
from datetime import datetime
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
import html

class BlogProcessor:
    def __init__(self, blogs_dir="blogs", output_file="data/blog_posts.json"):
        self.blogs_dir = Path(blogs_dir)
        self.output_file = Path(output_file)
        self.md = markdown.Markdown(extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.tables',
            'markdown.extensions.toc',
            'markdown.extensions.attr_list'
        ])
        
    def extract_frontmatter(self, content):
        """Extract YAML frontmatter from markdown content."""
        if not content.startswith('---'):
            return {}, content
            
        try:
            # Find the end of frontmatter
            end_index = content.find('---', 3)
            if end_index == -1:
                return {}, content
                
            frontmatter_text = content[3:end_index].strip()
            body = content[end_index + 3:].strip()
            
            # Simple YAML-like parser for basic key-value pairs
            frontmatter = {}
            for line in frontmatter_text.split('\n'):
                line = line.strip()
                if ':' in line and not line.startswith('#'):
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    
                    # Handle list values (tags)
                    if key == 'tags' and value.startswith('[') and value.endswith(']'):
                        # Simple list parsing
                        tags_str = value[1:-1]
                        tags = [tag.strip().strip('"').strip("'") for tag in tags_str.split(',')]
                        frontmatter[key] = tags
                    else:
                        frontmatter[key] = value
            
            return frontmatter, body
        except Exception as e:
            print(f"Error parsing frontmatter: {e}")
            return {}, content
    
    def process_math(self, content):
        """Process LaTeX math expressions."""
        print(f"Processing math in content (length: {len(content)})")
        
        # Protect LaTeX expressions from markdown processing
        # Replace $$...$$ with a placeholder
        math_blocks = []
        def replace_math_block(match):
            math_blocks.append(match.group(0))
            return f"MATH_BLOCK_{len(math_blocks)-1}"
        
        content = re.sub(r'\$\$(.*?)\$\$', replace_math_block, content, flags=re.DOTALL)
        print(f"Found {len(math_blocks)} math blocks: {math_blocks}")
        
        # Replace $...$ with a placeholder (but be careful with inline math)
        math_inline = []
        def replace_math_inline(match):
            math_inline.append(match.group(0))
            return f"MATH_INLINE_{len(math_inline)-1}"
        
        # Only replace $...$ that are not already part of $$...$$
        content = re.sub(r'(?<!\$)\$([^$\n]+?)\$(?!\$)', replace_math_inline, content)
        print(f"Found {len(math_inline)} inline math: {math_inline}")
        
        # Convert markdown to HTML
        html_content = self.md.convert(content)
        
        # Restore math blocks
        for i, math in enumerate(math_blocks):
            html_content = html_content.replace(f"MATH_BLOCK_{i}", math)
        
        # Restore math inline
        for i, math in enumerate(math_inline):
            html_content = html_content.replace(f"MATH_INLINE_{i}", math)
        
        print(f"Final HTML content length: {len(html_content)}")
        if math_blocks or math_inline:
            print("LaTeX expressions preserved in HTML")
        
        return html_content
    
    def extract_excerpt(self, content, max_length=200):
        """Extract excerpt from content."""
        # Remove HTML tags for excerpt
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        
        # Find first paragraph or sentence
        sentences = text.split('.')
        excerpt = sentences[0] + '.' if sentences else text[:max_length]
        
        if len(excerpt) > max_length:
            excerpt = excerpt[:max_length].rsplit(' ', 1)[0] + '...'
            
        return excerpt
    
    def generate_slug(self, title):
        """Generate URL-friendly slug from title."""
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def process_blog_file(self, file_path):
        """Process a single blog markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter and body
            frontmatter, body = self.extract_frontmatter(content)
            
            # Generate filename-based metadata if not in frontmatter
            filename = file_path.stem
            if not frontmatter.get('title'):
                frontmatter['title'] = filename.replace('_', ' ').title()
            
            if not frontmatter.get('date'):
                # Try to extract date from filename (e.g., blog1.md -> 2024-01-15)
                frontmatter['date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Process math expressions
            body = self.process_math(body)
            
            # Convert markdown to HTML
            html_content = self.md.convert(body)
            
            # Extract excerpt
            excerpt = frontmatter.get('excerpt') or self.extract_excerpt(html_content)
            
            # Generate slug
            slug = frontmatter.get('slug') or self.generate_slug(frontmatter['title'])
            
            # Create blog post object
            blog_post = {
                'id': filename,
                'slug': slug,
                'title': frontmatter['title'],
                'subtitle': frontmatter.get('subtitle', ''),
                'author': frontmatter.get('author', 'Arijit Ghosh'),
                'date': frontmatter['date'],
                'read_time': frontmatter.get('read_time', '5 min read'),
                'category': frontmatter.get('category', 'General'),
                'tags': frontmatter.get('tags', []),
                'image': frontmatter.get('image', 'assets/images/default-blog.jpg'),
                'excerpt': excerpt,
                'content': html_content,
                'filename': filename
            }
            
            return blog_post
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
    
    def process_all_blogs(self):
        """Process all markdown files in the blogs directory."""
        if not self.blogs_dir.exists():
            print(f"Blogs directory {self.blogs_dir} does not exist.")
            return []
        
        blog_posts = []
        
        # Find all markdown files
        md_files = list(self.blogs_dir.glob('*.md'))
        md_files.sort(key=lambda x: x.name)  # Sort by filename
        
        for md_file in md_files:
            print(f"Processing: {md_file.name}")
            blog_post = self.process_blog_file(md_file)
            if blog_post:
                blog_posts.append(blog_post)
        
        # Sort by date (newest first)
        blog_posts.sort(key=lambda x: x['date'], reverse=True)
        
        return blog_posts
    
    def save_blog_data(self, blog_posts):
        """Save blog posts data to JSON file."""
        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        blog_data = {
            'last_updated': datetime.now().isoformat(),
            'total_posts': len(blog_posts),
            'posts': blog_posts
        }
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(blog_data, f, indent=2, ensure_ascii=False)
        
        print(f"Blog data saved to {self.output_file}")
        print(f"Processed {len(blog_posts)} blog posts")
    
    def run(self):
        """Main execution method."""
        print("Starting blog processing...")
        blog_posts = self.process_all_blogs()
        self.save_blog_data(blog_posts)
        print("Blog processing completed!")

def main():
    processor = BlogProcessor()
    processor.run()

if __name__ == "__main__":
    main() 