---
#
# By default, content added below the "---" mark will appear in the home page
# between the top bar and the list of recent posts.
# To change the home page layout, edit the _layouts/home.html file.
# See: https://jekyllrb.com/docs/themes/#overriding-theme-defaults
#
layout: home
---
<div style="max-width: 800px; margin: 0 auto;">
  <div style="position: relative; padding-bottom: 56.25%;" id="mediaContainer">
    <img 
      id="mainImage"
      src="{{ site.baseurl }}/assets/images/og-image-small.jpg"
      alt="Dar El Bacha Museum, Marrakech"
      style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; display: block;">
    <button id="playTwitch" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: none; border: none; cursor: pointer;">
      <svg width="80" height="80" viewBox="0 0 80 80">
        <circle cx="40" cy="40" r="38" fill="rgba(0,0,0,0.5)" />
        <polygon points="32,25 60,40 32,55" fill="#fff"/>
      </svg>
    </button>
  </div>
</div>

<style>
  #mediaContainer img {
    object-fit: cover;
  }
  #mediaContainer iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: none;
  }
</style>

<script>
  document.getElementById('playTwitch').onclick = function() {
    document.getElementById('mediaContainer').innerHTML = `
      <iframe
        src="https://player.twitch.tv/?channel=prabhchintan&parent=${location.hostname}"
        height="480"
        width="100%"
        allowfullscreen
        frameborder="0"
        style="display:block; margin:0 auto; max-width:900px;">
      </iframe>
    `;
  };
</script>

<p style="font-size: 0.8em; font-style; text-align: center;">
  Dar El Bacha Museum, Marrakech, Morocco, February 2023
</p>