# Harness Workflow

This document defines the reusable operating model for the harness.

## 1. Inputs

Every run starts with:

- a short project brief
- optional examples or reference material
- stack and environment constraints
- delivery expectations
- evaluation priorities

These inputs are normalized into `project.yaml` and then used by all agents.

`project.yaml` is the single machine-readable entry point for the run. The operator should not infer active policies, artifact paths, or approval gates from directory contents.
When runtime metadata is present, the operator should also resolve the active CLI adapter from `project.yaml.runtime` rather than inferring one from the local environment.

## 2. Agent Roles

- Planner: converts a brief into a product spec and staged roadmap
- Generator: implements the next agreed scope of work
- Evaluator: checks alignment, tests behavior, and blocks incomplete work

Optional roles:

- Researcher: gathers domain or API context
- Reviewer: focuses on code quality and maintainability
- Release agent: packages, documents, and prepares handoff

These roles are logical responsibilities, not a requirement for parallel subagents. A CLI with limited delegation support may execute them sequentially while keeping the same artifact contract.

## 3. Operating Modes

### Continuous Mode

Use when the model can hold coherence across the full run.

- Planner writes a full spec.
- Generator builds against the spec.
- Evaluator reviews at major checkpoints or at the end.
- Generator iterates until thresholds pass.
- This mode works with both `native-multi-agent` and `single-agent-sequenced` execution.

### Sprint Mode

Use when the project is long-running, risky, or the model benefits from decomposition.

- Planner writes a roadmap with sprint candidates.
- For each sprint, generator and evaluator agree on a contract.
- Generator implements only that sprint scope.
- Evaluator runs QA and either passes or sends back defects.
- A handoff artifact records the latest state.
- If the runtime lacks subagent support, the same sprint loop should run sequentially through the operator.

## 4. File-Based State

Treat files as the durable coordination layer.

Required artifacts:

- `01-product-spec.md`
- `02-roadmap.md`
- `03-sprint-contract.md`
- `04-build-handoff.md`
- `05-qa-report.md`
- `06-run-log.md`
- `07-escalation-report.md`
- `08-final-handoff.md`

Benefits:

- less ambiguity across context resets
- easier auditability
- better recovery from interrupted runs
- cleaner collaboration between agents

## 4a. Adapter Layer

The harness should separate the core run contract from CLI-specific execution behavior.

- Core documents define what must happen.
- Adapter documents define how a given CLI should carry it out.
- Missing capabilities should degrade execution mode, not the artifact contract.

Examples:

- no subagents: run planner, generator, and evaluator sequentially
- no browser automation: use the most direct available QA method and record any unverified checks
- no structured patch tool: allow a different edit mechanism without changing build handoff requirements

## 5. Decision Gates

The evaluator should gate progress at three levels:

1. `spec_gate`: is the plan aligned with the brief?
2. `scope_change_gate`: has scope or architecture moved outside the approved envelope?
3. QA decision: does the implementation meet the thresholds?
4. `release_gate`: can the result be handed off or released safely?

If a gate fails, the evaluator must explain:

- what failed
- why it matters
- how to verify the fix

## 6. Context Strategy

Choose one approach per project:

- `compaction`: preserve continuity with summarized history
- `reset + handoff`: start fresh with structured artifacts

Prefer `reset + handoff` when:

- the model becomes inconsistent over time
- context pressure causes premature wrap-up
- the run may span many hours

Prefer `compaction` when:

- the model remains coherent
- the task is tightly coupled
- restart overhead is not worth it

## 7. Evaluation Philosophy

Do not let "looks good" count as QA.

The evaluator should test:

- user-facing behavior
- edge cases and failure states
- data persistence and state transitions
- visual quality where relevant
- alignment with the spec
- code health where relevant

The evaluator must be skeptical by design.

That skepticism should be operationalized through two separate mechanisms:

- an execution protocol that defines the minimum QA sequence for each round
- calibration rules that prevent generous scoring, silent assumptions, and score drift across rounds

## 8. File Contract

The harness should treat the following as stable machine-readable contracts:

- gate IDs come from the approval gates policy
- blocker IDs come from `project.yaml`
- artifact paths come from `project.yaml`
- completion checks come from `project.yaml` and the execution policy

If any of these disagree, the run should stop and write an escalation report instead of guessing.

## 9. Simplification Rule

Every harness component should justify its existence.

After successful runs, ask:

- Can this role be removed?
- Can this loop happen less often?
- Can this check be deferred to the end?
- Can the model now do this reliably without scaffolding?
