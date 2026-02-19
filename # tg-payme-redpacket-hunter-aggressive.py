# tg-payme-redpacket-hunter-aggressive.py
# Strongest realistic public version — multi-account, proxy support, stealth, fast claiming
# Requirements: pip install pyrogram tgcrypto python-dotenv playwright httpx tenacity
# playwright install --with-deps chromium
# Use high-quality residential proxies (rotating) — mandatory for decent hit rate

import asyncio
import random
import re
import os
import httpx
from datetime import datetime
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from playwright.async_api import async_playwright, BrowserContext, ProxySettings
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAMES = os.getenv("SESSION_NAMES", "hunter1,hunter2,hunter3").split(",")  # comma separated session names
PROXY_URL = os.getenv("PROXY_URL")  # format: http://user:pass@ip:port  or socks5://...

# PayMe link regex - covers most variants seen in 2025–2026
PAYME_REGEX = re.compile(r'https?://(?:payme\.hsbc\.com\.hk|pay\.me)/[a-zA-Z0-9\-_?=&]+', re.IGNORECASE)

# Tunable parameters — lower = faster but higher ban risk
MIN_CLICK_DELAY = 0.35
MAX_CLICK_DELAY = 1.20
GOTO_TIMEOUT = 12000  # ms

# Shared playwright instance (reuse browser)
playwright = None
browser = None

async def init_browser():
    global playwright, browser
    playwright = await async_playwright().start()
    proxy: ProxySettings | None = None
    if PROXY_URL:
        proxy = {"server": PROXY_URL}
    browser = await playwright.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
            "--window-size=1280,800",
        ]
    )
    print("[INIT] Stealth browser ready" + (f" with proxy {PROXY_URL}" if proxy else ""))

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
)
async def claim_payme_link(context: BrowserContext, url: str, session_name: str):
    page = await context.new_page()
    try:
        # Spoof common fingerprint signals
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            window.chrome = { runtime: {} };
        """)

        print(f"[{session_name}] Attempting → {url}")
        response = await page.goto(url, wait_until="networkidle", timeout=GOTO_TIMEOUT)

        if not response or response.status != 200:
            print(f"[{session_name}] Bad response {response.status if response else 'None'}")
            return False

        await asyncio.sleep(random.uniform(0.4, 1.1))  # human pause

        # Try multiple selectors — PayMe pages change often
        selectors = [
            'button:has-text("領取")',
            'button:has-text("Claim")',
            'button[aria-label*="claim" i]',
            '[role="button"]:has-text("領取")',
            'div[role="button"]:has-text("領取")',
            'button[type="submit"]',
            '#claim-button',
        ]

        claimed = False
        for sel in selectors:
            btn = await page.query_selector(sel)
            if btn:
                await asyncio.sleep(random.uniform(MIN_CLICK_DELAY, MAX_CLICK_DELAY))
                await btn.click(force=True)
                print(f"[{session_name}] CLICKED selector: {sel} → {url}")
                claimed = True
                await asyncio.sleep(1.5)  # wait for possible redirect/confirmation
                break

        if not claimed:
            # Last resort: click anything that looks clickable with "領" or "claim"
            possible = await page.query_selector_all('button, [role="button"], div[onclick], a[href*="claim"]')
            for el in possible[:3]:  # don't click everything
                text = await el.inner_text()
                if "領" in text or "claim" in text.lower():
                    await el.click(force=True)
                    print(f"[{session_name}] Fallback click on text: {text.strip()[:30]}")
                    claimed = True
                    break

        if claimed:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("claimed_log.txt", "a", encoding="utf-8") as f:
                f.write(f"{ts} | {session_name} | SUCCESS | {url}\n")
            await page.screenshot(path=f"success_{ts.replace(' ','_').replace(':','-')}.png")

        return claimed

    except Exception as e:
        print(f"[{session_name}] ERROR on {url}: {str(e)[:120]}")
        return False
    finally:
        await page.close()

async def main():
    await init_browser()

    clients = []
    contexts = []

    for name in SESSION_NAMES:
        cl = Client(
            name.strip(),
            api_id=API_ID,
            api_hash=API_HASH,
        )
        await cl.start()
        clients.append(cl)
        print(f"[TG] Started session: {name}")

        # Each session gets its own browser context (helps with fingerprint isolation)
        ctx = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="zh-HK",
            timezone_id="Asia/Hong_Kong",
            # proxy already set at browser level if used
        )
        contexts.append(ctx)

    print("\n" + "="*60)
    print(" Aggressive PayMe Hunter 2026 — monitoring all sessions...")
    print(" Log saved to claimed_log.txt | Screenshots on success")
    print("="*60 + "\n")

    async def handler(client: Client, message: Message, idx: int):
        text = message.text or message.caption or ""
        links = PAYME_REGEX.findall(text)
        if not links:
            return

        session_name = SESSION_NAMES[idx]
        print(f"[{session_name}] DETECTED {len(links)} PayMe link(s) in {message.chat.title or 'PM'}")

        tasks = []
        for link in links:
            tasks.append(claim_payme_link(contexts[idx], link, session_name))

        await asyncio.gather(*tasks, return_exceptions=True)

    # Register handlers for every client
    for i, cl in enumerate(clients):
        cl.on_message(filters.text)(lambda c, m, idx=i: handler(c, m, idx))

    # Keep alive forever
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        if browser:
            asyncio.run(browser.close())
        if playwright:
            asyncio.run(playwright.stop())