
CREATE DATABASE IF NOT EXISTS ecommerce_intelligence;

USE ecommerce_intelligence;

SELECT DATABASE();

USE ecommerce_intelligence;

SELECT 'customers' AS table_name, COUNT(*) AS row_count
FROM olist_customers_dataset
UNION ALL
SELECT 'orders', COUNT(*) FROM olist_orders_dataset
UNION ALL
SELECT 'order_items', COUNT(*) FROM olist_order_items_dataset
UNION ALL
SELECT 'payments', COUNT(*) FROM olist_order_payments_dataset
UNION ALL
SELECT 'reviews', COUNT(*) FROM olist_order_reviews_dataset
UNION ALL
SELECT 'products', COUNT(*) FROM olist_products_dataset
UNION ALL
SELECT 'sellers', COUNT(*) FROM olist_sellers_dataset
UNION ALL
SELECT 'geolocation', COUNT(*) FROM olist_geolocation_dataset
UNION ALL
SELECT 'category_translation', COUNT(*)
FROM product_category_name_translation;
USE ecommerce_intelligence;

SELECT
    order_status,
    COUNT(*) AS total_orders
FROM olist_orders_dataset
GROUP BY order_status
ORDER BY total_orders DESC;
SELECT
    DATE_FORMAT(
        STR_TO_DATE(order_purchase_timestamp, '%Y-%m-%d %H:%i:%s'),
        '%Y-%m'
    ) AS order_month,
    COUNT(DISTINCT order_id) AS total_orders
FROM olist_orders_dataset
WHERE order_purchase_timestamp IS NOT NULL
GROUP BY order_month
ORDER BY order_month;
SELECT
    COALESCE(
        t.product_category_name_english,
        p.product_category_name
    ) AS product_category,
    ROUND(SUM(i.price), 2) AS item_sales,
    COUNT(*) AS items_sold
FROM olist_order_items_dataset i
JOIN olist_products_dataset p
    ON i.product_id = p.product_id
LEFT JOIN product_category_name_translation t
    ON p.product_category_name = t.product_category_name
JOIN olist_orders_dataset o
    ON i.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY product_category
ORDER BY item_sales DESC
LIMIT 10;
SELECT
    COUNT(*) AS delivered_orders,
    ROUND(AVG(
        DATEDIFF(
            STR_TO_DATE(order_delivered_customer_date, '%Y-%m-%d %H:%i:%s'),
            STR_TO_DATE(order_purchase_timestamp, '%Y-%m-%d %H:%i:%s')
        )
    ), 2) AS avg_delivery_days,
    ROUND(AVG(
        CASE
            WHEN STR_TO_DATE(order_delivered_customer_date, '%Y-%m-%d %H:%i:%s')
                 > STR_TO_DATE(order_estimated_delivery_date, '%Y-%m-%d %H:%i:%s')
            THEN 1
            ELSE 0
        END
    ) * 100, 2) AS late_delivery_percentage
FROM olist_orders_dataset
WHERE order_status = 'delivered'
  AND order_purchase_timestamp IS NOT NULL
  AND order_delivered_customer_date IS NOT NULL
  AND order_estimated_delivery_date IS NOT NULL;
  SELECT
    CASE
        WHEN o.order_delivered_customer_date >
             o.order_estimated_delivery_date
        THEN 'Late'
        ELSE 'On time or early'
    END AS delivery_status,
    COUNT(*) AS total_reviews,
    ROUND(AVG(r.review_score), 2) AS average_review_score,
    ROUND(
        100.0 * SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS low_rating_percentage
FROM olist_orders_dataset o
JOIN olist_order_reviews_dataset r
    ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL
GROUP BY delivery_status
ORDER BY delivery_status;
SELECT
    payment_type,
    COUNT(*) AS payment_records,
    ROUND(SUM(payment_value), 2) AS total_payment_value,
    ROUND(AVG(payment_value), 2) AS average_payment_value
FROM olist_order_payments_dataset
GROUP BY payment_type
ORDER BY total_payment_value DESC;
SELECT
    customer_state,
    COUNT(DISTINCT customer_unique_id) AS total_customers
FROM olist_customers_dataset
GROUP BY customer_state
ORDER BY total_customers DESC
LIMIT 10;
SELECT
    CASE
        WHEN order_count = 1 THEN 'One-time customer'
        ELSE 'Repeat customer'
    END AS customer_type,
    COUNT(*) AS total_customers
FROM (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM olist_customers_dataset c
    JOIN olist_orders_dataset o
        ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
) AS customer_orders
GROUP BY customer_type
ORDER BY total_customers DESC;
SELECT
    order_month,
    COUNT(*) AS total_orders,
    ROUND(AVG(order_payment_total), 2) AS average_order_value
FROM (
    SELECT
        o.order_id,
        DATE_FORMAT(
            o.order_purchase_timestamp,
            '%Y-%m'
        ) AS order_month,
        SUM(p.payment_value) AS order_payment_total
    FROM olist_orders_dataset o
    JOIN olist_order_payments_dataset p
        ON o.order_id = p.order_id
    WHERE o.order_purchase_timestamp IS NOT NULL
    GROUP BY o.order_id, order_month
) AS monthly_orders
GROUP BY order_month
ORDER BY order_month;
SELECT
    i.seller_id,
    COUNT(DISTINCT i.order_id) AS total_orders,
    COUNT(*) AS items_sold,
    ROUND(SUM(i.price), 2) AS item_sales
FROM olist_order_items_dataset i
JOIN olist_orders_dataset o
    ON i.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY i.seller_id
ORDER BY item_sales DESC
LIMIT 10;