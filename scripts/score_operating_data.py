import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"
DATA.mkdir(exist_ok=True)
OUTPUTS.mkdir(parents=True, exist_ok=True)

random.seed(42)

ROOFTOPS = [
    ("CDJR", "Chrysler Dodge Jeep Ram", "Wrightsville", 0.57),
    ("FORD", "Ford", "Willow Street", 0.43),
]

CHANNELS = [
    ("Email service reminders", "email", 0.018, 36, 4200),
    ("Paid search fixed ops", "paid_search", 0.032, 12, 11800),
    ("Social inventory retargeting", "paid_social", 0.021, 8, 7600),
    ("Recall list outreach", "email_sms", 0.041, 44, 3100),
    ("Third-party lead provider", "vendor", 0.019, 5, 15400),
    ("Commercial service prospecting", "email_phone", 0.026, 18, 5200),
    ("Declined service recovery", "email_sms", 0.035, 31, 2600),
]

OPPORTUNITY_TYPES = [
    ("Recall due", 0.19, 0.38, 315),
    ("State inspection due", 0.24, 0.31, 285),
    ("Service lapse 12+ months", 0.22, 0.24, 245),
    ("Declined work recovery", 0.16, 0.29, 410),
    ("Hunter alignment finding", 0.12, 0.34, 195),
    ("Commercial fleet service", 0.07, 0.27, 520),
]

OWNERS = ["Service", "Sales", "Parts", "Marketing", "Commercial"]
BRANDS = ["Ram", "Jeep", "Dodge", "Chrysler", "Commercial"]


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def clamp(value, low, high):
    return max(low, min(high, value))


def weighted_rooftop():
    roll = random.random()
    return ROOFTOPS[0] if roll <= ROOFTOPS[0][3] else ROOFTOPS[1]


customers = []
for index in range(1, 481):
    rooftop_code, rooftop_name, market, _weight = weighted_rooftop()
    brand = random.choice(BRANDS if rooftop_code == "CDJR" else ["Ford", "Commercial"])
    customer_type = random.choices(["Retail", "Commercial", "Fleet"], weights=[0.74, 0.18, 0.08])[0]
    months_since_service = clamp(int(random.gauss(10, 6)), 0, 36)
    lifetime_ro = max(1, int(random.gauss(5, 3)))
    last_ro_gross = round(clamp(random.gauss(285, 115), 95, 890), 0)
    recall_open = 1 if random.random() < 0.18 else 0
    inspection_due_days = int(clamp(random.gauss(55, 70), -35, 210))
    alignment_flag = 1 if random.random() < 0.17 else 0
    declined_work = 1 if random.random() < 0.21 else 0
    phone_answer_rate = round(clamp(random.gauss(0.62, 0.18), 0.15, 0.96), 2)
    email_engagement = round(clamp(random.gauss(0.34, 0.16), 0.02, 0.86), 2)

    customers.append(
        {
            "customer_id": f"CUST{index:04d}",
            "rooftop": rooftop_name,
            "market": market,
            "brand": brand,
            "customer_type": customer_type,
            "months_since_service": months_since_service,
            "lifetime_repair_orders": lifetime_ro,
            "last_repair_order_gross": int(last_ro_gross),
            "open_recall": recall_open,
            "inspection_due_days": inspection_due_days,
            "hunter_alignment_flag": alignment_flag,
            "declined_work_flag": declined_work,
            "phone_answer_rate": phone_answer_rate,
            "email_engagement": email_engagement,
        }
    )

