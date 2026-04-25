# Project Bootstrap Prompt

Use this prompt when converting the reusable harness into a project-specific harness.

## Task

Read the generic harness templates and transform them into a project-specific harness using the provided project information.

## Required Work

- Fill in `project.yaml` from the project brief.
- Keep `project.yaml` valid against `harness/schema/project.v1.md`.
- Adapt the quality bar to the project.
- Adapt approval gates and stop conditions to the project's risk profile.
- Add project-specific QA checks.
- Update role prompts with domain-specific guidance if needed.
- Keep the structure reusable and explicit.

## Output Standard

The resulting harness should be detailed enough that the selected CLI adapter can run planning, implementation, and evaluation loops with minimal human intervention.

## Important Constraints

- Preserve bounded autonomy.
- Require human approval for high-consequence actions.
- Prefer explicit criteria over subjective completion language.
- Keep files readable and editable by humans.
- Do not introduce implicit paths or policy discovery; record them explicitly in `project.yaml`.
- Set `runtime.platform` and `runtime.adapter_path` explicitly when targeting a specific CLI.
- Record only paths that exist at execution time. In this skeleton, the default policy files are the checked-in `harness/policies/*.template.yaml` files.
- If you copy those policy templates to project-specific file names, update `project.yaml.policy_files` to the new paths in the same change.
- Do not rely on the operator or runtime to infer alternate file names such as stripping `.template`.
- Prefer adapter-local prompts and capability declarations over embedding CLI-specific instructions into the shared core files.
