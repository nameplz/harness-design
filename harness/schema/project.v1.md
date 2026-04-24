# Project Schema v1

This schema defines the machine-readable contract for a project-specific harness.

## Goals

- Give the operator one canonical entry point: `project.yaml`
- Remove implicit file discovery
- Use stable IDs for gates, checks, and artifacts
- Make pass/fail, retry, escalation, and completion decisions auditable

## Required Top-Level Fields

### `schema_version`

- Required
- Fixed value: `harness.project/v1`

### `project`

- `id`: stable slug for logs and automation
- `name`: human-readable project name
- `type`: product category such as `web-app`, `library`, `cli`, `service`
- `mode`: `continuous` or `sprint`

### `brief`

- `summary`: short project brief
- `primary_outcome`: concrete end-state
- `user_value`: why the project matters
- `non_goals`: explicit exclusions

### `product_context`

- `target_users`
- `core_jobs`
- `domain_notes`

### `delivery`

- `preferred_stack`
- `target_environments`
- `expected_deliverables`

### `constraints`

- `time_budget_hours`
- `budget_priority`
- `internet_policy`
- `must_use`
- `avoid`

### `quality_bar`

- `weighted_criteria`: numeric weights that sum to 1.0
- `pass_thresholds`: minimum passing scores by criterion
- `blocking_rules`: list of stable blocker IDs and descriptions

### `workflow`

- `planner_enabled`
- `generator_enabled`
- `evaluator_enabled`
- `sprint_contracts_enabled`
- `context_resets_enabled`
- `qa_round_limit`
- `max_build_rounds`
- `auto_retry_failed_rounds`
- `handoff_required`

### `references`

- `examples`
- `source_material`

### `project_specific_checks`

- `must_test`
- `nice_to_test`

Each check should have:

- `check_id`
- `description`

### `ai_features`

- `desired`
- `notes`

### `policy_files`

Explicit paths to the active policy files. The operator should not infer these.

- `execution`
- `qa`
- `approval_gates`
- `stop_conditions`

### `approval`

- `required_gates`: list of gate IDs enabled for this project

Gate IDs must match entries in the approval gates policy.

### `artifacts`

Explicit paths to canonical run artifacts.

- `product_spec`
- `roadmap`
- `sprint_contract`
- `build_handoff`
- `qa_report`
- `run_log`
- `escalation_report`
- `final_handoff`

### `completion_policy`

- `require_all_thresholds`
- `require_core_flows_passing`
- `require_known_critical_bugs_resolved`
- `require_all_required_deliverables`
- `require_handoff_written`

## Policy Contract

## Execution Policy

Must define:

- autonomy mode
- allowed and disallowed actions
- loop limits
- retry policy
- escalation action
- completion requirements

## QA Policy

Must define:

- execution protocol
- calibration rules
- scoring behavior
- severity model
- verdict logic
- requirements for unverified checks

## Approval Gates Policy

Each gate must define:

- `gate_id`
- `required`
- `trigger`
- `approver`
- `decision_options`

## Stop Conditions Policy

Must define structured stop conditions with stable IDs.

## Artifact Contract

## `05-qa-report.md`

Must include:

- verdict status
- round number
- weighted result
- threshold result by criterion
- blocker result by blocker ID
- unverified checks
- execution coverage
- verdict rationale tied to blockers, thresholds, or unverified checks
- findings with severity and repro
- explicit next action

## `07-escalation-report.md`

Must include:

- trigger ID
- current phase
- blocker summary
- safe options
- recommended decision

## `08-final-handoff.md`

Must include:

- outcome
- completion policy result
- final quality summary
- delivered artifacts
- deferred scope
- operational notes

## Ownership

- Planner owns `01-product-spec.md` and `02-roadmap.md`
- Generator owns `03-sprint-contract.md`, `04-build-handoff.md`, and run-log build entries
- Evaluator owns `05-qa-report.md` and run-log QA entries
- Operator owns `07-escalation-report.md` and `08-final-handoff.md`
