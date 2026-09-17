# 모델·도구 선택

## 실제 제작 경로

| 구간 | 도구 | 이유 |
| --- | --- | --- |
| 원문 탐색 | 웹 검색 + 발표기관 원문 | 최신 수치와 발표일을 직접 확인 |
| 초안·데이터 구조화 | 실행 환경의 Codex 모델 | 기사 문장을 카드 구조로 압축하고 검증 항목을 누락하지 않기 위해 사용 |
| 카드 비주얼 생성 | 기본 내장 GPT Image | 레퍼런스의 정보 위계와 시각적 완성도를 카드 이미지에 반영 |
| 정확 수치 보조 | HTML/CSS/JavaScript + Chrome Headless | 숫자·날짜·차트를 고정된 위치와 크기로 덧씌워야 할 때 사용 |
| 시각 검수 | 생성 PNG 직접 확인 | 코드 검사가 잡지 못하는 읽기 흐름과 여백을 확인 |

정확한 언어 모델 ID는 실행 환경이 노출할 때만 남긴다. 이 저장소는 특정 모델명을 부풀려 적지 않는다. 모델보다 중요한 것은 카드가 통과해야 할 데이터·검증·렌더링 계약이다.

## 이미지 모델은 언제 쓰는가

카드 비주얼의 기본 제작 경로는 기본 내장 GPT Image다. 두 개의 인포그래픽 레퍼런스에서 정보 위계와 색의 역할을 추출해 프롬프트에 반영했다. 한 글자도 틀리면 안 되는 숫자·날짜·축은 검증된 문구로 재생성하거나 HTML/CSS 렌더러를 보조로 쓴다. OpenAI 공식 모델 문서는 GPT Image 2.5 Sunburst를 이미지 생성·편집에 가장 높은 성능이 필요한 작업용으로, GPT Image 2.5 Flare를 빠른 고품질 생성용으로 소개한다. API의 이미지 생성 레퍼런스는 모델·크기·품질 값을 명시해 요청하도록 설명한다.

- [GPT Image 2.5 Sunburst 공식 문서](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)
- [GPT Image 2.5 Flare 공식 문서](https://developers.openai.com/api/docs/models/gpt-image-2.5-flare)
- [Images API: Create image](https://developers.openai.com/api/reference/cli/resources/images/methods/generate)

기본 내장 GPT Image 경로는 실행 로그에 모델 ID를 노출하지 않을 수 있다. 그래서 이 저장소는 확인되지 않은 특정 GPT Image 모델명을 결과물의 사용 모델이라고 주장하지 않는다.

## 공식 문서를 어떻게 적용했는가

- 이미지 문서의 모델 선택과 생성 파라미터 개념은 GPT Image 카드 비주얼 생성의 선택 기준으로 반영했다.
- [Codex Scheduled tasks 문서](https://learn.chatgpt.com/docs/automations?surface=app)의 반복 실행·알림 개념은 주간 훅의 실행 계약으로 반영했다.
- 최종 카드 비주얼은 GPT Image로 만들고, 정확도가 필요한 텍스트와 차트는 검증과 템플릿 렌더링으로 보조한다.
