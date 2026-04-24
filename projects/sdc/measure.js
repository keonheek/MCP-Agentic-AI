const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 600 } });
  
  await page.setContent(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 600" width="1400" height="600">
      <text id="s" x="0" y="300" font-family="Georgia, serif" font-size="240" font-weight="bold">S</text>
      <text id="dic" x="0" y="300" font-family="Georgia, serif" font-size="240" font-weight="bold">DIC</text>
    </svg>
  `);

  const sBox = await page.$eval('#s', el => {
    const bb = el.getBBox();
    return { x: bb.x, y: bb.y, width: bb.width, height: bb.height };
  });
  const dicBox = await page.$eval('#dic', el => {
    const bb = el.getBBox();
    return { x: bb.x, y: bb.y, width: bb.width, height: bb.height };
  });

  console.log('S bbox:', JSON.stringify(sBox));
  console.log('DIC bbox:', JSON.stringify(dicBox));
  
  await browser.close();
})();
