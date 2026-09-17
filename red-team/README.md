# Red-team bundle

기획의 전제와 코드의 실패 조건을 반대 입장에서 확인하는 읽기 전용 Skill이다. Petri·Bloom의 역할 분리와 반례 설계 방식을 참고해, 기존 운영 에이전트와 따로 등록할 수 있게 만들었다.

Claude는 Fable 5.1 xhigh, Codex는 Astra xhigh를 사용한다. 상·중·하는 발견한 문제의 영향 등급이며 모델의 추론 설정은 바꾸지 않는다.

## 설치

저장소 루트에서 실행한다.

```bash
python3 scripts/install.py claude --user --package red-team
python3 scripts/install.py codex --user --package red-team
```

특정 프로젝트에 설치하려면 `--user` 대신 `--project PATH`를 쓴다.

```bash
python3 scripts/install.py claude --project PATH --package red-team
python3 scripts/install.py codex --project PATH --package red-team
```

Claude에서는 `/adversarial-review`, Codex에서는 `$adversarial-review`로 호출한다. 메인 에이전트는 설치된 `ai-red-team`(Codex 설정 이름 `ai_red_team`)을 상속 없는 새 읽기 전용 인스턴스로 한 번 호출하고, 필요한 실행·웹 조사 증거는 직접 또는 별도 runner로 확보한다. 새 인스턴스임을 확인할 수 없으면 독립 검토는 미완료로 보고한다.

이 번들은 로컬 자료를 읽어 반례와 누락 증거를 찾는다. 외부 시스템을 공격하거나 스캔하지 않고, 파일을 바꾸지 않는다.
