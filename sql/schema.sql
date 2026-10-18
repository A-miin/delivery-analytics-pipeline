CREATE TABLE IF NOT EXISTS orders(
    order_id text primary key,
    customer_id text not null,
    city text not null,
    status text not null CHECK (status in ('delivered', 'cancelled')),
    amount numeric(10,2) not null CHECK (amount > 0),
    created_at TIMESTAMP NOT NULL,
    delivered_at TIMESTAMP,
    updated_at TIMESTAMP NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (delivered_at >= created_at));
