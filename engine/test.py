import asyncio
from scrapers.hm.scraper import scrape_hm_product

asyncio.run(scrape_hm_product("https://www2.hm.com/en_ca/productpage.1342410001.html"))

