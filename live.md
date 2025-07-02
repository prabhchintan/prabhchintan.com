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
  .twitch-fullscreen-container {
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
  }
  .twitch-fullscreen-container iframe {
    flex: 1 1 auto;
    width: 100vw !important;
    height: 100vh !important;
    border: none;
    display: block;
    margin: 0;
    padding: 0;
  }
  .twitch-link {
    text-align: center;
    font-size: 1em;
    color: #888;
    margin: 0.5em 0 0 0;
    background: none;
  }
</style>

<div class="twitch-fullscreen-container" id="twitchContainer"></div>
<script>
  document.getElementById('twitchContainer').innerHTML = `
    <iframe
      src="https://player.twitch.tv/?channel=prabhchintan&parent=${location.hostname}"
      allowfullscreen
      frameborder="0"
      allow="autoplay; fullscreen"
      title="Twitch Live Stream"
    ></iframe>
  `;
</script>