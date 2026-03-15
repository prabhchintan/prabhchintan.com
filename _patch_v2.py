"""Patch v2: Fix search, redesign panels, fix spacing, blue links, add standalone pages."""

with open('build.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 1. Replace the entire inline CSS + HTML section in build_blog_index
# ============================================================

css_start_marker = "<style>\n.blog-header"
css_start = content.find(css_start_marker)
if css_start == -1:
    raise RuntimeError("Could not find inline CSS start marker")

html_end_marker = "</div></div>"
# Find the specific one ending with '''
search_from = css_start
while True:
    pos = content.find(html_end_marker, search_from)
    if pos == -1:
        raise RuntimeError("Could not find HTML end marker")
    after = content[pos + len(html_end_marker):pos + len(html_end_marker) + 3]
    if after == "'''":
        html_end = pos + len(html_end_marker) + 3
        break
    search_from = pos + 1

new_css_html = ("<style>\n"
    ".blog-header{display:flex;align-items:baseline;justify-content:space-between}\n"
    ".blog-header h1{margin:0}\n"
    ".search-toggle{color:var(--meta-color);cursor:pointer;transition:color 0.2s}\n"
    ".search-toggle:hover{color:var(--text-color)}\n"
    ".blog-nav{font-size:0.85em;color:var(--meta-color);margin:0 0 1.5em}\n"
    ".search-panel,.subscribe-panel{display:none;border:1px solid var(--border-color);border-radius:4px;padding:0.6em 0.8em;margin:-0.8em 0 1.5em}\n"
    ".search-panel.open,.subscribe-panel.open{display:block}\n"
    ".search-panel input[type=\"text\"]{width:100%;padding:0.3em 0;border:none;border-bottom:1px solid var(--border-color);font-family:var(--font-body);font-size:0.95em;background:transparent;color:var(--text-color);outline:none;box-sizing:border-box}\n"
    ".search-panel input:focus{border-bottom-color:var(--text-color)}\n"
    ".search-panel input::placeholder{color:var(--meta-color)}\n"
    ".subscribe-panel input[type=\"email\"]{width:100%;padding:0.3em 0;border:none;border-bottom:1px solid var(--border-color);font-family:var(--font-body);font-size:0.9em;background:transparent;color:var(--text-color);outline:none;box-sizing:border-box}\n"
    ".subscribe-panel input[type=\"email\"]:focus{border-bottom-color:var(--text-color)}\n"
    ".subscribe-panel input::placeholder{color:var(--meta-color)}\n"
    ".search-results{max-height:300px;overflow-y:auto;display:none;margin-top:0.4em}\n"
    ".search-results.open{display:block}\n"
    ".search-result{display:block;padding:0.5em 0.3em;color:var(--text-color);text-decoration:none;border-bottom:1px solid var(--border-color);font-size:0.95em;transition:background 0.15s;border-radius:3px}\n"
    ".search-result:last-child{border-bottom:none}\n"
    ".search-result:hover,.search-result.active{background:rgba(0,0,0,0.03)}\n"
    ".search-result em{font-size:0.8em;color:var(--meta-color)}\n"
    ".search-empty{padding:0.5em 0;color:var(--meta-color);font-size:0.9em;font-style:italic}\n"
    ".sub-actions{margin-top:0.4em;font-size:0.85em}\n"
    "</style>\n"
    "</head>\n"
    "<body>\n"
    '<div class="blog-header"><h1>Blog</h1>'
    '<svg id="searchToggle" class="search-toggle" aria-label="Search posts" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
    "</div>\n"
    '<p class="blog-nav"><a href="/">\u2190 Home</a> \u00b7 <span class="subscribe-link" id="subLink">subscribe</span></p>\n'
    '<div class="search-panel" id="searchPanel">'
    '<input type="text" id="blogSearch" placeholder="Search posts\u2026" autocomplete="off" spellcheck="false">'
    '<div class="search-results" id="searchResults"></div>'
    "</div>\n"
    '<div class="subscribe-panel" id="subPanel">'
    '<input type="text" name="url" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" id="subHoney">'
    '<input type="email" id="subEmail" placeholder="your@email.com" autocomplete="email">'
    '<div class="sub-actions"><span id="subBtn" style="cursor:pointer;color:var(--link-color)">subscribe</span></div>'
    "</div>'''"
)

content = content[:css_start] + new_css_html + content[html_end:]

# ============================================================
# 2. Replace the script section (search + subscribe JS)
# ============================================================

script_start_marker = "blog_html += f'''\n<script>"
script_start = content.find(script_start_marker)
if script_start == -1:
    raise RuntimeError("Could not find script start marker")
line_start = content.rfind('\n', 0, script_start) + 1
indent = content[line_start:script_start]

script_end_marker = "blog_html += '\\n</body>\\n</html>'"
script_end = content.find(script_end_marker, script_start)
if script_end == -1:
    raise RuntimeError("Could not find script end marker")
script_end += len(script_end_marker)

# Build the new script using string concatenation to avoid quoting issues
new_script_lines = [
    indent + "blog_html += f'''\n",
    "<script>\n",
    "(function(){{\n",
    "var posts={posts_json};\n",
    "var input=document.getElementById('blogSearch');\n",
    "var results=document.getElementById('searchResults');\n",
    "var searchPanel=document.getElementById('searchPanel');\n",
    "var searchToggle=document.getElementById('searchToggle');\n",
    "var activeIdx=-1;\n",
    "function esc(s){{var d=document.createElement('div');d.textContent=s;return d.innerHTML;}}\n",
    "function hl(text,q){{var i=text.toLowerCase().indexOf(q);if(i===-1)return esc(text);return esc(text.slice(0,i))+'<strong>'+esc(text.slice(i,i+q.length))+'</strong>'+esc(text.slice(i+q.length));}}\n",
    "function snippet(text,q){{var i=text.toLowerCase().indexOf(q);if(i===-1)return'';var start=Math.max(0,i-40);var end=Math.min(text.length,i+q.length+60);var s=text.slice(start,end).trim();return(start>0?'\\u2026':'')+s+(end<text.length?'\\u2026':'');}}\n",
    "function updateActive(items){{for(var i=0;i<items.length;i++)items[i].classList.toggle('active',i===activeIdx);if(items[activeIdx])items[activeIdx].scrollIntoView({{block:'nearest'}});}}\n",
    "searchToggle.addEventListener('click',function(){{\n",
    "var isOpen=searchPanel.classList.toggle('open');\n",
    "if(isOpen){{document.getElementById('subPanel').classList.remove('open');input.focus();}}\n",
    "else{{input.value='';results.className='search-results';results.innerHTML='';}}\n",
    "}});\n",
    "input.addEventListener('keydown',function(e){{var items=results.querySelectorAll('.search-result');if(e.key==='Escape'){{searchPanel.classList.remove('open');input.value='';results.className='search-results';results.innerHTML='';return;}}if(e.key==='ArrowDown'){{e.preventDefault();activeIdx=Math.min(activeIdx+1,items.length-1);updateActive(items);}}else if(e.key==='ArrowUp'){{e.preventDefault();activeIdx=Math.max(activeIdx-1,0);updateActive(items);}}else if(e.key==='Enter'&&activeIdx>=0&&items[activeIdx]){{e.preventDefault();items[activeIdx].click();}}}});\n",
    "input.addEventListener('input',function(){{activeIdx=-1;var q=this.value.toLowerCase().trim();if(!q){{results.className='search-results';results.innerHTML='';return;}}var m=[];for(var i=0;i<posts.length;i++){{var p=posts[i];var inTitle=p.title.toLowerCase().indexOf(q)!==-1;var inBody=p.body.toLowerCase().indexOf(q)!==-1;if(inTitle||inBody)m.push({{post:p,inTitle:inTitle,inBody:inBody}});}}if(!m.length){{results.className='search-results open';results.innerHTML='<div class=\"search-empty\">No posts found</div>';return;}}var h='';for(var i=0;i<m.length;i++){{var r=m[i];h+='<a class=\"search-result\" href=\"'+r.post.url+'\">'+(r.inTitle?hl(r.post.title,q):esc(r.post.title))+'<br><em>'+esc(r.post.date);if(!r.inTitle&&r.inBody){{h+=' \\u2014 '+hl(snippet(r.post.body,q),q);}}h+='</em></a>';}}results.className='search-results open';results.innerHTML=h;}});\n",
    "document.addEventListener('click',function(e){{if(!e.target.closest('.search-panel')&&!e.target.closest('.search-toggle')){{results.className='search-results';results.innerHTML='';searchPanel.classList.remove('open');input.value='';}}if(!e.target.closest('.subscribe-panel')&&!e.target.closest('#subLink'))document.getElementById('subPanel').classList.remove('open');}});\n",
    "var subLink=document.getElementById('subLink');var subPanel=document.getElementById('subPanel');var subEmail=document.getElementById('subEmail');var subBtn=document.getElementById('subBtn');var subHoney=document.getElementById('subHoney');var isUnsub=location.hash==='#unsubscribe';\n",
    "if(localStorage.getItem('subscribed')&&!isUnsub){{subLink.textContent='subscribed';subLink.style.opacity='0.6';}}\n",
    "if(isUnsub){{subBtn.textContent='unsubscribe';subEmail.placeholder='your email';subPanel.classList.add('open');}}\n",
    "subLink.addEventListener('click',function(){{var isOpen=subPanel.classList.toggle('open');if(isOpen){{searchPanel.classList.remove('open');input.value='';results.className='search-results';results.innerHTML='';subEmail.focus();}}}});\n",
    "function doSub(){{var email=subEmail.value.trim();if(!email||!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email))return;var body={{email:email,url:subHoney.value}};if(isUnsub)body.remove=true;fetch('/api/subscribe',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(body)}}).then(function(r){{return r.json();}}).then(function(){{subPanel.classList.remove('open');subEmail.value='';if(isUnsub){{subLink.textContent='unsubscribed';localStorage.removeItem('subscribed');}}else{{subLink.textContent='subscribed';subLink.style.opacity='0.6';localStorage.setItem('subscribed','1');setTimeout(function(){{subLink.textContent='subscribe';subLink.style.opacity='';}},2000);}}}});}}\n",
    "subBtn.addEventListener('click',doSub);subEmail.addEventListener('keydown',function(e){{if(e.key==='Enter'){{e.preventDefault();doSub();}}}});\n",
    "}})();\n",
    "</script>\n",
    "'''\n\n",
    indent + "blog_html += '\\n</body>\\n</html>'"
]

new_script = "".join(new_script_lines)
content = content[:script_start] + new_script + content[script_end:]

# ============================================================
# 3. Add standalone /subscribe and /unsubscribe page generation
# ============================================================

with open('_subscribe_method.py', 'r', encoding='utf-8') as f:
    subscribe_pages_method = f.read()

insert_marker = "    def generate_slugs_json(self, posts, pages):"
insert_pos = content.find(insert_marker)
if insert_pos == -1:
    raise RuntimeError("Could not find generate_slugs_json")

content = content[:insert_pos] + subscribe_pages_method + "\n" + content[insert_pos:]

# ============================================================
# 4. Call build_subscribe_pages() in the build() method
# ============================================================

call_marker = "        self.build_blog_index(posts)"
call_pos = content.find(call_marker)
if call_pos == -1:
    raise RuntimeError("Could not find build_blog_index call")
call_end = content.find('\n', call_pos) + 1

content = content[:call_end] + "        self.build_subscribe_pages()\n" + content[call_end:]

# ============================================================
# 5. Add subscribe and unsubscribe to reserved slugs
# ============================================================

old_reserved = "for s in ['blog', 'store', 'sell', 'post', 'edit', 'delete',\n                   'certifications', '404', 'index']:"
new_reserved = "for s in ['blog', 'store', 'sell', 'post', 'edit', 'delete',\n                   'certifications', '404', 'index', 'subscribe', 'unsubscribe']:"
if old_reserved in content:
    content = content.replace(old_reserved, new_reserved, 1)
else:
    print("WARNING: Could not find reserved slugs to update")

with open('build.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: All v2 patches applied")
