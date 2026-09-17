# 카드 템플릿

`data.js`의 `theme`, `weekLabel`, `period`, `slides`만 이번 주 사실로 바꾼다. `slides`는 정확히 3개이며, 각 항목은 `headline`, `source`, `visual`, `note`를 가진다.

```bash
chmod +x render.sh
./render.sh
```

결과는 `output/weekly-economy-01.png`부터 `03.png`까지다. 렌더러는 Chrome Headless를 사용하며 텍스트 넘침과 1080×1920 크기를 실패 조건으로 처리한다.

완료한 파일은 `runs/YYYY-MM-DD/`로 복사하고 `sources.md`, `provenance.md`와 함께 ZIP으로 묶는다.

