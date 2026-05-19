# Executive Findings

## What I analyzed

I modeled 480 synthetic dealership customers, 224 campaign performance rows, 600 service opportunity triggers, 9 source quality checks, and 4 AI automation use cases.

## Findings

- Recall outreach, declined service recovery, and service reminder programs produce the strongest modeled returns because they use first-party owner and service history rather than broad media targeting.
- Third-party lead provider spend is the largest waste flag in the model because the attributed gross is too low relative to invoice spend.
- The highest-priority retention queue combines recall status, state inspection timing, service lapse, declined work, and Hunter alignment findings into a manager-readable score.
- Hunter alignment exports, phone system leads, Google Analytics events, and state inspection lists need explicit join-key and owner controls before they can be trusted in weekly reporting.
- The most practical AI starting points are content assistance for recall outreach, explainable targeting scores for service lapse customers, inbound call summarization, and photo plus social QA checks.

## Recommendation

Run the retention queue weekly, scale first-party service campaigns, require proof of incremental value from third-party spend, and implement AI only where a human approval control is clear.
