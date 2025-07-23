#!/usr/bin/env python3
import markdown
import os
import sys
from datetime import datetime
import re
import subprocess
from pathlib import Path

class SamuraiBlog:
    def __init__(self):
        self.posts_dir = Path('posts/')
        self.templates_dir = Path('templates/')
        
    def parse_filename(self, filename):
        # Extract date and slug from "2025_07_04_freedom.md"
        match = re.match(r'(\d{4})_(\d{2})_(\d{2})_(.+)\.md', filename)
        if match:
            year, month, day, slug = match.groups()
            date = datetime(int(year), int(month), int(day))
            return date, slug
        return None, None
    
    def extract_metadata(self, content):
        """Extract YAML front matter for future extensibility"""
        # For now, return defaults. Easy to add YAML parsing later.
        return {
            'description': content[:160] + '...' if len(content) > 160 else content,
            'tags': [],
            'category': None
        }
    
    def build_post(self, md_file):
        filename = Path(md_file).name
        date, slug = self.parse_filename(filename)
        
        if not date:
            print(f"Error: {filename} doesn't follow format (YYYY_MM_DD_slug.md)")
            return
        
        # Read markdown
        with open(md_file, 'r') as f:
            content = f.read()
        
        # Convert to HTML
        html = markdown.markdown(content)
        
        # Extract metadata
        metadata = self.extract_metadata(content)
        
        # Load template
        with open(self.templates_dir / 'post.html', 'r') as f:
            template = f.read()
        
        # Replace placeholders
        title = slug.replace('_', ' ').title()
        formatted_date = date.strftime("%B %d, %Y")
        
        post_html = template.replace('{{title}}', title)\
                           .replace('{{date}}', formatted_date)\
                           .replace('{{content}}', html)\
                           .replace('{{slug}}', slug)\
                           .replace('{{description}}', metadata['description'])
        
        # Output to root directory for slug-based URLs
        output_file = f'{slug}.html'
        with open(output_file, 'w') as f:
            f.write(post_html)
        
        print(f"✓ Built: /{slug}")
        return slug, title, formatted_date
    
    def update_blog_index(self):
        posts = []
        for file in self.posts_dir.glob('*.md'):
            if file.name.endswith('.md'):
                date, slug = self.parse_filename(file.name)
                if date:
                    title = slug.replace('_', ' ').title()
                    posts.append((date, title, f'{slug}.html'))
        
        # Sort chronologically (newest first)
        posts.sort(reverse=True)
        
        # Generate blog index
        blog_html = '''<!DOCTYPE html>
<html lang="en">
<head>
<title>Blog</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="global.css">
</head>
<body>
<h1>Blog</h1>'''
        
        for date, title, html_file in posts:
            blog_html += f'''
<p><a href="{html_file}">{title}</a><br>
<em>{date.strftime("%B %d, %Y")}</em></p>'''
        
        blog_html += '''
<footer>© 2024 Randhawa Inc.</footer>
</body>
</html>'''
        
        with open('blog.html', 'w') as f:
            f.write(blog_html)
        
        print(f"✓ Updated blog index with {len(posts)} posts")
    
    def publish(self):
        """One command to build and publish everything"""
        # Build all posts
        for file in self.posts_dir.glob('*.md'):
            self.build_post(str(file))
        
        # Update blog index
        self.update_blog_index()
        
        # Git operations
        subprocess.run(['git', 'add', '.'])
        subprocess.run(['git', 'commit', '-m', 'Auto-publish posts'])
        subprocess.run(['git', 'push'])
        
        print("✓ Published to GitHub!")

if __name__ == "__main__":
    blog = SamuraiBlog()
    if len(sys.argv) > 1:
        blog.build_post(sys.argv[1])
    else:
        blog.publish() 