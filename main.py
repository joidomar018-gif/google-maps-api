from fastapi import FastAPI, Query
from playwright.async_api import async_playwright
import urllib.parse

app = FastAPI()

@app.get("/")
def home():
    return {"status": "API is running successfully!"}

@app.get("/search")
async def search_places(q: str = Query(..., description="Search query"), limit: int = 20):
    results = []
    encoded_query = urllib.parse.quote(q)
    url = f"https://www.google.com/maps/search/{encoded_query}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(3000)

        items = await page.query_selector_all('div[role="feed"] > div')
        for item in items[:limit]:
            try:
                text = await item.inner_text()
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                if lines:
                    results.append({"raw_data": lines})
            except Exception:
                continue

        await browser.close()
        
    return {"query": q, "count": len(results), "data": results}
