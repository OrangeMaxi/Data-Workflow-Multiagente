CREATE OR REPLACE VIEW workspace.bakehouse.gold_franchise_geo_summary AS
SELECT
    franchise_name,
    customer_country,
    customer_city,
    COUNT(transactionID) AS total_transactions,
    COUNT(DISTINCT customerID) AS unique_customers
FROM
    workspace.bakehouse.silver_sales_enriched
GROUP BY
    franchise_name,
    customer_country,
    customer_city
ORDER BY
    franchise_name,
    customer_country,
    customer_city;