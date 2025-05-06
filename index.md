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
    <video 
      id="mainVideo"
      style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;" 
      controls 
      preload="metadata"
      poster="{{ site.baseurl }}/assets/images/og-image.jpg">
      <source src="{{ site.baseurl }}/assets/videos/2022-12-25-dar-el-bacha-museum.mp4" type="video/mp4">
      Your browser does not support the video tag.
    </video>
  </div>
</div>

<style>
  video[poster] {
    object-fit: cover;
  }
  iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: none;
  }
</style>

<script>
document.getElementById('mainVideo').addEventListener('ended', function() {
    const container = document.getElementById('mediaContainer');
    const video = document.getElementById('mainVideo');
    
    // Create Twitch embed
    const embed = document.createElement('iframe');
    embed.src = "https://player.twitch.tv/?channel=prabhchintan&parent=" + window.location.hostname;
    embed.allowFullscreen = true;
    
    // Replace video with Twitch embed
    video.style.display = 'none';
    container.appendChild(embed);
});
</script>

<p style="font-size: 0.8em; font-style; text-align: center;">
  Dar El Bacha Museum, Marrakech, Morocco, February 2023
</p>