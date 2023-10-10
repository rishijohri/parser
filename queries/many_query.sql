CREATE TABLE customer_orders AS (
  SELECT customer_id, order_id
  FROM customers
  INNER JOIN orders ON customers.customer_id = orders.customer_id
);

CREATE TABLE order_products AS (
  SELECT order_id, product_id
  FROM orders
  INNER JOIN order_items ON orders.order_id = order_items.order_id
);

CREATE TABLE customer_orders_products AS (
  SELECT customer_id, order_id, product_id
  FROM customer_orders
  INNER JOIN order_products ON customer_orders.customer_id = order_products.customer_id AND customer_orders.order_id = order_products.order_id
);

CREATE TABLE customer_orders_products_quantity AS (
  SELECT customer_id, order_id, product_id, SUM(quantity) AS quantity
  FROM customer_orders_products
  GROUP BY customer_id, order_id, product_id
);

CREATE TABLE customer_orders_products_total_price AS (
  SELECT customer_id, order_id, product_id, SUM(total_price) AS total_price
  FROM customer_orders_products
  GROUP BY customer_id, order_id, product_id
);

CREATE TABLE customer_orders_products_summary AS (
  SELECT customer_id, order_id, product_id, quantity, total_price
  FROM customer_orders_products_quantity
  INNER JOIN customer_orders_products_total_price ON customer_orders_products_quantity.customer_id = customer_orders_products_total_price.customer_id AND customer_orders_products_quantity.order_id = customer_orders_products_total_price.order_id AND customer_orders_products_quantity.product_id = customer_orders_products_total_price.product_id
);

-- Final Table

CREATE TABLE customer_orders_products_summary_final AS (
  SELECT customer_id, order_id, product_id, quantity, total_price
  FROM customer_orders_products_summary
  ORDER BY customer_id, order_id, product_id
);