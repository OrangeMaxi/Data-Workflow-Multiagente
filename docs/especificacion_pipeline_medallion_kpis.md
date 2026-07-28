# Especificacion Pipeline Medallion KPIs

## Arquitectura de Datos Medallion
- Bronze: `models/01_bronze/vw_stg_sales_transactions.sql`
- Silver: `models/02_silver/vw_silver_sales_enriched.sql`
- Gold: `models/03_gold/vw_gold_executive_kpis.sql`
