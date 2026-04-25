#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import sys
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECT_TEMPLATE_PATH = REPO_ROOT / "harness" / "project.template.yaml"
VALID_PLATFORMS = {"codex", "claude-code", "gemini-cli"}
VALID_EXECUTION_MODES = {"native-multi-agent", "single-agent-sequenced"}
VALID_CAPABILITIES = {
    "subagents",
    "interactive_approval",
    "browser_automation",
    "structured_patch",
    "web_access",
}
VALID_PROMPT_ROLES = {"operator", "planner", "generator", "evaluator"}


class HarnessCliError(Exception):
    pass


@dataclass(frozen=True)
class AdapterDefaults:
    platform: str
    adapter_path: str
    execution_mode: str
    capabilities: dict[str, bool]
    prompt_files: dict[str, str]
    bootstrap_notes: str


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if getattr(args, "command", None) != "runtime" or getattr(args, "runtime_command", None) != "set":
            parser.print_help()
            return 1

        return run_runtime_set(args)
    except HarnessCliError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="harness")
    subparsers = parser.add_subparsers(dest="command")

    runtime_parser = subparsers.add_parser("runtime", help="Manage runtime settings")
    runtime_subparsers = runtime_parser.add_subparsers(dest="runtime_command")

    set_parser = runtime_subparsers.add_parser("set", help="Set the active runtime adapter")
    set_parser.add_argument("platform", choices=sorted(VALID_PLATFORMS))
    set_parser.add_argument("--project", default="project.yaml", help="Path to project.yaml")
    set_parser.add_argument("--adapter-path", help="Explicit adapter directory override")
    set_parser.add_argument(
        "--execution-mode",
        choices=sorted(VALID_EXECUTION_MODES),
        help="Override execution mode instead of using the adapter default",
    )
    set_parser.add_argument(
        "--set-capability",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Override a runtime capability. May be repeated.",
    )
    set_parser.add_argument(
        "--prompt-override",
        action="append",
        default=[],
        metavar="ROLE=PATH",
        help="Override a prompt path. May be repeated.",
    )
    set_parser.add_argument("--print", dest="print_only", action="store_true", help="Print the resulting runtime block")
    set_parser.add_argument("--check", action="store_true", help="Validate the current runtime block without modifying files")
    set_parser.add_argument("--yes", action="store_true", help="Auto-create project.yaml from the template when missing")

    return parser


def run_runtime_set(args: argparse.Namespace) -> int:
    project_path = Path(args.project).resolve()
    project_dir = project_path.parent

    if args.check and args.print_only:
        raise HarnessCliError("--check and --print cannot be used together")

    project_path, created = ensure_project_file(project_path, args.yes)
    project_text = project_path.read_text(encoding="utf-8")
    validate_schema_version(project_text, project_path)

    current_runtime = parse_runtime_block(project_text)
    adapter_path_string = args.adapter_path or f"harness/adapters/{args.platform}"
    adapter_defaults = load_adapter_defaults(
        project_dir=project_dir,
        requested_platform=args.platform,
        adapter_path_string=adapter_path_string,
    )
    capability_overrides = parse_capability_overrides(args.set_capability)
    prompt_overrides = parse_prompt_overrides(args.prompt_override, project_dir)

    next_runtime = merge_runtime(
        current_runtime=current_runtime,
        adapter_defaults=adapter_defaults,
        execution_mode_override=args.execution_mode,
        capability_overrides=capability_overrides,
        prompt_overrides=prompt_overrides,
    )
    validate_runtime(next_runtime, project_dir)

    runtime_block = render_runtime_block(next_runtime)

    if args.check:
        if normalize_mapping(current_runtime) == normalize_mapping(next_runtime):
            print(f"runtime already matches {args.platform}")
            return 0
        print(f"runtime does not match {args.platform}", file=sys.stderr)
        print(runtime_block, file=sys.stderr)
        return 1

    if args.print_only:
        print(runtime_block)
        return 0

    updated_text = upsert_runtime_block(project_text, runtime_block)
    project_path.write_text(updated_text, encoding="utf-8")

    action = "created and updated" if created else "updated"
    print(f"{action} {project_path}")
    print(runtime_block)
    return 0


