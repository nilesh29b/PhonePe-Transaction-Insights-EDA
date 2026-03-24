-- =====================================================
-- Case Study 1 — Decoding Transaction Dynamics
-- Case Study 1 - Query 1
-- Goal: Find the most used payment categories overall
-- Table used: aggregated_transaction
-- We exclude 'india' because it is a sum of all states.
-- Including it would double count the numbers.
-- =====================================================

SELECT 
    transaction_type,
    SUM(transaction_count) AS total_transactions,
    ROUND(SUM(transaction_amount)::NUMERIC, 2) AS total_amount,
    ROUND(
        100.0 * SUM(transaction_count) / SUM(SUM(transaction_count)) OVER(),
        2
    ) AS percentage_share
FROM aggregated_transaction
WHERE state != 'india'
GROUP BY transaction_type
ORDER BY total_transactions DESC;

-- =====================================================
-- Case Study 1 - Query 2
-- Goal: Find which states have the highest transaction
--       volume and value
-- Table used: aggregated_transaction
-- This tells us which states are PhonePe's strongest
-- markets
-- =====================================================

SELECT
    state,
    SUM(transaction_count) AS total_transactions,
    ROUND(SUM(transaction_amount)::NUMERIC, 2) AS total_amount,
    ROUND(AVG(transaction_amount)::NUMERIC, 2) AS avg_transaction_value
FROM aggregated_transaction
WHERE state != 'india'
GROUP BY state
ORDER BY total_transactions DESC
LIMIT 10;



-- =====================================================
-- Case Study 1 - Query 3
-- Goal: Analyze transaction growth trend year over year
--       across all of India
-- Table used: aggregated_transaction
-- This tells us if PhonePe is growing, flat, or declining
-- over time
-- =====================================================

SELECT
    year,
    SUM(transaction_count) AS total_transactions,
    ROUND(SUM(transaction_amount)::NUMERIC, 2) AS total_amount,
    ROUND(
        100.0 * (SUM(transaction_count) - LAG(SUM(transaction_count)) OVER (ORDER BY year))
        / LAG(SUM(transaction_count)) OVER (ORDER BY year),
        2
    ) AS yoy_growth_percent
FROM aggregated_transaction
WHERE state != 'india'
GROUP BY year
ORDER BY year;




-- =====================================================
-- Case Study 2 — Device Dominance and User Engagement
-- =====================================================
-- Case Study 2 - Query 1
-- Goal: Find which device brands dominate PhonePe
--       usage nationally
-- Table used: aggregated_user
-- We exclude 'india' to avoid double counting
-- =====================================================

SELECT
    device_brand,
    SUM(device_count) AS total_users,
    ROUND(
        100.0 * SUM(device_count) / SUM(SUM(device_count)) OVER(),
        2
    ) AS percentage_share,
    ROUND((AVG(device_percentage) * 100)::NUMERIC, 2) AS avg_usage_percentage
FROM aggregated_user
WHERE state != 'india'
GROUP BY device_brand
ORDER BY total_users DESC;

-- =====================================================
-- Case Study 2 - Query 2 (corrected)
-- Goal: Compare engagement ratio across all states
--       to find highest and lowest engagement markets
-- Table used: aggregated_user
-- Higher ratio = users open app more frequently
-- =====================================================

SELECT
    state,
    SUM(registered_users) AS total_registered,
    SUM(app_opens) AS total_app_opens,
    ROUND(
        (SUM(app_opens)::NUMERIC / NULLIF(SUM(registered_users), 0)),
        2
    ) AS avg_opens_per_user
FROM aggregated_user
WHERE state != 'india'
GROUP BY state
ORDER BY avg_opens_per_user DESC;

-- =====================================================
-- Case Study 2 - Query 3
-- Goal: Track device brand user counts year over year
--       to see which brands are gaining or losing share
-- Table used: aggregated_user
-- We look at top 5 brands only for clarity
-- =====================================================

SELECT
    year,
    device_brand,
    SUM(device_count) AS total_users
FROM aggregated_user
WHERE state != 'india'
AND device_brand IN ('Xiaomi', 'Samsung', 'Vivo', 'Oppo', 'Realme')
GROUP BY year, device_brand
ORDER BY year ASC, total_users DESC;


-- =====================================================
-- Case Study 3 — Insurance Penetration and Growth Potential
-- =====================================================

