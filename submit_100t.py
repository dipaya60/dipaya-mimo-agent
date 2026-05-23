#!/usr/bin/env python3
"""
MiMo 100T Program — Auto Submit Script
"""
import asyncio
import argparse
from pathlib import Path
from playwright.async_api import async_playwright, Page

CONFIG = {
    "email": "dipaya60@gmail.com",
    "project_description": "MiMo Agent Advanced is a narrative trade intelligence platform powered by Xiaomi MiMo-V2.5-Pro. The core is an advanced whale tracker with 10 modules: Smart Money Score (wallet profiling 0-100 based on win rate, ROI, timing), Exchange Flow Analysis (CEX inflow/outflow tracking on Binance, Coinbase, OKX), Whale vs Retail Divergence detection (the strongest signal in crypto), Order Book Wall scanning (large limit orders + spoofing risk), Cross-chain Tracking across 7 networks (ETH, SOL, BSC, Arbitrum, Base, Optimism), VC Wallet Tracking (a16z, Paradigm, Coinbase Ventures, Jump), Historical Pattern Matching (compares current behavior to pre-pump/dump patterns), customizable Alert Thresholds (notify when whale buys >$500k), Holder Concentration Index using Gini coefficient (manipulation risk), and Activity Heatmap by hour/day for optimal entry timing. Market data layer uses CoinGecko API (free) for real-time volume and price, with pipelines for Open Interest, Funding Rate, Long/Short Ratio, and Liquidation Levels. MiMo-V2.5-Pro reasoning engine correlates whale behavior with derivatives data to generate actionable narrative trade signals with confidence scores and full reasoning chains. Sentiment analysis aggregates social media and news sources to output trend direction. I use this agent daily for whale tracking and narrative trade signal generation.",
    "github_link": "https://github.com/dipaya60/dipaya-mimo-agent",
    "screenshot_path": "/home/ubuntu/mimo-agent-advanced/assets/demo_v2.png",
    "ai_tools": ["Hermes Agent", "Cursor", "Claude Code"],
    "models": ["MiMo 系列"],
}

async def fill_form(page: Page, dry_run: bool = False):
    print("\n📝 Filling form...\n")
    await page.goto("https://100t.xiaomimimo.com/", wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(3000)

    # Click apply button
    apply_btn = page.locator('button:has-text("立即申请")')
    if await apply_btn.count() > 0:
        await apply_btn.first.click()
        print("  ✅ Clicked apply")
        # Wait for form to load — look for email input or textarea
        try:
            await page.wait_for_selector('input[type="email"], textarea', timeout=15000)
            print("  ✅ Form loaded")
        except:
            await page.wait_for_timeout(5000)
            print("  ⚠️ Form might not have loaded, continuing...")

    # Email
    email_input = page.locator('input[type="email"]')
    if await email_input.count() > 0:
        await email_input.fill(CONFIG["email"])
        print(f"  ✅ Email: {CONFIG['email']}")
    else:
        print("  ⚠️ Email input not found")

    # Description
    textarea = page.locator('textarea')
    if await textarea.count() > 0:
        await textarea.fill(CONFIG["project_description"])
        print(f"  ✅ Description: {len(CONFIG['project_description'])} chars")
    else:
        print("  ⚠️ Textarea not found")

    # AI Tools
    for tool in CONFIG["ai_tools"]:
        btn = page.locator(f'button:has-text("{tool}")')
        if await btn.count() > 0:
            await btn.first.click()
            await page.wait_for_timeout(300)
            print(f"  ✅ Tool: {tool}")

    # Models
    for model in CONFIG["models"]:
        btn = page.locator(f'button:has-text("{model}")')
        if await btn.count() > 0:
            await btn.first.click()
            await page.wait_for_timeout(300)
            print(f"  ✅ Model: {model}")

    # File upload
    uploaded = False
    for sel in ['input[type="file"]', 'input[accept*="image"]']:
        try:
            fi = page.locator(sel)
            if await fi.count() > 0 and Path(CONFIG["screenshot_path"]).exists():
                await fi.first.set_input_files(CONFIG["screenshot_path"])
                await page.wait_for_timeout(2000)
                print(f"  ✅ File: uploaded")
                uploaded = True
                break
        except:
            continue
    if not uploaded:
        print(f"  ⚠️ File upload failed")

    # GitHub link
    url_input = page.locator('input[type="url"]')
    if await url_input.count() > 0:
        await url_input.fill(CONFIG["github_link"])
        print(f"  ✅ GitHub: {CONFIG['github_link']}")
    else:
        print("  ⚠️ URL input not found")

    await page.screenshot(path="/home/ubuntu/mimo-agent-advanced/assets/form_filled.png", full_page=True)
    print(f"\n📸 Preview: assets/form_filled.png")

    if dry_run:
        print("\n🔍 DRY RUN — NOT submitted")
        return

    submit_btn = page.locator('button:has-text("提交")')
    if await submit_btn.count() > 0:
        print("\n🚀 Submitting...")
        await submit_btn.first.click()
        await page.wait_for_timeout(5000)
        await page.screenshot(path="/home/ubuntu/mimo-agent-advanced/assets/form_submitted.png", full_page=True)
        print("✅ Submitted!")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=args.headless, args=["--no-sandbox"])
        ctx = await browser.new_context(viewport={"width": 1280, "height": 900}, locale="zh-CN")
        page = await ctx.new_page()
        try:
            await fill_form(page, dry_run=args.dry_run)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await page.screenshot(path="/home/ubuntu/mimo-agent-advanced/assets/form_error.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
