# CS 393 — course-as-data

`data/course.json` is the **single source of truth** for this course. Everything else —
the student-facing markdown *and* the Canvas course — is generated from it.

## Layout

| Path | What |
|---|---|
| `data/course.json` | the course: schedule, weeks, topic exams, grading, points, Canvas layout, assignments |
| `build/build.py` + `build/templates/*.j2` | render `course.json` → the markdown files (`weekly/`, `topic-exams/`, `schedule.md`) |
| `build/canvas_sync.py` | render `course.json` → the Canvas course |
| `build/canvas_content.py` | markdown → Canvas HTML (descriptions, pages, syllabus) |
| `build/canvas-plan.json` | **desired** Canvas state (deterministic; committed so each edit is a diff) |
| `build/deploy.fall-2026.json` | **id map**: stable id → Canvas id (groups/assignments/pages/modules) |
| `build/canvas-state.json` | **actual** Canvas state, snapshotted after each apply |

## Workflow

```bash
# 1. edit data/course.json
# 2. regenerate the markdown
python build/build.py
# 3. preview the Canvas plan (no writes) — review the git diff of build/canvas-plan.json
python build/canvas_sync.py
# 4. mirror it to Canvas
export CANVAS_TOKEN=...            # a Canvas API token with teacher access on the course
python build/canvas_sync.py --apply
```

`--pull` snapshots actual Canvas state to `build/canvas-state.json` without writing.

## The Canvas mirror

`--apply` is a **declarative mirror**: it makes Canvas match `course.json` exactly.

- **Idempotent** — objects are matched by stable id via the deploy map and **updated in
  place** (ids preserved, so submissions/grades survive). Re-run any time.
- **Prune** — anything in Canvas that isn't in the plan is deleted… **except** an assignment
  that has student work (submissions/grades), which is never deleted.
- **Grade rules are data.** `grading` in `course.json` drives the weighted groups, the
  extra-credit float (weight = Σ points, so 1 pt = 1%), each category's `defaultScore`, and
  `missingSubmissionPolicy`.

## Design principle

**Content, structure, and policy are data (`course.json`); mechanics are code.** What exists,
how much it's worth, where it goes, and the grading rules live in the JSON. How to talk to
Canvas, render markdown, and route modules lives in Python. Keep that line — don't push
Canvas mechanics into the JSON, and don't hardcode course facts into the code.

## Requirements

Python 3 with `jinja2` and `markdown` (`pip install -r build/requirements.txt`).
