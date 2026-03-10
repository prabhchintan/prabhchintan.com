# Testing Your New World-Class Blog

## Pre-Flight Checklist

✅ Environment variables set in Cloudflare:
- `GITHUB_TOKEN` = Your GitHub personal access token
- `ADMIN_PASSWORD` = Your chosen password

✅ Pushed to GitHub (Cloudflare auto-deploys)

---

## Test 1: Real-Time Slug Collision Detection ⭐ NEW

**What to test:** The UI should prevent duplicate slugs before you even submit

**Steps:**
1. Visit `https://prabhchintan.com/post`
2. Type a title: "Americano"
3. **Watch the slug preview appear below the slug field**

**Expected Result:**
```
⚠️ Slug collision: americano-0823 already exists
Choose a different title or add a custom slug
```

**What should happen:**
- Publish button becomes **disabled** (grayed out)
- Red warning shows the conflicting slug
- You cannot submit until you change the title or add a custom slug

**Try fixing it:**
- Change title to "Americano 2" → Preview shows "✓ Will be published as: /americano-2-0823"
- OR add custom slug "my-coffee-post" → Preview shows "✓ Will be published as: /my-coffee-post"
- Publish button becomes **enabled** again

---

## Test 2: Media Upload

**Steps:**
1. Visit `https://prabhchintan.com/post`
2. Enter title: "Test Post"
3. Enter password
4. Click "📎 Attach Media"
5. Select an image from your phone/computer
6. Wait for upload

**Expected Result:**
- "Uploading..." appears
- After a few seconds: "✓ Uploaded"
- Markdown is auto-inserted into the content textarea:
  ```markdown
  ![filename.jpg](/media/2026_03_10_1234567890_filename.jpg)
  ```

**Verify:**
- The markdown appears at your cursor position
- You can continue typing around it
- Multiple uploads work (upload → type → upload again)

---

## Test 3: YouTube Embed

**Steps:**
1. Visit `https://prabhchintan.com/post`
2. Enter title: "Video Test"
3. In content, paste a YouTube URL:
   ```
   https://www.youtube.com/watch?v=dQw4w9WgXcQ
   ```
4. Enter password and publish

**Expected Result:**
- Post publishes successfully
- When you visit the post on your site, you see a responsive YouTube embed
- Video plays inline, no redirect to YouTube

**Edge cases:**
- Try short URL: `https://youtu.be/dQw4w9WgXcQ`
- Try URL with timestamp: `https://youtube.com/watch?v=dQw4w9WgXcQ&t=30s`

---

## Test 4: Fuzzy Search (Edit)

**Steps:**
1. Visit `https://prabhchintan.com/edit`
2. Enter password
3. In the search box, type just: "amer"
4. Click "Search Posts"

**Expected Result:**
- Shows post: "americano"
- Displays: `2026-03-10 • 2026_03_10_americano.md`

**Try other searches:**
- "2026" → Shows all posts from 2026
- "march" → Nothing (searches slug/filename/date, not month names)
- "khalsa" → Shows khalsa post
- "chick" → Shows chickfila post

**Real-time search:**
- After first search, just type in the search box
- Results update automatically as you type

---

## Test 5: Fuzzy Search (Delete)

**Steps:**
1. Visit `https://prabhchintan.com/delete`
2. Enter password
3. Type "test" or search for your test post
4. Click "Search Posts"
5. Click on the post

**Expected Result:**
- Post card gets red border and light red background
- "Delete Selected Post" button appears (red)
- Click it → confirmation dialog: "⚠️ Permanently delete...?"
- Confirm → Post disappears from list
- Success message: "✓ Deleted. Site updates in ~60 seconds."

---

## Test 6: Context-Aware Navigation

**What to test:** Navigation links change based on where you are

**Steps:**
1. Go to homepage (`/`)
2. Click "blog" link
3. You're now at `/blog` (blog index)
4. Click any post (e.g., "Americano")
5. You're now at `/americano` (post page)
6. Scroll to bottom

