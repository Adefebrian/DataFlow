import asyncio
from playwright.async_api import async_playwright
import requests

async def main():
    r = requests.post('http://localhost:8000/auth/login', json={'username':'admin', 'password':'admin123'})
    api_key = r.json()['api_key']
    r2 = requests.get('http://localhost:8000/pipeline/all', headers={'X-API-Key':api_key})
    job_id = r2.json()[0]['job_id']
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_init_script(f"localStorage.setItem('apiKey', '{api_key}'); localStorage.setItem('isAuthenticated', 'true');")
        page = await context.new_page()
        
        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
        
        await page.goto(f"http://localhost:3000/job/{job_id}")
        await page.wait_for_timeout(3000)
        await browser.close()

asyncio.run(main())