def ensure_project_file(project_path: Path, assume_yes: bool) -> tuple[Path, bool]:
    if project_path.exists():
        return project_path, False

    if not PROJECT_TEMPLATE_PATH.exists():
        raise HarnessCliError(f"project template not found: {PROJECT_TEMPLATE_PATH}")

    if not assume_yes:
        if not sys.stdin.isatty():
            raise HarnessCliError(
                f"{project_path} does not exist; rerun with --yes to create it from the template"
            )

        prompt = f"{project_path} does not exist. Create it from {PROJECT_TEMPLATE_PATH}? [y/N] "
        answer = input(prompt).strip().lower()
        if answer not in {"y", "yes"}:
            raise HarnessCliError("aborted without creating project.yaml")

    project_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PROJECT_TEMPLATE_PATH, project_path)
    return project_path, True


def validate_schema_version(project_text: str, project_path: Path) -> None:
    for line in project_text.splitlines():
        if line.startswith("schema_version:"):
            if '"harness.project/v1"' in line or "'harness.project/v1'" in line:
                return
            if line.split(":", 1)[1].strip() == "harness.project/v1":
                return
            raise HarnessCliError(f"{project_path} must use schema_version harness.project/v1")

    raise HarnessCliError(f"{project_path} is missing schema_version")


def load_adapter_defaults(
    project_dir: Path,
    requested_platform: str,
    adapter_path_string: str,
) -> AdapterDefaults:
    adapter_dir = resolve_existing_path(project_dir, adapter_path_string, "adapter directory")
    capabilities_path = adapter_dir / "capabilities.yaml"

    if not capabilities_path.exists():
        raise HarnessCliError(f"adapter capabilities not found: {capabilities_path}")

    payload = parse_simple_yaml(capabilities_path.read_text(encoding="utf-8"))
    platform = expect_string(payload.get("platform"), f"{capabilities_path}: platform")
    if platform != requested_platform:
        raise HarnessCliError(
            f"adapter platform mismatch: expected {requested_platform}, found {platform} in {capabilities_path}"
        )

    execution_mode = expect_string(payload.get("execution_mode"), f"{capabilities_path}: execution_mode")
    if execution_mode not in VALID_EXECUTION_MODES:
        raise HarnessCliError(f"invalid execution_mode in {capabilities_path}: {execution_mode}")

    capabilities = expect_bool_mapping(payload.get("capabilities"), f"{capabilities_path}: capabilities")
    unknown_capabilities = set(capabilities) - VALID_CAPABILITIES
    if unknown_capabilities:
        names = ", ".join(sorted(unknown_capabilities))
        raise HarnessCliError(f"unknown capabilities in {capabilities_path}: {names}")

    prompt_files = expect_string_mapping(payload.get("prompt_files"), f"{capabilities_path}: prompt_files")
    if "operator" not in prompt_files:
        raise HarnessCliError(f"{capabilities_path} must declare prompt_files.operator")

    bootstrap_notes = expect_string(payload.get("bootstrap_notes"), f"{capabilities_path}: bootstrap_notes")

    required_files = [adapter_dir / prompt_files["operator"], adapter_dir / bootstrap_notes]
    for required_path in required_files:
        if not required_path.exists():
            raise HarnessCliError(f"adapter file not found: {required_path}")

    return AdapterDefaults(
        platform=platform,
        adapter_path=adapter_path_string,
        execution_mode=execution_mode,
        capabilities=capabilities,
        prompt_files=prompt_files,
        bootstrap_notes=bootstrap_notes,
    )


def parse_capability_overrides(pairs: list[str]) -> dict[str, bool]:
    overrides: dict[str, bool] = {}
    for pair in pairs:
        key, raw_value = split_kv(pair, "--set-capability")
        if key not in VALID_CAPABILITIES:
            names = ", ".join(sorted(VALID_CAPABILITIES))
            raise HarnessCliError(f"invalid capability {key!r}; expected one of: {names}")
        overrides[key] = parse_bool(raw_value, f"capability {key}")
    return overrides


def parse_prompt_overrides(pairs: list[str], project_dir: Path) -> dict[str, str]:
    overrides: dict[str, str] = {}
    for pair in pairs:
        role, raw_path = split_kv(pair, "--prompt-override")
        if role not in VALID_PROMPT_ROLES:
            names = ", ".join(sorted(VALID_PROMPT_ROLES))
            raise HarnessCliError(f"invalid prompt role {role!r}; expected one of: {names}")
        resolve_existing_path(project_dir, raw_path, f"prompt override {role}")
        overrides[role] = raw_path
    return overrides


