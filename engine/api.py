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

