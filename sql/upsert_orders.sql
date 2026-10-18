-- Insert a clean order, or update it if the source sent a newer version.
-- Used by src/load.py: values are passed as named parameters.
INSERT INTO orders (
    order_id, customer_id, city, status, amount,
    created_at, delivered_at, updated_at
)
VALUES (
    %(order_id)s, %(customer_id)s, %(city)s, %(status)s, %(amount)s,
    %(created_at)s, %(delivered_at)s, %(updated_at)s
)
ON CONFLICT (order_id) DO UPDATE SET
    customer_id  = EXCLUDED.customer_id,
    city         = EXCLUDED.city,
    status       = EXCLUDED.status,
    amount       = EXCLUDED.amount,
    created_at   = EXCLUDED.created_at,
    delivered_at = EXCLUDED.delivered_at,
    updated_at   = EXCLUDED.updated_at,
    loaded_at    = now()
-- Update only when the incoming version is strictly newer.
WHERE orders.updated_at < EXCLUDED.updated_at;
