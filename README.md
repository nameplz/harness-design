# Reusable Multi-CLI Agent Harness Skeleton

Korean version: [`README.ko.md`](./README.ko.md)

This repository is a reusable skeleton for long-running project harnesses built around the planner-generator-evaluator pattern.

The current baseline is a quasi-executable v1 spec. An operator or agent should be able to read `project.yaml`, load the explicitly declared policy files and artifact paths, and run the harness without guessing.

## What This Is

Use this project when you want a reusable harness that can be copied into another repository and specialized there.
The core contract is vendor-neutral and can be adapted to Codex, Claude Code, Gemini CLI, or other agentic CLIs without changing the underlying project artifacts.

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
- `project.yaml.runtime` may declare the active CLI adapter without changing the core contract
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
- `harness/prompts/`: shared bootstrap and compatibility prompts
- `harness/adapters/`: CLI-specific operator prompts, capability declarations, and bootstrap notes

In this skeleton repository, the default policy files are the checked-in `*.template.yaml` files under `harness/policies/`.
Those defaults are intentionally explicit so a fresh clone can be read without inferring alternate file names.

Supported adapter targets in this repository:

- Codex
- Claude Code
- Gemini CLI

## Platform Guide

Use the same core harness files for every CLI and switch behavior through `project.yaml.runtime`.

### Codex

Recommended when you want the strongest fit with the current repository defaults.

- Set `runtime.platform` to `codex`
- Set `runtime.adapter_path` to `harness/adapters/codex`
- Prefer this when you want native multi-agent execution, explicit approval handling, and structured editing workflows
- Keep shared planner, generator, and evaluator prompts in `harness/roles/` unless the project needs Codex-specific overrides

### Claude Code

Recommended when you want the same artifact-driven workflow but with Claude Code as the top-level operator.

- Set `runtime.platform` to `claude-code`
- Set `runtime.adapter_path` to `harness/adapters/claude-code`
- Prefer this when you want delegated execution but still want approvals, QA gates, and handoff artifacts to remain explicit
- Keep Claude-specific orchestration notes in the adapter files instead of copying them into the shared core prompts

### Gemini CLI

Recommended when you want the same harness contract in a simpler runtime that may rely on sequential execution.

- Set `runtime.platform` to `gemini-cli`
- Set `runtime.adapter_path` to `harness/adapters/gemini-cli`
- Prefer this when you want to preserve the planner-generator-evaluator workflow even if subagents, browser automation, or structured patch tooling are limited
- Assume sequential role execution by default and keep the same artifact, approval, and QA expectations

In all three cases, `project.yaml`, policy files, and artifact paths remain the source of truth. The adapter only changes how the CLI carries out the run, not what the run must produce.

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
2. Treat the default `policy_files` values as valid starter paths for this skeleton. They point at the existing `harness/policies/*.template.yaml` files.
3. Set `runtime.platform` and `runtime.adapter_path` to the active CLI target.
4. Fill out `project.yaml` using the rules in [`harness/schema/project.v1.md`](./harness/schema/project.v1.md).
5. Decide whether the project runs in `continuous` or `sprint` mode.
6. Point `artifacts` at the canonical output files for that run.
7. Fill in quality thresholds, blocker IDs, required gates, and project-specific checks.
8. If you want project-specific policy file names, copy the template policy files to new paths and then update `project.yaml.policy_files` to match those paths exactly.
9. Override prompts or capabilities only when the adapter default is not sufficient.

The runtime contract stays the same in both cases: operators should read only the file paths declared in `project.yaml` and should not guess fallback names such as non-template variants.

## Runtime CLI

This repository includes a small helper CLI for setting the `runtime` block without manually editing YAML.

Use the local wrapper:

```bash
./bin/harness runtime set <platform>
```

Examples:

```bash
./bin/harness runtime set codex
./bin/harness runtime set claude-code --project ./project.yaml
./bin/harness runtime set gemini-cli --set-capability browser_automation=false
./bin/harness runtime set codex --check
./bin/harness runtime set codex --print
```

Notes:

- The executable is `./bin/harness` because this repository already uses `harness/` as a directory name.
- If `project.yaml` is missing, the command can create it from `harness/project.template.yaml`.
- The command only updates `runtime`; it does not rewrite `policy_files`, `artifacts`, or other project settings.
- Adapter defaults come from `harness/adapters/*/capabilities.yaml`.
- Relative runtime paths are resolved from the directory that contains `project.yaml`, so the project should include the `harness/` directory alongside that file.

## Minimal Runtime Flow

1. Read `project.yaml`.
2. Resolve the active adapter from `project.yaml.runtime`.
3. Load the policy files declared in `project.yaml.policy_files`.
4. Resolve artifact paths from `project.yaml.artifacts`.
5. Plan, contract, build, and evaluate according to `project.mode`.
6. Decide pass, retry, escalate, or stop using the configured policies.
7. Write escalation or final handoff artifacts when the run requires them.

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
- Keep the core contract independent from any single CLI.
- Prefer explicit acceptance criteria over vague completion language.
- Keep bounded autonomy intact.
- Add structure only when it improves reliability.
- Make evaluator judgment repeatable through explicit QA protocol and calibration rules.

## Current Status

This repository now defines the contract for a reusable harness skeleton, not a fully automated runner. It is intended to be read by scripts or agents as a quasi-executable spec and then specialized per project.
