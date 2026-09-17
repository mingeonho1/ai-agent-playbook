# AI Agent Playbook

**AI 에이전트를 역할별로 분배하고, 토큰 낭비 없이 반복 가능한 실행 시스템으로 만드는 개인 운영 저장소다.**

한 모델에게 계획·구현·검증을 전부 맡기면 추론은 반복되고 결과 책임도 흐려진다. 이 저장소는 역할, 파일 책임, 병렬 경계, 중단 조건을 Skill로 고정한다.

## Workflow

[Claude 에이전트 운영](workflows/claude-agent-operations/)은 Fable 고급 기획, Opus 빌더, Sonnet 실행 보조를 분리해 운영하는 실제 기준을 담는다.

| 역할 | 모델 | 맡길 일 |
| --- | --- | --- |
| 기획·복잡한 판단 | Claude Opus 5.1 | 설계, 우선순위, 상충하는 근거 판단 |
| 빌더 | Claude Opus 5.0 | 구현, 수정, 테스트, 검수 |
| 실행 보조 | Claude Sonnet 5 | 탐색, 명령 실행, 파일·로그 확인 |

## 설치 가능한 Skill

```bash
git clone https://github.com/mingeonho1/ai-agent-playbook.git
cp -R ai-agent-playbook/skills/claude-agent-operations ~/.codex/skills/
```

[claude-agent-operations](skills/claude-agent-operations/SKILL.md)은 다음을 강제한다.

- 독립적인 조사·검증만 병렬로 돌린다.
- 동일 파일의 최종 편집자는 한 명이다.
- 고급 모델은 결정이 어려운 한 번의 판단에만 쓴다.
- 빌더는 확정된 사실·파일 범위·검증 기준만 받아 실행한다.
- 결과는 짧은 결론, 근거, 불확실성만 반환한다.

