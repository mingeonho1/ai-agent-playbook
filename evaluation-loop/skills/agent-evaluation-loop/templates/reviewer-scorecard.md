# Reviewer scorecard

리뷰어에게 이전 점수나 반복 기록을 보여주지 않은 새 독립 context에서 아래 구조를 채우게 한다. 근거가 없으면 점수를 추정하지 않고 `null`을 쓴다.

```json
{
  "dimensions": {
    "intent": {"score": null, "evidence": []},
    "correctness": {"score": null, "evidence": []},
    "verification": {"score": null, "evidence": []},
    "clarity": {"score": null, "evidence": []},
    "efficiency": {"score": null, "evidence": []}
  },
  "mandatory_criteria": [
    {"id": "criterion-id", "passed": null, "evidence": []}
  ],
  "findings": [
    {"id": "finding-id", "status": "needs_evidence", "severity": "medium", "confidence": 0.5, "reproducible": false, "resolved": false, "evidence": ["추가 확인이 필요한 관찰"]}
  ]
}
```
