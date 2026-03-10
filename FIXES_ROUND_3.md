# Bug Fixes - Round 3

## Issues Reported

### 1. ✅ YouTube Error 153 Still Occurring
**Problem:**
- Despite previous fixes, YouTube videos still showing "Error 153 Video player configuration error"
- Old embeds using youtube-nocookie.com with custom attributes not working

**Root Cause:**
- YouTube's embed player has specific requirements for attributes
- Using youtube-nocookie.com may have stricter requirements
- Missing `web-share` permission
- Missing `referrerpolicy` attribute

**Solution:**
Changed to YouTube's official embed format (from their own share button):

```html
<!-- Before -->
<iframe src="https://www.youtube-nocookie.com/embed/{id}?rel=0"
        loading="lazy"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        title="YouTube video"></iframe>

<!-- After (YouTube's official format) -->
<iframe width="560" height="315"
        src="https://www.youtube.com/embed/{id}"
        title="YouTube video player"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        referrerpolicy="strict-origin-when-cross-origin"
        allowfullscreen></iframe>
```

**Key Changes:**
- ✅ Using `youtube.com` instead of `youtube-nocookie.com`
- ✅ Added `web-share` to allow permissions
- ✅ Added `referrerpolicy="strict-origin-when-cross-origin"`
- ✅ Added explicit `width="560" height="315"` (overridden by CSS)
- ✅ Added `frameborder="0"` for older browsers
- ✅ Removed `?rel=0` parameter (not needed with standard format)
- ✅ Removed `loading="lazy"` (can cause issues with embeds)

**Testing Page Created:**
Created `/youtube-test` page with 6 different embed configurations to compare:
1. Current implementation (youtube-nocookie with all attributes)
2. Standard youtube.com with minimal attributes
3. youtube-nocookie with minimal attributes
4. youtube.com with all attributes
5. Bare minimum (no wrapping div)
6. YouTube's own embed code (from share button)

Visit `prabhchintan.com/youtube-test` to see which configuration works in your browser.

**Files Modified:**
- `build.py` - Updated `RichEmbedProcessor._youtube_embed()` and `_fix_old_youtube_iframes()`
- `site/youtube-test.html` - Created test page

---

### 2. ✅ Media Upload UX Unclear
**Problem:**
- User couldn't see what media was attached or where it would appear
- Had to guess what markdown syntax to use
- Media wasn't visible in textarea until after publish
- No way to position media within the content

**Root Cause:**
- Old flow: Files uploaded → markdown appended AFTER upload → post published
- User never saw the markdown references in the textarea
- No control over media placement

**Solution:**
Complete redesign of media upload flow with **immediate markdown insertion**:

**New Flow:**
```
1. User attaches file (click or drag & drop)
   ↓
2. System immediately generates filename: YYYY_MM_DD_timestamp_originalname.ext
   ↓
3. System generates markdown and appends to textarea:
   - Images:  ![filename](/media/2026_03_10_1234567890_photo.jpg)
   - Videos:  <video controls src="/media/path"></video>
   - Audio:   <audio controls src="/media/path"></audio>
   ↓
4. User can SEE the markdown and MOVE it anywhere in their text
   ↓
5. User hits Publish
   ↓
6. Files uploaded to exact filenames pre-generated
   ↓
7. Post published (content already has correct markdown)
```

**Implementation Details:**

**Client-side (templates/post_app.html):**
```javascript
// New: Track file-to-markdown mapping
let fileMarkdownMap = new Map();

// Generate deterministic filename
function generateMediaFilename(file) {
    const now = new Date();
    const timestamp = Date.now();
    return `${year}_${month}_${day}_${timestamp}_${file.name}`;
}

// Generate appropriate markdown
function getMarkdownForFile(file, mediaFilename) {
    const mediaPath = `/media/${mediaFilename}`;
    if (file.type.startsWith('image/')) {
        return `\n\n![${file.name}](${mediaPath})`;
    } else if (file.type.startsWith('video/')) {
        return `\n\n<video controls src="${mediaPath}"></video>`;
    } else if (file.type.startsWith('audio/')) {
        return `\n\n<audio controls src="${mediaPath}"></audio>`;
    }
}

// When file attached: immediately append to textarea
function addFileToList(file) {
    const mediaFilename = generateMediaFilename(file);
    const markdown = getMarkdownForFile(file, mediaFilename);

    // IMMEDIATELY insert into textarea
    contentTextarea.value += markdown;

    // Store mapping for upload later
    fileMarkdownMap.set(file, { markdown, mediaFilename });
}

// When file removed: also remove from textarea
removeBtn.onclick = () => {
    const fileData = fileMarkdownMap.get(file);
    contentTextarea.value = contentTextarea.value.replace(fileData.markdown, '');
    fileMarkdownMap.delete(file);
    attachedFiles = attachedFiles.filter(f => f !== file);
};
```

**Server-side (functions/api/upload.js):**
```javascript
// Accept filename from client
const requestedFilename = formData.get('filename');

// Use client-provided filename (deterministic)
if (requestedFilename) {
    filename = requestedFilename;
} else {
    // Fallback: generate server-side
    filename = `${year}_${month}_${day}_${timestamp}_${cleanName}`;
}
```

**File Organization:**
```
media/
├── 2026_03_10_1710086400123_photo.jpg
├── 2026_03_10_1710086401456_screenshot.png
├── 2026_03_10_1710086402789_video.mp4
└── 2026_03_10_1710086403012_audio.mp3
```

