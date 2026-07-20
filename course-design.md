# CS 393 — Course Design (working spec)

> A working design document for the Fall 2026 redesign. It captures **what** we ask students
> to do each week and **why**, and how it maps to Canvas. This spec will inform the
> [syllabus](syllabus.md). **Nothing here is in Canvas yet** — it's for us to react to first.

## Philosophy: the exposure ladder

Interviewing is a performance skill. Beyond algorithms, students need to think out loud,
collaborate, and stay composed under pressure. The course builds that in graduated steps of
increasing social/performance pressure:

1. **Collaborative study** — work *with* a peer on problems. Low stakes; builds
   communication and normalizes thinking out loud.
2. **Peer mock interview** — a peer puts you *on the spot*. Exposure therapy for nerves and
   anxiety, not just collaboration.
3. **Live topic exam** — a TA or instructor interviews you and awards a score.
4. **Final exam** — solo and high-stakes, but with hints, like a real interview.

Every weekly requirement maps onto a rung of this ladder — that's the "why" behind it.

## Weekly deliverables — one item per weighted category

Each week a student owes one clear item per graded category, so the "what" and the "why" are
legible at a glance:

| Category (weight) | Weekly item | Purpose (why) |
|---|---|---|
| **Study** (40%) | Practice hours + required problems | Deliberate practice + collaboration |
| **Communication** (20%) | Peer mock interview | Exposure therapy; collaboration |
| **Topic Exams** (20%) | The topic-exam step due that week | Mastery checkpoints (~1/week; 12 over 14 weeks) |
| **Final** (20%) | — (end of term) | Comprehensive performance |

## Study rubric (proposed)

Study is **9 hours/week** total (class counts as 3), with collaboration built in:

