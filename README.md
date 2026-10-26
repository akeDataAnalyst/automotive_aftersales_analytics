# **Automotive After-Sales Analytics & Retention Intelligence Hub**

**Executive Decision-Support System & Predictive Churn Pipeline for Authorized Dealership Networks**

---

## **Overview**
The **Automotive After-Sales Analytics & Retention Hub** is an end-to-end data analytics, machine learning, and business intelligence platform built for authorized dealership networks (supporting Suzuki & Citroën operations across 7 major branches). 

The platform bridges the gap between raw Dealer Management System (DMS) records and strategic executive decision-making, offering deep visibility into workshop bay utilization, technician productivity, First-Time Fix Rates (FTFR), outbound CRM campaign ROI, and customer lifecycle defection risks.

---

## **The Business Problem**
Authorized automotive dealerships in the UAE face several acute operational and revenue challenges:
1. **Post-Warranty Customer Defection:** A significant percentage of vehicle owners drop out of the authorized service network after the initial warranty period expires (typically 3 to 5 years), defecting to independent garages ("third-party service centers").
2. **Unoptimized Service Bay Yields:** Variance in technician efficiency and repair order (RO) turnaround times creates bottlenecks across regional service hubs in Dubai, Abu Dhabi, and Sharjah.
3. **Reactive Rather Than Proactive Retention:** Dealership CRM teams lack predictive visibility to identify which high-value customers are about to lapse before they actually defect.
4. **Repeat Repairs (Comebacks):** Quality control gaps leading to higher-than-target comeback rates erode customer trust and warranty margins.

---

## **The Solution**
An integrated, 3-tier analytical architecture designed to ingest, model, predict, and visualize after-sales intelligence:
* **Relational DMS Data Generator:** Simulates 36 months of realistic operational data across 7 relational tables (branches, technicians, customers, vehicles, repair orders, bookings, and CRM interactions).
* **Machine Learning Churn Engine:** Trains a tuned Gradient Boosting Classifier to predict customer return probability within a 90-day window, achieving an **82.44% ROC-AUC score**.
* **Interactive Executive Dashboard:** A 6-page multi-page Streamlit web application providing real-time KPI scorecards, branch benchmarking, customer lifecycle segmentation, and an actionable high-risk CRM lead exporter.

---

## **Tech Stack & Architecture**

| Category | Technologies & Tools |
| :--- | :--- |
| **Core Language** | Python 3.10+ |
| **Data Manipulation & Analysis** | Pandas, NumPy |
| **Machine Learning** | Scikit-Learn (Gradient Boosting Classifier), Joblib |
| **Data Visualization** | Plotly, Streamlit Native Charts |
| **Interactive Dashboard** | Streamlit (Multi-Page Architecture) |
| **Data Persistence** | Apache Parquet (Optimized columnar storage) |
| **Environment & Version Control** | Git, GitHub, Virtual Environments |

---

## **Developed By Aklilu Abera | Data Analyst**
