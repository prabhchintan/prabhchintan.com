# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Jekyll-based static website (prabhchintan.github.io) for Randhawa Inc., a technology consultancy. The site uses GitHub Pages with the Minima theme and includes custom styling and JavaScript functionality.

## Development Commands

### Setup
```bash
# Install dependencies
./script/bootstrap
# or manually:
gem install bundler
bundle install
```

### Development
```bash
# Start local development server
./script/server
# or manually:
bundle exec jekyll serve
```

### Build
```bash
# Build the site
./script/build  
# or manually:
bundle exec jekyll build
```

## Architecture

### Key Directories
- `_posts/` - Blog posts in Markdown format using Jekyll conventions
- `_layouts/` - HTML templates (base, home, page, post)
- `_includes/` - Reusable template components (header, footer, social icons)
- `_sass/minima/` - Sass stylesheets extending the Minima theme
- `assets/` - Static assets (CSS, JavaScript, images, fonts)
- `script/` - Development utility scripts

### Theme System
The site uses a custom theme toggle system implemented in `assets/js/theme-toggle.js`:
- Supports light/dark/auto modes
- Respects system preferences
- Persists user choice in localStorage
- Prevents flash of unstyled content with CSS transitions

### Content Structure
- Posts use Jekyll's `title` for URL generation (permalink: /:title)
- Default Open Graph image set for all pages
- Custom social media integration via Minima theme configuration
- Multi-language support with Unicode characters in titles

### Deployment
- Automated deployment via GitHub Actions (`.github/workflows/jekyll.yml`)
- Builds on Ruby 3.2 with bundler cache optimization
- Deploys to GitHub Pages on push to main branch