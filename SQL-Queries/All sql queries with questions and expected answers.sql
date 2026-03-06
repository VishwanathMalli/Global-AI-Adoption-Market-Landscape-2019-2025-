Q1. What is the average AI adoption rate for each year globally?
Expected Answer:  Adoption grew from ~41% (2019) to ~78% (2025). COVID years 2020–2021 show a clear acceleration spike across all industries.

SELECT
    year,
    ROUND(AVG(ai_adoption_rate_pct), 2)  AS avg_adoption_pct,
    ROUND(MIN(ai_adoption_rate_pct), 2)  AS min_pct,
    ROUND(MAX(ai_adoption_rate_pct), 2)  AS max_pct,
    COUNT(DISTINCT industry)             AS industries_counted
FROM ai_industry
GROUP BY year
ORDER BY year;


Q2. Which industries have the highest average AI adoption rate?
Expected Answer:  Technology leads at ~73% avg. Professional Services ~64%, Financial Services ~58%. Healthcare is lowest at ~35% — biggest gap and biggest opportunity.

SELECT
    industry,
    ROUND(AVG(ai_adoption_rate_pct), 2)  AS avg_adoption_pct,
    ROUND(MIN(ai_adoption_rate_pct), 2)  AS min_pct,
    ROUND(MAX(ai_adoption_rate_pct), 2)  AS max_pct,
    COUNT(*)                             AS data_points
FROM ai_industry
GROUP BY industry
ORDER BY avg_adoption_pct DESC;


Q3. Which region has the highest total AI spending across all years?
Expected Answer:  North America leads total spend at ~$845B. Asia-Pacific is 2nd at ~$510B, Europe 3rd at ~$380B. Developing Markets lag at ~$95B — a 9x gap vs North America.

SELECT
    region,
    ROUND(SUM(ai_spending_usd_bn), 2)      AS total_spend_bn,
    ROUND(AVG(ai_spending_usd_bn), 2)      AS avg_spend_bn,
    ROUND(AVG(pilot_to_prod_rate_pct), 1)  AS avg_prod_rate_pct
FROM ai_industry
WHERE ai_spending_usd_bn IS NOT NULL
GROUP BY region
ORDER BY total_spend_bn DESC;


Q4. What is the total AI investment per country across all years?
Expected Answer:  USA leads at $349.5B cumulative. China is 2nd at $63.8B (18% of USA). India is the fastest-growing emerging market, rising from Rank 7 to Rank 4 between 2019 and 2024.

SELECT
    country,
    region,
    ROUND(SUM(ai_investment_usd_bn), 2)  AS total_investment_bn,
    ROUND(AVG(ai_investment_usd_bn), 2)  AS avg_per_year_bn,
    COUNT(year)                          AS years_covered
FROM ai_geo
GROUP BY country, region
ORDER BY total_investment_bn DESC;

Q5. How many AI policies has each region enacted in total?
Expected Answer:  North America has the most policies (~148 total), followed by Europe (~126). Developing Markets have the fewest (~40), revealing a governance and regulatory gap.

SELECT
    region,
    SUM(policy_count)                    AS total_policies,
    ROUND(AVG(policy_count), 1)          AS avg_per_year,
    ROUND(AVG(ai_readiness_score), 2)    AS avg_readiness_score,
    COUNT(DISTINCT country)              AS countries_in_region
FROM ai_geo
GROUP BY region
ORDER BY total_policies DESC;


Q6. For each industry and use case, what is the avg adoption rate and total spend?
Expected Answer:  NLP in Technology has the highest adoption (75%+) and spend. Computer Vision in Healthcare has the lowest production rate (28%) despite growing spend — signals a serious scaling problem.

SELECT
    industry,
    use_case_category,
    ROUND(AVG(ai_adoption_rate_pct), 2)    AS avg_adoption_pct,
    ROUND(SUM(ai_spending_usd_bn), 2)      AS total_spend_bn,
    ROUND(AVG(pilot_to_prod_rate_pct), 1)  AS avg_prod_rate_pct
FROM ai_industry
WHERE use_case_category IS NOT NULL
GROUP BY industry, use_case_category
ORDER BY industry, avg_adoption_pct DESC;


Q7. Which industries had the biggest YoY adoption growth in 2023?
Expected Answer:  Professional Services grew +12pp YoY in 2023 (driven by ChatGPT/GenAI adoption). Technology grew +7pp. Healthcare had the slowest growth at only +3pp.

SELECT
    industry,
    region,
    year,
    ROUND(ai_adoption_rate_pct, 2)  AS adoption_pct,
    ROUND(yoy_growth_pct, 2)        AS yoy_growth_pct
FROM ai_industry
WHERE year = 2023
  AND yoy_growth_pct IS NOT NULL
ORDER BY yoy_growth_pct DESC;


Q8. Show cloud provider revenue and market share for each year.
Expected Answer:  AWS held 33% share in 2019 but fell to 30% by 2024. Azure climbed from 18% to 25%. GCP grew steadily from 9% to 12% — the market is becoming more competitive every year.

