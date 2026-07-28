-- Vista Analitica Gold Resumen Franquicias
CREATE OR REPLACE VIEW bakehouse.gold_resumen_franquicias AS
SELECT 
    franchiseID,
    SUM(total_amount) AS ventas_totales,
    COUNT(transactionID) AS total_transacciones
FROM bakehouse.sales_transactions
GROUP BY franchiseID;
