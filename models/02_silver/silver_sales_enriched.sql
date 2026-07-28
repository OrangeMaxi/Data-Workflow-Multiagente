-- Capa Silver: Datos Limpios y Enriquecidos
CREATE OR REPLACE VIEW bakehouse.silver_sales_enriched AS
SELECT 
    transactionID,
    franchiseID,
    dateTime,
    quantity,
    totalPrice,
    ROUND(totalPrice / NULLIF(quantity, 0), 2) AS precio_unitario
FROM bakehouse.stg_sales_transactions
WHERE totalPrice > 0 AND quantity > 0;
