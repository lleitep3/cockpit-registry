---
name: infrastructure-critic
description: Review Terraform and IaC PRs for integration, flexibility, gaps, and operational risk.
---

# Infrastructure Critic

Use this skill when reviewing an infrastructure-as-code PR, Terraform module,
cloud architecture proposal, or deployment change. The goal is to find concrete
risks and missing design decisions before implementation or apply.

## Review scope

Inspect the PR diff, repository conventions, related modules, environment roots,
CI workflows, documentation, and tests. Review the proposal as a connected
system, not as isolated resources.

Prioritize:

- integration between modules, resources, providers, environments, and pipelines;
- variable design: correct types, defaults, validation, sensitivity, naming,
  environment flexibility, and avoidance of hidden hardcoding;
- output design: useful consumer-facing values, stable names, sensitive outputs,
  and no unnecessary leakage;
- resource boundaries, dependencies, ordering, provider aliases, regions, and
  state separation;
- security: least privilege, public exposure, encryption, secrets, IAM/OIDC,
  network boundaries, and destructive behavior;
- cost: always-on resources, regional pricing, data transfer, logs, lifecycle,
  quotas, and missing budgets or alerts;
- operability: observability, drift, backup/recovery, rollout, rollback,
  idempotence, failure modes, and ownership;
- testability: fmt, validate, plan, lint, security scans, policy checks, smoke
  tests, and whether the CI actually exercises the changed paths;
- proposal gaps: unresolved account, region, domain, environment, data,
  compliance, availability, or acceptance criteria decisions.

## Review method

1. Establish the intended outcome, environments, account ownership, region,
   budget, data sensitivity, availability target, recovery expectation, and
   rollback boundary. Mark unknowns explicitly; do not invent values.
2. Map each changed logical component to its consumers and dependencies. Check
   whether the integration is represented in variables, outputs, IAM policies,
   workflow inputs, and documentation.
3. Compare the diff with repository patterns before suggesting redesign. Reuse
   existing module and environment conventions where they are sound.
4. Trace the main and failure paths: create, update, destroy, partial failure,
   deployment retry, drift, and rollback.
5. Run safe local checks when available. Prefer read-only validation; never run
   apply, destroy, migration, credential changes, or production mutations as
   part of a review without explicit authorization.
6. Report findings ordered by severity and cite exact file/line locations.

## Severity

- P0: likely outage, data loss, privilege escalation, secret exposure, or
  irreversible/destructive action.
- P1: high-probability production failure, broken environment integration,
  unsafe deployment/rollback, or materially uncontrolled cost/security risk.
- P2: correctness, maintainability, operability, or test gap that should be
  fixed before merge when practical.
- P3: improvement or consistency suggestion with limited immediate risk.

Do not report style preferences as findings. A finding must explain the failure
mode, affected scope, evidence, and a concrete fix or decision needed.

## Output format

Start with the overall verdict: `block`, `request changes`, `approve with
follow-ups`, or `no findings`.

Then provide findings in this format:

```text
[P1] Short problem statement
Location: path/to/file.tf:line
Evidence: what the diff/repository shows.
Impact: what can fail, leak, cost more, or become difficult to operate.
Recommendation: smallest safe fix or explicit decision required.
```

After findings, include compact sections:

- Integration map: changed components and their consumers.
- Missing decisions: unresolved inputs that block safe implementation or apply.
- Validation performed: commands/checks and results.
- Residual risk: what remains after the proposed fixes.

If the user asks for implementation, keep review and fixes separate: first state
findings, then make only the requested changes, re-run relevant checks, and
summarize the remaining risk.

## Boundaries

This is a review skill, not authorization to apply infrastructure, merge PRs,
create credentials, or change production. For architecture planning, include
component count, dependencies, cost, risks, acceptance criteria, and rollback,
but leave implementation to the user-approved next step.
