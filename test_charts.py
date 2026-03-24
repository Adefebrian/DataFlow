"""
Playwright QA Test - Charts Page
================================

Focus on testing chart display
"""

import asyncio
from playwright.async_api import async_playwright
import requests

API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"
USERNAME = "admin"
PASSWORD = "admin123"


async def test_charts():
    """Test charts page specifically"""

    # Get API key
    print("Getting API token...")
    response = requests.post(
        f"{API_BASE}/auth/login", json={"username": USERNAME, "password": PASSWORD}
    )
    api_key = response.json().get("api_key", "")

    # Get job ID
    print("Getting job ID...")
    response = requests.get(f"{API_BASE}/pipeline/all", headers={"X-API-Key": api_key})
    jobs = response.json()
    job_id = jobs[0].get("job_id") if jobs else None
    print(f"  Job ID: {job_id}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Run with UI for debugging
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})

        # Add API key to localStorage
        await context.add_init_script(f"""
            localStorage.setItem('apiKey', '{api_key}');
        """)

        page = await context.new_page()

        # Navigate to login first
        print("\nNavigating to login...")
        await page.goto(f"{FRONTEND_BASE}/login")
        await page.wait_for_load_state("networkidle")

        # Fill login form
        username_input = await page.query_selector(
            'input[type="text"], input[name="username"]'
        )
        password_input = await page.query_selector('input[type="password"]')

        if username_input and password_input:
            await username_input.fill(USERNAME)
            await password_input.fill(PASSWORD)

            login_btn = await page.query_selector('button[type="submit"]')
            if login_btn:
                await login_btn.click()
                await page.wait_for_timeout(3000)

        # Navigate to job detail page
        if job_id:
            print(f"\nNavigating to job detail: {job_id}")
            await page.goto(f"{FRONTEND_BASE}/jobs/{job_id}")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)

            # Take screenshot of overview
            await page.screenshot(
                path="/Users/brianeedsleep/Documents/Vibecode/test_screenshots/job_overview.png"
            )
            print("  Screenshot: job_overview.png")

            # Find and click Charts tab
            print("\nLooking for Charts tab...")
            tabs = await page.query_selector_all("button")
            for tab in tabs:
                text = await tab.text_content()
                if text and "charts" in text.lower():
                    print(f"  Found tab: {text}")
                    await tab.click()
                    await page.wait_for_timeout(3000)
                    break

            # Take screenshot of charts tab
            await page.screenshot(
                path="/Users/brianeedsleep/Documents/Vibecode/test_screenshots/job_charts.png"
            )
            print("  Screenshot: job_charts.png")

            # Check for images
            images = await page.query_selector_all("img")
            print(f"\n  Found {len(images)} images on page")

            for i, img in enumerate(images):
                src = await img.get_attribute("src")
                if src:
                    print(f"    Image {i + 1}: {src[:50]}...")

            # Check for chart titles
            h2_elements = await page.query_selector_all("h2")
            print(f"\n  Found {len(h2_elements)} h2 elements:")
            for h2 in h2_elements:
                text = await h2.text_content()
                print(f"    - {text}")

        # Keep browser open for inspection
        print("\nBrowser will stay open for 30 seconds for inspection...")
        await page.wait_for_timeout(30000)

        await browser.close()


if __name__ == "__main__":
    import os

    os.makedirs(
        "/Users/brianeedsleep/Documents/Vibecode/test_screenshots", exist_ok=True
    )
    asyncio.run(test_charts())
