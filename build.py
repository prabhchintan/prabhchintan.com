#!/usr/bin/env python3
import markdown
import sys
from datetime import datetime
import re
import subprocess
from pathlib import Path
import shutil
from urllib.parse import quote
import os

class UltimateBlog:
    def __init__(self):
        self.posts_dir = Path('posts/')
        self.pages_dir = Path('pages/')
        self.templates_dir = Path('templates/')
        self.site_dir = Path('site/')
        
        # Critical CSS - read from file
        try:
            with open(self.templates_dir / 'critical.css', 'r', encoding='utf-8') as f:
                self.critical_css = f.read().strip()
        except FileNotFoundError:
            print("Warning: templates/critical.css not found, using default")
            self.critical_css = "body{max-width:600px;margin:0 auto;padding:2em}"
        

        
    def setup_dirs(self):
        """Ensure all directories exist"""
        for dir_path in [self.posts_dir, self.pages_dir, self.templates_dir, self.site_dir]:
            dir_path.mkdir(exist_ok=True, parents=True)

    def clean_site_dir(self):
        """Remove and recreate site/ to prevent stale artifacts."""
        if self.site_dir.exists():
            shutil.rmtree(self.site_dir)
        self.site_dir.mkdir(exist_ok=True, parents=True)
    
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
            stripped = line.strip()
            # Skip headings, empty lines, and HTML blocks
            if stripped and not stripped.startswith('#') and not stripped.startswith('<'):
                desc_lines.append(stripped)
                if len(' '.join(desc_lines)) > 140:
                    break
        
        description = ' '.join(desc_lines)[:157] + '...' if len(' '.join(desc_lines)) > 160 else ' '.join(desc_lines)
        
        # Strip any remaining HTML tags from description
        description = re.sub(r'<[^>]+>', '', description).strip()
        
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
    
    # (Removed duplicate early build_post definition)
    
    def build_page(self, md_file):
        """Build standalone page (no date, no blog listing)"""
        filename = Path(md_file).name
        slug = filename.replace('.md', '')
        
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
        
        # Generate content (no date for pages)
        html_with_date = html  # Pages don't get dates
        
        # Replace placeholders
        page_html = template.replace('{{title}}', actual_title)\
                           .replace('{{date}}', '')\
                           .replace('{{content}}', html_with_date)\
                           .replace('{{slug}}', slug)\
                           .replace('{{description}}', metadata['description'])\
                           .replace('{{url}}', f'https://prabhchintan.com/{slug}')\
                           .replace('{{year}}', '')\
                           .replace('{{critical_css}}', self.critical_css)\
                           .replace('https://prabhchintan.com/profile.png', 'https://prabhchintan.com/profile.png')
        

        
        # Output to site directory
        output_file = self.site_dir / f'{slug}.html'
        
        # Apply universal footer
        page_html = self.apply_universal_footer(page_html)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(page_html)
        
        print(f"Built page: /{slug}")
        return {
            'slug': slug,
            'title': actual_title,
            'description': metadata['description'],
            'url': f'/{slug}'
        }
    
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
                           .replace('{{year}}', str(date.year))\
                           .replace('{{critical_css}}', self.critical_css)
        

        
        # Output to site directory
        output_file = self.site_dir / f'{slug}.html'
        
        # Apply universal footer
        post_html = self.apply_universal_footer(post_html)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(post_html)
        
        print(f"Built: /{slug}")
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

<!-- Social Media Meta Tags -->
<meta property="og:title" content="Redirecting...">
<meta property="og:description" content="Redirecting to {target}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://prabhchintan.com/{source}">
<meta property="og:site_name" content="prabhchintan.com">
<meta property="og:image" content="https://prabhchintan.com/profile.png">
<meta property="og:image:width" content="400">
<meta property="og:image:height" content="400">

