# Bug Fixes - Round 2

## Issues Reported

### 1. ✅ Media Upload UX Unclear
**Problem:**
- Unclear if files were attached
- Password asked too early
- "Maximum call stack size exceeded" error
- No visual feedback of what's attached
- Unclear how to include media in body

**Fixed:**
- **Drag and drop support** - Files can be clicked OR dragged
- **Visual file list** - Shows thumbnail, filename, size for each file
- **Remove button** - Click × to remove files before upload
- **Password moved to end** - Only asked when you hit Publish
- **Progressive upload** - Shows "Uploading 1/3..." with filename
- **Auto-append to content** - Markdown added to end of body automatically
- **File size check** - Warns if file > 25MB (Cloudflare limit)
- **Clear error messages** - Tells you exactly what failed and why

**New UX Flow:**
```
1. Write title + content
2. Click/drag files → See preview list
3. Remove any you don't want (×  button)
4. Enter password
5. Hit Publish
   → Uploads files (shows progress)
   → Publishes post
   → Success!
```

---

### 2. ✅ YouTube Embed Error 152
**Problem:**
- YouTube embeds showed "Error 152 Video player configuration error"
- "Watch video on YouTube" message instead of video

**Root Cause:**
- Missing required iframe attributes
- Using youtube.com instead of youtube-nocookie.com
- Missing `allow` permissions

**Fixed:**
```html
<!-- Before -->
<iframe src="https://www.youtube.com/embed/{id}">

<!-- After -->
<iframe src="https://www.youtube-nocookie.com/embed/{id}?rel=0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        title="YouTube video">
```

**Why this works:**
- `youtube-nocookie.com` - Privacy-friendly, fewer restrictions
- `?rel=0` - Disables related videos
- `allow=` - Grants required permissions for embed
- `title=` - Accessibility compliance

---

### 3. ✅ Blog Page Double Navigation
**Problem:**
- Blog page (/blog) showed both "← Home" AND "← Back to Blog"
- Confusing and redundant

**Fixed:**
- Blog page now shows only: **"← Home"**
- Blog posts show: **"← Blog"** (not "Back to Blog")
- Other pages show: **"← Home"**
- Removed all "Back to" prefix (cleaner)

**Navigation Logic:**
```
Homepage (/)        → No navigation (you're home)
Blog index (/blog)  → ← Home
Blog post (/post)   → ← Blog
Static page (/ai)   → ← Home
Certifications      → ← Home
```

---

## Additional Issues Found & Fixed

### 4. ✅ Duplicate Navigation Removal
**Problem:**
- `apply_footer()` was adding navigation without removing existing ones
- Could lead to multiple nav links stacking

**Fixed:**
- Added regex to remove existing navigation before adding new
- Ensures only ONE navigation link per page

---

### 5. ✅ File Size Limits Clarified
**Problem:**
- Unclear what file sizes are allowed
- GitHub limit (100MB) vs Cloudflare limit (25MB)

**Fixed:**
- Clear 25MB limit enforced client-side
- Error message shows actual file size
- Suggests external hosting for large files
- Format example: "photo.jpg is too large (32.5 MB). Maximum: 25MB"

---

### 6. ✅ Media Upload Progress Feedback
**Problem:**
- No feedback during upload
- User doesn't know if it's working

**Fixed:**
- Blue info box appears: "Uploading 1/3..."
- Shows current filename being uploaded
- Changes to "Publishing post..." after uploads
- Success message shows final filename

---

### 7. ✅ Form Persists on Error
**Problem:**
- If password is wrong, form would lose data
- Attached files would disappear

**Fixed:**
- Password only validated when you hit Publish
- If upload fails, files stay in list
- If password wrong, just shows error - data persists
- Only clears form on successful publish

---

## Technical Improvements

### YouTube Embed Enhancement
```python
# Added proper iframe attributes
allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
title="YouTube video"
```

### Media Upload Architecture
```javascript
// Files staged locally first
attachedFiles = []

// Upload one by one with progress
for (let i = 0; i < attachedFiles.length; i++) {
    statusDiv.innerHTML = `Uploading ${i+1}/${attachedFiles.length}: ${file.name}...`
    // Upload via API
    // Add markdown to content
}

// Publish post with final content
```

### Navigation Cleanup
```python
# Remove any existing navigation
html = re.sub(r'<p><a href="[^"]*">← (?:Back to Blog|Home)</a></p>\s*', '', html)

# Add new navigation based on context
if is_post:
    nav = '<p><a href="/blog">← Blog</a></p>'
```

---

## User Experience Improvements

### Before Media Upload:
```
[📎 Attach Media]
"Uploading..." (no details)
"✗ Maximum call stack size exceeded"
```

### After Media Upload:
```
📎 Attach Media
Click or drag files here (images, videos, audio)

[Image preview] photo.jpg (2.3 MB)  [×]
[Image preview] screenshot.png (890 KB)  [×]

Uploading 1/2: photo.jpg...
Uploading 2/2: screenshot.png...
Publishing post...
✓ Published as 2026_03_10_my-post.md
Site updates in ~60 seconds.
```

---

## Testing Checklist

- [x] YouTube embeds work without Error 152
- [x] Blog page shows only "← Home"
- [x] Blog posts show "← Blog"  - [x] Media upload shows file list with previews
- [x] Can remove files before upload (× button)
- [x] Drag and drop works
- [x] File size limit enforced (25MB)
- [x] Progress shows during upload
- [x] Form persists if password wrong
- [x] Form clears only on success
- [x] Multiple file upload works
- [x] Image previews show for images
- [x] Auto-appends markdown to content

---

## Files Modified

```
build.py
- Fixed YouTube embed (youtube-nocookie, allow attribute, title)
- Fixed navigation duplication in apply_footer()
- Changed "Back to Blog" → "Blog"
- Added regex to remove existing navigation

templates/post_app.html
- Complete rewrite of media upload
- Added drag & drop support
- Added file preview list with thumbnails
- Added remove buttons
- Moved password to end of form
- Added progress feedback
- Added file size validation
- Better error handling
```

---

## Deployment

```bash
git add .
git commit -m "Fix YouTube embeds, media upload UX, and navigation"
git push origin main
```

---

## Known Limitations

### Media Files
- **Max size: 25MB** (Cloudflare Pages Functions limit)
- **GitHub limit: 100MB** per file (repo limit)
- **No compression** - Files uploaded as-is
- **For larger files:** Use external hosting (YouTube for video, Imgur for images)

### iPhone Photos
- Typical iPhone photo: 2-5MB (supported ✓)
- iPhone ProRAW: 20-30MB (supported ✓)
- 4K video: Can be 100MB+ (use YouTube instead)

### Image Optimization
- Not implemented yet
- Future enhancement: Client-side compression before upload
- For now: Use macOS Preview or online tools to compress first

---

## Future Enhancements (Not Implemented)

1. **Client-side image compression**
   - Compress images before upload
   - Reduce iPhone photo sizes automatically
   - Use browser Canvas API

2. **Upload progress bar**
   - Visual progress bar instead of text
   - Percentage complete

3. **Paste images from clipboard**
   - Cmd+V to paste screenshots
   - Auto-upload pasted images

4. **Video thumbnail generation**
   - Show video thumbnail in file list
   - Extract first frame

5. **Media library**
   - Browse previously uploaded media
   - Reuse images across posts

---

**All reported bugs fixed and tested.** ✅
