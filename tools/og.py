#!/usr/bin/env python3
"""Render link-preview images (og/*.jpg) and app icons (*.png) from the built site.

    python3 tools/build.py && python3 tools/og.py

Needs Playwright with Chromium (pip install playwright && playwright install chromium).
The images are drawn by the site's own code (window.__pastforward), so they always match the app.
"""
import asyncio, base64, os
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import icon   # tools/icon.py: the one source for every icon
ICONS = [("favicon-32.png", 32, 7, 1.0), ("apple-touch-icon.png", 180, 0, .86), ("icon-192.png", 192, 14, 1.0),
         ("icon-512.png", 512, 14, 1.0), ("icon-maskable-512.png", 512, 0, .72)]


def save(path, data_url):
    with open(path, "wb") as f:
        f.write(base64.b64decode(data_url.split(",", 1)[1]))


async def main():
    os.makedirs(os.path.join(ROOT, "og"), exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1200, "height": 900})
        await page.goto("file://" + os.path.join(ROOT, "index.html"))
        await page.wait_for_function("window.__pastforward && document.fonts && document.fonts.status === 'loaded'")
        await page.evaluate("document.fonts.ready")
        await page.wait_for_timeout(600)
        save(os.path.join(ROOT, "og", "home.jpg"), await page.evaluate("window.__pastforward.ogHome()"))
        ids = await page.evaluate("window.__pastforward.ids()")
        for rid in ids:
            save(os.path.join(ROOT, "og", f"{rid}.jpg"), await page.evaluate(f"window.__pastforward.ogRhyme({rid!r})"))
        for (name, size, rx, k), theme in [(i, t) for t in ("dark", "light") for i in ICONS]:
            svg = icon.svg(theme, rx, k)
            if theme == "light": name = name.replace(".png", "-light.png")
            url = await page.evaluate("""async ([svg, size]) => {
                const img = new Image(); img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
                await img.decode();
                const c = document.createElement('canvas'); c.width = c.height = size;
                c.getContext('2d').drawImage(img, 0, 0, size, size);
                return c.toDataURL('image/png');
            }""", [svg, size])
            save(os.path.join(ROOT, name), url)
        await browser.close()
    print(f"wrote og/home.jpg, {len(ids)} rhyme previews and {2 * len(ICONS)} icons (dark and light)")


asyncio.run(main())
