# 재사용 가능한 멀티-CLI 에이전트 하네스 스켈레톤

영문 버전: [`README.md`](./README.md)

이 저장소는 planner-generator-evaluator 패턴을 기반으로 한 장기 실행형 프로젝트 하네스를 위한 재사용 가능한 스켈레톤입니다.

현재 기준선은 준실행형(quasi-executable) v1 스펙입니다. 오퍼레이터나 에이전트는 `project.yaml`을 읽고, 명시적으로 선언된 정책 파일과 산출물 경로를 로드한 뒤, 추측 없이 하네스를 실행할 수 있어야 합니다.

## 무엇을 위한 저장소인가

이 프로젝트는 다른 저장소로 복사해 프로젝트별로 특화할 수 있는 재사용 가능한 하네스가 필요할 때 사용합니다.
핵심 계약은 벤더 중립적이며, 기본 프로젝트 산출물을 바꾸지 않고도 Codex, Claude Code, Gemini CLI 같은 에이전트형 CLI에 맞게 적용할 수 있습니다.

이 하네스는 다음 결정을 명시적으로 드러내도록 설계되었습니다.

- 프로젝트가 무엇을 전달하려는지
- 어떤 품질 기준을 만족해야 하는지
- 어떤 승인 게이트가 활성화되어 있는지
- 어떤 파일이 정식 산출물인지
- 오퍼레이터가 언제 계속, 재시도, 에스컬레이션, 중단해야 하는지
- evaluator가 QA를 어떻게 수행하고 점수를 어떻게 보정해야 하는지

## v1 계약

v1 계약의 중심은 [`harness/schema/project.v1.md`](./harness/schema/project.v1.md)입니다.

v1에서는 다음을 전제로 합니다.

- `project.yaml`은 유일한 기계 판독 진입점입니다
- `project.yaml.runtime`은 코어 계약을 바꾸지 않고도 활성 CLI adapter를 선언할 수 있습니다
- 정책 파일은 `project.yaml.policy_files`에서 해석됩니다
- 정식 산출물 경로는 `project.yaml.artifacts`에서 해석됩니다
- 승인 게이트는 안정적인 `gate_id` 값을 사용합니다
- blocker는 안정적인 `blocker_id` 값을 사용합니다
- 프로젝트별 QA 체크는 안정적인 `check_id` 값을 사용합니다
- 완료 여부는 서술형 문장이 아니라 명시적 completion-policy 필드로 결정합니다
- evaluator QA는 명시적인 실행 프로토콜과 calibration policy를 따릅니다

이 입력들이 서로 어긋나면, 오퍼레이터는 의도를 추론하지 말고 중단한 뒤 escalation report를 작성해야 합니다.

## 구조

- `harness/project.template.yaml`: 실제 프로젝트용 `project.yaml` 시작 템플릿
- `harness/schema/project.v1.md`: 정식 스키마와 교차 파일 계약
- `harness/workflow.md`: end-to-end 운영 모델
- `harness/automation.md`: 범위가 제한된 자동화 루프
- `harness/policies/`: 실행, QA, 승인 게이트, 중단 조건 정책 템플릿
- `harness/roles/`: planner, generator, evaluator 역할 정의
- `harness/templates/`: 실행 중 작성되는 정식 산출물 템플릿
- `harness/prompts/`: 공용 bootstrap 및 호환성 프롬프트
- `harness/adapters/`: CLI별 operator prompt, capability 선언, bootstrap notes

이 스켈레톤 저장소에서는 기본 정책 파일로 `harness/policies/` 아래의 체크인된 `*.template.yaml` 파일을 사용합니다.
이 기본값은 fresh clone 상태에서도 다른 파일명을 추론하지 않고 읽을 수 있도록 의도적으로 명시돼 있습니다.

이 저장소에서 지원하는 adapter 대상:

- Codex
- Claude Code
- Gemini CLI

## 플랫폼 가이드

모든 CLI에서 같은 코어 하네스 파일을 사용하고, 동작 차이는 `project.yaml.runtime`으로 전환합니다.

### Codex

