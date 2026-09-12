Prompt architecture is implemented as focused stages in:
- core/planner.py
- core/generator.py
- core/repair.py

The assignment specifically asks whether the solution uses one prompt or
multiple stages; this project uses multiple stages so analysis, planning,
generation and repair can be inspected independently.
