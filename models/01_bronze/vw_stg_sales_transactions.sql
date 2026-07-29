-- Capa Bronze: Ingesta Staging
CREATE OR REPLACE VIEW bakehouse.vw_stg_sales_transactions AS
SELECT transactionID, franchiseID, dateTime, quantity, unitPrice, cardNumber
FROM bakehouse.sales_transactions;
