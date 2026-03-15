    def build_subscribe_pages(self):
        """Generate standalone /subscribe and /unsubscribe pages"""

        for mode in ('subscribe', 'unsubscribe'):
            is_unsub = mode == 'unsubscribe'
            title = 'Unsubscribe' if is_unsub else 'Subscribe'
            desc = 'Unsubscribe from blog notifications.' if is_unsub else 'Get notified when new posts are published.'
            btn_label = 'unsubscribe' if is_unsub else 'subscribe'
            success_msg = 'unsubscribed' if is_unsub else 'subscribed'
            remove_js = 'true' if is_unsub else 'false'

            page_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<title>Randhawa: {title}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/favicon.svg">
<meta name="description" content="{desc}">
<meta property="og:title" content="Randhawa: {title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://prabhchintan.com/{mode}">
<meta property="og:site_name" content="Randhawa">
<meta property="og:image" content="https://prabhchintan.com/social.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="2400">
<meta property="og:image:height" content="1260">
<link rel="canonical" href="https://prabhchintan.com/{mode}">
<style>{self.critical_css}</style>
</head>
<body>
<h1>{title}</h1>
<p>{desc}</p>
<div style="margin:2em 0">
<input type="text" name="url" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" id="honey">
<input type="email" id="email" placeholder="your@email.com" autocomplete="email" style="width:100%;padding:0.4em 0;border:none;border-bottom:1px solid var(--border-color);font-family:var(--font-body);font-size:1em;background:transparent;color:var(--text-color);outline:none;box-sizing:border-box">
<p id="status" style="font-size:0.9em;color:var(--meta-color);min-height:1.4em;margin:0.5em 0"></p>
<p><a href="#" id="submitBtn" style="color:var(--link-color)">{btn_label}</a></p>
</div>
<p><a href="/blog">\u2190 Blog</a></p>
<script>
(function(){{
var emailInput=document.getElementById('email');
var honey=document.getElementById('honey');
var statusEl=document.getElementById('status');
var btn=document.getElementById('submitBtn');
var remove={remove_js};
if(!remove&&localStorage.getItem('subscribed')){{
statusEl.textContent='You are already subscribed. Enter your email again to re-subscribe or visit /unsubscribe.';
}}
btn.addEventListener('click',function(e){{
e.preventDefault();
var email=emailInput.value.trim();
if(!email||!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)){{statusEl.textContent='Please enter a valid email.';return;}}
statusEl.textContent='One moment\u2026';
var body={{email:email,url:honey.value}};
if(remove)body.remove=true;
fetch('/api/subscribe',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(body)}})
.then(function(r){{return r.json();}})
.then(function(d){{
emailInput.value='';
if(remove){{statusEl.textContent='You have been unsubscribed.';localStorage.removeItem('subscribed');}}
else{{statusEl.textContent='You are now subscribed!';localStorage.setItem('subscribed','1');}}
}}).catch(function(){{statusEl.textContent='Something went wrong. Please try again.';}});
}});
emailInput.addEventListener('keydown',function(e){{if(e.key==='Enter'){{e.preventDefault();btn.click();}}}});
}})();
</script>
</body>
</html>'''

            page_html = self.apply_footer(page_html, is_post=False)

            with open(self.site_dir / f'{mode}.html', 'w', encoding='utf-8') as f:
                f.write(page_html)

            log.info(f"Built /{mode} page")

