-- All clean orders with deliv.time, for Tableau
SELECT
    order_id,
    customer_id,
    city,
    status,
    amount,
    created_at::date AS order_date,
    delivered_at,
    round(extract(epoch FROM delivered_at-created_at)/60,1) as delivery_minutes
FROM orders
ORDER BY order_id;