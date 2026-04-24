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

## 2. Agent Roles

- Planner: converts a brief into a product spec and staged roadmap
- Generator: implements the next agreed scope of work
- Evaluator: checks alignment, tests behavior, and blocks incomplete work

Optional roles:

- Researcher: gathers domain or API context
- Reviewer: focuses on code quality and maintainability
- Release agent: packages, documents, and prepares handoff

## 3. Operating Modes

### Continuous Mode

Use when the model can hold coherence across the full run.

- Planner writes a full spec.
- Generator builds against the spec.
- Evaluator reviews at major checkpoints or at the end.
- Generator iterates until thresholds pass.

### Sprint Mode

Use when the project is long-running, risky, or the model benefits from decomposition.

- Planner writes a roadmap with sprint candidates.
- For each sprint, generator and evaluator agree on a contract.
- Generator implements only that sprint scope.
- Evaluator runs QA and either passes or sends back defects.
- A handoff artifact records the latest state.

## 4. File-Based State

Treat files as the durable coordination layer.

Required artifacts:

- `01-product-spec.md`
- `02-roadmap.md`
- `03-sprint-contract.md`
- `04-build-handoff.md`
- `05-qa-report.md`
- `06-run-log.md`

Benefits:

- less ambiguity across context resets
- easier auditability
- better recovery from interrupted runs
- cleaner collaboration between agents

## 5. Decision Gates

The evaluator should gate progress at three levels:

1. Spec gate: is the plan aligned with the brief?
2. Contract gate: is the proposed scope concrete and testable?
3. QA gate: does the implementation meet the thresholds?

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

## 8. Simplification Rule

Every harness component should justify its existence.

After successful runs, ask:

- Can this role be removed?
- Can this loop happen less often?
- Can this check be deferred to the end?
- Can the model now do this reliably without scaffolding?