campaigns = []
for week in range(1, 17):
    for rooftop_code, rooftop_name, _market, _weight in ROOFTOPS:
        for channel_name, channel_type, conversion_rate, roi_benchmark, base_spend in CHANNELS:
            spend = int(base_spend * random.uniform(0.72, 1.32))
            if channel_type == "paid_search":
                delivered = int(spend / random.uniform(7.5, 13.5))
                rate_floor, rate_ceiling = 0.018, 0.075
            elif channel_type == "paid_social":
                delivered = int(spend / random.uniform(9.5, 18.0))
                rate_floor, rate_ceiling = 0.01, 0.05
            elif channel_type == "vendor":
                delivered = int(spend / random.uniform(65.0, 120.0))
                rate_floor, rate_ceiling = 0.08, 0.24
            elif channel_type == "email_phone":
                delivered = int(spend / random.uniform(18.0, 36.0))
                rate_floor, rate_ceiling = 0.08, 0.22
            else:
                delivered = int(spend * random.uniform(2.4, 4.8))
                rate_floor, rate_ceiling = 0.006, 0.07
            booked = int(delivered * clamp(random.gauss(conversion_rate, conversion_rate / 3), rate_floor, rate_ceiling))
            show_rate = clamp(random.gauss(0.78, 0.09), 0.46, 0.94)
            repair_orders = int(booked * show_rate)
            avg_gross = clamp(random.gauss(285, 82), 145, 610)
            sales_units = 0
            if "inventory" in channel_name.lower() or "lead provider" in channel_name.lower():
                sales_units = int(booked * random.uniform(0.08, 0.18))
            attributed_gross = int(repair_orders * avg_gross + sales_units * random.uniform(1450, 2700))
            roi = round((attributed_gross - spend) / spend, 2)
            vendor_flag = 1 if channel_type == "vendor" else 0
            campaigns.append(
                {
                    "week": f"2026-W{week:02d}",
                    "rooftop": rooftop_name,
                    "channel": channel_name,
                    "channel_type": channel_type,
                    "spend": spend,
                    "delivered_or_clicks": delivered,
                    "booked_appointments": booked,
                    "shown_appointments": repair_orders,
                    "sales_units": sales_units,
                    "attributed_gross": attributed_gross,
                    "roi": roi,
                    "roi_benchmark": roi_benchmark,
                    "vendor_flag": vendor_flag,
                }
            )

opportunities = []
for customer in customers:
    for opportunity_type, base_rate, conversion_multiplier, gross_value in OPPORTUNITY_TYPES:
        trigger = random.random() < base_rate
        if opportunity_type == "Recall due":
            trigger = bool(customer["open_recall"])
        elif opportunity_type == "State inspection due":
            trigger = customer["inspection_due_days"] <= 45 and random.random() < 0.72
        elif opportunity_type == "Service lapse 12+ months":
            trigger = customer["months_since_service"] >= 12 and random.random() < 0.68
        elif opportunity_type == "Declined work recovery":
            trigger = bool(customer["declined_work_flag"])
        elif opportunity_type == "Hunter alignment finding":
            trigger = bool(customer["hunter_alignment_flag"])
        elif opportunity_type == "Commercial fleet service":
            trigger = customer["customer_type"] in {"Commercial", "Fleet"} and random.random() < 0.34

        if not trigger:
            continue

        urgency = 0
        if customer["open_recall"]:
            urgency += 24
        if customer["inspection_due_days"] <= 30:
            urgency += 18
        if customer["months_since_service"] >= 12:
            urgency += 16
        if customer["declined_work_flag"]:
            urgency += 13
        if customer["hunter_alignment_flag"]:
            urgency += 11
        if customer["customer_type"] in {"Commercial", "Fleet"}:
            urgency += 9

        response_score = (
            customer["email_engagement"] * 28
            + customer["phone_answer_rate"] * 24
            + customer["lifetime_repair_orders"] * 1.7
        )
        predicted_book_rate = clamp(
            conversion_multiplier
            + customer["email_engagement"] * 0.09
            + customer["phone_answer_rate"] * 0.05
            - customer["months_since_service"] * 0.003,
            0.05,
            0.62,
        )
        estimated_gross = int(gross_value * (1 + customer["lifetime_repair_orders"] / 12))
        priority_score = round(
            clamp(urgency * 0.72 + response_score * 0.58 + predicted_book_rate * 45 + estimated_gross / 65, 0, 100),
            1,
        )
        best_channel = "Email + SMS"
        if customer["phone_answer_rate"] > 0.72:
            best_channel = "Phone + Email"
        if customer["email_engagement"] < 0.18:
            best_channel = "Phone follow-up"
        if opportunity_type == "Hunter alignment finding":
            best_channel = "Advisor video + SMS"

        opportunities.append(
            {
                "customer_id": customer["customer_id"],
                "rooftop": customer["rooftop"],
                "brand": customer["brand"],
                "opportunity_type": opportunity_type,
                "best_channel": best_channel,
                "priority_score": priority_score,
                "predicted_book_rate": round(predicted_book_rate, 3),
                "estimated_gross": estimated_gross,
                "owner": "Service" if opportunity_type != "Commercial fleet service" else "Commercial",
                "recommended_next_step": {
                    "Recall due": "Send safety recall booking sequence",
                    "State inspection due": "Trigger inspection reminder with online scheduler",
                    "Service lapse 12+ months": "Run win-back offer with advisor call list",
                    "Declined work recovery": "Send deferred maintenance estimate recap",
                    "Hunter alignment finding": "Send alignment finding video and tire offer",
                    "Commercial fleet service": "Assign fleet service cadence outreach",
                }[opportunity_type],
            }
        )

