# Reusable Agent Harness Skeleton

This workspace contains a reusable skeleton for long-running project harnesses inspired by the planner-generator-evaluator pattern.

The goal is to let you start with a generic harness, then customize only the project-specific parts through Codex when you begin a real project.

## Structure

- `harness/project.template.yaml`: the main project configuration template
- `harness/workflow.md`: end-to-end operating model
- `harness/automation.md`: semi-autonomous operating loop
- `harness/policies/`: stop rules, approval gates, and execution policy
- `harness/roles/`: role definitions for each agent
- `harness/templates/`: reusable artifacts passed between agents
- `harness/prompts/`: Codex-facing operating prompts

## Core Ideas

- Separate planning, building, and evaluation responsibilities.
- Use files as the source of truth between agents.
- Prefer explicit acceptance criteria over vague notions of completion.
- Add complexity only when the task actually needs it.
- Revisit the harness as models improve.

## Recommended Usage

1. Copy `harness/project.template.yaml` for a real project.
2. Fill in the project brief, stack, constraints, and evaluation criteria.
3. Update the role prompts to reflect the product domain if needed.
4. Fill in the automation policy, approval gates, and stop conditions.
5. Run the harness in either:
   - `continuous` mode for stronger models and simpler projects
   - `sprint` mode for harder or longer builds
6. Let Codex refine the templates into a project-specific harness.

## Minimal Flow

1. Planner expands the brief into a product spec.
2. Generator proposes a scoped implementation contract.
3. Evaluator approves or revises the contract.
4. Generator implements the scoped work.
5. Evaluator tests the result and writes a QA report.
6. Generator fixes issues or moves to the next scope unit.

## When To Use More Structure

Use sprinted contracts, explicit handoffs, and stricter QA thresholds when:

- the app is large or multi-surface
- correctness matters more than raw speed
- the model drifts during long tasks
- the project has many moving parts or hidden dependencies

Use a simpler continuous flow when:

- the project is small
- the model can stay coherent without decomposition
- QA is still valuable but per-sprint negotiation is unnecessary

## Semi-Autonomous Operation

This skeleton now supports policy-based automation for:

- planning
- implementation loops
- QA loops
- escalation and stop conditions
- approval checkpoints

The intended model is:

- Codex runs autonomously inside a bounded policy
- the harness decides when to continue, retry, escalate, or stop
- a human approves only the high-consequence checkpoints