SELECT
    provider_name,
    year,
    ROUND(cloud_revenue_usd_bn, 2)  AS revenue_bn,
    ROUND(market_share_pct, 2)      AS market_share_pct,
    ROUND(yoy_growth_pct, 2)        AS revenue_growth_pct
FROM ai_cloud
ORDER BY year, market_share_pct DESC;


Q9. Which countries have high AI readiness but low market revenue? (Opportunity gap)
Expected Answer:  Indonesia (readiness 58, revenue <$1B), Mexico (readiness 57, revenue <$1B) and South Africa (readiness 50, revenue <$1B) are the top 3 opportunity markets for AI expansion.

SELECT
    country,
    region,
    income_group,
    ROUND(AVG(ai_readiness_score), 1)     AS avg_readiness,
    ROUND(AVG(market_revenue_usd_bn), 2)  AS avg_revenue_bn,
    ROUND(AVG(ai_investment_usd_bn), 2)   AS avg_investment_bn,
    ROUND(
        AVG(ai_readiness_score) - AVG(market_revenue_usd_bn)
    , 1)                                  AS opportunity_gap_score
FROM ai_geo
GROUP BY country, region, income_group
HAVING AVG(ai_readiness_score) > 50
   AND AVG(market_revenue_usd_bn) < 5
ORDER BY opportunity_gap_score DESC;


Q10. What is the most common AI scaling barrier per industry?
Expected Answer:  Data Quality blocks Technology and Financial Services most. Regulatory Compliance is the #1 barrier in Healthcare. Legacy Systems dominate Manufacturing.

SELECT
    industry,
    barrier_type,
    COUNT(*)                               AS frequency,
    ROUND(AVG(pilot_to_prod_rate_pct), 1)  AS avg_prod_rate_when_this_barrier
FROM ai_industry
WHERE barrier_type IS NOT NULL
GROUP BY industry, barrier_type
ORDER BY industry, frequency DESC;


Q11. Rank countries by AI investment within each year using DENSE_RANK.
Expected Answer:  USA is Rank 1 every single year. India climbed from Rank 7 (2019) to Rank 4 (2024) — the fastest rank improvement of any country, driven by consistent investment growth.

SELECT
    year,
    country,
    region,
    ROUND(ai_investment_usd_bn, 2)  AS investment_bn,
    DENSE_RANK() OVER (
        PARTITION BY year
        ORDER BY ai_investment_usd_bn DESC
    ) AS rank_in_year
FROM ai_geo
ORDER BY year, rank_in_year;


Q12. Show cumulative (running total) AI investment per country across years.
Expected Answer:  USA cumulative investment crossed $100B in 2021 and reached $349B by 2024. China cumulative is $63.8B — just 18% of USA total, showing the scale of the investment divide.

