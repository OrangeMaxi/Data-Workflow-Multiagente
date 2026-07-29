-- Capa Silver: Datos Limpios y Enriquecidos
CREATE OR REPLACE VIEW bakehouse.vw_silver_sales_enriched AS
SELECT 
    transactionID,
    franchiseID,
    dateTime,
    quantity,
    unitPrice,
    (quantity * unitPrice) AS venta_total
FROM bakehouse.vw_stg_sales_transactions
WHERE unitPrice > 0 AND quantity > 0;
