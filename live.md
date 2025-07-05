---
layout: page
title: ੧੩.com/live
permalink: /live
redirect_from:
    - /tv
    - /twitch
    - /now
---

<style>
  .stream-fullscreen-container {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    width: 100vw;
    height: 100vh;
    background: #000;
    z-index: 9999;
    margin: 0;
    padding: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }
  .video-js {
    width: 100vw !important;
    height: 100vh !important;
    max-width: 100vw;
    max-height: 100vh;
    background: #000;
    border: none;
    display: block;
    margin: 0;
    padding: 0;
  }
</style>

<div class="stream-fullscreen-container">
  <video-js id="my-video" class="vjs-default-skin" controls preload="auto" data-setup='{}'>
    <source src="http://37.27.197.113/hls/12345.m3u8" type="application/x-mpegURL" />
    <p class="vjs-no-js">
      To view this video please enable JavaScript, and consider upgrading to a web browser that
      supports HTML5 video.
    </p>
  </video-js>
</div>

<link href="https://vjs.zencdn.net/7.20.3/video-js.css" rel="stylesheet" />
<script src="https://vjs.zencdn.net/7.20.3/video.min.js"></script>
<script>
  var player = videojs('my-video');
</script>