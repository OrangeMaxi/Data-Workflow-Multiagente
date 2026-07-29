CREATE VIEW silver.grouped_sales_vw AS
SELECT
    product_category,
    SUM(amount) AS total_sales,
    COUNT(*) AS total_transactions
FROM
    bronze.sales
GROUP BY
    product_category;