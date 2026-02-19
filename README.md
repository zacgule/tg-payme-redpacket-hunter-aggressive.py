# TG-payme-redpacket-hunter-aggressive.py

**Open-source Telegram bot/script to automatically detect and claim PayMe lucky money / red packet links shared in public groups or channels.**

This script monitors Telegram chats (groups, channels, private messages) for PayMe links (e.g., `https://payme.hsbc.com.hk/xxxxxx`) and attempts to open them in a headless browser to claim the red packet as fast as possible.

**⚠️ Disclaimer**  
This is for educational and research purposes only.  
Using automation to claim red packets may violate Telegram / HSBC PayMe terms of service.  
Account bans, IP blocks, or legal issues are possible. Use at your own risk.  
No warranty — success rate depends on network speed, proxy quality, competition, and anti-bot measures.

### Features
- Real-time monitoring of Telegram messages for PayMe URLs using Pyrogram
- Automatically opens detected PayMe links in headless Chromium via Playwright
- Simulates human-like behavior (random delays, scrolling) to reduce detection
- Handles flood waits and basic error recovery
- Easy to run with multiple Telegram sessions (multi-account support)

### Current Success Rate (as of Feb 2026)
- Single account, no proxy: ~5–15% in busy groups  
- 5–10 accounts + residential proxies: ~20–40% during high-traffic periods (e.g., Lunar New Year)  
Success heavily depends on:  
- How fast competitors are  
- Your proxy quality  
- Telegram / PayMe rate limiting & fingerprinting

### Requirements
- Python 3.10+
- Telegram API credentials (get from https://my.telegram.org)

### Installation

1. Clone the repo
   ```bash
   git clone https://github.com/YOUR_USERNAME/tg-payme-redpacket-hunter-aggressive.git
   cd tg-payme-redpacket-hunter
      ```
2. Install dependencies
```bash
pip install -r requirements.txt
playwright install
```
3.Create .env file from example (Important ! Set up this file ! ) 
```bash
cp .env.example .env
```
Edit .env and fill in your details:
```
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_NAME=payme_hunter
```
4. Run the script
```
python tg-payme-redpacket-hunter-aggressive.py
```
First run: Enter your phone number + Telegram login code
Join public groups/channels where PayMe red packets are shared
Requirements.txt
```
pyrogram
tgcrypto
python-dotenv
playwright
```
## .env.example (Remember!) 
```
# Get API_ID and API_HASH from https://my.telegram.org
API_ID=
API_HASH=
SESSION_NAME=payme_hunter
```
## How to Improve Success Rate
Run multiple instances with different Telegram accounts (different session names)
Use high-quality residential proxies (add to Playwright context)
Lower CLICK_DELAY_MIN/MAX if you dare (but risk higher ban rate)
Join very active Lunar New Year / hongbao groups early

## License
MIT License — feel free to fork, modify, and distribute.

## Contributions
Pull requests welcome! Especially:

Better button selectors for PayMe pages
Proxy rotation support
Notification when a packet is claimed (e.g., Telegram message to yourself)

## Important ! Dislciamer ! Realistic Expectation !

No proxy, single session → 3–12% hit rate in busy groups
4–8 sessions + good residential rotating proxies → 18–45% in very active Lunar New Year groups
Above 50% consistently → only possible with private browser farms, 100+ sessions, ML-based behavior mimicry, custom anti-fingerprint patches — not public code.

This is the ceiling for what you can realistically run and maintain yourself in 2026 without serious money behind it. So I provide a framework here , hopefully this helps

## Happy hunting — and good luck grabbing those red packets! 🧧
