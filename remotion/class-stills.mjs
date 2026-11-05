// Render storyboard stills with one reused browser. Run from remotion/:
//   node class-stills.mjs <outDir> <rebundle:0|1> <outputSecond> [<outputSecond> ...]
import {bundle} from '@remotion/bundler';
import {openBrowser, renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';

const [outDir, re, ...times] = process.argv.slice(2);
const cacheFile = path.resolve('../renders/day1/bundle-path.txt');
let serveUrl = !Number(re) && fs.existsSync(cacheFile) ? fs.readFileSync(cacheFile, 'utf8').trim() : null;
if (!serveUrl || !fs.existsSync(serveUrl)) {
  serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), publicDir: path.resolve('public')});
  fs.mkdirSync(path.dirname(cacheFile), {recursive: true});
  fs.writeFileSync(cacheFile, serveUrl);
}
fs.mkdirSync(outDir, {recursive: true});
const puppeteerInstance = await openBrowser('chrome', {shouldDumpIo: false});
const composition = await selectComposition({serveUrl, id: 'Day1Class', puppeteerInstance, timeoutInMilliseconds: 120000});
for (const s of times) {
  const frame = Math.round(Number(s) * 30);
  await renderStill({composition, serveUrl, frame, puppeteerInstance, output: `${outDir}/t${s}.jpg`, imageFormat: 'jpeg', jpegQuality: 88, timeoutInMilliseconds: 120000});
  console.log('still', s);
}
await puppeteerInstance.close({silent: true});
