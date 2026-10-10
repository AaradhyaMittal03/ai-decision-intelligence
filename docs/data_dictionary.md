# Data dictionary

| Field | Type | Meaning |
|---|---|---|
| event_id | string | Unique identifier for one event |
| user_id | integer | Synthetic user identifier |
| session_id | string | Synthetic session identifier |
| event_timestamp | UTC timestamp | Time the event occurred |
| event_date | date string | UTC date derived during cleaning |
| event_type | category | page_view, search, product_view, add_to_cart, checkout, purchase |
| device | category | Android, iOS, Desktop, Tablet |
| country | category | Synthetic country label |
| product_id | string | Synthetic product identifier |
| session_duration_seconds | float | Synthetic session-duration value |
| page_latency_ms | float | Synthetic page latency in milliseconds |
| click_count | integer | Number of clicks associated with the event |
| conversion | 0/1 | Synthetic conversion flag; simplified for this demo |
| revenue | float | Synthetic revenue associated with purchase events; otherwise zero |

## Important caveats

The data is simulated, not collected from real users. `conversion` is generated at the event level for demo convenience. It is not a rigorous session-level conversion definition. The inactivity label is based on each user's last observed event relative to the maximum timestamp in the generated data and is not an independently observed future outcome.