현재 저장소 기본값과 가장 잘 맞는 사용 방식입니다.

- `runtime.platform`을 `codex`로 설정
- `runtime.adapter_path`를 `harness/adapters/codex`로 설정
- native multi-agent 실행, 명시적 승인 처리, structured editing workflow가 필요할 때 권장
- 프로젝트에 Codex 전용 override가 꼭 필요하지 않다면 planner, generator, evaluator 프롬프트는 `harness/roles/`의 공용 정의를 유지

### Claude Code

Claude Code를 최상위 오퍼레이터로 사용하되, artifact 중심 워크플로를 그대로 유지하고 싶을 때 권장합니다.

- `runtime.platform`을 `claude-code`로 설정
- `runtime.adapter_path`를 `harness/adapters/claude-code`로 설정
- delegated execution을 사용하면서도 승인, QA 게이트, handoff artifact를 명시적으로 유지하고 싶을 때 권장
- Claude Code 전용 orchestration 지침은 공용 코어 프롬프트에 복사하지 말고 adapter 파일에 유지

### Gemini CLI

더 단순한 런타임에서도 동일한 하네스 계약을 유지하고 싶을 때 권장합니다.

- `runtime.platform`을 `gemini-cli`로 설정
- `runtime.adapter_path`를 `harness/adapters/gemini-cli`로 설정
- subagent, browser automation, structured patch 도구가 제한적이어도 planner-generator-evaluator 워크플로 자체는 유지하고 싶을 때 권장
- 기본값은 순차 역할 실행으로 보고, artifact, 승인, QA 기대 수준은 동일하게 유지

세 플랫폼 모두에서 `project.yaml`, 정책 파일, 산출물 경로가 source of truth입니다. adapter는 실행 방법을 바꾸는 것이지, 실행 결과물 자체를 바꾸는 것이 아닙니다.

## 정식 파일

`project.yaml`은 다음 파일 그룹을 명시적으로 선언해야 합니다.

- 정책 파일:
  - execution policy
  - QA policy
  - approval-gates policy
  - stop-conditions policy
- 산출물:
  - `01-product-spec.md`
  - `02-roadmap.md`
  - `03-sprint-contract.md`
  - `04-build-handoff.md`
  - `05-qa-report.md`
  - `06-run-log.md`
  - `07-escalation-report.md`
  - `08-final-handoff.md`

기본값은 [`harness/project.template.yaml`](./harness/project.template.yaml)에 들어 있지만, 실제 프로젝트는 명시적으로만 기록한다면 다른 경로를 사용해도 됩니다.

## 빠른 시작

1. [`harness/project.template.yaml`](./harness/project.template.yaml)을 대상 프로젝트의 `project.yaml`로 복사합니다.
2. 기본 `policy_files` 값은 이 스켈레톤에서 바로 사용할 수 있는 유효한 시작 경로로 취급합니다. 이 값들은 실제로 존재하는 `harness/policies/*.template.yaml` 파일을 가리킵니다.
3. 활성 CLI 대상에 맞게 `runtime.platform`과 `runtime.adapter_path`를 설정합니다.
4. [`harness/schema/project.v1.md`](./harness/schema/project.v1.md)의 규칙에 따라 `project.yaml`을 채웁니다.
5. 프로젝트를 `continuous`로 돌릴지 `sprint`로 돌릴지 결정합니다.
6. 이번 실행의 정식 출력 파일이 되도록 `artifacts`를 지정합니다.
7. 품질 임계값, blocker ID, 필수 게이트, 프로젝트별 체크를 채웁니다.
8. 프로젝트 전용 정책 파일명을 쓰고 싶다면, 템플릿 정책 파일을 새 경로로 복사하고 `project.yaml.policy_files`도 정확히 그 경로로 갱신합니다.
9. adapter 기본값이 부족한 경우에만 프롬프트나 capability를 override합니다.

두 경우 모두 런타임 계약은 같습니다. 오퍼레이터는 `project.yaml`에 적힌 경로만 읽어야 하며, non-template 파일명 같은 fallback 이름을 추측하면 안 됩니다.

## Runtime CLI

