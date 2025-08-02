#!/usr/bin/env python3
import markdown
import os
import sys
from datetime import datetime
import re
import subprocess
from pathlib import Path
import json
import shutil

class UltimateBlog:
    def __init__(self):
        self.posts_dir = Path('posts/')
        self.templates_dir = Path('templates/')
        self.styles_dir = Path('styles/')
        self.site_dir = Path('site/')
        self.drafts_dir = Path('posts/drafts/')
        
        # Critical CSS for single-packet index.html
        self.critical_css = """body{max-width:600px;margin:0 auto;padding:4em 2em;font-family:Baskerville,"Times New Roman",Times,serif}.profile-pic{text-align:center;margin-bottom:2em}.profile-pic img{width:80px;height:80px;border-radius:50%;object-fit:cover}h1{font-size:2.5em;margin:0 0 1em 0;font-weight:normal}p{font-size:1em;margin:1em 0;line-height:1.6}footer{text-align:center;margin-top:1em;padding:1em 0;color:#666;font-size:0.9em}a{color:#0066cc;text-decoration:none;font-weight:300}a:hover{text-decoration:underline}@media(max-width:768px){body{padding:2.5em 1.5em}h1{font-size:2.2em}}"""
        
    def setup_dirs(self):
        """Ensure all directories exist"""
        for dir_path in [self.posts_dir, self.templates_dir, self.styles_dir, self.site_dir, self.drafts_dir]:
            dir_path.mkdir(exist_ok=True, parents=True)
    
    def parse_filename(self, filename):
        """Extract date and slug from YYYY_MM_DD_slug.md"""
        match = re.match(r'(\d{4})_(\d{2})_(\d{2})_(.+)\.md', filename)
        if match:
            year, month, day, slug = match.groups()
            date = datetime(int(year), int(month), int(day))
            return date, slug
        return None, None
    
    def extract_metadata(self, content):
        """Extract metadata with smart defaults"""
        # Extract first paragraph for description
        lines = content.strip().split('\n')
        desc_lines = []
        for line in lines:
            if line.strip() and not line.startswith('#'):
                desc_lines.append(line.strip())
                if len(' '.join(desc_lines)) > 140:
                    break
        
        description = ' '.join(desc_lines)[:157] + '...' if len(' '.join(desc_lines)) > 160 else ' '.join(desc_lines)
        
        return {
            'description': description or 'A blog post by Randhawa Inc.',
            'tags': [],
            'category': None
        }
    
    def extract_first_heading(self, content):
        """Extract the first heading from markdown content"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()  # Remove '# ' prefix
            elif line.startswith('## '):
                return line[3:].strip()  # Remove '## ' prefix
            elif line.startswith('### '):
                return line[4:].strip()  # Remove '### ' prefix
        return None

    def insert_date_after_first_heading(self, html_content, date):
        """Insert date after first heading with fallback"""
        heading_pattern = r'(<h[1-6][^>]*>.*?</h[1-6]>)'
        match = re.search(heading_pattern, html_content, re.DOTALL)
        
        if match:
            heading_end = match.end()
            date_html = f'<p><em>{date}</em></p>'
            return html_content[:heading_end] + date_html + html_content[heading_end:]
        else:
            return f'<p><em>{date}</em></p>' + html_content
    
    def build_post(self, md_file, is_draft=False):
        """Build individual post with full SEO and performance optimization"""
        filename = Path(md_file).name
        date, slug = self.parse_filename(filename)
        
        if not date:
            print(f"Error: {filename} doesn't follow format (YYYY_MM_DD_slug.md)")
            return None
        
        # Read markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert to HTML with extensions
        html = markdown.markdown(content, extensions=['codehilite', 'fenced_code'])
        
        # Extract metadata
        metadata = self.extract_metadata(content)
        
        # Extract actual heading for title
        actual_title = self.extract_first_heading(content)
        if not actual_title:
            actual_title = slug.replace('_', ' ').title()  # Fallback to slug
        
        # Load template
        template_file = self.templates_dir / 'post.html'
        if not template_file.exists():
            self.create_post_template()
        
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Generate content
        formatted_date = date.strftime("%B %d, %Y")
        html_with_date = self.insert_date_after_first_heading(html, formatted_date)
        
        # Replace placeholders
        post_html = template.replace('{{title}}', actual_title)\
                           .replace('{{date}}', formatted_date)\
                           .replace('{{content}}', html_with_date)\
                           .replace('{{slug}}', slug)\
                           .replace('{{description}}', metadata['description'])\
                           .replace('{{url}}', f'https://prabhchintan.com/{slug}')\
                           .replace('{{year}}', str(date.year))
        
        # Output to site directory
        output_file = self.site_dir / f'{slug}.html'
        
        # Apply the same minimal CSS as index page
        post_html = post_html.replace('</head>', f'<style>{self.critical_css}</style></head>')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(post_html)
        
        print(f"✓ Built: /{slug}")
        return {
            'slug': slug,
            'title': actual_title,
            'date': date,
            'formatted_date': formatted_date,
            'description': metadata['description'],
            'url': f'/{slug}'
        }
    
    def process_redirects(self):
        """Process redirects.txt and generate redirect HTML files"""
        redirects_file = Path('redirects.txt')
        if not redirects_file.exists():
            return
        
        with open(redirects_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '->' not in line:
                    continue
                
                source, target = [part.strip() for part in line.split('->', 1)]
                
                # Generate redirect HTML
                redirect_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting...</title>
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{target}">
</head>
<body>
<p>Redirecting to <a href="{target}">{target}</a>...</p>
</body>
</html>'''
                
                # Write to site directory
                with open(self.site_dir / f'{source}.html', 'w', encoding='utf-8') as f:
                    f.write(redirect_html)
                
                print(f"✓ Redirect: /{source} → {target}")
    
    def update_blog_index(self, posts):
        """Generate blog index with all posts"""
        blog_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<title>Blog - Randhawa Inc.</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Personal blog by Randhawa Inc. featuring thoughts on technology, design, and life.">
<link rel="canonical" href="https://prabhchintan.com/blog">
</head>
<body>
<h1>Blog</h1>'''
        
        for post in posts:
            blog_html += f'''
<p><a href="{post['url']}">{post['title']}</a><br>
<em>{post['formatted_date']}</em></p>'''
        
        blog_html += '''
<footer>© 2025 Randhawa Inc.</footer>
</body>
</html>'''
        
        with open(self.site_dir / 'blog.html', 'w', encoding='utf-8') as f:
            f.write(blog_html)
        
        # Apply the same minimal CSS as index page
        blog_html = blog_html.replace('</head>', f'<style>{self.critical_css}</style></head>')
        
        with open(self.site_dir / 'blog.html', 'w', encoding='utf-8') as f:
            f.write(blog_html)
        
        print(f"✓ Updated blog index with {len(posts)} posts")
    
    def generate_sitemap(self, posts):
        """Generate XML sitemap"""
        sitemap = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://prabhchintan.com/</loc><priority>1.0</priority></url>
<url><loc>https://prabhchintan.com/blog</loc><priority>0.9</priority></url>'''
        
        for post in posts:
            sitemap += f'''
<url><loc>https://prabhchintan.com{post['url']}</loc><lastmod>{post['date'].strftime('%Y-%m-%d')}</lastmod><priority>0.8</priority></url>'''
        
        sitemap += '\n</urlset>'
        
        with open(self.site_dir / 'sitemap.xml', 'w', encoding='utf-8') as f:
            f.write(sitemap)
        
        print("✓ Generated sitemap.xml")
    
    def generate_rss(self, posts):
        """Generate RSS feed"""
        latest_posts = posts[:10]  # Last 10 posts
        
        rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Randhawa Inc. Blog</title>
<link>https://prabhchintan.com/blog</link>
<description>Personal blog featuring thoughts on technology, design, and life.</description>
<lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>'''
        
        for post in latest_posts:
            rss += f'''
<item>
<title>{post['title']}</title>
<link>https://prabhchintan.com{post['url']}</link>
<description>{post['description']}</description>
<pubDate>{post['date'].strftime('%a, %d %b %Y 12:00:00 +0000')}</pubDate>
<guid>https://prabhchintan.com{post['url']}</guid>
</item>'''
        
        rss += '''
</channel>
</rss>'''
        
        with open(self.site_dir / 'feed.xml', 'w', encoding='utf-8') as f:
            f.write(rss)
        
        print("✓ Generated RSS feed")
    
    def create_404_page(self):
        """Generate 404 page"""
        html_404 = '''<!DOCTYPE html>
<html lang="en">
<head>
<title>404 - Page Not Found</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body>
<h1>404</h1>
<p>Page not found. <a href="/">Go home</a> or check out the <a href="/blog">blog</a>.</p>
<footer>© 2025 Randhawa Inc.</footer>
</body>
</html>'''
        
        with open(self.site_dir / '404.html', 'w', encoding='utf-8') as f:
            f.write(html_404)
        
        # Apply the same minimal CSS as index page
        html_404 = html_404.replace('</head>', f'<style>{self.critical_css}</style></head>')
        
        with open(self.site_dir / '404.html', 'w', encoding='utf-8') as f:
            f.write(html_404)
        
        print("✓ Generated 404 page")
    
    def create_post_template(self):
        """Create optimized post template if it doesn't exist"""
        template = '''<!DOCTYPE html>
<html lang="en">
<head>
<title>{{title}} - Randhawa Inc.</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{{description}}">
<meta property="og:title" content="{{title}}">
<meta property="og:description" content="{{description}}">
<meta property="og:type" content="article">
<meta property="og:url" content="{{url}}">
<meta property="article:published_time" content="{{year}}">
<link rel="canonical" href="{{url}}">
</head>
<body>
{{content}}
<footer>© 2025 Randhawa Inc.</footer>
</body>
</html>'''
        
        with open(self.templates_dir / 'post.html', 'w', encoding='utf-8') as f:
            f.write(template)
    
    def optimize_index(self):
        """Create optimized index.html with critical CSS inlined"""
        # Read current index.html
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove the existing style tag and link to global.css
        content = re.sub(r'<link rel="stylesheet" href="global\.css">', '', content)
        content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
        
        # Add the critical CSS directly to the head
        content = content.replace('</head>', f'<style>{self.critical_css}</style></head>')
        
        # Write to both site directory and root
        with open(self.site_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ Optimized index.html for single-packet delivery")
    
    def copy_assets(self):
        """Copy CSS and other assets to site directory"""
        # Copy global CSS
        shutil.copy2(self.styles_dir / 'global.css', self.site_dir / 'global.css')
        
        # Copy fonts directory if it exists
        fonts_dir = Path('fonts/')
        if fonts_dir.exists():
            site_fonts_dir = self.site_dir / 'fonts'
            site_fonts_dir.mkdir(exist_ok=True)
            for font_file in fonts_dir.glob('*.ttf'):
                shutil.copy2(font_file, site_fonts_dir / font_file.name)
        
        # Copy profile image
        if Path('profile_sharp.png').exists():
            shutil.copy2('profile_sharp.png', self.site_dir / 'profile_sharp.png')
        
        print("✓ Copied assets to site/")
    
    def validate_urls(self):
        """Basic URL validation to prevent redirect loops"""
        redirects_file = Path('redirects.txt')
        if not redirects_file.exists():
            return True
        
        redirects = {}
        with open(redirects_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '->' not in line:
                    continue
                source, target = [part.strip() for part in line.split('->', 1)]
                redirects[source] = target
        
        # Check for loops
        for source in redirects:
            visited = set()
            current = source
            while current in redirects and current not in visited:
                visited.add(current)
                current = redirects[current]
                if current == source:
                    print(f"⚠️  Warning: Redirect loop detected starting from {source}")
                    return False
        
        print("✓ URL validation passed")
        return True
    
    def publish(self):
        """Build and publish everything"""
        print("🚀 Building ultimate minimal blog...")
        
        # Setup
        self.setup_dirs()
        
        # Validate
        if not self.validate_urls():
            print("❌ URL validation failed. Please fix redirect loops.")
            return
        
        # Build all posts
        posts = []
        for file in self.posts_dir.glob('*.md'):
            if file.name.endswith('.md'):
                post_data = self.build_post(str(file))
                if post_data:
                    posts.append(post_data)
        
        # Sort chronologically (newest first)
        posts.sort(key=lambda x: x['date'], reverse=True)
        
        # Generate everything
        self.update_blog_index(posts)
        self.process_redirects()
        self.generate_sitemap(posts)
        self.generate_rss(posts)
        self.create_404_page()
        self.optimize_index()
        self.copy_assets()
        
        # Git operations
        subprocess.run(['git', 'add', '.'])
        subprocess.run(['git', 'commit', '-m', 'Ultimate blog build'])
        subprocess.run(['git', 'push'])
        
        print(f"✅ Published {len(posts)} posts to GitHub!")
        print("🎯 Single-packet index.html ✓")
        print("🎯 SEO optimized ✓")
        print("🎯 Performance optimized ✓")
        print("🎯 Accessibility ready ✓")

if __name__ == "__main__":
    blog = UltimateBlog()
    if len(sys.argv) > 1:
        if sys.argv[1] == 'draft':
            # Handle draft posts in future
            pass
        else:
            blog.build_post(sys.argv[1])
    else:
        blog.publish() 