def merge_runtime(
    current_runtime: dict[str, Any],
    adapter_defaults: AdapterDefaults,
    execution_mode_override: str | None,
    capability_overrides: dict[str, bool],
    prompt_overrides: dict[str, str],
) -> OrderedDict[str, Any]:
    next_runtime: OrderedDict[str, Any] = OrderedDict()
    next_runtime["platform"] = adapter_defaults.platform
    next_runtime["adapter_path"] = adapter_defaults.adapter_path
    next_runtime["execution_mode"] = execution_mode_override or adapter_defaults.execution_mode

    existing_capabilities = current_runtime.get("capabilities")
    if existing_capabilities is not None and not isinstance(existing_capabilities, dict):
        raise HarnessCliError("runtime.capabilities must be a mapping")
    merged_capabilities = OrderedDict()
    for key, value in (existing_capabilities or {}).items():
        merged_capabilities[key] = value
    for key, value in capability_overrides.items():
        merged_capabilities[key] = value
    if merged_capabilities:
        next_runtime["capabilities"] = merged_capabilities

    existing_prompts = current_runtime.get("prompt_overrides")
    if existing_prompts is not None and not isinstance(existing_prompts, dict):
        raise HarnessCliError("runtime.prompt_overrides must be a mapping")
    merged_prompts = OrderedDict()
    for key, value in (existing_prompts or {}).items():
        merged_prompts[key] = value
    for key, value in prompt_overrides.items():
        merged_prompts[key] = value
    if merged_prompts:
        next_runtime["prompt_overrides"] = merged_prompts

    return next_runtime


def validate_runtime(runtime: dict[str, Any], project_dir: Path) -> None:
    platform = expect_string(runtime.get("platform"), "runtime.platform")
    adapter_path = expect_string(runtime.get("adapter_path"), "runtime.adapter_path")
    execution_mode = expect_string(runtime.get("execution_mode"), "runtime.execution_mode")

    if platform not in VALID_PLATFORMS:
        names = ", ".join(sorted(VALID_PLATFORMS))
        raise HarnessCliError(f"invalid runtime.platform {platform!r}; expected one of: {names}")
    if execution_mode not in VALID_EXECUTION_MODES:
        names = ", ".join(sorted(VALID_EXECUTION_MODES))
        raise HarnessCliError(f"invalid runtime.execution_mode {execution_mode!r}; expected one of: {names}")

    resolve_existing_path(project_dir, adapter_path, "runtime.adapter_path")

    capabilities = runtime.get("capabilities")
    if capabilities is not None:
        for key, value in expect_bool_mapping(capabilities, "runtime.capabilities").items():
            if key not in VALID_CAPABILITIES:
                names = ", ".join(sorted(VALID_CAPABILITIES))
                raise HarnessCliError(f"invalid runtime capability {key!r}; expected one of: {names}")
            if not isinstance(value, bool):
                raise HarnessCliError(f"runtime.capabilities.{key} must be a boolean")

    prompt_overrides = runtime.get("prompt_overrides")
    if prompt_overrides is not None:
        for role, raw_path in expect_string_mapping(prompt_overrides, "runtime.prompt_overrides").items():
            if role not in VALID_PROMPT_ROLES:
                names = ", ".join(sorted(VALID_PROMPT_ROLES))
                raise HarnessCliError(f"invalid runtime prompt override {role!r}; expected one of: {names}")
            resolve_existing_path(project_dir, raw_path, f"runtime.prompt_overrides.{role}")


def parse_runtime_block(project_text: str) -> dict[str, Any]:
    lines = project_text.splitlines()
    block_range = find_top_level_block(lines, "runtime")
    if block_range is None:
        return {}
    start, end = block_range
    block_text = "\n".join(lines[start:end])
    parsed = parse_simple_yaml(block_text)
    runtime = parsed.get("runtime")
    if runtime is None:
        return {}
    if not isinstance(runtime, dict):
        raise HarnessCliError("runtime block must be a mapping")
    return runtime