-- Case Study 3 - Query 1
-- Goal: Track insurance transaction growth year over year
-- Table used: aggregated_insurance
-- Note: Data starts from 2020 Q2, not 2018.
--       This is a data availability issue, not a code error.
--       We document this as a finding.
-- =====================================================

SELECT
    year,
    SUM(transaction_count) AS total_insurance_transactions,
    ROUND(SUM(transaction_amount)::NUMERIC, 2) AS total_insurance_amount,
    ROUND(
        100.0 * (SUM(transaction_count) - LAG(SUM(transaction_count)) OVER (ORDER BY year))
        / NULLIF(LAG(SUM(transaction_count)) OVER (ORDER BY year), 0),
        2
    ) AS yoy_growth_percent
FROM aggregated_insurance
WHERE state != 'india'
GROUP BY year
ORDER BY year;


-- =====================================================
-- Case Study 3 - Query 2
-- Goal: Find top states by insurance transaction volume
--       and value to identify strongest markets
-- Table used: aggregated_insurance
-- =====================================================

SELECT
    state,
    SUM(transaction_count) AS total_insurance_transactions,
    ROUND(SUM(transaction_amount)::NUMERIC, 2) AS total_amount,
    ROUND(
        100.0 * SUM(transaction_count) / SUM(SUM(transaction_count)) OVER(),
        2
    ) AS percentage_share
FROM aggregated_insurance
WHERE state != 'india'
GROUP BY state
ORDER BY total_insurance_transactions DESC
LIMIT 10;

-- =====================================================
-- Case Study 3 - Query 3
-- Goal: Find states that are high in regular transactions
--       but low in insurance -- these are untapped markets
-- Table uses: aggregated_transaction + aggregated_insurance
-- We JOIN two tables here for the first time
-- =====================================================

SELECT
    t.state,
    SUM(t.transaction_count) AS regular_transactions,
    SUM(i.transaction_count) AS insurance_transactions,
    ROUND(
        100.0 * SUM(i.transaction_count) /
        NULLIF(SUM(t.transaction_count), 0),
        4
    ) AS insurance_penetration_rate
FROM aggregated_transaction t
LEFT JOIN aggregated_insurance i
    ON t.state = i.state
    AND t.year = i.year
    AND t.quarter = i.quarter
WHERE t.state != 'india'
AND t.year >= 2020
GROUP BY t.state
ORDER BY insurance_penetration_rate ASC
LIMIT 10;


-- =====================================================
--  Case Study 7 — Transaction Analysis Across States and Districts
-- =====================================================
-- Case Study 7 - Query 1
-- Goal: Find top 10 districts nationally by transaction
--       volume and value
-- Table used: map_transaction
-- This is district level data -- more granular than
-- aggregated_transaction which is state level
-- =====================================================

SELECT
    state,
    district,
    SUM(transaction_count) AS total_transactions,
    ROUND(SUM(transaction_amount)::NUMERIC, 2) AS total_amount
FROM map_transaction
GROUP BY state, district
ORDER BY total_transactions DESC
LIMIT 10;

-- =====================================================
-- Case Study 7 - Query 2
-- Goal: Find top 10 pin codes by transaction volume
-- Table used: top_transaction
-- top_transaction has pincode level data which
-- map_transaction does not have
-- =====================================================

SELECT
    state,
    entity_name AS pincode,
    SUM(transaction_count) AS total_transactions,
    ROUND(SUM(transaction_amount)::NUMERIC, 2) AS total_amount
FROM top_transaction
WHERE entity_type = 'pincode'
GROUP BY state, entity_name
ORDER BY total_transactions DESC
LIMIT 10;

-- =====================================================
-- Case Study 7 - Query 3
-- Goal: Track year over year growth of top districts
--       to identify emerging markets
-- Table used: map_transaction
-- We focus on top 5 districts from Query 1 to keep
-- results readable and meaningful
-- =====================================================

SELECT
    year,
    district,
    state,
    SUM(transaction_count) AS total_transactions,
    ROUND(SUM(transaction_amount)::NUMERIC, 2) AS total_amount
FROM map_transaction
WHERE district IN (
    'bengaluru urban district',
    'pune district',
    'hyderabad district',
    'jaipur district',
    'rangareddy district'
)
GROUP BY year, district, state
ORDER BY district, year;