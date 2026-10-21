#!/usr/bin/env python3
"""Render link-preview images (og/*.jpg) and app icons (*.png) from the built site.

    python3 tools/build.py && python3 tools/og.py

Needs Playwright with Chromium (pip install playwright && playwright install chromium).
The images are drawn by the site's own code (window.__pastforward), so they always match the app.
"""
import asyncio, base64, os
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="{rx}" fill="#0C0A1D"/>
<g transform="translate(32 32) scale({k}) translate(-32 -32)">
<path d="M10 44 Q21 18 32 40 Q43 62 54 22" fill="none" stroke="#CDB9FF" stroke-width="4" stroke-linecap="round"/>
<circle cx="10" cy="44" r="5" fill="#E2B35E"/><circle cx="32" cy="40" r="5" fill="#72D3C5"/><circle cx="54" cy="22" r="6" fill="#CDB9FF"/>
</g></svg>"""
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
        for name, size, rx, k in ICONS:
            svg = ICON.format(rx=rx, k=k)
            url = await page.evaluate("""async ([svg, size]) => {
                const img = new Image(); img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
                await img.decode();
                const c = document.createElement('canvas'); c.width = c.height = size;
                c.getContext('2d').drawImage(img, 0, 0, size, size);
                return c.toDataURL('image/png');
            }""", [svg, size])
            save(os.path.join(ROOT, name), url)
        await browser.close()
    print(f"wrote og/home.jpg, {len(ids)} rhyme previews and {len(ICONS)} icons")


asyncio.run(main())
