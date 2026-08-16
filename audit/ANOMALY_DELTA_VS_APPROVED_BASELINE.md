# Anomaly Delta vs Approved Baseline

- **Approved Baseline Active**: `6541`
- **Current Raw Anomalies**: `6425`

## Exact Breakdown

- `unchanged`: `6221`
- `resolved`: `248`
- `modified_fingerprint`: `0`
- `replacement_pair`: `72`
- `genuinely_new`: `132`
- `reintroduced`: `0`
- `scope_expansion`: `0`
- `analyzer_model_change`: `0`
- `possible_false_positive`: `0`
- `unqualified`: `0`

Total verification:
`6221 (unchanged) + 72 (replacement_pair) + 132 (genuinely_new) = 6425 (current_raw_anomalies)`
`6221 (unchanged) + 72 (replacement_pair) + 248 (resolved) = 6541 (approved_baseline_active)`

Sum is 100% exact. UNKNOWN = 0.