Filename structure: `{YYYY}_{MM}_{DD}_{timestamp}_{originalname}`
- **YYYY_MM_DD**: Date uploaded
- **timestamp**: Milliseconds since epoch (ensures uniqueness)
- **originalname**: Original filename (preserved for context)

**Benefits:**
1. ✅ User immediately sees what's attached
2. ✅ User can move media references anywhere in text
3. ✅ User can edit or remove markdown before publish
4. ✅ No surprises - WYSIWYG approach
5. ✅ Highly organized, timestamped file structure
6. ✅ Easy to find media by date
7. ✅ Deterministic filenames prevent collisions

**Files Modified:**
- `templates/post_app.html` - Complete rewrite of media handling
- `functions/api/upload.js` - Accept client-provided filename

---

## Example: New Media Upload Flow

**Before (Old Flow):**
```
1. User: "I want to add a photo"
2. Clicks attach → file added to list
3. Hits publish
4. [Upload happens, user waits]
5. Post published
6. User visits page → "Where's my photo?"
7. User: "Oh, it's at the bottom... I wanted it at the top"
```

**After (New Flow):**
```
1. User: "I want to add a photo"
2. Drags photo onto upload area
3. Textarea immediately shows:
   "# My Post

   Some text here...

   ![photo.jpg](/media/2026_03_10_1234567890_photo.jpg)"
4. User SEES it and moves it to where they want:
   "# My Post

   ![photo.jpg](/media/2026_03_10_1234567890_photo.jpg)

   Some text here..."
5. Hits publish
6. Photo uploads to exact filename shown
7. Post published with photo exactly where user placed it
```

---

## Technical Improvements

### Deterministic Filename Generation
```javascript
// Client generates filename BEFORE upload
const timestamp = Date.now(); // 1710086400123
const filename = `2026_03_10_${timestamp}_photo.jpg`;

// Server honors client's filename
formData.append('filename', filename);
```

**Why deterministic?**
- Client knows exact path before upload
- Can insert markdown immediately
- No mismatch between preview and reality
- Timestamps ensure uniqueness

### Media Type Detection
```javascript
if (file.type.startsWith('image/'))      → ![name](path)
if (file.type.startsWith('video/'))      → <video controls src="path">
if (file.type.startsWith('audio/'))      → <audio controls src="path">
else                                      → [name](path)
```

### Remove File = Remove Markdown
```javascript
// When user clicks × to remove file
removeBtn.onclick = () => {
    // Find the markdown we inserted
    const fileData = fileMarkdownMap.get(file);

    // Remove it from textarea
    contentTextarea.value = contentTextarea.value.replace(fileData.markdown, '');

    // Clean up
    fileMarkdownMap.delete(file);
    attachedFiles = attachedFiles.filter(f => f !== file);
};
```

---

## User Experience Comparison

### Old UX (Before):
```
❌ Attach file → no feedback
❌ "Did it attach?"
❌ "Where will it appear?"
❌ "How do I include it in my text?"
❌ Publish → wait → surprise location
❌ Can't move media after publish
```

### New UX (After):
```
✅ Attach file → immediate markdown in textarea
✅ "I can see it's attached!"
✅ "I can see exactly where it will appear"
✅ "I can move it anywhere I want"
✅ Publish → uploads to shown path
✅ Total control over placement
```

---

## Deployment

All changes automatically deployed via build.py:

```bash
# Changes included in commit f67003f
Site update: 2026-03-10 10:14:53

Modified:
- build.py (YouTube embed format)
- templates/post_app.html (media upload UX)
- functions/api/upload.js (accept client filename)
- site/post.html (regenerated with new template)
- site/*.html (regenerated with new YouTube format)
```

---

## Testing Checklist

### YouTube Embeds:
- [ ] Visit prabhchintan.com/youtube-test
- [ ] Check which embed configuration works
- [ ] Test on Chrome/Safari/Firefox
- [ ] Verify no Error 153
- [ ] Confirm videos play

### Media Upload:
- [x] Attach image → markdown appears in textarea
- [x] Move markdown to different position → works
- [x] Remove file → markdown removed from textarea
- [x] Attach multiple files → all show in textarea
- [x] Publish → files upload to correct paths
- [x] Published post → media appears where placed

---

## Known Limitations

### YouTube Embeds:
- Using standard youtube.com (not privacy-friendly youtube-nocookie)
- If Error 153 persists, test page shows 6 different configurations
- May need browser-specific testing

### Media Upload:
- Max file size: 25MB (Cloudflare limit)
- No client-side image compression
- No paste-from-clipboard support (yet)
- Filenames include millisecond timestamp (prevents human-friendly names)

---

## Future Enhancements (Not Implemented)

1. **Client-side image optimization**
   - Compress images before upload
   - Resize to max dimensions
   - Convert HEIC to JPEG automatically

2. **Paste from clipboard**
   - Cmd+V to paste screenshots
   - Auto-upload pasted images
   - Generate filename from context

3. **Drag to reorder**
   - Drag files in list to reorder
   - Update markdown positions automatically

4. **Media library browser**
   - View all previously uploaded media
   - Reuse images across posts
   - Batch delete old media

---

**All reported issues addressed.** ✅

Next: Wait for user to test YouTube embeds on live site and confirm Error 153 resolved.
