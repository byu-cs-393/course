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

## 14-week schedule (draft)

Topic sequence follows the existing weekly materials: **Data Structures → Graphs → Dynamic
Programming → Sorting/Two-Pointer**, with review at the end. Each topic runs its three exams
(**OA → Performance → Live**) across its weeks. Peer mock interviews run every week **except
live-exam weeks**. Peer mocks are kept even on performance weeks — they're the low-stakes
rehearsal for the live interview and final, and a key source of fresh on-the-spot
problem-solving reps. The **professional** mock replaces the peer mock in the final week.

| Wk | Topic focus | Topic exam due | Mock interview |
|---:|---|---|---|
| 1 | Data Structures | DS — Online Assessment | Connect with class |
| 2 | Data Structures | DS — Performance | Peer |
| 3 | Data Structures | DS — **Live** | — *(live-exam week)* |
| 4 | Graphs | Graphs — Online Assessment | Peer |
| 5 | Graphs | Graphs — Performance | Peer |
| 6 | Graphs | Graphs — **Live** | — *(live-exam week)* |
| 7 | Dynamic Programming | DP — Online Assessment | Peer |
| 8 | Dynamic Programming | DP — Performance | Peer |
| 9 | Dynamic Programming | *(catch-up / practice)* | Peer |
| 10 | Dynamic Programming | DP — **Live** | — *(live-exam week)* |
| 11 | Sorting, Two-Pointer | Sorting — Online Assessment | Peer |
| 12 | Sorting, Two-Pointer | Sorting — Performance | Peer |
| 13 | Sorting, Two-Pointer | Sorting — **Live** | — *(live-exam week)* |
| 14 | Review & final prep | — | **Professional** (in lieu of peer) |

**Study is due every week** (constant, so not shown). Totals: **12 topic exams**, **14 study**,
**10 communication** items (8 peer + 1 connect + 1 professional), **1 final**.

It fits: 12 exams land one per week across weeks 1–13, with **week 9 as DP breathing room**
(DP is the hardest — 4 weeks, 3 exams). Caveats to design around:

- **The professional mock needs ~a month of lead time.** Reaching a professional takes weeks
  of outreach (see [LinkedIn outreach](mock-interviews/linkedin-outreach.md)). Due week 14 →
  students must start by ~week 10. Plant a reminder/assignment around weeks 9–10.
- **Instructor pass/fail interview** (required to pass) is not a weekly item — it floats.
  Students complete it with the instructor by ~week 14; satisfiable by a mock *or* a topic
  exam done with the instructor.
- **Final exam** is the last two days of class (week 14 / finals period).
- **Week numbers are relative to when each topic is taught** and slide to the real Fall
  calendar. In practice the first DS OA may be assigned week 1 and due week 2.
- **OA timing is intentional.** The OA lands at the *start* of a topic, before it's fully
  taught — as a diagnostic + practice instrument (attempt 1 cold surfaces gaps; later
  attempts use resources/help). It's non-failable, with a **passing attempt accepted through
  the following week**, so early timing primes the topic rather than penalizing unpreparedness.
  On OA weeks the required study problems come from **class**, not extra HW (see the Study
  rubric note).

## Completion: the dual-path pattern

The core mechanic of the redesign:

> **Every weekly item can be completed two ways — via the extension (auto-credit), or
> manually. Same gradebook column either way. The extension is the investment in ease of
> use; the manual path guarantees no one is forced to use it.**

- **Extension path:** [Jack Leonard's extension](https://github.com/byu-cs-393/extension)
  reports the work and posts credit to Canvas.
- **Manual path:** the student submits the item themselves (URLs / a short template).

**Decided: everything is a Canvas Assignment — no quizzes.** Assignments keep the extension
integration simple (easy to submit/grade via API) and the student experience uniform.

**Time is always self-reported, even by extension users.** Study time is often spent at a
whiteboard or in discussion — work the extension can't observe — so hours are entered by the
student regardless of whether they use the extension. The extension still helps where it can
(pre-filling completed-problem links, mock, and topic-exam reporting).

Labor-savers: Canvas's **"Set Default Grade"** grants full credit to all submitters in one
action (good for completion-style items like mock/topic). For the rubric-graded Study report,
a possible **AI-assisted grader** could pre-score the 4/4/5 rubric from the submission text —
_TBD._

## Per-item mechanism

| Item | Canvas type | Completion |
|---|---|---|
| **Study** (hours + problems) | Assignment — one item | Hours **always self-reported**; problem links manual or extension-prefilled. Points by the **4/4/5 rubric** (see below). |
| **Mock interview** | Assignment | Manual: who you paired with + which problem |
| **Topic exam** | Assignment | Manual template, or extension (see [topic-exams](topic-exams/)) |

The Study assignment description carries the rubric so students see how points are earned.
Grading is by the 4/4/5 rubric — potentially with an AI-assisted first pass (TBD) to keep
the TA workload down.

## Tapering the manual path

Early in the term (especially Fall) students are highly engaged; late in the term the
clicking/overhead grates. So **taper the manual template, not the Canvas item type**:

- **Week 1:** richer submission — reflection prompts ("what did you do to make this problem
  more valuable to your growth?"), full detail. Great while motivation is high.
- **Later weeks:** streamlined self-report — hours + links + a line on what you did.

Because the item type never changes, the extension path stays identical all semester and the
gradebook stays consistent; only the manual template shrinks.

## Manual submission templates

### Study — Week 1 (rich)

```
- BYU Net ID:
- Required problems (paste passing-submission URLs):
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
- BYU Net ID:
- Required problem URLs: 1) __  2) __
- Hours: collaborative __ / personal __
- Anything you want feedback on? (optional)
```

### Mock interview

```
- BYU Net ID:
- Peer you interviewed with:
- Problem(s) worked on:
- How it went / what you practiced:
```

Topic-exam template already lives at [`topic-exams/submission-template.md`](topic-exams/submission-template.md).

## Decisions made

- **No quizzes.** Every item is a Canvas Assignment.
- **Study is one assignment** with hours **always self-reported** (even by extension users,
  since whiteboard/discussion time is invisible to the extension), graded by the 4/4/5 rubric.
  Only **1 collaborative hour required outside class**; the 5 personal hours are the point.
- **Peer mock interviews are their own thing** — not double-counted with TA/instructor
  interviews. **No peer mock only in a live-exam week.** Peer mocks are kept on performance
  weeks — they're the rehearsal for the live interview and final and the main source of fresh
  on-the-spot reps. The **professional** mock is required and lands in the **final week in
  lieu of** the peer mock.
- **Feedback is opt-in.** Everyone always gets the rubric **score**; qualitative **written
  feedback** goes only to students who request it (with encouragement to ask, and proactive
  outreach to strugglers).
- **AI-assisted grader** for the Study rubric is a possible labor-saver — _TBD._

## Open decisions

- **Professional-mock lead time** — where to plant the outreach reminder (weeks 9–10?).
- **Instructor pass/fail interview** — exact placement / deadline.
- Fit the draft schedule to the **real Fall 2026 calendar** (start date, holidays, finals).
