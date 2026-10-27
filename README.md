# E-Commerce Sales & Customer Intelligence

A portfolio project exploring the Brazilian E-Commerce Public Dataset
(Olist) using **Python, MySQL, and Power BI**. The project focuses on
sales performance, order trends, payment methods, customer geography,
product categories, delivery performance, and customer reviews.

## Project Objectives

-   Organize and validate e-commerce data from multiple CSV tables.
-   Clean and prepare data for analysis.
-   Use SQL to answer business questions.
-   Build a Power BI dashboard to communicate key metrics and patterns.
-   Identify opportunities to improve delivery experience and customer
    satisfaction.

## Tools & Technologies

-   **Python:** data cleaning and preparation
-   **MySQL 8.0:** relational data storage, validation, and SQL analysis
-   **Power BI Desktop:** KPI cards and interactive visuals
-   **Pandas:** data manipulation (where used in the preparation
    scripts)

## Dataset

The project uses the Olist Brazilian E-Commerce Public Dataset. The
loaded database contains nine tables:

  Table                               Rows
  ------------------------------ ---------
  Customers                         99,441
  Orders                            99,441
  Order items                      112,650
  Payments                         103,886
  Reviews                           99,224
  Products                          32,951
  Sellers                            3,095
  Geolocation                      738,332
  Product category translation          71

**Note:** Counts above are from the project's database validation.
Before publishing, include the dataset source/usage attribution required
by the dataset provider and confirm that the repository does not contain
oversized raw files or private credentials.

## Repository Structure

``` text
ecommerce-sales-intelligence/
├── data/
│   ├── archive/       # Raw source files (keep large raw files out of GitHub if needed)
│   └── final/         # Cleaned/prepared files
├── src/               # Python cleaning/preparation scripts
├── sql/               # SQL analysis queries
├── reports/           # Project report and analysis outputs
├── dashboard/         # Power BI .pbix and dashboard screenshot
└── README.md
```

Adjust this tree to match the exact files in your repository.

## Database Validation

The project loaded nine tables into the `ecommerce_intelligence` MySQL
database. The 17 validation checks completed successfully.

## Analysis Highlights

### Order status

-   Total orders: **99,441**
-   Delivered orders: **96,478** (approximately **97.02%**)
-   Other statuses include shipped, canceled, unavailable, invoiced,
    processing, created, and approved.

### Product categories

Top delivered-category item sales (BRL, excluding freight) included: 1.
Health & Beauty --- R\$1,233,131.72 2. Watches & Gifts ---
R\$1,166,176.98 3. Bed, Bath & Table --- R\$1,023,434.76 4. Sports &
Leisure --- R\$954,852.55 5. Computers & Accessories --- R\$888,724.61

### Delivery performance and reviews

-   Average delivery time: **12.50 days** across 96,470 delivered orders
    with the required dates.
-   Late delivery rate: **8.11%**.
-   Late-delivered orders had an average review score of **2.57**;
    **54.03%** received a score of 1 or 2.
-   Orders delivered on time or early had an average review score of
    **4.29**; **9.23%** received a score of 1 or 2.

These figures show an association between late delivery and lower review
scores; they do not by themselves prove causation.

### Payment methods

Credit card was the most common payment method by payment records, with
76,795 records and total recorded payment value of approximately
**R\$12.54 million**. Boleto was next, with 19,784 records and
approximately **R\$2.87 million**.

### Customer geography and repeat purchasing

-   São Paulo (SP) had the largest customer count: **40,302**.
-   The repeat-customer analysis found **93,099 one-time** and **2,997
    repeat** customers using `customer_unique_id` and the project's
    defined grouping.

## Dashboard

The Power BI dashboard includes KPI cards and visuals for: - Total
orders - Total item sales (BRL) - Average item value (BRL) - Average
payment value (BRL) - Monthly sales trend - Sales by payment method -
Top 10 product categories by sales - Customer review score
distribution - Customers by state - Monthly order volume

**Metric definitions matter:** item sales based on `order_items.price`
exclude freight and may include items from orders in statuses other than
delivered unless a filter is applied. Average payment value is based on
the payment table and is not directly interchangeable with average item
price.

## How to Reproduce

1.  Download the dataset from its official provider and place the CSVs
    in the expected data folder.
2.  Run the Python preparation scripts in `src/` (review file paths and
    dependencies first).
3.  Create the MySQL database and load the prepared tables.
4.  Run the SQL scripts in `sql/`.
5.  Open the Power BI `.pbix` file in Power BI Desktop and refresh the
    data connection as needed.

Exact commands depend on the scripts and connection settings included in
the repository. Do not commit database passwords or other secrets.

## Limitations & Next Improvements

-   Verify Power BI relationship cardinality and filter directions
    before treating every visual as final.
-   Ensure the monthly sales visual displays monthly values rather than
    cumulative totals.
-   The earliest and latest months may be partial periods, so interpret
    them cautiously.
-   Add data dictionary and documented setup commands after checking the
    final repository contents.
-   Add a screenshot of the finished dashboard to `dashboard/`.

## Author

**Vimal D** --- B.Tech Artificial Intelligence & Data Science student.

This project is intended for learning and portfolio demonstration.
Validate all measures and data relationships before using results for
business decisions.