**Expected Result at `/americano`:**
- Footer says: "← Back to Blog" (not "← Home")
- Clicking it takes you to `/blog`

**Now test a page (not post):**
1. Visit `/ai` or `/analytics`
2. Scroll to bottom

**Expected Result at `/ai`:**
- Footer says: "← Home" (not "← Back to Blog")
- Clicking it takes you to `/`

**Why this matters:**
- Posts are part of the blog → go back to blog index
- Pages are standalone → go back to homepage
- This is standard blog navigation UX

---

## Test 7: Rich Auto-Linking

**Steps:**
1. Visit `https://prabhchintan.com/post`
2. Enter title: "Links Test"
3. In content, paste:
   ```
   Check out https://github.com

   And this https://wikipedia.org/wiki/Baskerville

   Here's my [explicit link](https://example.com)
   ```
4. Publish

**Expected Result:**
- First two URLs become clickable links automatically
- Third URL (already markdown link) stays as is
- No double-linking of the explicit link

---

## Test 8: Password Security

**What to test:** GitHub token never exposed, password protects all admin actions

**Steps:**
1. Visit `https://prabhchintan.com/post`
2. Open browser DevTools (F12) → Network tab
3. Enter wrong password
4. Try to publish

**Expected Result:**
- Request goes to `/api/publish`
- Response: `401 Unauthorized` with `{"error": "Invalid password"}`
- Error message shown in UI: "✗ Invalid password"

**What you should NOT see:**
- No GitHub token anywhere in:
  - JavaScript source
  - Network requests
  - Local storage
  - Cookies
- Token is only on Cloudflare server

**Try correct password:**
- Post publishes successfully
- Server verifies password before touching GitHub API

---

## Test 9: Mobile Experience

**If on desktop, simulate mobile:**
1. Open DevTools (F12)
2. Click device toolbar icon (or Cmd+Shift+M / Ctrl+Shift+M)
3. Select "iPhone 13 Pro" or similar

**Test on actual mobile:**
1. Visit `https://prabhchintan.com/post` on your phone
2. Save as bookmark on home screen (iOS: Share → Add to Home Screen)
3. Open from home screen → feels like an app

**Expected Results:**
- Forms are touch-friendly
- Font sizes are readable
- Buttons are easy to tap
- No horizontal scrolling
- Media upload works from camera

**Pro tip:**
- Bookmark all three: `/post`, `/edit`, `/delete`
- Quick access to your blog admin from anywhere

---

## Test 10: Build-Time Slug Collision (Fallback)

**What to test:** If somehow UI detection fails, build still catches it

**Steps:**
1. Manually create duplicate file:
   ```bash
   cp posts/2026_03_10_americano.md posts/2026_03_11_americano.md
   ```
2. Try to build:
   ```bash
   python3 build.py
   ```

**Expected Result:**
```
INFO: Building site...
INFO: Redirect validation passed
ERROR: Slug collision: 'americano' used in both 2026_03_10_americano.md and 2026_03_11_americano.md
ERROR: Build aborted. Please rename one of the files.
```

**What should happen:**
- Build **fails** immediately (fail-fast)
- Error message is clear
- No partial site generated
- Git commit doesn't happen

**Fix it:**
```bash
rm posts/2026_03_11_americano.md
python3 build.py  # Should work now
```

---

## Test 11: Responsive Typography

**Steps:**
1. Visit any post
2. Resize browser window from wide to narrow
3. Or switch between desktop and mobile

**Expected Result:**
- **Desktop (>768px):**
  - Max width: 600px (centered)
  - Padding: 4em sides
  - H1: 2em
  - Body: 1em

- **Mobile (≤768px):**
  - Max width: 600px (still centered)
  - Padding: 2.5em sides
  - H1: 1.8em (slightly smaller)
  - Body: 1em (same)

**Font family everywhere:**
- Baskerville (falls back to Times New Roman)
- No font switching between pages
- Consistent serif aesthetic

---

## Test 12: SEO & Feeds

