# Reusable Agent Harness Skeleton

This repository is a reusable skeleton for long-running project harnesses built around the planner-generator-evaluator pattern.

The current baseline is a quasi-executable v1 spec. An operator or agent should be able to read `project.yaml`, load the explicitly declared policy files and artifact paths, and run the harness without guessing.

## What This Is

Use this project when you want a reusable harness that can be copied into another repository and specialized there.

The harness is designed to make these decisions explicit:

- what the project is trying to deliver
- what quality bar must be met
- which approval gates are active
- which files are the canonical run artifacts
- when the operator should continue, retry, escalate, or stop
- how the evaluator should execute QA and calibrate scoring

## v1 Contract

The v1 contract is centered on [`harness/schema/project.v1.md`](./harness/schema/project.v1.md).

In v1:

- `project.yaml` is the single machine-readable entry point
- policy files are resolved from `project.yaml.policy_files`
- canonical artifact paths are resolved from `project.yaml.artifacts`
- approval gates use stable `gate_id` values
- blockers use stable `blocker_id` values
- project-specific QA checks use stable `check_id` values
- completion is decided from explicit completion-policy fields, not prose
- evaluator QA follows an explicit execution protocol and calibration policy

If those inputs disagree, the operator should stop and write an escalation report rather than infer intent.

## Structure

- `harness/project.template.yaml`: starter `project.yaml` for a real project
- `harness/schema/project.v1.md`: canonical schema and cross-file contract
- `harness/workflow.md`: end-to-end operating model
- `harness/automation.md`: bounded automation loop
- `harness/policies/`: execution, QA, approval-gate, and stop-condition policy templates
- `harness/roles/`: planner, generator, and evaluator role definitions
- `harness/templates/`: canonical artifacts written during a run
- `harness/prompts/`: operator and bootstrap prompts

## Canonical Files

`project.yaml` should declare these file groups explicitly:

- Policy files:
  - execution policy
  - QA policy
  - approval-gates policy
  - stop-conditions policy
- Artifacts:
  - `01-product-spec.md`
  - `02-roadmap.md`
  - `03-sprint-contract.md`
  - `04-build-handoff.md`
  - `05-qa-report.md`
  - `06-run-log.md`
  - `07-escalation-report.md`
  - `08-final-handoff.md`

The defaults live in [`harness/project.template.yaml`](./harness/project.template.yaml), but a real project can point to different paths as long as it does so explicitly.

## Quickstart

1. Copy [`harness/project.template.yaml`](./harness/project.template.yaml) to `project.yaml` in the target project.
2. Fill it out using the rules in [`harness/schema/project.v1.md`](./harness/schema/project.v1.md).
3. Decide whether the project runs in `continuous` or `sprint` mode.
4. Point `policy_files` at the active policy documents for that project.
5. Point `artifacts` at the canonical output files for that run.
6. Fill in quality thresholds, blocker IDs, required gates, and project-specific checks.
7. Adapt prompts and role docs only where domain-specific guidance is actually needed.

## Minimal Runtime Flow

1. Read `project.yaml`.
2. Load the policy files declared in `project.yaml.policy_files`.
3. Resolve artifact paths from `project.yaml.artifacts`.
4. Plan, contract, build, and evaluate according to `project.mode`.
5. Decide pass, retry, escalate, or stop using the configured policies.
6. Write escalation or final handoff artifacts when the run requires them.

## Artifact Expectations

The harness expects certain artifacts to carry machine-usable structure, not only prose.

- `05-qa-report.md` should record scores, threshold results, blocker results, unverified checks, execution coverage, findings, and next action.
- `07-escalation-report.md` should record trigger ID, phase, blocker summary, options, and requested human decision.
- `08-final-handoff.md` should record outcome, completion-policy results, delivered artifacts, deferred work, and operational notes.

## When To Use More Structure

Prefer `sprint` mode when:

- the project is long-running
- the work is risky or multi-surface
- the model tends to drift over longer sessions
- you need explicit scope negotiation between build and QA

Prefer `continuous` mode when:

- the project is small
- the task is tightly coupled
- the model can stay coherent end to end
- per-sprint contracting would add more overhead than value

## Design Principles

- Separate planning, building, and evaluation responsibilities.
- Use files as the durable coordination layer.
- Prefer explicit acceptance criteria over vague completion language.
- Keep bounded autonomy intact.
- Add structure only when it improves reliability.
- Make evaluator judgment repeatable through explicit QA protocol and calibration rules.

## Current Status

This repository now defines the contract for a reusable harness skeleton, not a fully automated runner. It is intended to be read by scripts or agents as a quasi-executable spec and then specialized per project.
