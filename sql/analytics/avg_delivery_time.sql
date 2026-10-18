-- AVG delivery time in minuter per city, only delivered orders
SELECT
    city,
    count(*) as delivered_orders,
    round(avg(extract(epoch from delivered_at-created_at)/60),1) as avg_delivery_minutes
FROM orders
WHERE status='delivered'
GROUP BY city
ORDER BY avg_delivery_minutes;