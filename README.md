# AI Agent Playbook

**반복 업무를 AI 에이전트가 재현 가능하게 끝내도록, 역할·검증·산출물·비용을 코드와 문서로 고정해 둔 개인 운영 저장소다.**

좋은 결과를 한 번 받는 것보다, 다음 세션에서도 같은 판단 기준으로 다시 만드는 쪽에 집중했다. 각 폴더는 바로 실행할 수 있는 Skill, 실제 산출물, 실패에서 고친 기준, 자동화 훅을 함께 둔다.

## Workflows

| 폴더 | 무엇을 하는가 | 핵심 도구 |
| --- | --- | --- |
| [경제 뉴스 카드 제작](workflows/economy-news-cards/) | 공식 원문 3개를 검증해 인스타 스토리 카드·출처·ZIP으로 패키징 | GPT Image, 웹 리서치, Codex 자동화 |
| [Claude 에이전트 운영](workflows/claude-agent-operations/) | Fable 기획과 Opus 빌더를 분리해 품질을 유지하며 토큰을 통제 | Claude Opus 5.1, Opus 5.0, Sonnet 5 |

## 설치 가능한 Skills

```bash
git clone https://github.com/mingeonho1/ai-agent-playbook.git
cp -R ai-agent-playbook/skills/weekly-economy-cards ~/.codex/skills/
cp -R ai-agent-playbook/skills/claude-agent-operations ~/.codex/skills/
```

| Skill | 사용할 때 |
| --- | --- |
| [weekly-economy-cards](skills/weekly-economy-cards/SKILL.md) | 경제·주식·금융 뉴스를 검증해 주간 인스타 스토리 3장으로 만들 때 |
| [claude-agent-operations](skills/claude-agent-operations/SKILL.md) | 여러 Claude 에이전트를 역할·토큰 예산·파일 책임으로 운영할 때 |

각 Skill은 `SKILL.md`와 `agents/openai.yaml`을 포함한다. 세션 기억이나 대화 맥락이 없어도 필요한 작업 규칙을 로드하도록 만들었다.

## 운영 원칙

- 모델에게 판단을 위임하되, 숫자·기간·출처는 원문과 다시 대조한다.
- 비싼 추론은 방향을 정하는 한 번의 판단에 쓰고, 반복 작업은 짧은 계약과 파일로 넘긴다.
- 병렬화는 독립 검증에서만 사용하고, 같은 파일의 최종 편집자는 한 명으로 둔다.
- 결과는 이미지 하나가 아니라 입력 데이터, 출처, 생성 기록, ZIP까지 남긴다.