| Points | For |
|---:|---|
| 4 | **4 hours of collaborative study** (class counts toward this) |
| 4 | **Required problems done** (2 assigned HW + in-class problems; others recommended. *On OA weeks the OA replaces the 2 HW — see note below.*) |
| 5 | **5 hours of personal study** (may be collaborative, but doesn't have to be) |
| **13** | **weekly total** |

> **Decided:** only **1 collaborative hour is required outside class** (3 of the 4 come from
> class; students who skip class owe all 4 on their own). The **5 personal hours** are the
> point — sharpening your own skills is what makes you a better collaborator and prepares you
> to be put on the spot.

**On OA weeks, the required problems are the in-class problems** — the two assigned HW
problems are replaced by the OA, which students do on their own as that week's outside
practice. Benefits:

- The **OA stays a clean Topic-Exam checkpoint** — no cross-category double-count.
- The week's required problems are the ones worked **collaboratively in class**, so it
  **rewards attendance** and reinforces the collaboration theme precisely when no outside HW
  is assigned.
- **Outside-of-class load stays sane:** the OA is the outside practice; the required problems
  were done in class.

The Study rubric is unchanged (still 4 pts for required problems); only that week's
*definition* of "required problems" shifts, which the weekly assignment description spells
out. So the study survey stays uniform.

## Semester schedule

The dated, student-facing schedule is [`schedule.md`](schedule.md) (the Fall 2026 Tue/Thu
section — 15 real weeks). Design notes behind it:

- **Topic sequence follows the existing weekly problem sets** — DS (W01–03) → Graphs
  (W04–06) → DP (W07–10) → Sorting (W11–14), review at the end. Each topic runs
  **OA → Performance → Live**.
- **Week 1 is a half week done at half load** — students do *all* the weekly activities
  (study, problems, peer mock, connect, start the DS OA). It's the best intro to the rhythm.
- **Peer mocks every week except live-exam weeks and Thanksgiving** (9 peer mocks). Kept on
  performance weeks — the low-stakes rehearsal for the live interview and final, and the main
  source of fresh on-the-spot reps. **Connect with class** (post + Teams photo) is a separate
  trivial onboarding item, *not* a mock.
- **Thanksgiving (Wk 13)** is a natural flex/catch-up half week (only Tue Nov 24). Labor Day
  costs nothing (it's a Monday).
- **Professional mock is due Wk 14** (before the final crunch); students **schedule it in
  Wk 10** given the ~month of lead time.
- **Instructor pass/fail interview** (required to pass) floats — complete with the instructor
  by ~Wk 14; a mock or an instructor-run topic exam counts.
- **OA timing is intentional.** The OA lands at the *start* of a topic as a non-failable
  diagnostic + practice instrument (attempt 1 cold surfaces gaps; later attempts use help);
  a passing attempt is accepted **through the following week**. On OA weeks the required study
  problems come from **class**, not extra HW (see the Study rubric note above).
- **Final** — one exam across three sittings: Tue Dec 8 (75 min) + Thu Dec 10 (75 min) +
  Thu Dec 17, 7–10 am (3 hrs) = **5½ hours, 12 questions**.

## Completion

Every weekly item is completed by a **manual Canvas submission** — the student enters URLs
and a short template, and it's graded in Canvas. Same one-assignment-per-item structure
everywhere.

**Decided: everything is a Canvas Assignment — no quizzes.** Assignments keep the student
experience uniform and are easy to grade (and, later, to automate).

**Time is always self-reported.** Study time is often spent at a whiteboard or in discussion,
so hours are simply entered by the student.

Labor-saver: Canvas's **"Set Default Grade"** grants full credit to all submitters in one
action (good for completion-style items like mock/topic).

> **Extension-ready, not extension-dependent.** This structure (uniform Canvas Assignments,
> one per item, with fields an API could fill) is deliberately built so that
> [Jack Leonard's extension](https://github.com/byu-cs-393/extension) can later post credit
> automatically. It is **not integrated yet** — the course runs entirely on the manual path
> for now, and we'll add the extension once it's tested and working. Nothing about the manual
> design changes when it lands.

## Per-item mechanism

| Item | Canvas type | Completion |
|---|---|---|
| **Study** (hours + problems) | Assignment — one item | Hours **always self-reported**; problem links pasted manually. Points by the **4/4/5 rubric** (see below). |
| **Mock interview** | Assignment | Manual: who you paired with + which problem |
| **Topic exam** | Assignment | Manual template (see [topic-exams](topic-exams/)) |

The Study assignment description carries the rubric so students see how points are earned.
Grading is by the 4/4/5 rubric.

## Tapering the manual path

Early in the term (especially Fall) students are highly engaged; late in the term the
clicking/overhead grates. So **taper the manual template, not the Canvas item type**:

- **Week 1:** richer submission — reflection prompts ("what did you do to make this problem
  more valuable to your growth?"), full detail. Great while motivation is high.
- **Later weeks:** streamlined self-report — hours + links + a line on what you did.

Because the item type never changes, the gradebook stays consistent all semester; only the
manual template shrinks. (This also keeps a future extension integration trivial.)

## Manual submission templates

> **How to paste a submission URL:** paste the link to your *accepted* submission — not the
> problem page. On LeetCode: open the problem → **Submissions** tab → click your accepted
> attempt → copy the address bar. It looks like:
> `https://leetcode.com/problems/two-sum/submissions/1046917577/`

### Study — Week 1 (rich)

```
- Required problems (paste your accepted-submission URLs — see note above):
    1.
    2.
- In-class problems (URLs or "done in class"):
- Collaborative study: __ hrs (with whom?)
- Personal study: __ hrs
- What did you do to make a problem more valuable to your growth?
    [ ] Re-did it and timed myself
    [ ] Re-did it without looking up syntax/solutions
    [ ] Studied others' solutions to learn from them
    [ ] Just finished and moved on
    [ ] Other:
- Would you like a TA/instructor to review a solution and give feedback? (Yes / No)
```

### Study — later weeks (light)

```
- Required problem URLs (accepted-submission links, e.g. .../submissions/1046917577/): 1) __  2) __
- Hours: collaborative __ / personal __
- Anything you want feedback on? (optional)
```

### Peer mock interview

```
- Peer you interviewed with:
- Problem(s) worked on:
- How it went / what you practiced:
```

### Professional mock interview (Wk 14)

```
- Professional you interviewed with (name):
- Company & role:
- Problem(s) worked on:
- How it went & feedback received:
```

Topic-exam templates (three — OA / Performance / Live) live at
[`topic-exams/submission-templates.md`](topic-exams/submission-templates.md).

## Decisions made

- **No quizzes.** Every item is a Canvas Assignment.
- **Study is one assignment** with hours **always self-reported** (whiteboard/discussion time
  can't be auto-captured), graded by the 4/4/5 rubric.
  Only **1 collaborative hour required outside class**; the 5 personal hours are the point.
- **Peer mock interviews are their own thing** — not double-counted with TA/instructor
  interviews. **No peer mock only in a live-exam week** (or Thanksgiving). Peer mocks are kept
  on performance weeks — they're the rehearsal for the live interview and final and the main
  source of fresh on-the-spot reps. The **professional** mock is required and is **due Wk 14**
  (before finals). **Connect with class** is a separate trivial onboarding item, not a mock.
- **Feedback is opt-in.** Everyone always gets the rubric **score**; qualitative **written
  feedback** goes only to students who request it (with encouragement to ask, and proactive
  outreach to strugglers).
- **Instructor pass/fail interview** — students **schedule it on Day 1** (Wk 1); see
  [`scheduling.md`](scheduling.md). Satisfiable by a mock or an instructor-run topic exam.
- **Schedule** fit to the real Fall 2026 calendar — done ([`schedule.md`](schedule.md));
  professional mock scheduled Wk 10, due Wk 14.
- **Extra credit** — handled via Canvas weighted categories that can exceed 100%; items in
  [`extra-credit.md`](extra-credit.md).

## Open decisions

- **Fall 2026 TAs** — TBD (Jack Leonard confirmed).
