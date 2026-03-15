import sqlite3
import re
from pathlib import Path
from config import DB_PATH

QUERIES_FILE = Path(__file__).parent / "queries.sql"

def get_connection():
    return sqlite3.connect(DB_PATH)

def parse_queries(sql_path: Path):
    text = sql_path.read_text(encoding="utf-8")
    blocks = re.split(r"\n-- (Q\d+):", text)
    out = []
    for i in range(1, len(blocks) - 1, 2):
        name = blocks[i].strip()
        rest = blocks[i + 1].strip()
        first_line = rest.split("\n")[0].strip()
        title = first_line
        sql = "\n".join(rest.split("\n")[1:]).strip()
        if sql:
            out.append((name, title, sql))
    return out

def run_all_queries(conn=None):
    import pandas as pd
    close = False
    if conn is None:
        conn = get_connection()
        close = True
    try:
        parsed = parse_queries(QUERIES_FILE)
        results = []
        for name, title, sql in parsed:
            df = pd.read_sql_query(sql, conn)
            results.append({"name": name, "title": title, "sql": sql, "df": df})
        return results
    finally:
        if close:
            conn.close()

def get_summary_metrics(conn=None):
    import pandas as pd
    close = False
    if conn is None:
        conn = get_connection()
        close = True
    try:
        df = pd.read_sql_query(
            "SELECT Booking_Status, COUNT(*) AS c FROM rides GROUP BY Booking_Status",
            conn,
        )
        total = df["c"].sum()
        success = df[df["Booking_Status"] == "Success"]["c"].values
        success_count = int(success[0]) if len(success) else 0
        revenue_df = pd.read_sql_query(
            """SELECT SUM(CAST(Booking_Value AS REAL)) AS total
               FROM rides WHERE Booking_Status = 'Success' AND Booking_Value != '' AND Booking_Value IS NOT NULL""",
            conn,
        )
        total_revenue = float(revenue_df["total"].iloc[0] or 0)
        return {
            "total_bookings": int(total),
            "successful_rides": success_count,
            "success_rate_pct": round(100.0 * success_count / total, 2) if total else 0,
            "total_revenue": round(total_revenue, 2),
        }
    finally:
        if close:
            conn.close()

if __name__ == "__main__":
    from db_setup import load_csv_to_sqlite
    load_csv_to_sqlite()
    results = run_all_queries()
    for r in results:
        print(r["name"], r["title"])
        print(r["df"].head())
        print("---")