def upsert_runtime_block(project_text: str, runtime_block: str) -> str:
    lines = project_text.splitlines()
    block_range = find_top_level_block(lines, "runtime")

    runtime_lines = runtime_block.splitlines()
    if block_range is not None:
        start, end = block_range
        updated_lines = lines[:start] + runtime_lines + lines[end:]
    else:
        project_range = find_top_level_block(lines, "project")
        if project_range is None:
            raise HarnessCliError("project.yaml is missing the project block; cannot insert runtime")
        insert_at = project_range[1]
        updated_lines = lines[:insert_at] + [""] + runtime_lines + [""] + lines[insert_at:]

    return "\n".join(updated_lines).rstrip() + "\n"


def render_runtime_block(runtime: dict[str, Any]) -> str:
    lines = ["runtime:"]
    lines.append(f'  platform: "{runtime["platform"]}"')
    lines.append(f'  adapter_path: "{runtime["adapter_path"]}"')
    lines.append(f'  execution_mode: "{runtime["execution_mode"]}"')

    capabilities = runtime.get("capabilities")
    if capabilities:
        lines.append("  capabilities:")
        for key in capability_order(capabilities):
            lines.append(f"    {key}: {render_bool(capabilities[key])}")

    prompt_overrides = runtime.get("prompt_overrides")
    if prompt_overrides:
        lines.append("  prompt_overrides:")
        for role in prompt_override_order(prompt_overrides):
            lines.append(f'    {role}: "{prompt_overrides[role]}"')

    return "\n".join(lines)


def capability_order(mapping: dict[str, Any]) -> list[str]:
    preferred = ["subagents", "interactive_approval", "browser_automation", "structured_patch", "web_access"]
    seen = [key for key in preferred if key in mapping]
    extras = sorted(key for key in mapping if key not in preferred)
    return seen + extras


def prompt_override_order(mapping: dict[str, Any]) -> list[str]:
    preferred = ["operator", "planner", "generator", "evaluator"]
    seen = [key for key in preferred if key in mapping]
    extras = sorted(key for key in mapping if key not in preferred)
    return seen + extras


def find_top_level_block(lines: list[str], key: str) -> tuple[int, int] | None:
    start = None
    for index, line in enumerate(lines):
        if line.startswith(f"{key}:"):
            start = index
            break
    if start is None:
        return None

    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if not line.strip():
            continue
        if line.startswith("#"):
            continue
        if not line.startswith((" ", "\t")):
            end = index
            break
    return start, end


def parse_simple_yaml(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, result)]

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()
        if ":" not in stripped:
            raise HarnessCliError(f"unsupported YAML line: {raw_line}")
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()

        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if not value:
            new_mapping: dict[str, Any] = {}
            parent[key] = new_mapping
            stack.append((indent, new_mapping))
            continue

        parent[key] = parse_scalar(value)

    return result


def parse_scalar(value: str) -> Any:
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value


def parse_bool(value: str, label: str) -> bool:
    if value == "true":
        return True
    if value == "false":
        return False
    raise HarnessCliError(f"{label} must be true or false")


def render_bool(value: bool) -> str:
    return "true" if value else "false"


def split_kv(pair: str, flag_name: str) -> tuple[str, str]:
    if "=" not in pair:
        raise HarnessCliError(f"{flag_name} expects KEY=VALUE")
    key, value = pair.split("=", 1)
    key = key.strip()
    value = value.strip()
    if not key or not value:
        raise HarnessCliError(f"{flag_name} expects KEY=VALUE")
    return key, value


def resolve_existing_path(project_dir: Path, raw_path: str, label: str) -> Path:
    candidate = Path(raw_path)
    resolved = candidate if candidate.is_absolute() else project_dir / candidate
    if not resolved.exists():
        raise HarnessCliError(f"{label} not found: {resolved}")
    return resolved.resolve()


def expect_string(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise HarnessCliError(f"{label} must be a string")
    return value


def expect_bool_mapping(value: Any, label: str) -> dict[str, bool]:
    if not isinstance(value, dict):
        raise HarnessCliError(f"{label} must be a mapping")
    converted: dict[str, bool] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise HarnessCliError(f"{label} contains a non-string key")
        if not isinstance(item, bool):
            raise HarnessCliError(f"{label}.{key} must be a boolean")
        converted[key] = item
    return converted


def expect_string_mapping(value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise HarnessCliError(f"{label} must be a mapping")
    converted: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise HarnessCliError(f"{label} contains a non-string key")
        if not isinstance(item, str):
            raise HarnessCliError(f"{label}.{key} must be a string")
        converted[key] = item
    return converted


def normalize_mapping(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalize_mapping(value[key]) for key in sorted(value)}
    return value
