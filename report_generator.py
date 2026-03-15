from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted
from reportlab.lib.enums import TA_CENTER
import sqlite3
from pathlib import Path

from config import DB_PATH, REPORT_PDF_PATH
from db_setup import load_csv_to_sqlite
from run_analysis import run_all_queries, get_summary_metrics

def get_table_schema(conn):
    cur = conn.execute("PRAGMA table_info(rides)")
    rows = cur.fetchall()
    return [("Column", "Type")] + [(r[1], r[2]) for r in rows]

def build_report():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    if not Path(DB_PATH).exists():
        load_csv_to_sqlite()
    conn = sqlite3.connect(DB_PATH)
    metrics = get_summary_metrics(conn)
    results = run_all_queries(conn)
    schema = get_table_schema(conn)
    conn.close()

    doc = SimpleDocTemplate(
        REPORT_PDF_PATH,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="ReportTitle",
        parent=styles["Heading1"],
        fontSize=22,
        spaceAfter=20,
        alignment=TA_CENTER,
    )
    h2 = ParagraphStyle(name="H2", parent=styles["Heading2"], fontSize=14, spaceAfter=10)
    body = styles["Normal"]
    flow = []

    flow.append(Paragraph("Ola Rides – Data Analysis Report", title_style))
    flow.append(Spacer(1, 0.3 * inch))
    flow.append(Paragraph("Summary metrics", h2))
    flow.append(Paragraph(
        f"Total bookings: <b>{metrics['total_bookings']:,}</b> | "
        f"Successful rides: <b>{metrics['successful_rides']:,}</b> | "
        f"Success rate: <b>{metrics['success_rate_pct']}%</b> | "
        f"Total revenue: <b>₹{metrics['total_revenue']:,.2f}</b>",
        body,
    ))
    flow.append(Spacer(1, 0.2 * inch))

    flow.append(Paragraph("1. Data structure (rides table)", h2))
    t = Table(schema, colWidths=[3 * inch, 1.5 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    flow.append(t)
    flow.append(Spacer(1, 0.3 * inch))

    flow.append(Paragraph("2. SQL queries and results", h2))
    for r in results:
        flow.append(Paragraph(f"{r['name']}: {r['title']}", h2))
        flow.append(Preformatted(r["sql"], body))
        flow.append(Spacer(1, 0.1 * inch))
        df = r["df"]
        if df.empty:
            flow.append(Paragraph("No rows returned.", body))
        else:
            header = [df.columns.tolist()]
            data = [list(row) for row in df.head(20).itertuples(index=False)]
            if len(df) > 20:
                data.append([f"... and {len(df) - 20} more rows"])
            table_data = header + data
            ncol = len(df.columns)
            col_width = min(1.2, max(0.5, 4.5 / ncol))
            t2 = Table(table_data, colWidths=[col_width * inch] * ncol)
            t2.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498DB")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            flow.append(t2)
        flow.append(Spacer(1, 0.25 * inch))

    flow.append(Paragraph("3. Key insights", h2))
    insights = [
        "Booking status mix shows success vs cancellations and driver not found.",
        "Vehicle type usage: Prime Sedan/SUV and Mini lead; Bike and eBike for shorter trips.",
        "Payment: UPI and Cash dominate; Credit Card is smaller share.",
        "Top pickups and drops show high-demand corridors.",
        "Cancel and incomplete reasons help prioritise operations.",
        "Ratings by vehicle type support quality and allocation.",
        "Daily ride and success/fail counts support trend monitoring.",
    ]
    for s in insights:
        flow.append(Paragraph(f"• {s}", body))
        flow.append(Spacer(1, 0.05 * inch))

    doc.build(flow)
    print(f"Report saved to {REPORT_PDF_PATH}")
    return REPORT_PDF_PATH

if __name__ == "__main__":
    build_report()
