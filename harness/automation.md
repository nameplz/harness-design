# Automation Model

This document defines how the harness should operate once a project-specific configuration has been filled in.

## Objective

Automate as much of the project loop as possible while staying inside explicit risk, quality, and cost boundaries.

## Automation Scope

The harness may autonomously:

- expand the brief into a spec
- break work into stages or sprints
- implement approved scope
- run builds, tests, and local QA
- write logs and handoff artifacts
- retry failed work within bounded limits

The harness should not autonomously:

- change product direction without policy support
- deploy to production without explicit approval
- take destructive actions outside approved policy
- silently weaken acceptance criteria to force completion

## Main Loop

1. Read `project.yaml`.
2. Read the policy files listed in `project.yaml.policy_files`.
3. Resolve the canonical artifact paths from `project.yaml.artifacts`.
4. Generate or refresh the product spec and roadmap.
5. Check whether a human approval gate is required.
6. Select the next work unit.
7. Write or update a sprint contract if sprint mode is enabled.
8. Implement the approved work unit.
9. Run self-checks and write a build handoff.
10. Run evaluator QA and score the result.
11. Decide one of:
   - pass and continue
   - fail and retry
   - escalate
   - stop
12. Repeat until completion policy is satisfied or a stop condition fires.

## Decision Engine

After each QA cycle, the harness should evaluate:

- Did all blocking checks pass?
- Were thresholds met?
- Is the failure new or repeated?
- Is the remaining work still within budget and time?
- Is a human decision now required?
- Were any configured blockers triggered by blocker ID?
- Are any required checks still unverified?

## Retry Strategy

Retry automatically when:

- the issue is concrete and actionable
- the root cause is plausibly fixable in one more round
- the retry limit has not been reached

Escalate instead when:

- the same class of issue repeats
- the spec appears internally inconsistent
- the work requires credentials, policy, or external access decisions

## Recommended Approval Pattern

- After spec generation: optional but recommended
- After each major milestone: optional for high-risk projects
- Before release or deployment: required

## Completion Rule

A run is complete only if:

- required thresholds are met
- all core flows pass
- blocking bugs are resolved
- required deliverables exist
- the final handoff is written

When stopping or escalating, the harness must write the configured escalation report before pausing.