<!-- Twitter Card Meta Tags -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Redirecting...">
<meta name="twitter:description" content="Redirecting to {target}">
<meta name="twitter:url" content="https://prabhchintan.com/{source}">
<meta name="twitter:image" content="https://prabhchintan.com/profile.png">

<!-- Canonical URL -->
<link rel="canonical" href="{target}">
</head>
<body>
<p>Redirecting to <a href="{target}">{target}</a>...</p>
</body>
</html>'''
                
                # Intentionally do not apply site footer to redirect pages
                
                # Write to site directory
                with open(self.site_dir / f'{source}.html', 'w', encoding='utf-8') as f:
                    f.write(redirect_html)
                
                print(f"Redirect: /{source} -> {target}")
    
    def update_blog_index(self, posts):
        """Generate blog index with all posts"""
        blog_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<title>Blog - Randhawa Inc.</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="favicon.ico">
<link rel="apple-touch-icon" href="favicon.svg">
<meta name="description" content="Personal blog by Randhawa Inc. featuring thoughts on technology, design, and life.">

<!-- Social Media Meta Tags -->
<meta property="og:title" content="Blog - Randhawa Inc.">
<meta property="og:description" content="Personal blog by Randhawa Inc. featuring thoughts on technology, design, and life.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://prabhchintan.com/blog">
<meta property="og:site_name" content="prabhchintan.com">
<meta property="og:image" content="https://prabhchintan.com/profile.png">
<meta property="og:image:width" content="400">
<meta property="og:image:height" content="400">

<!-- Twitter Card Meta Tags -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Blog - Randhawa Inc.">
<meta name="twitter:description" content="Personal blog by Randhawa Inc. featuring thoughts on technology, design, and life.">
<meta name="twitter:url" content="https://prabhchintan.com/blog">
<meta name="twitter:image" content="https://prabhchintan.com/profile.png">

<!-- Canonical URL -->
<link rel="canonical" href="https://prabhchintan.com/blog">
<link rel="alternate" type="application/rss+xml" title="RSS" href="/feed.xml">
<style>{self.critical_css}</style>
</head>
<body>
<h1>Blog</h1>'''
        
        for post in posts:
            blog_html += f'''
<p><a href="{post['url']}">{post['title']}</a><br>
<em>{post['formatted_date']}</em></p>'''
        
        blog_html += '''
</body>
</html>'''
        
        # Apply universal footer
        blog_html = self.apply_universal_footer(blog_html)
        
        with open(self.site_dir / 'blog.html', 'w', encoding='utf-8') as f:
            f.write(blog_html)
        
        print(f"Updated blog index with {len(posts)} posts")
    
    def generate_sitemap(self, posts, pages=None):
        """Generate XML sitemap"""
        sitemap = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://prabhchintan.com/</loc><priority>1.0</priority></url>
<url><loc>https://prabhchintan.com/blog</loc><priority>0.9</priority></url>
<url><loc>https://prabhchintan.com/certifications</loc><priority>0.8</priority></url>'''
        
        for post in posts:
            sitemap += f'''
<url><loc>https://prabhchintan.com{post['url']}</loc><lastmod>{post['date'].strftime('%Y-%m-%d')}</lastmod><priority>0.8</priority></url>'''
        
        # Add standalone pages to sitemap (excluding noindex pages)
        if pages:
            for page in pages:
                sitemap += f'''
<url><loc>https://prabhchintan.com{page['url']}</loc><priority>0.7</priority></url>'''
        
        sitemap += '\n</urlset>'
        
        with open(self.site_dir / 'sitemap.xml', 'w', encoding='utf-8') as f:
            f.write(sitemap)
        
        print("Generated sitemap.xml")
    
    def generate_rss(self, posts):
        """Generate RSS feed"""
        # Filter out hidden posts
        visible_posts = posts[:10]
        
        rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>Randhawa Inc. Blog</title>
