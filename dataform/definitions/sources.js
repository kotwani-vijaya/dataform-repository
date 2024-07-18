publish("raw_sales").query(ctx => `
  SELECT
    order_id,
    customer_id,
    product_id,
    quantity,
    unit_price,
    order_date
  FROM
    \`retail_dataset.raw_sales_data\`
`);