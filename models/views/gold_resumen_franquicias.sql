-- Vista Analitica Gold Resumen Franquicias
CREATE OR REPLACE VIEW bakehouse.gold_resumen_franquicias AS
SELECT 
    franchise_id,
    SUM(total_amount) AS ventas_totales,
    COUNT(transaction_id) AS total_transacciones
FROM bakehouse.sales_transactions
GROUP BY franchise_id;
