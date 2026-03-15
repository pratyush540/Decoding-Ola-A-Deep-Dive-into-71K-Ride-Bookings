# 🚗 Ola Ride Booking Data Analysis

A data analysis project exploring **71,201 Ola ride bookings** to uncover insights on ride success rates, cancellations, revenue patterns, and customer behavior.

---

## 📊 Project Overview

This project analyzes ride booking data using **SQL and Python** to generate business insights for operational improvement.

The analysis focuses on:

* Booking success vs failure trends
* Revenue distribution by vehicle type and payment method
* Customer and driver cancellation patterns
* Geographic demand for pickup and drop locations
* Driver and customer rating performance

---

## 📈 Key Metrics

| Metric                | Value        |
| --------------------- | ------------ |
| Total Bookings        | 71,201       |
| Successful Rides      | 44,271       |
| Success Rate          | 62.18%       |
| Total Revenue         | ₹24,216,619  |
| Average Booking Value | ₹547         |
| Total Distance        | 1,011,524 km |
| Average Ride Distance | 22.85 km     |

---

## 🔍 Key Insights

**Operational Insights**

* 37.8% of bookings fail due to cancellations or driver unavailability.
* Driver-side cancellations are the largest contributor.

**Revenue Insights**

* Premium vehicles such as **Prime Sedan** generate higher average booking value.
* **Cash payments dominate (54.6%)**, followed by **UPI (40.5%)**.

**Customer Behavior**

* Top pickup location: **Banashankari**
* Top drop location: **Mysore Road**
* Common customer complaint: driver not moving toward pickup location.

---

## 🧰 Technologies Used

* **SQL** – Data querying and analysis
* **Python (Pandas, NumPy)** – Data processing
* **Streamlit** – Interactive dashboard
* **Power BI / PPT** – Data visualization and reporting
* **Git & GitHub** – Version control

---

## 📂 Project Structure

```
ola-rides-analysis
│
├── data
│   └── ola.csv
│
├── analysis
│   ├── sql_queries.sql
│   └── data_processing.py
│
├── dashboard
│   └── app.py
│
├── visualizations
│   └── Ola-Rides-Data-Analysis.pptx
│
└── README.md
```

---

## 🚀 How to Run

Clone the repository

```bash
git clone https://github.com/pratyush540/ola-rides-analysis.git
cd ola-rides-analysis
```

Run SQL queries

```bash
sqlite3 ola_rides.db
.read analysis/sql_queries.sql
```

Run the Streamlit dashboard

```bash
cd dashboard
streamlit run app.py
```

---

## 📌 Business Recommendations

* Improve driver availability to reduce booking failures
* Introduce incentives for drivers to move toward pickup faster
* Promote **digital payments (UPI/cards)** to reduce cash dependency
* Deploy more drivers in high-demand pickup zones

---

## 👤 Author

**Pratyush Anand**

Data Analyst | SQL | Python | Power BI | Data Visualization

LinkedIn: https:www.linkedin.com/in/pratyush-anand
GitHub: https://github.com/pratyush540
