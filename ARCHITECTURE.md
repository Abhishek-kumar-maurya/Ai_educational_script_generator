# Architecture / Workflow

## Major stages

```text
┌──────────────┐
│  PDF Upload  │
└──────┬───────┘
       ↓
┌────────────────────┐
│ PyMuPDF Extraction │
└──────┬─────────────┘
       ↓
┌──────────────────────┐
│ Clean + Classify     │
│ Instruction/Activity │
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│ Concept Extraction   │
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│ Evidence Retrieval   │
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│ AI Planning          │
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│ AI Script Generation │
└──────┬───────────────┘
       ↓
┌──────────────────────┐
│ Validation           │
│ schema / duration /  │
│ coverage / quality   │
└──────┬───────────────┘
       ↓
   pass? ────── no ───→ Repair ──→ Validate
       │
      yes
       ↓
┌──────────────────────┐
│ Final Script + Score │
└──────────────────────┘
```

## Design principle

The system deliberately avoids:

`PDF → one giant prompt → script`

Instead, each stage has a focused responsibility.
