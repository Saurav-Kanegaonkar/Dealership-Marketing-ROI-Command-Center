-- Dealership marketing ROI reporting examples.
-- These Snowflake-style queries show how the artifact would be validated in a warehouse.

-- 1. Channel ROI by rooftop and campaign channel.
select
  rooftop,
  channel,
  sum(spend) as spend,
  sum(attributed_gross) as attributed_gross,
  sum(attributed_gross) / nullif(sum(spend), 0) as roas,
  sum(shown_appointments) / nullif(sum(booked_appointments), 0) as show_rate
from campaign_performance
group by 1, 2
order by roas desc;

-- 2. Weekly service retention queue.
select
  customer_id,
  rooftop,
  opportunity_type,
  best_channel,
  priority_score,
  predicted_book_rate,
  estimated_gross,
  recommended_next_step
from service_opportunities
where priority_score >= 85
order by priority_score desc, estimated_gross desc;

-- 3. Source controls that need an owner before recurring reporting.
select
  source,
  rows,
  freshness_score,
  match_rate,
  join_key,
  quality_risk,
  recommended_control
from source_quality_checks
where quality_risk >= 20
order by quality_risk desc;

-- 4. Vendor spend requiring incrementality proof.
select
  channel,
  sum(spend) as spend,
  sum(attributed_gross) as attributed_gross,
  sum(attributed_gross) / nullif(sum(spend), 0) as roas
from campaign_performance
where vendor_flag = 1
group by 1
having sum(attributed_gross) / nullif(sum(spend), 0) < 1.5;
