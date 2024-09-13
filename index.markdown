---
#
# By default, content added below the "---" mark will appear in the home page
# between the top bar and the list of recent posts.
# To change the home page layout, edit the _layouts/home.html file.
# See: https://jekyllrb.com/docs/themes/#overriding-theme-defaults
#
layout: home
---
<div style="padding:56.25% 0 0 0;position:relative;">
  <video 
    style="position:absolute;top:0;left:0;width:100%;height:100%;" 
    controls 
    preload="metadata">
    <source src="{{ site.baseurl }}/assets/videos/2023-04-09-morocco.mp4" type="video/mp4">
    Your browser does not support the video tag.
  </video>
</div>

<style>
  video::-webkit-media-controls-panel {
    display: flex !important;
    opacity: 1 !important;
  }
</style>