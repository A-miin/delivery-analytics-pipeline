-- number of orders per city: total, delivered. cancelled and cancel rate
SELECT city, count(*)
    as total_orders,
        count(*) FILTER (WHERE status='delivered')
    as delivered_orders,
        count(*) FILTER(WHERE status='delivered')
    as cancelled_orders,
        round(100.0 * count(*) FILTER(WHERE status='cancelled')/count(*),1) as cancel_rate_pct
FROM orders
GROUP BY city
ORDER BY total_orders DESC;