SELECT
    country,
    year,
    ROUND(ai_investment_usd_bn, 2)  AS yearly_investment_bn,
    ROUND(SUM(ai_investment_usd_bn) OVER (
        PARTITION BY country
        ORDER BY year
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2)                           AS cumulative_investment_bn
FROM ai_geo
ORDER BY country, year;

Q13. Calculate year-over-year adoption change per industry using LAG.
Expected Answer:  Technology had its biggest single-year jump in 2021 (+8.5pp). Every industry showed positive YoY in 2020 — COVID accelerated AI adoption unexpectedly across all sectors.

SELECT
    industry,
    region,
    year,
    ROUND(ai_adoption_rate_pct, 2)  AS adoption_pct,
    ROUND(
        LAG(ai_adoption_rate_pct)
        OVER (PARTITION BY industry, region ORDER BY year)
    , 2)                            AS prev_year_pct,
    ROUND(
        ai_adoption_rate_pct -
        LAG(ai_adoption_rate_pct)
        OVER (PARTITION BY industry, region ORDER BY year)
    , 2)                            AS yoy_change_pp
FROM ai_industry
ORDER BY industry, region, year;


Q14. Calculate each cloud providers exact % share of total revenue per year using window SUM.
Expected Answer:  This calculates live share from actual revenue. AWS share fell from 33% to 30% (2019–2024). Azure rose 18% to 25%. GCP grew from 9% to 12%. The 3-way race is tightening.

SELECT
    year,
    provider_name,
    ROUND(cloud_revenue_usd_bn, 2)  AS revenue_bn,
    ROUND(
        cloud_revenue_usd_bn /
        SUM(cloud_revenue_usd_bn) OVER (PARTITION BY year) * 100
    , 2)                            AS calculated_share_pct
FROM ai_cloud
ORDER BY year, calculated_share_pct DESC;


Q15. Show a 3-year moving average of AI market revenue per country.
Expected Answer:  Moving average smooths out the 2021 GenAI spike. India shows the cleanest, most consistent upward curve with no dips — the most stable growth story in the dataset.

SELECT
    country,
    year,
    ROUND(market_revenue_usd_bn, 2)  AS yearly_revenue_bn,
    ROUND(AVG(market_revenue_usd_bn) OVER (
        PARTITION BY country
        ORDER BY year
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2)                            AS moving_avg_3yr_bn
FROM ai_geo
ORDER BY country, year;


Q16. Calculate the 5-year CAGR of AI market revenue per country (2019 to 2024).
Expected Answer:  India leads CAGR at ~38.5%. UAE and Singapore lead their regions at ~29% and ~24%. USA shows ~52% CAGR driven by the GenAI investment surge in 2023–2024.

SELECT
    country,
    region,
    ROUND(MIN(CASE WHEN year = 2019 THEN market_revenue_usd_bn END), 2)  AS rev_2019,
    ROUND(MAX(CASE WHEN year = 2024 THEN market_revenue_usd_bn END), 2)  AS rev_2024,
    ROUND(
        (POWER(
            MAX(CASE WHEN year = 2024 THEN market_revenue_usd_bn END) /
            NULLIF(MIN(CASE WHEN year = 2019 THEN market_revenue_usd_bn END), 0),
            1.0 / 5
        ) - 1) * 100
    , 2)                                                                  AS cagr_5yr_pct
FROM ai_geo
GROUP BY country, region
HAVING rev_2019 IS NOT NULL AND rev_2024 IS NOT NULL
ORDER BY cagr_5yr_pct DESC;


Q17. Categorise each industry by its scaling tier based on pilot-to-production rate.
Expected Answer:  Technology and Professional Services are Scale Leaders (60%+). Healthcare and Government are Struggling (<30%). This shows exactly where AI ROI is being lost.

SELECT
    industry,
    ROUND(AVG(ai_adoption_rate_pct), 2)    AS avg_adoption_pct,
    ROUND(AVG(pilot_to_prod_rate_pct), 1)  AS avg_prod_rate_pct,
    ROUND(100 - AVG(pilot_to_prod_rate_pct), 1)  AS stuck_in_pilot_pct,
    ROUND(AVG(ai_spending_usd_bn), 2)      AS avg_spend_bn,
    CASE
        WHEN AVG(pilot_to_prod_rate_pct) >= 60 THEN 'Scale Leader'
        WHEN AVG(pilot_to_prod_rate_pct) >= 45 THEN 'Moderate Scaler'
        WHEN AVG(pilot_to_prod_rate_pct) >= 30 THEN 'Slow Scaler'
        ELSE 'Struggling'
    END AS scaling_tier
FROM ai_industry
WHERE pilot_to_prod_rate_pct IS NOT NULL
GROUP BY industry
ORDER BY avg_prod_rate_pct DESC;


Q18. Compare NLP vs Computer Vision vs Automation adoption and spend year by year.
Expected Answer:  Automation has the highest avg adoption (50%+) as cost savings drive adoption. NLP surged after 2022 due to the GenAI effect. Computer Vision is lowest but fastest-growing in Manufacturing.

SELECT
    year,
    use_case_category,
    ROUND(AVG(ai_adoption_rate_pct), 2)  AS avg_adoption_pct,
    ROUND(SUM(ai_spending_usd_bn), 2)    AS total_spend_bn,
    COUNT(*)                             AS record_count
FROM ai_industry
WHERE use_case_category IN (
    'NLP', 'Computer Vision', 'Automation', 'Predictive Analytics'
)
GROUP BY year, use_case_category
ORDER BY year, avg_adoption_pct DESC;


Q19. Compare G20 vs Non-G20 countries on investment, readiness, and market revenue.
Expected Answer:  G20 nations average $19.6B annual investment vs $0.6B for non-G20 — a 32x gap. Average readiness: 84 (G20) vs 56 (non-G20). This 28-point gap defines the global AI divide.

SELECT
    CASE
        WHEN is_g20_member = 1 THEN 'G20 Members'
        ELSE 'Non-G20 Countries'
    END                                   AS country_group,
    year,
    COUNT(DISTINCT country)               AS country_count,
    ROUND(AVG(ai_investment_usd_bn), 2)   AS avg_investment_bn,
    ROUND(SUM(ai_investment_usd_bn), 2)   AS total_investment_bn,
    ROUND(AVG(ai_readiness_score), 2)     AS avg_readiness_score,
    ROUND(AVG(market_revenue_usd_bn), 2)  AS avg_market_revenue_bn
FROM ai_geo
GROUP BY country_group, year
ORDER BY year, country_group;


Q20. Which countries improved their AI readiness score the most from 2019 to 2024?
Expected Answer:  Indonesia improved +19.5 points — the biggest gain globally. India gained +15.8 points, UAE gained +13.7 points. These 3 are the highest-priority targets for AI infrastructure investment.

SELECT
    country,
    region,
    income_group,
    ROUND(
        MIN(CASE WHEN year = 2019 THEN ai_readiness_score END)
    , 2)  AS readiness_2019,
    ROUND(
        MAX(CASE WHEN year = 2024 THEN ai_readiness_score END)
    , 2)  AS readiness_2024,
    ROUND(
        MAX(CASE WHEN year = 2024 THEN ai_readiness_score END) -
        MIN(CASE WHEN year = 2019 THEN ai_readiness_score END)
    , 2)  AS readiness_improvement
FROM ai_geo
GROUP BY country, region, income_group
HAVING readiness_2019 IS NOT NULL AND readiness_2024 IS NOT NULL
ORDER BY readiness_improvement DESC;
