#!/usr/bin/env python3
import markdown
import logging
import sys
from datetime import datetime
import re
import subprocess
from pathlib import Path
import shutil
from urllib.parse import quote
from html import escape as html_escape
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
log = logging.getLogger(__name__)


class RichEmbedProcessor:
    """Process rich embeds for YouTube, X/Twitter, Wikipedia, etc."""

    @staticmethod
    def process(content):
        """Convert URLs to rich embeds"""
        # Fix old YouTube iframes first
        content = RichEmbedProcessor._fix_old_youtube_iframes(content)
        # YouTube embed from URLs
        content = RichEmbedProcessor._youtube_embed(content)
        # X/Twitter embed
        content = RichEmbedProcessor._twitter_embed(content)
        # Generic auto-linking (but preserve markdown links)
        content = RichEmbedProcessor._auto_link(content)
        return content

    @staticmethod
    def _fix_old_youtube_iframes(text):
        """Fix old YouTube iframe embeds that are missing required attributes"""
        # Match old iframe embeds and extract video ID
        old_iframe_pattern = r'<div[^>]*><iframe src="https://www\.youtube\.com/embed/([a-zA-Z0-9_-]{11})"[^>]*></iframe></div>'

        def replace_old_iframe(match):
            video_id = match.group(1)
            # Return properly formatted iframe using YouTube's standard embed format
            return f'<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;border-radius:8px;margin:2em 0"><iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;border:0"></iframe></div>'

        return re.sub(old_iframe_pattern, replace_old_iframe, text)

    @staticmethod
    def _youtube_embed(text):
        """Convert YouTube URLs to responsive embeds using YouTube's standard format"""
        pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?[^\s]*v=|youtu\.be\/)([a-zA-Z0-9_-]{11})[^\s]*'

        def replace(match):
            video_id = match.group(1)
            # Using YouTube's official embed code format
            return f'\n\n<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;border-radius:8px;margin:2em 0"><iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen style="position:absolute;top:0;left:0;width:100%;height:100%;border:0"></iframe></div>\n\n'

        return re.sub(pattern, replace, text)

    @staticmethod
    def _twitter_embed(text):
        """Convert X/Twitter URLs to embeds"""
        pattern = r'https?://(?:twitter\.com|x\.com)/([^/]+)/status/(\d+)'

        def replace(match):
            username, tweet_id = match.groups()
            # Simple iframe embed for now
            return f'\n\n<blockquote class="twitter-tweet"><a href="https://x.com/{username}/status/{tweet_id}">View on X</a></blockquote>\n\n'

        return re.sub(pattern, replace, text)

    @staticmethod
    def _auto_link(text):
        """Auto-link URLs that aren't already in markdown or HTML"""
        # Skip URLs already in markdown links or HTML attributes
        lines = text.split('\n')
        result = []
        for line in lines:
            # Skip if line contains markdown link or HTML attribute
            if '](http' in line or 'src="http' in line or 'href="http' in line:
                result.append(line)
            else:
                # Auto-link bare URLs
                line = re.sub(r'(https?:\/\/[^\s]+)', r'[\1](\1)', line)
                result.append(line)
        return '\n'.join(result)


