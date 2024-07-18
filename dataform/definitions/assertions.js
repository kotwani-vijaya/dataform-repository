assert("sales_summary_sanity_check")
  .query(ctx => `
    SELECT *
    FROM ${ctx.ref("sales_summary")}
    WHERE total_quantity < 0 OR total_revenue < 0
  `)