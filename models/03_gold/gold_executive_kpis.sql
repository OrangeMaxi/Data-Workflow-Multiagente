-- Capa Gold: KPIs Ejecutivos de Negocio
CREATE OR REPLACE VIEW bakehouse.gold_executive_kpis AS
SELECT 
    franchiseID,
    SUM(totalPrice) AS ventas_totales,
    SUM(quantity) AS unidades_vendidas,
    COUNT(transactionID) AS total_transacciones,
    ROUND(AVG(totalPrice), 2) AS ticket_promedio
FROM bakehouse.silver_sales_enriched
GROUP BY franchiseID;