class BlogBuilder:
    def __init__(self):
        self.posts_dir = Path('posts/')
        self.pages_dir = Path('pages/')
        self.media_dir = Path('media/')
        self.templates_dir = Path('templates/')
        self.site_dir = Path('site/')

        # Load critical CSS
        try:
            with open(self.templates_dir / 'critical.css', 'r', encoding='utf-8') as f:
                self.critical_css = f.read().strip()
        except FileNotFoundError:
            log.warning("critical.css not found, using fallback")
            self.critical_css = "body{max-width:600px;margin:0 auto;padding:2em}"

        # Load comments template
        try:
            with open(self.templates_dir / 'comments.html', 'r', encoding='utf-8') as f:
                self.comments_template = f.read().strip()
        except FileNotFoundError:
            log.warning("comments.html not found, comments disabled")
            self.comments_template = ''

        self.slug_registry = {}  # Track slugs to detect collisions

        # Color palette shared between blog and index drop cap JS
        self._drop_cap_colors = """[
            'rgba(0,102,204,0.45)',   'rgba(20,80,180,0.48)',   'rgba(40,100,200,0.42)',
            'rgba(10,70,160,0.5)',    'rgba(30,90,190,0.44)',   'rgba(50,110,210,0.46)',
            'rgba(153,50,50,0.48)',   'rgba(170,60,60,0.45)',   'rgba(130,40,55,0.5)',
            'rgba(185,45,45,0.42)',   'rgba(145,55,65,0.47)',   'rgba(160,40,50,0.44)',
            'rgba(60,120,80,0.45)',   'rgba(45,130,70,0.42)',   'rgba(70,140,90,0.48)',
            'rgba(55,145,75,0.46)',   'rgba(40,110,65,0.5)',    'rgba(75,135,85,0.44)',
            'rgba(140,90,40,0.48)',   'rgba(160,100,30,0.45)',  'rgba(120,80,50,0.5)',
            'rgba(175,115,35,0.42)',  'rgba(150,95,45,0.46)',   'rgba(135,85,55,0.44)',
            'rgba(100,60,140,0.45)',  'rgba(120,70,160,0.42)',  'rgba(90,50,130,0.48)',
            'rgba(110,65,150,0.46)',  'rgba(85,55,125,0.5)',    'rgba(130,75,170,0.44)',
            'rgba(50,120,130,0.45)',  'rgba(40,130,140,0.42)',  'rgba(60,110,120,0.48)',
            'rgba(45,140,135,0.46)',  'rgba(55,125,145,0.5)',   'rgba(65,115,125,0.44)',
            'rgba(180,70,90,0.42)',   'rgba(160,55,80,0.45)',   'rgba(140,65,100,0.48)',
            'rgba(170,60,85,0.46)',   'rgba(150,50,75,0.5)',    'rgba(190,75,95,0.44)',
            'rgba(80,100,60,0.45)',   'rgba(90,110,50,0.42)',   'rgba(70,90,70,0.48)',
            'rgba(85,105,55,0.46)',   'rgba(75,95,65,0.5)',     'rgba(95,115,45,0.44)',
            'rgba(110,80,110,0.45)',  'rgba(130,70,90,0.42)',   'rgba(95,85,120,0.48)',
            'rgba(120,75,105,0.46)',  'rgba(105,90,115,0.5)',   'rgba(115,80,100,0.44)',
            'rgba(170,110,50,0.42)',  'rgba(180,120,60,0.48)',  'rgba(165,105,40,0.46)',
            'rgba(60,90,150,0.45)',   'rgba(70,80,140,0.42)',   'rgba(50,100,160,0.48)',
            'rgba(140,50,70,0.45)',   'rgba(90,130,100,0.42)',  'rgba(110,100,140,0.45)'
        ]"""

        # Blog drop cap JS — per-font scale/shift from actual glyph metrics
        # Each entry: [fontName, scale, shiftEm]
        # scale adjusts font-size so all glyphs appear visually similar
        # shift adjusts vertical position for fonts that overflow or sit too high/low
        self.drop_cap_js = f"""<script>
    (function(){{
        var d=document.querySelector('.drop-cap');
        if(!d)return;
        d.classList.add('drop-cap-loading');
        var colors={self._drop_cap_colors};
        var fonts=[
            ['AcornInitials',     1.0,   0],
            ['AngloText',         1.0,   0],
            ['ApexLake',          0.80,  0.05],
            ['CamelotCaps',       1.0,   0],
            ['DecoratedRoman',    1.0,   0],
            ['EileenCaps',        0.92, -0.02],
            ['ElzevierCaps',      1.03,  0],
            ['FleurCornerCaps',   1.0,   0],
            ['FlowerInitials',    1.19, -0.03],
            ['GothicFlourish',    1.0,   0],
            ['GoudyInitialen',    1.0,   0],
            ['PaulusFranck',      1.0,   0],
            ['Romantik',          0.93,  0.02],
            ['TypographerCaps',   0.79,  0.03],
            ['VictorianInitials', 0.96,  0],
            ['WoodcutInitials',   0.82,  0.06],
            ['ZallmanCaps',       1.04,  0]
        ];
        var pick=fonts[Math.floor(Math.random()*fonts.length)];
        d.style.setProperty('--drop-cap-color',colors[Math.floor(Math.random()*colors.length)]);
        d.style.setProperty('--drop-cap-font',pick[0]);
        d.style.setProperty('--drop-cap-scale',pick[1]);
        if(pick[2])d.style.setProperty('--drop-cap-shift',pick[2]+'em');
        document.fonts.load('1em '+pick[0]).then(function(){{
            d.classList.remove('drop-cap-loading');
        }}).catch(function(){{
            d.classList.remove('drop-cap-loading');
        }});
    }})();
    </script>"""

        # Index uses the same full drop cap JS (fonts + colors + metrics)
        self.drop_cap_js_index = self.drop_cap_js

    def setup_dirs(self):
        """Ensure all directories exist"""
        for dir_path in [self.posts_dir, self.pages_dir, self.media_dir,
                         self.templates_dir, self.site_dir]:
            dir_path.mkdir(exist_ok=True, parents=True)

    def clean_site_dir(self):
        """Remove and recreate site/ directory"""
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

    def check_slug_collision(self, slug, filename):
        """Detect and warn about slug collisions"""
        if slug in self.slug_registry:
            log.error(f"Slug collision: '{slug}' used in both {self.slug_registry[slug]} and {filename}")
            log.error("Build aborted. Please rename one of the files.")
            sys.exit(1)
        self.slug_registry[slug] = filename

    def extract_metadata(self, content):
        """Extract metadata from content"""
        lines = content.strip().split('\n')
        desc_lines = []

        for line in lines:
            stripped = line.strip()
            # Skip headings, HTML, blockquotes, and blank lines
            if stripped and not stripped.startswith('#') and not stripped.startswith('<') and not stripped.startswith('>'):
                desc_lines.append(stripped)
                if len(' '.join(desc_lines)) > 140:
                    break

        description = ' '.join(desc_lines)[:157] + '...' if len(' '.join(desc_lines)) > 160 else ' '.join(desc_lines)
        # Strip HTML tags
        description = re.sub(r'<[^>]+>', '', description)
        # Strip markdown formatting: bold, italic, links, images
        description = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', description)  # images
        description = re.sub(r'\[([^\]]*)\]\([^)]+\)', r'\1', description)   # links
        description = re.sub(r'\*\*(.+?)\*\*', r'\1', description)           # bold
        description = re.sub(r'\*(.+?)\*', r'\1', description)               # italic
        description = re.sub(r'_(.+?)_', r'\1', description)                 # italic alt
        description = re.sub(r'`(.+?)`', r'\1', description)                 # inline code
        description = description.strip()

        return description or 'A blog post by Randhawa'

    def extract_title(self, content):
        """Extract first heading from markdown"""
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
            elif line.startswith('## '):
                return line[3:].strip()
            elif line.startswith('### '):
                return line[4:].strip()
        return None

    def insert_date_after_heading(self, html, date):
        """Insert date after first heading"""
        pattern = r'(<h[1-6][^>]*>.*?</h[1-6]>)'
        match = re.search(pattern, html, re.DOTALL)

        if match:
            heading_end = match.end()
            date_html = f'<p class="post-date"><em>{date}</em></p>'
            return html[:heading_end] + date_html + html[heading_end:]
        else:
            return f'<p class="post-date"><em>{date}</em></p>' + html

    def add_drop_cap(self, html):
        """Add drop-cap class to the first qualifying body paragraph.

        Rules:
        - Must be after the post-date element
        - Skip paragraphs that are entirely italic/emphasis (subtitles)
        - Skip paragraphs shorter than 150 characters of text
        - Only apply to the first qualifying paragraph
        """
        # Find the post-date marker
        date_match = re.search(r'<p class="post-date">.*?</p>', html)
        if not date_match:
            return html

        search_start = date_match.end()

        # Find all <p> tags after the date
        for p_match in re.finditer(r'<p>(.*?)</p>', html[search_start:], re.DOTALL):
            inner = p_match.group(1).strip()

            # Skip if entirely wrapped in <em> or <strong> (subtitle pattern)
            if re.match(r'^<em>.*</em>$', inner, re.DOTALL):
                continue
            if re.match(r'^<strong>.*</strong>$', inner, re.DOTALL):
                continue

            # Get plain text length (strip HTML tags)
            plain_text = re.sub(r'<[^>]+>', '', inner).strip()
            if len(plain_text) < 150:
                continue

            # This paragraph qualifies — add the drop-cap class
            abs_start = search_start + p_match.start()
            html = html[:abs_start] + '<p class="drop-cap">' + html[abs_start + 3:]
            break

        return html

    def build_post(self, md_file):
        """Build individual blog post"""
        filename = Path(md_file).name
        date, slug = self.parse_filename(filename)

        if not date:
            log.error(f"{filename} doesn't follow YYYY_MM_DD_slug.md format")
            return None

        # Check for slug collision
        self.check_slug_collision(slug, filename)

        # Read and process markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Process rich embeds
        content = RichEmbedProcessor.process(content)

        # Convert to HTML
        html = markdown.markdown(content, extensions=['codehilite', 'fenced_code'])

        # Extract metadata
        description = self.extract_metadata(content)
        title = self.extract_title(content) or slug.replace('_', ' ').title()

        # Load template
        with open(self.templates_dir / 'post.html', 'r', encoding='utf-8') as f:
            template = f.read()

        # Insert date
        formatted_date = date.strftime("%B %d, %Y")
        html_with_date = self.insert_date_after_heading(html, formatted_date)

        # Add drop cap to first qualifying paragraph
        html_with_date = self.add_drop_cap(html_with_date)

        # Generate comments section for this post
        comments_html = self.comments_template.replace('{{slug}}', slug) if self.comments_template else ''

        # Replace placeholders (escape description for use in HTML attributes)
        safe_description = html_escape(description, quote=True)
        post_html = (template
            .replace('{{title}}', html_escape(title, quote=True))
            .replace('{{date}}', formatted_date)
            .replace('{{content}}', html_with_date)
            .replace('{{post_nav}}', '<p><a href="/blog">\u2190 Blog</a></p>')
            .replace('{{comments_section}}', comments_html)
            .replace('{{slug}}', slug)
            .replace('{{description}}', safe_description)
            .replace('{{url}}', f'https://prabhchintan.com/{slug}')
            .replace('{{year}}', str(date.year))
            .replace('{{critical_css}}', self.critical_css)
            .replace('{{drop_cap_js}}', self.drop_cap_js))

        # Apply footer
        post_html = self.apply_footer(post_html)

        # Write output
        with open(self.site_dir / f'{slug}.html', 'w', encoding='utf-8') as f:
            f.write(post_html)

        log.info(f"Built post: /{slug}")

        return {
            'slug': slug,
            'title': title,
            'date': date,
            'formatted_date': formatted_date,
            'description': description,
            'url': f'/{slug}'
        }

    def build_page(self, md_file):
        """Build standalone page"""
        filename = Path(md_file).name
        slug = filename.replace('.md', '')

        # Check for slug collision
        self.check_slug_collision(slug, filename)

        # Read and process markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Process rich embeds
        content = RichEmbedProcessor.process(content)

        # Convert to HTML
        html = markdown.markdown(content, extensions=['codehilite', 'fenced_code'])

        # Extract metadata
        description = self.extract_metadata(content)
        title = self.extract_title(content) or slug.replace('_', ' ').title()

        # Load template
        with open(self.templates_dir / 'post.html', 'r', encoding='utf-8') as f:
            template = f.read()

        # Replace placeholders (no date or comments for pages)
        safe_description = html_escape(description, quote=True)
        page_html = (template
            .replace('{{title}}', html_escape(title, quote=True))
            .replace('{{date}}', '')
            .replace('{{content}}', html)
            .replace('{{post_nav}}', '')
            .replace('{{comments_section}}', '')
            .replace('{{slug}}', slug)
            .replace('{{description}}', safe_description)
            .replace('{{url}}', f'https://prabhchintan.com/{slug}')
            .replace('{{year}}', '')
            .replace('{{critical_css}}', self.critical_css)
            .replace('{{drop_cap_js}}', self.drop_cap_js))

        # Apply footer with home navigation
        page_html = self.apply_footer(page_html, is_post=False)

        # Write output
        with open(self.site_dir / f'{slug}.html', 'w', encoding='utf-8') as f:
            f.write(page_html)

        log.info(f"Built page: /{slug}")

        return {
            'slug': slug,
            'title': title,
            'description': description,
            'url': f'/{slug}'
        }

    def process_redirects(self):
        """Process redirects.txt"""
        redirects_file = Path('redirects.txt')
        if not redirects_file.exists():
            return

        with open(redirects_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '->' not in line:
                    continue

                source, target = [part.strip() for part in line.split('->', 1)]

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

                with open(self.site_dir / f'{source}.html', 'w', encoding='utf-8') as f:
                    f.write(redirect_html)

                log.info(f"Redirect: /{source} → {target}")

    def build_blog_index(self, posts):
        """Generate blog index"""
        blog_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<title>Blog - Randhawa</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="favicon.svg" type="image/svg+xml">

<link rel="apple-touch-icon" href="favicon.svg">
<meta name="description" content="Personal blog by Randhawa">
<meta property="og:title" content="Blog - Randhawa">
<meta property="og:description" content="Personal blog by Randhawa">
<meta property="og:type" content="website">
<meta property="og:url" content="https://prabhchintan.com/blog">
<meta property="og:image" content="https://prabhchintan.com/profile.png">
<meta name="twitter:card" content="summary_large_image">
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

        blog_html += '\n<br>\n<p><a href="/">← Home</a></p>\n</body>\n</html>'

        # Apply footer but mark this as blog index (not a post, not a page)
        blog_html = self.apply_footer(blog_html, is_post=False)

        with open(self.site_dir / 'blog.html', 'w', encoding='utf-8') as f:
            f.write(blog_html)

        log.info(f"Built blog index with {len(posts)} posts")

    def generate_sitemap(self, posts, pages):
        """Generate XML sitemap"""
        sitemap = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://prabhchintan.com/</loc><priority>1.0</priority></url>
<url><loc>https://prabhchintan.com/blog</loc><priority>0.9</priority></url>
<url><loc>https://prabhchintan.com/certifications</loc><priority>0.8</priority></url>
<url><loc>https://prabhchintan.com/store</loc><priority>0.8</priority></url>'''

        for post in posts:
            sitemap += f'\n<url><loc>https://prabhchintan.com{post["url"]}</loc><lastmod>{post["date"].strftime("%Y-%m-%d")}</lastmod><priority>0.8</priority></url>'

        if pages:
            for page in pages:
                sitemap += f'\n<url><loc>https://prabhchintan.com{page["url"]}</loc><priority>0.7</priority></url>'

        sitemap += '\n</urlset>'

        with open(self.site_dir / 'sitemap.xml', 'w', encoding='utf-8') as f:
            f.write(sitemap)

        log.info("Generated sitemap.xml")

    def generate_rss(self, posts):
        """Generate RSS feed"""
        rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>Randhawa Blog</title>
<link>https://prabhchintan.com/blog</link>
<atom:link href="https://prabhchintan.com/feed.xml" rel="self" type="application/rss+xml"/>
<description>Personal blog featuring thoughts on technology, design, and life.</description>
<lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>'''

        for post in posts[:10]:
            safe_title = html_escape(post['title'])
            safe_desc = html_escape(post['description'])
            rss += f'''
<item>
<title>{safe_title}</title>
<link>https://prabhchintan.com{post['url']}</link>
<description>{safe_desc}</description>
<pubDate>{post['date'].strftime('%a, %d %b %Y 12:00:00 +0000')}</pubDate>
<guid>https://prabhchintan.com{post['url']}</guid>
</item>'''

        rss += '\n</channel>\n</rss>'

        with open(self.site_dir / 'feed.xml', 'w', encoding='utf-8') as f:
            f.write(rss)

        log.info("Generated RSS feed")

    def create_404_page(self):
        """Generate 404 page"""
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<title>404 - Page Not Found</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="canonical" href="https://prabhchintan.com/404">
<style>{self.critical_css}</style>
</head>
<body>
<h1>404</h1>
<p>Page not found. <a href="/">Go home</a> or check out the <a href="/blog">blog</a>.</p>
</body>
</html>'''

        html = self.apply_footer(html)

        with open(self.site_dir / '404.html', 'w', encoding='utf-8') as f:
            f.write(html)

        log.info("Generated 404 page")

    def create_admin_ui(self, ui_type):
        """Generate admin UI (post/edit/delete)"""
        template_file = self.templates_dir / f'{ui_type}_app.html'
        if not template_file.exists():
            log.warning(f"{ui_type}_app.html not found, skipping")
            return

        with open(template_file, 'r', encoding='utf-8') as f:
            html = f.read()

        # Inject critical CSS
        css_block = f'<style>{self.critical_css}</style>'
        html = html.replace('<!-- CRITICAL_CSS_PLACEHOLDER -->', css_block)

        # Apply footer
        html = self.apply_footer(html)

        with open(self.site_dir / f'{ui_type}.html', 'w', encoding='utf-8') as f:
            f.write(html)

        log.info(f"Generated /{ui_type} UI")

    def add_drop_cap_index(self, html):
        """Add drop-cap class to the first qualifying paragraph on the homepage.

        Similar to add_drop_cap but starts after the site-headline h1 instead of post-date.
        """
        # Find the site-headline h1
        headline_match = re.search(r'<h1[^>]*class="site-headline"[^>]*>.*?</h1>', html, re.DOTALL)
        if not headline_match:
            return html

        search_start = headline_match.end()

        for p_match in re.finditer(r'<p>(.*?)</p>', html[search_start:], re.DOTALL):
            inner = p_match.group(1).strip()
            if re.match(r'^<em>.*</em>$', inner, re.DOTALL):
                continue
            if re.match(r'^<strong>.*</strong>$', inner, re.DOTALL):
                continue
            plain_text = re.sub(r'<[^>]+>', '', inner).strip()
            if len(plain_text) < 150:
                continue
            abs_start = search_start + p_match.start()
            html = html[:abs_start] + '<p class="drop-cap">' + html[abs_start + 3:]
            break

        return html

    def optimize_index(self):
        """Optimize homepage with critical CSS"""
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()

        # Inject critical CSS
        content = content.replace('</head>', f'<style>{self.critical_css}</style>\n</head>')

        # Add drop cap to first qualifying paragraph
        content = self.add_drop_cap_index(content)

        # Add drop cap JS before </body> (index: color only, no fancy fonts)
        content = content.replace('</body>', f'{self.drop_cap_js_index}\n</body>')

        # Apply footer (no nav — homepage is the top level)
        content = self.apply_footer(content, is_post=None)

        with open(self.site_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(content)

        log.info("Optimized index.html")

    def apply_footer(self, html, is_post=True):
        """Apply universal footer with context-aware navigation"""
        footer = '<footer>Randhawa 1309 Coffeen Ave Ste 1386 Sheridan, WY</footer>'

        # Remove existing footer if present
        html = re.sub(r'<footer>.*?</footer>', '', html, flags=re.DOTALL)

        # Remove any existing navigation to avoid duplication
        html = re.sub(r'<p><a href="[^"]*">← (?:Back to Blog|Home)</a></p>\s*', '', html)

        # Add navigation if not present (posts handle their own nav via template)
        if is_post is True:
            html = html.replace('</body>', f'{footer}\n</body>')
        elif is_post is False and '← Home' not in html:
            nav = '<p><a href="/">← Home</a></p>'
            html = html.replace('</body>', f'{nav}\n{footer}\n</body>')
        else:
            html = html.replace('</body>', f'{footer}\n</body>')

        return html

    def generate_robots_txt(self):
        """Generate robots.txt"""
        robots = '''User-agent: *
Allow: /

Sitemap: https://prabhchintan.com/sitemap.xml
'''
        with open(self.site_dir / 'robots.txt', 'w', encoding='utf-8') as f:
            f.write(robots)

        log.info("Generated robots.txt")

    def copy_assets(self):
        """Copy assets to site directory"""
        # Copy images
        for asset in ['profile.png', 'favicon.svg']:
            if Path(asset).exists():
                shutil.copy2(asset, self.site_dir / asset)

        # Copy certifications
        certs_dir = Path('certifications/')
        if certs_dir.exists():
            site_certs = self.site_dir / 'certifications'
            site_certs.mkdir(exist_ok=True)
            for cert_file in certs_dir.glob('*'):
                if cert_file.is_file() and cert_file.suffix.lower() in ['.pdf', '.jpg', '.jpeg', '.png']:
                    shutil.copy2(cert_file, site_certs / cert_file.name)

        # Copy media directory
        if self.media_dir.exists():
            site_media = self.site_dir / 'media'
            site_media.mkdir(exist_ok=True)
            for media_file in self.media_dir.glob('*'):
                if media_file.is_file():
                    shutil.copy2(media_file, site_media / media_file.name)

        # Copy fonts directory
        fonts_dir = Path('fonts/')
        if fonts_dir.exists():
            site_fonts = self.site_dir / 'fonts'
            site_fonts.mkdir(exist_ok=True)
            for font_file in fonts_dir.glob('*'):
                if font_file.is_file() and font_file.suffix.lower() in ['.woff2', '.woff', '.ttf', '.otf']:
                    shutil.copy2(font_file, site_fonts / font_file.name)

        # Copy store widget
        widget_file = self.templates_dir / 'store-widget.js'
        if widget_file.exists():
            shutil.copy2(widget_file, self.site_dir / 'store-widget.js')

        log.info("Copied assets to site/")

    def generate_certifications_page(self):
        """Generate certifications showcase"""
        certs_mapping_file = Path('certifications.txt')
        certs_dir = Path('certifications/')

        # Load mapping
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

        # Collect certifications
        certifications = []
        if certs_dir.exists():
            for cert_file in certs_dir.glob('*'):
                if cert_file.is_file() and cert_file.suffix.lower() in ['.pdf', '.jpg', '.jpeg', '.png']:
                    filename = cert_file.name

                    if filename in certs_mapping:
                        display_name = certs_mapping[filename]['display_name']
                        organization = certs_mapping[filename]['organization']
                    else:
                        display_name = filename.replace(cert_file.suffix, '').replace('_', ' ').title()
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

        # Generate HTML
        certs_html = ''
        for org in sorted(org_groups.keys()):
            certs_html += f'<h2>{org}</h2>\n'
            org_certs = sorted(org_groups[org], key=lambda x: len(x['display_name']))
            for cert in org_certs:
                url_filename = quote(cert["filename"], safe='')
                certs_html += f'<p><a href="/certifications/{url_filename}" target="_blank">{cert["display_name"]}</a></p>\n'
            certs_html += '\n'

        if not certifications:
            certs_html = '<p>No certifications found.</p>'

        # Full page
        page_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<title>Certifications - Randhawa</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta name="description" content="Professional certifications of Prabhchintan Randhawa">
<meta property="og:title" content="Certifications - Randhawa">
<meta property="og:url" content="https://prabhchintan.com/certifications">
<link rel="canonical" href="https://prabhchintan.com/certifications">
<style>{self.critical_css}</style>
</head>
<body>
<h1>Certifications</h1>

{certs_html}

</body>
</html>'''

        page_html = self.apply_footer(page_html, is_post=False)

        with open(self.site_dir / 'certifications.html', 'w', encoding='utf-8') as f:
            f.write(page_html)

        log.info("Generated certifications page")

    def generate_store_page(self):
        """Generate public store page"""
        template_file = self.templates_dir / 'store.html'
        if not template_file.exists():
            log.warning("store.html not found, skipping")
            return

        with open(template_file, 'r', encoding='utf-8') as f:
            html = f.read()

        html = html.replace('{{critical_css}}', self.critical_css)
        html = self.apply_footer(html, is_post=False)

        with open(self.site_dir / 'store.html', 'w', encoding='utf-8') as f:
            f.write(html)

        log.info("Generated store page")

    def validate_redirects(self):
        """Validate redirect configuration"""
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
                    log.error(f"Redirect loop detected: {source}")
                    return False

        log.info("Redirect validation passed")
        return True

    def git_commit_and_push(self):
        """Commit and push changes if not in CI"""
        if os.environ.get('SKIP_GIT_PUSH', '0').lower() in ('1', 'true', 'yes'):
            log.info("Skipping git operations (CI mode)")
            return

        # Abort any in-progress rebase before starting
        subprocess.run(['git', 'rebase', '--abort'], capture_output=True)

        # Ensure we're on a branch (not detached HEAD)
        branch = subprocess.run(
            ['git', 'symbolic-ref', '--short', 'HEAD'],
            capture_output=True, text=True
        )
        if branch.returncode != 0:
            log.warning("Detached HEAD detected, checking out main...")
            subprocess.run(['git', 'checkout', 'main'], check=False)

        subprocess.run(['git', 'add', '.'], check=False)
        status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)

        if not status.stdout.strip():
            log.info("No changes to commit")
            return

        # Commit message
        commit_msg = f"Site update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=False)

        try:
            # Sync with remote
            subprocess.run(['git', 'fetch'], check=False)
            behind_status = subprocess.run(['git', 'status', '-sb'], capture_output=True, text=True)

            if 'behind' in behind_status.stdout:
                log.info("Syncing with remote...")
                subprocess.run(['git', 'pull', '--rebase'], check=True)

            subprocess.run(['git', 'push'], check=True)
            log.info("Published to GitHub")
        except subprocess.CalledProcessError as e:
            log.error(f"Git push failed: {e}")

    def build(self):
        """Main build pipeline"""
        log.info("Building site...")

        self.setup_dirs()
        self.clean_site_dir()

        if not self.validate_redirects():
            log.error("Build aborted due to redirect errors")
            sys.exit(1)

        # Build posts
        posts = []
        for file in sorted(self.posts_dir.glob('*.md')):
            post_data = self.build_post(str(file))
            if post_data:
                posts.append(post_data)

        # Build pages
        pages = []
        for file in sorted(self.pages_dir.glob('*.md')):
            page_data = self.build_page(str(file))
            if page_data:
                pages.append(page_data)

        # Sort posts by date (newest first)
        posts.sort(key=lambda x: x['date'], reverse=True)

        # Generate everything
        self.build_blog_index(posts)
        self.process_redirects()
        self.generate_sitemap(posts, pages)
        self.generate_rss(posts)
        self.generate_robots_txt()
        self.create_404_page()
        self.optimize_index()
        self.generate_certifications_page()
        self.generate_store_page()
        self.copy_assets()

        # Generate admin UIs
        for ui_type in ['post', 'edit', 'delete', 'sell']:
            self.create_admin_ui(ui_type)

        # Git operations
        self.git_commit_and_push()

        log.info("✓ Build complete")


if __name__ == "__main__":
    builder = BlogBuilder()
    builder.build()
