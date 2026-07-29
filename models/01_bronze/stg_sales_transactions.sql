-- Capa Bronze: Ingesta Staging
CREATE OR REPLACE VIEW bakehouse.stg_sales_transactions AS
SELECT transactionID, franchiseID, dateTime, quantity, totalPrice, cardNumber
FROM bakehouse.sales_transactions;
