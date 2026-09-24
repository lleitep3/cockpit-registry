#!/usr/bin/env bash
set -euo pipefail

PACKAGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$PACKAGE_ROOT/bin/cloud-infrastructure"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEST_ROOT"' EXIT

components_output="$($CLI components)"
grep -q "storage-private-s3" <<<"$components_output"
grep -q "identity-cognito" <<<"$components_output"

target="$TEST_ROOT/generated-infra"
$CLI init \
  --create "$target" \
  --project-name sample-infra \
  --display-name "Sample Infra" \
  --client-slug sample \
  --region eu-west-1 \
  --environment dev \
  --yes

test -d "$target/.git"
test -f "$target/environments/dev/main.tf"
grep -q 'default     = "eu-west-1"' "$target/environments/dev/variables.tf"
grep -q 'default     = "sample-infra"' "$target/environments/dev/variables.tf"
grep -q 'Sample Infra' "$target/modules/cognito/main.tf"
! grep -R -q '__PROJECT_' "$target"

$CLI validate "$target"
printf 'cloud-infrastructure CLI tests passed\n'
