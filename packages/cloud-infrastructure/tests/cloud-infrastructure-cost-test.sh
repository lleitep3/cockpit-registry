#!/usr/bin/env bash
set -euo pipefail

PACKAGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$PACKAGE_ROOT/bin/cloud-infrastructure"
TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT
mkdir -p "$TEMP_DIR/bin" "$TEMP_DIR/mock"

cat > "$TEMP_DIR/mock/actual.json" <<'JSON'
{
  "ResultsByTime": [
    {
      "Groups": [
        {"Keys": ["Amazon Simple Storage Service"], "Metrics": {"UnblendedCost": {"Amount": "1.25", "Unit": "USD"}}},
        {"Keys": ["AWS Lambda"], "Metrics": {"UnblendedCost": {"Amount": "0.75", "Unit": "USD"}}}
      ]
    },
    {
      "Groups": [
        {"Keys": ["Amazon Simple Storage Service"], "Metrics": {"UnblendedCost": {"Amount": "0.50", "Unit": "USD"}}}
      ]
    }
  ]
}
JSON

cat > "$TEMP_DIR/mock/forecast.json" <<'JSON'
{
  "Total": {"Amount": "12.50", "Unit": "USD"},
  "ForecastResultsByTime": [
    {
      "MeanValue": "12.50",
      "PredictionIntervalLowerBound": "9.00",
      "PredictionIntervalUpperBound": "17.00"
    }
  ]
}
JSON

cat > "$TEMP_DIR/bin/aws" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail
case "$*" in
  *get-cost-and-usage*) cat "$MOCK_DIR/actual.json" ;;
  *get-cost-forecast*) cat "$MOCK_DIR/forecast.json" ;;
  *) exit 1 ;;
esac
MOCK
chmod +x "$TEMP_DIR/bin/aws"

cat > "$TEMP_DIR/state.json" <<'JSON'
{
  "values": {
    "root_module": {
      "resources": [
        {"address": "aws_s3_bucket.assets", "type": "aws_s3_bucket"},
        {"address": "aws_cognito_user_pool.main", "type": "aws_cognito_user_pool"}
      ]
    }
  }
}
JSON

cat > "$TEMP_DIR/assumptions.json" <<'JSON'
{"aws_s3_bucket.assets": 1.25}
JSON

export MOCK_DIR="$TEMP_DIR/mock"
actual_output="$(PATH="$TEMP_DIR/bin:$PATH" "$CLI" cost actual --json --start 2026-09-01 --end 2026-09-03 --cost-center partilhar)"
printf '%s' "$actual_output" | grep -q '"total": 2.5'
printf '%s' "$actual_output" | grep -q 'Amazon Simple Storage Service'

forecast_output="$(PATH="$TEMP_DIR/bin:$PATH" "$CLI" cost forecast --json)"
printf '%s' "$forecast_output" | grep -q '"mean": 12.5'
printf '%s' "$forecast_output" | grep -q '"upper": 17.0'

estimate_output="$("$CLI" cost estimate --json --state "$TEMP_DIR/state.json" --assumptions "$TEMP_DIR/assumptions.json")"
printf '%s' "$estimate_output" | grep -q '"scenario_monthly_total": 1.25'
printf '%s' "$estimate_output" | grep -q '"unmodeled_resources": 1'

printf '%s
' "cloud-infrastructure cost tests passed"
