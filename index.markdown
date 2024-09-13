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
  <div style="position: relative; padding-bottom: 56.25%;">
    <video 
      style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;" 
      controls 
      preload="metadata"
      poster="{{ site.baseurl }}/assets/images/2022-12-25-dar-el-bacha-museum.jpeg">
      <source src="{{ site.baseurl }}/assets/videos/2023-04-09-morocco.mp4" type="video/mp4">
      Your browser does not support the video tag.
    </video>
  </div>
</div>

<style>
  video[poster] {
    object-fit: cover;
  }
</style>
<p style="font-size: 0.8em; font-style; text-align: center;">
  Dar El Bacha Museum, Marrakech, Morocco, December 2022
</p>