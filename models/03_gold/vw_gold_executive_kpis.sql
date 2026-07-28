-- Capa Gold: KPIs Ejecutivos de Negocio
CREATE OR REPLACE VIEW bakehouse.vw_gold_executive_kpis AS
SELECT 
    franchiseID,
    SUM(venta_total) AS ventas_totales,
    SUM(quantity) AS unidades_vendidas,
    COUNT(transactionID) AS total_transacciones,
    ROUND(AVG(venta_total), 2) AS ticket_promedio
FROM bakehouse.vw_silver_sales_enriched
GROUP BY franchiseID;
