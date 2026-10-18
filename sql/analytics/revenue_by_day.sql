-- Dqily revenue from delivered orders, grouped by the order date.
SELECT
    created_at::date as order_date,
    count(*) as delivered_orders,
    sum(amount) as revenue,
    round(avg(amount),2) as avg_order_value
FROM orders
WHERE status='delivered'
GROUP BY order_date
ORDER BY order_date;