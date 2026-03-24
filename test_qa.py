"""
Playwright QA Test for DataFlow Analytics Platform
==================================================

Automated testing of chart pages and functionality
"""

import asyncio
from playwright.async_api import async_playwright
import json
import time
import requests

API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"
USERNAME = "admin"
PASSWORD = "admin123"


async def run_qa_tests():
    """Run comprehensive QA tests"""

    # First, get a valid job ID via API
    print("Getting API token...")
    try:
        response = requests.post(
            f"{API_BASE}/auth/login", json={"username": USERNAME, "password": PASSWORD}
        )
        api_key = response.json().get("api_key", "")
        print(f"  API Key obtained: {api_key[:20]}...")
    except Exception as e:
        print(f"  Failed to get API key: {e}")
        api_key = ""

    # Get existing jobs
    print("Getting existing jobs...")
    try:
        response = requests.get(
            f"{API_BASE}/pipeline/all", headers={"X-API-Key": api_key}
        )
        jobs = response.json() if response.status_code == 200 else []
        print(f"  Found {len(jobs)} jobs")
        job_id = jobs[0].get("job_id") if jobs else None
    except Exception as e:
        print(f"  Failed to get jobs: {e}")
        job_id = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})

        # Add API key to localStorage
        await context.add_init_script(f"""
            localStorage.setItem('apiKey', '{api_key}');
        """)

        page = await context.new_page()

        print("\n" + "=" * 60)
        print("DataFlow Analytics Platform - QA Test Suite")
        print("=" * 60)

        # Test 1: Login
        print("\n[TEST 1] Testing Login...")
        try:
            await page.goto(f"{FRONTEND_BASE}/login")
            await page.wait_for_load_state("networkidle")

            # Fill login form
            username_input = await page.query_selector(
                'input[type="text"], input[name="username"], input[placeholder*="username" i]'
            )
            password_input = await page.query_selector(
                'input[type="password"], input[name="password"]'
            )

            if username_input and password_input:
                await username_input.fill(USERNAME)
                await password_input.fill(PASSWORD)

                # Click login button
                login_btn = await page.query_selector(
                    'button[type="submit"], button:has-text("Login"), button:has-text("Sign In")'
                )
                if login_btn:
                    await login_btn.click()
                    await page.wait_for_timeout(3000)

                print("  [PASS] Login form submitted")
            else:
                print("  [INFO] Login form not found, may already be logged in")

            await page.screenshot(
                path="/Users/brianeedsleep/Documents/Vibecode/test_screenshots/01_login.png"
            )
        except Exception as e:
            print(f"  [FAIL] Login failed: {e}")
            await page.screenshot(
                path="/Users/brianeedsleep/Documents/Vibecode/test_screenshots/01_login_error.png"
            )

        # Test 2: Navigate to Dashboard
        print("\n[TEST 2] Testing Dashboard Navigation...")
        try:
            await page.goto(f"{FRONTEND_BASE}/dashboard")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)
            print("  [PASS] Dashboard loaded")
            await page.screenshot(
                path="/Users/brianeedsleep/Documents/Vibecode/test_screenshots/02_dashboard.png"
            )
        except Exception as e:
            print(f"  [FAIL] Dashboard failed: {e}")

        # Test 3: Navigate directly to job detail page
        if job_id:
            print(f"\n[TEST 3] Testing Job Detail Page (ID: {job_id})...")
            try:
                await page.goto(f"{FRONTEND_BASE}/jobs/{job_id}")
                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(3000)

                print("  [PASS] Job detail page loaded")
                await page.screenshot(
                    path="/Users/brianeedsleep/Documents/Vibecode/test_screenshots/03_job_detail.png"
                )

                # Check for stages
                stage_elements = await page.query_selector_all(
                    '[class*="stage"], [class*="badge"]'
                )
                print(f"  [INFO] Found {len(stage_elements)} stage elements")

            except Exception as e:
                print(f"  [FAIL] Job detail failed: {e}")
                await page.screenshot(
                    path="/Users/brianeedsleep/Documents/Vibecode/test_screenshots/03_job_error.png"
                )
        else:
            print("\n[TEST 3] Skipping job detail test - no job ID")

        # Test 4: Charts Tab
        print("\n[TEST 4] Testing Charts Tab...")
        try:
            # Look for charts tab button
            charts_tab = await page.query_selector('button:has-text("Charts")')
            if charts_tab:
                await charts_tab.click()
                await page.wait_for_timeout(3000)
                print("  [PASS] Charts tab clicked")
            else:
                print("  [INFO] Charts tab button not found, checking current view")

            # Check for chart images
            chart_images = await page.query_selector_all(
                'img[src*="base64"], img[src*="data:image"]'
            )
            print(f"  [INFO] Found {len(chart_images)} chart images")

            # Check for chart containers
            chart_containers = await page.query_selector_all(
                '[class*="chart"], [class*="glass"]'
            )
            print(f"  [INFO] Found {len(chart_containers)} chart containers")

            # Check for any image elements
            all_images = await page.query_selector_all("img")
            print(f"  [INFO] Found {len(all_images)} total images on page")

            await page.screenshot(
                path="/Users/brianeedsleep/Documents/Vibecode/test_screenshots/04_charts.png"
            )

            if len(chart_images) > 0:
                print("  [PASS] Charts are rendering")
            else:
                print("  [WARN] No chart images found on page")

                # Check page content for debugging
                content = await page.content()
                if "base64" in content:
                    print("  [INFO] Found base64 content in HTML")
                if "Executive Dashboard" in content:
                    print("  [INFO] Found 'Executive Dashboard' text")

        except Exception as e:
            print(f"  [FAIL] Charts tab failed: {e}")
            await page.screenshot(
                path="/Users/brianeedsleep/Documents/Vibecode/test_screenshots/04_charts_error.png"
            )

        # Test 5: Overview Tab
        print("\n[TEST 5] Testing Overview Tab...")
        try:
            overview_tab = await page.query_selector('button:has-text("Overview")')
            if overview_tab:
                await overview_tab.click()
                await page.wait_for_timeout(2000)
                print("  [PASS] Overview tab clicked")

            await page.screenshot(
                path="/Users/brianeedsleep/Documents/Vibecode/test_screenshots/05_overview.png"
            )
        except Exception as e:
            print(f"  [FAIL] Overview tab failed: {e}")

        # Test 6: Insights Tab
        print("\n[TEST 6] Testing Insights Tab...")
        try:
            insights_tab = await page.query_selector('button:has-text("Insights")')
            if insights_tab:
                await insights_tab.click()
                await page.wait_for_timeout(2000)
                print("  [PASS] Insights tab clicked")

            await page.screenshot(
                path="/Users/brianeedsleep/Documents/Vibecode/test_screenshots/06_insights.png"
            )
        except Exception as e:
            print(f"  [FAIL] Insights tab failed: {e}")

        # Test 7: Analytics Tab
        print("\n[TEST 7] Testing Analytics Tab...")
        try:
            analytics_tab = await page.query_selector('button:has-text("Analytics")')
            if analytics_tab:
                await analytics_tab.click()
                await page.wait_for_timeout(2000)
                print("  [PASS] Analytics tab clicked")

            await page.screenshot(
                path="/Users/brianeedsleep/Documents/Vibecode/test_screenshots/07_analytics.png"
            )
        except Exception as e:
            print(f"  [FAIL] Analytics tab failed: {e}")

        # Test 8: Console Errors Check
        print("\n[TEST 8] Checking for Console Errors...")
        console_messages = []
        page.on(
            "console",
            lambda msg: console_messages.append({"type": msg.type, "text": msg.text}),
        )

        await page.reload()
        await page.wait_for_timeout(3000)

        errors = [m for m in console_messages if m["type"] == "error"]
        if errors:
            print(f"  [WARN] Found {len(errors)} console errors:")
            for error in errors[:5]:
                print(f"    - {error['text'][:100]}")
        else:
            print("  [PASS] No console errors found")

        # Summary
        print("\n" + "=" * 60)
        print("QA Test Summary")
        print("=" * 60)
        print(f"Job ID tested: {job_id or 'None'}")
        print(
            f"Screenshots saved to: /Users/brianeedsleep/Documents/Vibecode/test_screenshots/"
        )
        print("\nTest completed!")

        await browser.close()


if __name__ == "__main__":
    import os

    os.makedirs(
        "/Users/brianeedsleep/Documents/Vibecode/test_screenshots", exist_ok=True
    )

    asyncio.run(run_qa_tests())
