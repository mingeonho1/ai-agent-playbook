window.WEEKLY_ECONOMY = {
  theme: "teal-orange",
  weekLabel: "SEP · WEEK 3",
  period: "2026.09.09 — 09.13",
  slides: [
    {
      type: "gdp",
      kicker: "01 / 청년 고용",
      headline: "청년 고용률은<br><span class=\"marker\">1년 전보다 하락</span>",
      source: "자료  국가데이터처 · 2026.09.09",
      visual: {
        change: "−1.0%p",
        context: "8월 청년 고용률 · 15~29세",
        direction: "전년 대비",
        first: { label: "2025년 8월", value: "45.1%" },
        second: { label: "2026년 8월", value: "44.1%" },
        caption: "청년 인구 중 취업자의 비율",
      },
      note: {
        heading: "그래서 우리한텐?",
        body: "전체 고용 증가와 청년 채용은 달라요.<br>지원할 업종의 채용 흐름을 따로 봐요.",
      },
    },
    {
      type: "inflation",
      kicker: "02 / 미국 물가",
      headline: "미국 물가 상승 속도<br><span class=\"marker\">한 달 새 빨라졌어요</span>",
      source: "자료  미국 BLS · 2026.09.11",
      visual: {
        context: "미국 CPI · 전월 대비 · 계절조정",
        axisMax: 0.8,
        first: { label: "7월", value: 0.1 },
        second: { label: "8월", value: 0.4 },
        delta: "+0.3%p",
      },
      note: {
        heading: "그래서 우리한텐?",
        body: "고금리가 길어지면 미국 주식에 부담이에요.<br>금리 경로는 다음 발표도 함께 봐야 해요.",
      },
    },
    {
      type: "gdp",
      kicker: "03 / 유럽 금리",
      headline: "유럽, 물가 잡으려<br><span class=\"marker\">금리 인상 결정</span>",
      source: "자료  ECB · 2026.09.10",
      visual: {
        change: "+0.25%p",
        context: "ECB 예금금리 · 9월 10일 결정",
        direction: "인상 예정",
        first: { label: "현재", value: "2.25%" },
        second: { label: "9월 16일부터", value: "2.50%" },
        caption: "9월 13일 기준 · 새 금리는 적용 전",
      },
      note: {
        heading: "그래서 우리한텐?",
        body: "유로가 강해지면 유럽 여행비가 늘 수 있어요.<br>여행 예산은 실제 환율로 다시 계산해요.",
      },
    },
  ],
};
