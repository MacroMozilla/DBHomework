from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import psycopg2
from contextlib import contextmanager
from pathlib import Path

app = FastAPI()


@app.get("/")
async def home():
    """a) Start page with search form."""
    html = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")
    from fastapi.responses import HTMLResponse
    return HTMLResponse(html)

# Update these to match your PostgreSQL settings
DB_CONFIG = {
    "dbname": "hw3",
    "user": "admin",
    "password": "pass",
    "host": "localhost",
    "port": 5432,
}


@contextmanager
def get_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SET search_path TO q1")
    cur.close()
    try:
        yield conn
    finally:
        conn.close()



@app.get("/api/flights")
async def api_search_flights(origin: str, destination: str, date_from: str, date_to: str):
    """b) Return matching flights as JSON."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT f.flight_number,
                   f.departure_date,
                   fs.origin_code,
                   fs.dest_code,
                   fs.departure_time
            FROM Flight f
                     JOIN FlightService fs ON f.flight_number = fs.flight_number
            WHERE fs.origin_code = %s
              AND fs.dest_code = %s
              AND f.departure_date BETWEEN %s AND %s
            ORDER BY f.departure_date, fs.departure_time
            """,
            (origin.upper(), destination.upper(), date_from, date_to),
        )
        rows = cur.fetchall()

    flights = [
        {
            "flight_number": r[0],
            "departure_date": r[1].isoformat(),
            "origin_code": r[2],
            "dest_code": r[3],
            "departure_time": r[4].strftime("%H:%M"),
        }
        for r in rows
    ]
    return JSONResponse(flights)


@app.get("/api/flight/{flight_number}/{departure_date}")
async def api_flight_detail(flight_number: str, departure_date: str):
    """c) Return seat availability as JSON."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.capacity, a.plane_type
            FROM Flight f
                     JOIN Aircraft a ON f.plane_type = a.plane_type
            WHERE f.flight_number = %s
              AND f.departure_date = %s
            """,
            (flight_number, departure_date),
        )
        row = cur.fetchone()
        if not row:
            return JSONResponse({"error": "Flight not found"}, status_code=404)
        capacity, plane_type = row

        cur.execute(
            """
            SELECT COUNT(*)
            FROM Booking
            WHERE flight_number = %s
              AND departure_date = %s
            """,
            (flight_number, departure_date),
        )
        booked = cur.fetchone()[0]

        cur.execute(
            """
            SELECT fs.airline_name,
                   fs.origin_code,
                   fs.dest_code,
                   fs.departure_time,
                   fs.duration
            FROM FlightService fs
            WHERE fs.flight_number = %s
            """,
            (flight_number,),
        )
        fs = cur.fetchone()

    return JSONResponse({
        "flight_number": flight_number,
        "departure_date": departure_date,
        "plane_type": plane_type,
        "capacity": capacity,
        "booked": booked,
        "available": capacity - booked,
        "airline": fs[0],
        "origin": fs[1],
        "dest": fs[2],
        "departure_time": fs[3].strftime("%H:%M"),
        "duration": str(fs[4]),
    })
