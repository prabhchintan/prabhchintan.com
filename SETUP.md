# Setup Guide

## Cloudflare Pages Configuration

### 1. Environment Variables

In your Cloudflare Pages dashboard, add these environment variables:

```
GITHUB_TOKEN=<your-github-personal-access-token>
ADMIN_PASSWORD=<your-secure-password>
```

**Getting a GitHub Token:**
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope (full control of private repositories)
3. Copy the token immediately (you won't see it again)

**Setting Admin Password:**
- Choose a strong password for your mobile publishing interface
- This password will be required for /post, /edit, and /delete pages

### 2. Build Configuration

In Cloudflare Pages:
- **Build command:** `python3 build.py`
- **Build output directory:** `site`
- **Root directory:** `/`

### 3. Deploy

Push to your `main` branch. Cloudflare will automatically:
1. Run the build script
2. Deploy the `site/` directory
3. Enable the Functions API at `/api/*`

---

## Publishing Workflow

### Create a Post
1. Visit `https://prabhchintan.com/post` on your phone or computer
2. Enter title and content (markdown supported)
3. Optional: Add custom slug
4. Optional: Upload media (images/video/audio)
5. Enter admin password
6. Click "Publish"

**Rich Media Support:**
- Paste YouTube URLs → Auto-embedded video player
- Paste X/Twitter URLs → Auto-embedded tweets
- Paste regular URLs → Auto-linked
- Upload images/videos → Auto-inserted as markdown

### Edit a Post
1. Visit `https://prabhchintan.com/edit`
2. Enter password
3. Search for post (fuzzy search: type partial slug, date, or title)
4. Select post from results
5. Edit content
6. Save changes

### Delete a Post
1. Visit `https://prabhchintan.com/delete`
2. Enter password
3. Search for post
4. Select post
5. Confirm deletion

---

## Local Development

###Build Locally
```bash
python3 build.py
```

This will:
- Clean and rebuild the `site/` directory
- Process all markdown files
- Generate sitemap, RSS, etc.
- Auto-commit and push (unless `SKIP_GIT_PUSH=1`)

### Test Build Without Committing
```bash
SKIP_GIT_PUSH=1 python3 build.py
```

---

## Project Structure

```
prabhchintan.com/
├── build.py                 # Build engine
├── index.html               # Homepage source
├── requirements.txt         # Python dependencies
├── redirects.txt            # URL redirects
├── certifications.txt       # Certification mappings
│
├── posts/                   # Blog posts (YYYY_MM_DD_slug.md)
├── pages/                   # Static pages (slug.md)
├── media/                   # Uploaded media files
├── certifications/          # Certificate PDFs/images
│
├── templates/
│   ├── critical.css         # Global styles
│   ├── post.html            # Post/page template
│   ├── post_app.html        # Create UI
│   ├── edit_app.html        # Edit UI
│   └── delete_app.html      # Delete UI
│
├── functions/api/           # Cloudflare Pages Functions
│   ├── posts.js             # List posts
│   ├── publish.js           # Create post
│   ├── update.js            # Update post
│   ├── delete.js            # Delete post
│   └── upload.js            # Upload media
│
└── site/                    # Generated static files (git-tracked for Cloudflare)
```

---

## Features

### Rich Embeds
- **YouTube**: Paste URL → Responsive embed
- **X/Twitter**: Paste URL → Tweet card
- **Auto-linking**: Plain URLs → Clickable links
- **Images**: Upload → `![alt](/media/filename.jpg)`
- **Videos**: Upload → `<video>` tag (small files only)

### SEO
- XML sitemap at `/sitemap.xml`
- RSS feed at `/feed.xml`
- OpenGraph & Twitter Cards on all pages
- Canonical URLs
- Robots.txt

### Performance
- Critical CSS inlined
- Single-packet homepage delivery
- Static generation (no runtime)
- Cloudflare CDN

### Security
- GitHub token never exposed to client
- Password-protected admin UIs
- Server-side auth via Cloudflare Functions
- No database, no attack surface

---

## Tips

### Slug Collisions
The build will fail if two posts have the same slug. Rename one of the files to fix.

### Media File Sizes
- GitHub has a 100MB file limit
- Keep images under 5MB
- For large videos, use YouTube embeds instead of uploading

### Mobile Publishing
Save `/post`, `/edit`, and `/delete` as bookmarks on your phone home screen for quick access.

### Markdown Tips
- Use `#` for h1, `##` for h2, etc.
- Inline images: `![alt text](/media/file.jpg)`
- Code blocks: Use triple backticks
- Links: `[text](url)`

---

## Troubleshooting

**Build fails:** Check Python and markdown package are installed
```bash
pip install markdown
```

**Functions not working:** Verify environment variables in Cloudflare dashboard

**Password not working:** Ensure `ADMIN_PASSWORD` matches exactly (case-sensitive)

**Slug collision error:** Two posts have the same slug - rename one

**Media upload fails:** File might be too large (>25MB Cloudflare limit)

---

## Maintenance

### Backup
All content is in Git - your repository IS the backup.

### Updates
1. Edit files locally
2. Run `python3 build.py`
3. Push to GitHub
4. Cloudflare auto-deploys

### Add New Certifications
1. Drop PDF/PNG/JPG in `certifications/` directory
2. Add mapping to `certifications.txt`:
   ```
   filename.pdf -> Display Name -> Organization Name
   ```
3. Build and push

---

**You're all set!** 🎉

Visit your site and start publishing from anywhere.
