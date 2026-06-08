from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


db_path = Path(__file__).resolve().parents[1] / "data" / "database.db"

class Measurement(BaseModel):
    height: float
    weight: float
    bust: float
    waist: float
    hip: float
    shoulder: float
    sleeve: float

@app.post("/save-measurements")
def save_measurements(m: Measurement):
    print("Received:", m)

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        print("DB Path:", db_path)

        cur.execute("""
            INSERT INTO measurements (user_id, height, weight, bust, waist, hip, shoulder, sleeve)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, m.height, m.weight, m.bust, m.waist, m.hip, m.shoulder, m.sleeve))

        conn.commit()
        conn.close()

        print("Insert complete")

        return {"message": "Measurements saved successfully!"}

    except Exception as e:
        print("ERROR:", e)
        return {"message": f"Error: {e}"}

@app.get("/api/products")
def get_products(store: str, size: str = "XS", user_id: int = 1):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. Load user measurements
    cur.execute("""
        SELECT height, weight, bust, waist, hip, shoulder, sleeve
        FROM measurements
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id,))
    row = cur.fetchone()

    if not row:
        return {"error": "No measurements found"}

    user_measurements = {
        "height": row[0],
        "weight": row[1],
        "bust": row[2],
        "waist": row[3],
        "hip": row[4],
        "shoulder": row[5],
        "sleeve": row[6]
    }

    # 2. Load products
    cur.execute("""
        SELECT id, product_id, name, url, price, size, in_stock
        FROM products
        WHERE store = ? AND size = ?
        ORDER BY created_at DESC
    """, (store, size))

    rows = cur.fetchall()
    conn.close()

    # 3. Compute fit score for each product
    from engine.fit_engine import compute_fit_score

    results = []
    for row in rows:
        db_id, product_id, name, url, price, size_label, in_stock = row

        score, explanation = compute_fit_score(store, size_label, user_measurements)

        results.append({
            "id": db_id,
            "product_id": product_id,
            "name": name,
            "url": url,
            "price": price,
            "size": size_label,
            "in_stock": bool(in_stock),
            "fit_score": score,
            "fit_explanation": explanation
        })

    return results

@app.get("/api/scrape")
async def scrape(store: str, url: str):
    store = store.lower().strip()

    if store == "hm":
        try:
            from scrapers.hm.scraper import scrape_hm_product
            result = await scrape_hm_product(url)

            # If scraper returns an anti‑bot error
            if isinstance(result, dict) and result.get("error"):
                return {
                    "status": "blocked",
                    "message": "H&M blocked the scraper. Try again or use a different URL.",
                    "details": result
                }

            return {
                "status": "success",
                "store": "H&M",
                "url": url,
                "data": result
            }

        except Exception as e:
            return {
                "status": "error",
                "message": "Scraper crashed",
                "details": str(e)
            }

    return {"error": f"Store '{store}' not supported yet"}

@app.get("/api/history")
def get_history(product_id: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT in_stock, price, timestamp
        FROM snapshots
        WHERE product_id = ?
        ORDER BY timestamp ASC
    """, (product_id,))

    rows = cur.fetchall()
    conn.close()

    return [
        {"in_stock": r[0], "price": r[1], "timestamp": r[2]}
        for r in rows
    ]
