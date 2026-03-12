-- queries.sql
-- Resale comps pricing engine queries for comps_db

-- =========================================
-- 1. View all search categories
-- =========================================
SELECT * FROM search_query;

-- =========================================
-- 2. View all listings
-- =========================================
SELECT * FROM listing_snapshot;

-- =========================================
-- 3. Full database view
-- Shows every listing with its linked search keyword
-- =========================================
SELECT
  sq.keywords,
  ls.title,
  ls.total_price,
  ls.condition,
  ls.seller_username,
  ls.item_url
FROM search_query sq
JOIN listing_snapshot ls
  ON sq.id = ls.search_query_id
ORDER BY sq.keywords, ls.total_price;

-- =========================================
-- 4. Average prices by category/search term
-- =========================================
SELECT
  sq.keywords,
  COUNT(ls.id) AS listings,
  ROUND(AVG(ls.total_price), 2) AS avg_price,
  MIN(ls.total_price) AS min_price,
  MAX(ls.total_price) AS max_price
FROM search_query sq
JOIN listing_snapshot ls
  ON sq.id = ls.search_query_id
GROUP BY sq.keywords
ORDER BY sq.keywords;

-- =========================================
-- 5. Full database with average price per category
-- =========================================
SELECT
  sq.keywords,
  ls.title,
  ls.total_price,
  ls.condition,
  ls.seller_username,
  ls.item_url,
  ROUND(AVG(ls.total_price) OVER (PARTITION BY sq.keywords), 2) AS avg_price
FROM search_query sq
JOIN listing_snapshot ls
  ON sq.id = ls.search_query_id
ORDER BY sq.keywords, ls.total_price;

-- =========================================
-- 6. Add estimated USPS-style shipping weight column
-- Run once only
-- =========================================
ALTER TABLE listing_snapshot
ADD COLUMN IF NOT EXISTS estimated_weight_lbs NUMERIC(6,2);

-- =========================================
-- 7. Populate estimated shipping weights
-- Based on item title/category heuristics
-- =========================================
UPDATE listing_snapshot
SET estimated_weight_lbs =
CASE
    WHEN title ILIKE '%airpods%' THEN 0.75
    WHEN title ILIKE '%iphone%' THEN 0.80
    WHEN title ILIKE '%jersey%' THEN 1.00
    WHEN title ILIKE '%shirt%' THEN 1.00
    WHEN title ILIKE '%shoes%' THEN 2.50
    WHEN title ILIKE '%drone%' THEN 4.00
    ELSE 1.50
END;

-- =========================================
-- 8. Full dashboard query
-- current price, average price, suggested listing price,
-- estimated USPS shipping, total cost with shipping, and item link
-- =========================================
SELECT
  sq.keywords,
  ls.title,
  ls.total_price AS current_price,
  ROUND(AVG(ls.total_price) OVER (PARTITION BY sq.keywords), 2) AS avg_price,
  ROUND(AVG(ls.total_price) OVER (PARTITION BY sq.keywords) * 1.15, 2) AS suggested_listing_price,
  ls.estimated_weight_lbs,
  ROUND(ls.estimated_weight_lbs * 1.40, 2) AS estimated_usps_shipping,
  ROUND(ls.total_price + (ls.estimated_weight_lbs * 1.40), 2) AS total_cost_with_shipping,
  ls.condition,
  ls.seller_username,
  ls.item_url
FROM search_query sq
JOIN listing_snapshot ls
  ON sq.id = ls.search_query_id
ORDER BY sq.keywords, ls.total_price;

-- =========================================
-- 9. Export dashboard to JSON from psql
-- Run in psql, not inside standard SQL-only environments
-- =========================================
-- \copy (
--   SELECT row_to_json(t)
--   FROM (
--     SELECT
--       sq.keywords,
--       ls.title,
--       ls.total_price AS current_price,
--       ROUND(AVG(ls.total_price) OVER (PARTITION BY sq.keywords), 2) AS avg_price,
--       ROUND(AVG(ls.total_price) OVER (PARTITION BY sq.keywords) * 1.15, 2) AS suggested_listing_price,
--       ls.estimated_weight_lbs,
--       ROUND(ls.estimated_weight_lbs * 1.40, 2) AS estimated_usps_shipping,
--       ROUND(ls.total_price + (ls.estimated_weight_lbs * 1.40), 2) AS total_cost_with_shipping,
--       ls.condition,
--       ls.seller_username,
--       ls.item_url
--     FROM search_query sq
--     JOIN listing_snapshot ls
--       ON sq.id = ls.search_query_id
--     ORDER BY sq.keywords, ls.total_price
--   ) t
-- ) TO 'resale_dashboard.json';

-- =========================================
-- 10. Remove accessory or junk AirPods listings
-- Example cleanup query
-- =========================================
DELETE FROM listing_snapshot
WHERE title ILIKE '%case%'
   OR title ILIKE '%cover%'
   OR title ILIKE '%skin%'
   OR title ILIKE '%replacement%';

-- =========================================
-- 11. Count listings per category/search term
-- =========================================
SELECT
  sq.keywords,
  COUNT(ls.id) AS listings
FROM search_query sq
LEFT JOIN listing_snapshot ls
  ON sq.id = ls.search_query_id
GROUP BY sq.keywords
ORDER BY sq.keywords;
