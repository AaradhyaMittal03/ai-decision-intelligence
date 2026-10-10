# AI analyst evaluation plan

The current MVP routes questions to fixed analytics intents and optionally uses an LLM only to explain the computed result. Before describing this as a reliable AI agent, build and publish an evaluation set.

## Starter evaluation cases

| Question | Expected intent | Evidence required |
|---|---|---|
| How many events were processed? | event_count | event count from the database |
| What is the average latency? | average_latency | average latency in ms |
| Show revenue by device | revenue_by_device | revenue grouped by device |
| Which country has the most events? | top_country | top country and event count |
| What was conversion yesterday? | latest_conversion | latest available date and defined rate |
| What anomalies were detected? | anomalies | metric, date, observed value, baseline |
| Tell me a joke | unsupported | no SQL execution |

## Measures to implement

- Intent accuracy = correctly routed test questions / total questions.
- Evidence correctness = answers whose numerical claims match query output / evaluated answers.
- Unsupported-query safety = unsupported requests that do not execute database queries / unsupported requests.
- Grounding coverage = material claims linked to returned evidence / all material claims.
- Latency and token cost for optional LLM explanations.

Do not claim an evaluation score until the tests are run and the result is recorded.
