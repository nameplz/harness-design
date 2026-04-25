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

### `runtime`

Optional runtime metadata for selecting a CLI adapter without changing the core harness contract.

- `platform`: `codex`, `claude-code`, or `gemini-cli`
- `adapter_path`: explicit path to the active adapter directory
- `execution_mode`: `native-multi-agent` or `single-agent-sequenced`
- `capabilities`: optional runtime overrides
- `prompt_overrides`: optional prompt path overrides

If `runtime` is present, `platform` and `adapter_path` should both be present.

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

Each configured path must exist at execution time. It is valid to point at checked-in template policy files or at copied project-specific policy files, but the runtime should use only the paths declared in `project.yaml`.

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

## Runtime Contract

The harness core stays vendor-neutral. CLI-specific behavior should be attached through adapter files rather than baked into the core policy or artifact contract.

### `runtime.capabilities`

Use this only for project-specific overrides. Adapter defaults should live in the adapter itself.

- `subagents`
- `interactive_approval`
- `browser_automation`
- `structured_patch`
- `web_access`

### `runtime.prompt_overrides`

Optional explicit prompt paths:

- `operator`
- `planner`
- `generator`
- `evaluator`

Any configured override path must exist at execution time.

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

## Adapter Contract

Each adapter directory should provide:

- `operator.prompt.md`
- `capabilities.yaml`
- `bootstrap-notes.md`

The runtime should resolve behavior in this order:

1. `project.yaml.runtime.prompt_overrides`
2. files under `project.yaml.runtime.adapter_path`
3. shared role prompts under `harness/roles/`

The runtime should not guess alternate adapter names or paths.

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
