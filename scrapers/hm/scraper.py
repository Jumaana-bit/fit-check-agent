import sqlite3
import hashlib
from pathlib import Path
from playwright.async_api import async_playwright

# Path to /data/database.db
db_path = Path(__file__).resolve().parents[2] / "data" / "database.db"

# Your real Chrome profile path
CHROME_PROFILE = r"C:/Users/jumia/AppData/Local/Google/Chrome/User Data"


async def scrape_hm_product(url: str):
    """
    H&M scraper using your REAL Chrome profile.
    This bypasses Akamai anti-bot and avoids Access Denied pages.
    """

    async with async_playwright() as p:

        # -----------------------------------------
        # 1. Launch persistent Chrome profile
        # -----------------------------------------
        context = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_PROFILE,
            headless=False,  # MUST be false or H&M blocks you
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--start-maximized",
            ]
        )

        page = await context.new_page()

        # -----------------------------------------
        # 2. Navigate to product page
        # -----------------------------------------
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)  # allow JS to render

        # If Access Denied still appears, detect it
        if "Access Denied" in (await page.content()):
            await context.close()
            return {"error": "Access Denied — H&M blocked even Chrome profile"}

        # -----------------------------------------
        # 3. Extract product name
        # -----------------------------------------
        try:
            await page.wait_for_selector('h1[data-testid="product-name"]', timeout=10000)
            name = await page.text_content("h1")
            name = name.strip() if name else None
        except:
            name = None

        # -----------------------------------------
        # 4. Extract price
        # -----------------------------------------
        price_selectors = [
            "div:has-text('$')",
            "span:has-text('$')",
            "p:has-text('$')",
            ".ProductPrice-module--price__value"
        ]

        price = None
        for sel in price_selectors:
            try:
                price_raw = await page.text_content(sel)
                if price_raw and "$" in price_raw:
                    price = float(price_raw.replace("$", "").strip())
                    break
            except:
                continue

        # -----------------------------------------
        # 5. Extract sizes + stock
        # -----------------------------------------
        await page.click("[data-testid='size-selector']")
        await page.wait_for_timeout(1500)

        size_elements = await page.query_selector_all("div[role='radio']")
        sizes = []

        for el in size_elements:
            label = await el.get_attribute("aria-label")
            # Example: "Size XXS: Available. Select the size."
            if label:
                # Extract the size text
                size = label.split(" ")[1]  # XXS, XS, S, etc.
                in_stock = 1 if "Available" in label else 0
                sizes.append((size, in_stock))


        # -----------------------------------------
        # 6. Optional measurements (H&M rarely provides)
        # -----------------------------------------
        measurements = {
            "bust": None,
            "waist": None,
            "hip": None,
            "shoulder": None,
            "sleeve": None,
            "length": None
        }
        print("Product name:", name)
        print("Price:", price)
        print("Sizes:", sizes)

        await context.close()

    # -----------------------------------------
    # 7. Product ID (hash of URL)
    # -----------------------------------------
    product_id = hashlib.md5(url.encode()).hexdigest()

    # -----------------------------------------
    # 8. Insert into DB
    # -----------------------------------------
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    for size_label, in_stock in sizes:
        cur.execute("""
            INSERT INTO products (store, product_id, name, url, price, size, in_stock)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "H&M",
            product_id,
            name,
            url,
            price,
            size_label,
            in_stock
        ))

        cur.execute("""
            INSERT INTO snapshots (product_id, in_stock, price)
            VALUES (?, ?, ?)
        """, (
            cur.lastrowid,
            in_stock,
            price
        ))

    conn.commit()
    conn.close()

    # -----------------------------------------
    # 9. Return scraped data
    # -----------------------------------------
    return {
        "product_id": product_id,
        "name": name,
        "price": price,
        "sizes": sizes,
        "measurements": measurements
    }


# Local test
if __name__ == "__main__":
    import asyncio
    TEST_URL = "https://www2.hm.com/en_ca/productpage.1342410001.html"
    print(asyncio.run(scrape_hm_product(TEST_URL)))