이 저장소에는 YAML을 수동 편집하지 않고 `runtime` 블록을 설정할 수 있는 작은 helper CLI가 포함되어 있습니다.

로컬 래퍼를 이렇게 사용합니다.

```bash
./bin/harness runtime set <platform>
```

예시:

```bash
./bin/harness runtime set codex
./bin/harness runtime set claude-code --project ./project.yaml
./bin/harness runtime set gemini-cli --set-capability browser_automation=false
./bin/harness runtime set codex --check
./bin/harness runtime set codex --print
```

참고:

- 이 저장소는 이미 `harness/`를 디렉터리 이름으로 쓰고 있으므로 실행 파일은 `./bin/harness`입니다.
- `project.yaml`이 없으면 `harness/project.template.yaml`에서 생성할 수 있습니다.
- 이 명령은 `runtime`만 갱신하며, `policy_files`, `artifacts`, 그 밖의 프로젝트 설정은 다시 쓰지 않습니다.
- adapter 기본값은 `harness/adapters/*/capabilities.yaml`에서 읽습니다.
- 상대 runtime 경로는 `project.yaml`이 있는 디렉터리를 기준으로 해석되므로, 일반적으로 해당 파일 옆에 `harness/` 디렉터리가 함께 있어야 합니다.

## 최소 런타임 흐름

1. `project.yaml`을 읽습니다.
2. `project.yaml.runtime`에서 활성 adapter를 해석합니다.
3. `project.yaml.policy_files`에 선언된 정책 파일을 로드합니다.
4. `project.yaml.artifacts`에서 산출물 경로를 해석합니다.
5. `project.mode`에 따라 계획, 계약, 구현, 평가를 수행합니다.
6. 설정된 정책에 따라 pass, retry, escalate, stop 중 하나를 결정합니다.
7. 실행이 요구할 때 escalation 또는 final handoff 산출물을 작성합니다.

## 산출물 기대사항

이 하네스는 특정 산출물에 단순 서술이 아니라 기계적으로 사용할 수 있는 구조가 담기길 기대합니다.

- `05-qa-report.md`는 점수, 임계값 결과, blocker 결과, 미검증 체크, 실행 커버리지, 발견 사항, 다음 액션을 기록해야 합니다.
- `07-escalation-report.md`는 trigger ID, phase, blocker 요약, 선택지, 요청할 인간 의사결정을 기록해야 합니다.
- `08-final-handoff.md`는 outcome, completion-policy 결과, 전달된 산출물, 보류된 작업, 운영 메모를 기록해야 합니다.

## 언제 더 많은 구조가 필요한가

다음 상황에서는 `sprint` 모드를 선호합니다.

- 프로젝트가 장기 실행형일 때
- 작업이 위험하거나 여러 표면을 동시에 다룰 때
- 모델이 긴 세션에서 드리프트하기 쉬울 때
- 구현과 QA 사이에서 명시적 범위 협상이 필요할 때

다음 상황에서는 `continuous` 모드를 선호합니다.

- 프로젝트가 작을 때
- 작업이 강하게 결합돼 있을 때
- 모델이 끝까지 일관성을 유지할 수 있을 때
- 스프린트별 계약 오버헤드가 이득보다 클 때

## 설계 원칙

- 계획, 구현, 평가 책임을 분리합니다.
- 파일을 지속 가능한 조정 계층으로 사용합니다.
- 코어 계약은 특정 CLI 하나에 종속되지 않게 유지합니다.
- 모호한 완료 표현보다 명시적인 acceptance criteria를 선호합니다.
- bounded autonomy를 유지합니다.
- 신뢰성을 실제로 높일 때만 구조를 추가합니다.
- evaluator의 판단이 반복 가능하도록 명시적 QA 프로토콜과 calibration rules를 둡니다.

## 현재 상태

이 저장소는 완전한 자동 실행기가 아니라, 재사용 가능한 하네스 스켈레톤의 계약을 정의합니다. 스크립트나 에이전트가 이를 읽는 준실행형 스펙이며, 이후 프로젝트별로 특화해서 사용하는 것을 전제로 합니다.