source_quality = []
source_specs = [
    ("CRM customer records", 97, 0.91, "customer_id"),
    ("DMS service history", 99, 0.95, "vin"),
    ("Recall manifest", 74, 0.84, "vin"),
    ("State inspection list", 88, 0.79, "vin"),
    ("Hunter alignment export", 61, 0.68, "repair_order"),
    ("Phone system leads", 82, 0.72, "phone"),
    ("Google Analytics events", 96, 0.76, "gclid"),
    ("Paid media invoices", 93, 0.88, "campaign_id"),
    ("Social content calendar", 86, 0.81, "post_id"),
]
for source, freshness, match_rate, join_key in source_specs:
    rows = int(random.uniform(400, 9200))
    missing_owner = 1 if match_rate < 0.75 or freshness < 70 else 0
    source_quality.append(
        {
            "source": source,
            "rows": rows,
            "freshness_score": freshness,
            "match_rate": match_rate,
            "join_key": join_key,
            "quality_risk": round((100 - freshness) * 0.45 + (1 - match_rate) * 70 + missing_owner * 8, 1),
            "recommended_control": "Map owner and reconcile weekly" if missing_owner else "Monitor in weekly load check",
        }
    )

ai_use_cases = [
    {
        "use_case": "Recall outreach content assistant",
        "workflow": "Draft channel-specific copy from VIN recall type and appointment availability",
        "owner": "Marketing",
        "effort_hours": 12,
        "expected_monthly_gross": 18600,
        "risk_level": "Low",
        "control": "Human approval before send",
    },
    {
        "use_case": "Service lapse targeting score",
        "workflow": "Prioritize customers by service gap, lifetime RO count, and response history",
        "owner": "Service",
        "effort_hours": 18,
        "expected_monthly_gross": 24750,
        "risk_level": "Medium",
        "control": "Explainable scorecard and opt-out filters",
    },
    {
        "use_case": "Inbound call summarizer",
        "workflow": "Summarize phone leads, tag intent, and route missed opportunities",
        "owner": "BDC",
        "effort_hours": 22,
        "expected_monthly_gross": 15300,
        "risk_level": "Medium",
        "control": "PII minimization and transcript retention policy",
    },
    {
        "use_case": "Photo and social post QA checklist",
        "workflow": "Check missing photos, captions, and brand-safe vehicle posts",
        "owner": "Marketing",
        "effort_hours": 10,
        "expected_monthly_gross": 8900,
        "risk_level": "Low",
        "control": "Template library and final human review",
    },
]

campaign_summary = defaultdict(lambda: {"spend": 0, "gross": 0, "booked": 0, "shown": 0})
for row in campaigns:
    key = row["channel"]
    campaign_summary[key]["spend"] += row["spend"]
    campaign_summary[key]["gross"] += row["attributed_gross"]
    campaign_summary[key]["booked"] += row["booked_appointments"]
    campaign_summary[key]["shown"] += row["shown_appointments"]

channel_rows = []
for channel, values in campaign_summary.items():
    spend = values["spend"]
    gross = values["gross"]
    roas = gross / spend if spend else 0
    show_rate = values["shown"] / values["booked"] if values["booked"] else 0
    channel_rows.append(
        {
            "channel": channel,
            "spend": spend,
            "attributed_gross": gross,
            "roas": round(roas, 2),
            "booked_appointments": values["booked"],
            "show_rate": round(show_rate, 3),
            "recommendation": "Scale" if roas >= 5 else "Fix measurement" if "provider" in channel.lower() else "Optimize",
        }
    )
channel_rows.sort(key=lambda item: item["roas"], reverse=True)

opportunities.sort(key=lambda item: item["priority_score"], reverse=True)
top_opportunities = []
seen_customers = set()
for item in opportunities:
    if item["customer_id"] in seen_customers:
        continue
    top_opportunities.append(item)
    seen_customers.add(item["customer_id"])
    if len(top_opportunities) == 40:
        break

