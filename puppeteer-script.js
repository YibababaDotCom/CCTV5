const fs = require('fs');
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
  headless: true,
  args: ['--no-sandbox', '--disable-setuid-sandbox']
});
  const page = await browser.newPage();
  await page.goto('https://huaren.live/viv/detail/id/536/nid/1.html', { waitUntil: 'networkidle2' });

  const streamUrl = await page.evaluate(() => {
    const scripts = Array.from(document.getElementsByTagName('script'));
    for (const script of scripts) {
      const match = script.textContent.match(/url=(https[^']+)/);
      if (match) return decodeURIComponent(match[1]);
    }
    return null;
  });

  await browser.close();

  if (streamUrl) {
    fs.writeFileSync('latest.m3u8', streamUrl);
    console.log("Saved stream URL to latest.m3u8:", streamUrl);
  } else {
    console.error("Stream URL not found.");
    process.exit(1);
  }
})();