<link>https://prabhchintan.com/blog</link>
<atom:link href="https://prabhchintan.com/feed.xml" rel="self" type="application/rss+xml"/>
<description>Personal blog featuring thoughts on technology, design, and life.</description>
<lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>'''
        
        for post in visible_posts:
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
        
        print("Generated RSS feed")
    
    def create_404_page(self):
        """Generate 404 page"""
        html_404 = f'''<!DOCTYPE html>
<html lang="en">
<head>
<title>404 - Page Not Found</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="favicon.ico">
<link rel="apple-touch-icon" href="favicon.svg">

<!-- Social Media Meta Tags -->
<meta property="og:title" content="404 - Page Not Found">
<meta property="og:description" content="The page you're looking for doesn't exist.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://prabhchintan.com/404">
<meta property="og:site_name" content="prabhchintan.com">
<meta property="og:image" content="https://prabhchintan.com/profile.png">
<meta property="og:image:width" content="400">
<meta property="og:image:height" content="400">

<!-- Twitter Card Meta Tags -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="404 - Page Not Found">
<meta name="twitter:description" content="The page you're looking for doesn't exist.">
<meta name="twitter:url" content="https://prabhchintan.com/404">
<meta name="twitter:image" content="https://prabhchintan.com/profile.png">

<!-- Canonical URL -->
<link rel="canonical" href="https://prabhchintan.com/404">
<style>{self.critical_css}</style>
</head>
<body>
<h1>404</h1>
<p>Page not found. <a href="/">Go home</a> or check out the <a href="/blog">blog</a>.</p>
</body>
</html>'''
        
        # Apply universal footer
        html_404 = self.apply_universal_footer(html_404)
        
        with open(self.site_dir / '404.html', 'w', encoding='utf-8') as f:
            f.write(html_404)
        
        print("Generated 404 page")
    
    def create_post_ui(self):
        """Generate the post UI for mobile blogging"""
        app_file = self.templates_dir / 'post_app.html'
        if not app_file.exists():
            return
            
        with open(app_file, 'r', encoding='utf-8') as f:
            app_html = f.read()
            
        # Replace the comment placeholder with a full style block
        css_block = f'<style>{self.critical_css}</style>'
        app_html = app_html.replace('<!-- CRITICAL_CSS_PLACEHOLDER -->', css_block)
        
        # Apply universal footer
        app_html = self.apply_universal_footer(app_html)
        
        with open(self.site_dir / 'post.html', 'w', encoding='utf-8') as f:
            f.write(app_html)
            
        print("Generated post UI at /post.html")

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
<p><a href="/">← Home</a></p>
</body>
</html>'''
        
        with open(self.templates_dir / 'post.html', 'w', encoding='utf-8') as f:
            f.write(template)
    
    def optimize_index(self):
        """Create optimized index.html with critical CSS inlined and universal footer"""
        # Read current index.html
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove the existing style tag and link to global.css
        content = re.sub(r'<link rel="stylesheet" href="global\.css">', '', content)
        content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
        
        # Add the critical CSS directly to the head
        content = content.replace('</head>', f'<style>{self.critical_css}</style></head>')
        
        # Ensure universal footer is always present
        universal_footer = '<footer>Randhawa Inc. 1309 Coffeen Ave Ste 1386 Sheridan, WY</footer>'
        
        # Replace any existing footer with the universal one
        content = re.sub(r'<footer>.*?</footer>', universal_footer, content, flags=re.DOTALL)
        
        # If no footer exists, add it before closing body tag
        if universal_footer not in content:
            content = content.replace('</body>', f'{universal_footer}\n</body>')
        
        # Write to site directory only (do not mutate source index.html)
        with open(self.site_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Optimized index.html for single-packet delivery with universal footer")
    
    def apply_universal_footer(self, html_content):
        """Apply universal footer to any HTML content"""
        universal_footer = '<footer>Randhawa Inc. 1309 Coffeen Ave Ste 1386 Sheridan, WY</footer>'
        
        # Replace any existing footer with the universal one
        html_content = re.sub(r'<footer>.*?</footer>', universal_footer, html_content, flags=re.DOTALL)
        
        # If no footer exists, add it before closing body tag
        if universal_footer not in html_content:
            html_content = html_content.replace('</body>', f'{universal_footer}\n</body>')
        
        return html_content
    
    def generate_robots_txt(self):
        """Generate robots.txt allowing all crawlers with sitemap reference"""
        robots = '''User-agent: *
Allow: /

Sitemap: https://prabhchintan.com/sitemap.xml
'''
        with open(self.site_dir / 'robots.txt', 'w', encoding='utf-8') as f:
            f.write(robots)
        print("Generated robots.txt")
    
    
    def copy_assets(self):
        """Copy only necessary assets to site directory"""
        # Copy profile image
        if Path('profile.png').exists():
            shutil.copy2('profile.png', self.site_dir / 'profile.png')
        
        # Copy favicon files
        if Path('favicon.svg').exists():
            shutil.copy2('favicon.svg', self.site_dir / 'favicon.svg')
        if Path('favicon.ico').exists():
            shutil.copy2('favicon.ico', self.site_dir / 'favicon.ico')
        
        # Copy certifications directory if it exists
        certs_dir = Path('certifications/')
        if certs_dir.exists():
            site_certs_dir = self.site_dir / 'certifications'
            site_certs_dir.mkdir(exist_ok=True)
            for cert_file in certs_dir.glob('*'):
                if cert_file.is_file():
                    shutil.copy2(cert_file, site_certs_dir / cert_file.name)
        
        print("Copied assets to site/")
    
    def generate_certifications_page(self):
        """Generate certifications page with static list organized by organization"""
        certs_dir = Path('certifications/')
        certs_mapping_file = Path('certifications.txt')
        
        # Load certifications mapping
        certs_mapping = {}
        if certs_mapping_file.exists():
            with open(certs_mapping_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or '->' not in line:
                        continue
                    parts = [part.strip() for part in line.split('->')]
                    if len(parts) >= 3:
                        filename, display_name, organization = parts[0], parts[1], parts[2]
                        certs_mapping[filename] = {
                            'display_name': display_name,
                            'organization': organization
                        }
        
        # Collect certifications from files
        certifications = []
        if certs_dir.exists():
            for cert_file in certs_dir.glob('*'):
                if cert_file.is_file() and cert_file.suffix.lower() in ['.pdf', '.jpg', '.jpeg', '.png']:
                    filename = cert_file.name
                    
                    # Use mapping if available, otherwise default
                    if filename in certs_mapping:
                        display_name = certs_mapping[filename]['display_name']
                        organization = certs_mapping[filename]['organization']
                    else:
                        # Default: convert filename to readable name
                        display_name = filename.replace(cert_file.suffix, '').replace('_', ' ').replace('-', ' ').title()
                        organization = 'Misc'
                    
                    certifications.append({
                        'filename': filename,
                        'display_name': display_name,
                        'organization': organization
                    })
        
        # Group by organization
        org_groups = {}
        for cert in certifications:
            org = cert['organization']
            if org not in org_groups:
                org_groups[org] = []
            org_groups[org].append(cert)
        
        # Sort organizations alphabetically
        sorted_orgs = sorted(org_groups.keys())
        
        # Generate HTML
        certs_html = ''
        for org in sorted_orgs:
            certs_html += f'<h2>{org}</h2>\n'
            # Sort certifications within each org by display name length
            org_certs = sorted(org_groups[org], key=lambda x: len(x['display_name']))
            for cert in org_certs:
                # URL-encode the filename for the href (handle all special characters)
                url_filename = quote(cert["filename"], safe='')
                certs_html += f'<p><a href="/certifications/{url_filename}" target="_blank">{cert["display_name"]}</a></p>\n'
            certs_html += '\n'
        
        if not certifications:
            certs_html = '<p>No certifications found. Add files to the certifications/ directory.</p>'
        
        # Full page HTML
        page_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<title>Certifications - Randhawa Inc.</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="favicon.ico">
<link rel="apple-touch-icon" href="favicon.svg">
<meta name="description" content="Professional certifications and qualifications of Prabhchintan Randhawa">

<!-- Social Media Meta Tags -->
<meta property="og:title" content="Certifications - Randhawa Inc.">
<meta property="og:description" content="Professional certifications and qualifications of Prabhchintan Randhawa">
<meta property="og:type" content="website">
<meta property="og:url" content="https://prabhchintan.com/certifications">
<meta property="og:site_name" content="prabhchintan.com">
<meta property="og:image" content="https://prabhchintan.com/profile.png">
<meta property="og:image:width" content="400">
<meta property="og:image:height" content="400">

<!-- Twitter Card Meta Tags -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Certifications - Randhawa Inc.">
<meta name="twitter:description" content="Professional certifications and qualifications of Prabhchintan Randhawa">
<meta name="twitter:url" content="https://prabhchintan.com/certifications">
<meta name="twitter:image" content="https://prabhchintan.com/profile.png">

<!-- Canonical URL -->
<link rel="canonical" href="https://prabhchintan.com/certifications">
<style>{self.critical_css}</style>
</head>
<body>
<h1>Certifications</h1>

{certs_html}

<p><a href="/">← Back to home</a></p>

</body>
</html>'''
        
        # Apply universal footer
        page_html = self.apply_universal_footer(page_html)
        
        with open(self.site_dir / 'certifications.html', 'w', encoding='utf-8') as f:
            f.write(page_html)
    
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
        
        print("URL validation passed")
        return True
    
    def publish(self):
        """Build and publish everything"""
        print("Building site...")
        
        # Setup (and clean site dir)
        self.setup_dirs()
        self.clean_site_dir()

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
        
        # Build all standalone pages
        pages = []
        for file in self.pages_dir.glob('*.md'):
            if file.name.endswith('.md'):
                page_data = self.build_page(str(file))
                if page_data:
                    pages.append(page_data)
        
        # Sort chronologically (newest first)
        posts.sort(key=lambda x: x['date'], reverse=True)
        
        # Generate everything
        self.update_blog_index(posts)
        self.process_redirects()
        self.generate_sitemap(posts, pages)
        self.generate_rss(posts)
        self.generate_robots_txt()
        self.create_404_page()
        self.optimize_index()
        self.copy_assets()
        
        # Generate certifications page
        self.generate_certifications_page()
        print("Generated certifications page")
        
        self.create_post_ui()
        
        # Git operations (optional; commit only if there are changes)
        subprocess.run(['git', 'add', '.'])
        status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if status.stdout.strip():
            commit_message = os.environ.get('CURSOR_CONTEXT', '').strip()
            if not commit_message:
                commit_message = os.environ.get('CI_COMMIT_MESSAGE', '').strip()
            if not commit_message:
                # Fallback to a concise default
                commit_message = f"Site update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_message])
            # Only push if not explicitly disabled
            if os.environ.get('SKIP_GIT_PUSH', '0') not in ('1', 'true', 'yes'):
                try:
                    # Check if we are behind origin/main (usually because of a previous GitHub Action run)
                    subprocess.run(['git', 'fetch'], check=False)
                    behind_status = subprocess.run(['git', 'status', '-sb'], capture_output=True, text=True)
                    if 'behind' in behind_status.stdout:
                        print("Local branch is behind remote. Syncing with origin/main (favoring local build)...")
                        # Use 'ours' strategy to avoid conflicts on auto-generated site/ files
                        subprocess.run(['git', 'merge', 'origin/main', '--no-edit', '-s', 'recursive', '-X', 'ours'], check=True)
                        
                    subprocess.run(['git', 'push'], check=True)
                    print("Published changes to GitHub")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Git push failed with return code {e.returncode}")
                    print("Please check your git configuration and connection.")
        else:
            print("No changes to publish")

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