budget_waste = sum(row["spend"] for row in campaigns if row["vendor_flag"] and row["roi"] < 1.4)
total_spend = sum(row["spend"] for row in campaigns)
total_gross = sum(row["attributed_gross"] for row in campaigns)
total_booked = sum(row["booked_appointments"] for row in campaigns)
total_shown = sum(row["shown_appointments"] for row in campaigns)
avg_roas = total_gross / total_spend
retention_queue_value = sum(row["estimated_gross"] * row["predicted_book_rate"] for row in top_opportunities)
high_quality_sources = sum(1 for row in source_quality if row["quality_risk"] < 22)

summary = {
    "total_spend": total_spend,
    "total_gross": total_gross,
    "avg_roas": round(avg_roas, 2),
    "booked_appointments": total_booked,
    "shown_appointments": total_shown,
    "show_rate": round(total_shown / total_booked, 3),
    "retention_queue_customers": len(top_opportunities),
    "retention_queue_expected_gross": int(retention_queue_value),
    "budget_waste": budget_waste,
    "high_quality_sources": high_quality_sources,
    "source_count": len(source_quality),
    "top_opportunity_type": top_opportunities[0]["opportunity_type"],
}

write_csv(
    DATA / "customers.csv",
    customers,
    [
        "customer_id",
        "rooftop",
        "market",
        "brand",
        "customer_type",
        "months_since_service",
        "lifetime_repair_orders",
        "last_repair_order_gross",
        "open_recall",
        "inspection_due_days",
        "hunter_alignment_flag",
        "declined_work_flag",
        "phone_answer_rate",
        "email_engagement",
    ],
)
write_csv(
    DATA / "campaign_performance.csv",
    campaigns,
    [
        "week",
        "rooftop",
        "channel",
        "channel_type",
        "spend",
        "delivered_or_clicks",
        "booked_appointments",
        "shown_appointments",
        "sales_units",
        "attributed_gross",
        "roi",
        "roi_benchmark",
        "vendor_flag",
    ],
)
write_csv(
    DATA / "service_opportunities.csv",
    opportunities,
    [
        "customer_id",
        "rooftop",
        "brand",
        "opportunity_type",
        "best_channel",
        "priority_score",
        "predicted_book_rate",
        "estimated_gross",
        "owner",
        "recommended_next_step",
    ],
)
write_csv(
    DATA / "source_quality_checks.csv",
    source_quality,
    [
        "source",
        "rows",
        "freshness_score",
        "match_rate",
        "join_key",
        "quality_risk",
        "recommended_control",
    ],
)
write_csv(
    DATA / "ai_use_cases.csv",
    ai_use_cases,
    [
        "use_case",
        "workflow",
        "owner",
        "effort_hours",
        "expected_monthly_gross",
        "risk_level",
        "control",
    ],
)
write_csv(
    OUTPUTS / "channel_roi_summary.csv",
    channel_rows,
    ["channel", "spend", "attributed_gross", "roas", "booked_appointments", "show_rate", "recommendation"],
)
write_csv(
    OUTPUTS / "retention_priority_queue.csv",
    top_opportunities,
    [
        "customer_id",
        "rooftop",
        "brand",
        "opportunity_type",
        "best_channel",
        "priority_score",
        "predicted_book_rate",
        "estimated_gross",
        "owner",
        "recommended_next_step",
    ],
)
write_csv(
    OUTPUTS / "data_quality_queue.csv",
    sorted(source_quality, key=lambda item: item["quality_risk"], reverse=True),
    ["source", "rows", "freshness_score", "match_rate", "join_key", "quality_risk", "recommended_control"],
)

payload = {
    "summary": summary,
    "channels": channel_rows,
    "opportunities": top_opportunities[:12],
    "quality": sorted(source_quality, key=lambda item: item["quality_risk"], reverse=True),
    "ai": ai_use_cases,
}
(OUTPUTS / "dashboard_payload.json").write_text(json.dumps(payload, indent=2))
(OUTPUTS / "summary.json").write_text(json.dumps(summary, indent=2))

print("Generated dealership marketing ROI artifact data")
print(f"Customers: {len(customers)}")
print(f"Campaign rows: {len(campaigns)}")
print(f"Service opportunities: {len(opportunities)}")
print(f"Average ROAS: {summary['avg_roas']}x")
print(f"Retention queue expected gross: ${summary['retention_queue_expected_gross']:,}")
