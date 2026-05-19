# Data Dictionary

| Table | Grain | Purpose |
|---|---|---|
| `data/customers.csv` | customer | Synthetic owner and vehicle attributes used for retention scoring |
| `data/campaign_performance.csv` | rooftop x week x channel | Marketing spend, appointments, sales, attributed gross, and ROAS inputs |
| `data/service_opportunities.csv` | customer x trigger | Recall, inspection, lapse, declined work, alignment, and fleet service opportunities |
| `data/source_quality_checks.csv` | source system | Freshness, match rate, join key, quality risk, and recommended controls |
| `data/ai_use_cases.csv` | AI use case | Practical automation ideas with effort, gross impact, risk, and control |
| `analysis/outputs/channel_roi_summary.csv` | channel | Dashboard-ready marketing ROI and recommendation summary |
| `analysis/outputs/retention_priority_queue.csv` | top service opportunity | Manager-ready retention call list |
| `analysis/outputs/data_quality_queue.csv` | source system | Ranked source quality risk queue |
| `analysis/outputs/dashboard_payload.json` | artifact payload | JSON consumed by the static web app |
| `analysis/outputs/summary.json` | artifact summary | Top-level metrics used by README and app |