**XML Sitemap:**
1. Visit `https://prabhchintan.com/sitemap.xml`
2. Should see XML with all posts, pages, certifications

**RSS Feed:**
1. Visit `https://prabhchintan.com/feed.xml`
2. Should see RSS XML with latest 10 posts
3. Test in RSS reader (Feedly, etc.)

**Robots.txt:**
1. Visit `https://prabhchintan.com/robots.txt`
2. Should see:
   ```
   User-agent: *
   Allow: /

   Sitemap: https://prabhchintan.com/sitemap.xml
   ```

**OpenGraph (Social Sharing):**
1. Share a post link on Twitter/X or Slack
2. Should show:
   - Post title
   - Description (first paragraph)
   - Profile image
   - Site name: prabhchintan.com

---

## Test 13: Performance

**Homepage Speed:**
1. Open DevTools → Network tab
2. Hard refresh (Cmd+Shift+R / Ctrl+Shift+R)
3. Look at `index.html` request

**Expected Result:**
- Single request loads everything (HTML + CSS inlined)
- No external stylesheet requests
- No JavaScript on homepage
- Lighthouse score: 95+ for Performance

**Blog Post Speed:**
1. Visit any post
2. Check Network tab

**Expected Result:**
- HTML with inline CSS
- Images lazy-load
- YouTube embeds lazy-load (loading="lazy")
- No jQuery, no frameworks

---

## Test 14: Certifications Page

**Steps:**
1. Visit `https://prabhchintan.com/certifications`

**Expected Result:**
- Organized by organization (alphabetical)
- Within each org, sorted by name length
- All 15 certificates listed
- Click any → Opens PDF/image in new tab

**Test URL encoding:**
- Files with spaces should work
- Special characters in filenames handled correctly

---

## Troubleshooting

### Issue: "Invalid password"
- **Check:** Cloudflare environment variable `ADMIN_PASSWORD` matches exactly
- **Case-sensitive:** "password" ≠ "Password"

### Issue: Slug preview not showing
- **Check:** Browser console (F12) for errors
- **Try:** Hard refresh (Cmd+Shift+R)
- **Fallback:** Build will still catch collisions

### Issue: Media upload fails
- **Check:** File size (GitHub limit: 100MB, Cloudflare: 25MB)
- **Check:** `GITHUB_TOKEN` has `repo` scope
- **Try:** Smaller file or use external hosting (YouTube, Imgur)

### Issue: YouTube embed not showing
- **Check:** URL format (should be `youtube.com/watch?v=` or `youtu.be/`)
- **Try:** Viewing source → should see `<iframe>` tag
- **Note:** Embeds process during build, not in real-time preview

### Issue: Functions not working (401/403)
- **Check:** Both secrets set in Cloudflare
- **Check:** Deployed to Cloudflare Pages (not local)
- **Check:** Using correct domain (not localhost)

---

## Success Criteria ✓

Your blog is working perfectly if:

- ✅ Slug collision shows warning + disables publish
- ✅ Media uploads and inserts markdown
- ✅ YouTube URLs become embeds
- ✅ Fuzzy search finds posts with partial matches
- ✅ Password required for all admin actions
- ✅ Navigation is context-aware (posts → blog, pages → home)
- ✅ Mobile UI is smooth and responsive
- ✅ Build fails on duplicate slugs (safety net)
- ✅ SEO meta tags on all pages
- ✅ Font is Baskerville throughout

---

## Next Steps After Testing

1. **Delete test posts** (via `/delete` UI)
2. **Write your first real post** with media!
3. **Bookmark admin pages** on mobile
4. **Share a post** to verify social previews
5. **Monitor Cloudflare** dashboard for Functions usage

---

**Happy Publishing!** 🚀

You now have a Formula 1-grade blog that's:
- Secure (server-side auth)
- Smart (collision detection)
- Beautiful (Baskerville typography)
- Fast (static generation)
- Rich (media + embeds)
- Mobile-first (anywhere publishing)

Go write something great. ✍️
