# Run package

Create a dated directory using the weekly end date.

```text
runs/YYYY-MM-DD/
├── weekly-economy-01.png
├── weekly-economy-02.png
├── weekly-economy-03.png
├── data.js
├── sources.md
├── provenance.md
└── economy-stories.zip
```

`provenance.md` records the date, coverage period, palette, rendering command, source list, and actual model/tool identifiers only when the platform exposes them. Do not invent model IDs.

The notification contains a one-sentence completion notice, three inline previews when supported, and the ZIP’s local download path.

