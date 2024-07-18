function createSalesSummary(timePeriod) {
  return `
    SELECT
      DATE_TRUNC(order_date, ${timePeriod}) AS period,
      product_id,
      SUM(quantity) AS total_quantity,
      SUM(quantity * unit_price) AS total_revenue
    FROM
      retail_dataset.raw_sales
    GROUP BY
      period,
      product_id
  `;
}

publish("daily_sales_summary").query(createSalesSummary("DAY"));
publish("monthly_sales_summary").query(createSalesSummary("MONTH"));
