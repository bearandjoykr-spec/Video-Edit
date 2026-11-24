import { createStage, makeFilm, boot } from './kit.js';
import { buildStory, ASSETS } from './story.js';
import B from './beats.json';

// fonts and the book art must be in before the story draws its paper textures
(async () => {
  try { await Promise.all(['700 40px Gaegu', '400 40px PatrickHand', '600 40px Title', '400 40px Brush', '700 40px Batang'].map(f => document.fonts.load(f))); } catch (e) {}
  const IMG = {};
  await Promise.all(Object.entries(ASSETS).map(([k, url]) => new Promise(res => {
    const im = new Image(); im.onload = () => { IMG[k] = im; res(); }; im.onerror = () => { console.error('asset failed', k); res(); }; im.src = url;
  })));
  const stage = createStage({ video: { width: B.width, height: B.height, fps: B.fps, duration: B.duration }, exposure: 1.0 });
  const story = buildStory(stage, B, IMG);
  const film = makeFilm(stage, story);
  boot(film, stage, story);
})();
