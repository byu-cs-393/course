#!/usr/bin/env python3
"""Plan (and later apply) the Canvas course from course.json.

Default mode is DRY-RUN: it computes the full plan (assignment groups,
assignments with points/due-dates/groups, weekly modules) and prints it,
making ZERO Canvas calls. `--apply` (not yet implemented) will create the
objects and write build/deploy.fall-2026.json mapping each stable id -> Canvas id.

Token (apply only): gcloud secrets versions access latest
  --secret=CANVAS_API_TOKEN --project=personal-automation-mt
"""
import json, os, re, sys, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COURSE_ID = 35464
CANVAS_HOST = "byu.instructure.com"

with open(os.path.join(ROOT, "data", "course.json"), encoding="utf-8") as f:
    C = json.load(f)

TOPIC = {t["id"]: t for t in C["topics"]}
PTS = C["points"]

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


def end_date(dates):
    """Last calendar day of a schedule 'dates' range, as (month, day) in 2026."""
    tail = dates.split("–")[-1].strip()          # after the en-dash
    m = re.match(r"([A-Z][a-z]{2})?\s*(\d+)", tail)
    mon = m.group(1) or dates.split()[0]         # carry month from range start
    return MONTHS[mon], int(m.group(2))


def due_iso(mon, day):
    """23:59 America/Denver on 2026-mon-day (DST ends Nov 1 2026)."""
    off = "-06:00" if (mon, day) < (11, 1) else "-07:00"
    return f"2026-{mon:02d}-{day:02d}T23:59:00{off}"


# week number -> due ISO (end of that week)
WEEK_DUE = {}
for s in C["schedule"]:
    if "week" in s:
        WEEK_DUE[s["week"]] = due_iso(*end_date(s["dates"]))

EC_DUE = due_iso(*(8, 31))   # extra credit: 2026-08-31

# ---- assignment groups (pinned weights; EC = sum of its points) ----
ec_pts = sum(a["points"] for a in C["assignments"]
             if a["category"] == "extra-credit" and not a.get("tbd"))
GROUPS = []
for g in C["grading"]["categories"]:
    w = ec_pts if g["weightMode"] == "sum-of-points" else g["weight"]
    GROUPS.append({"id": g["id"], "name": g["label"], "weight": w})


# ---- assignments ----
def A(id, title, group, points, due, module, subtype="online_text_entry", note=""):
    return dict(id=id, title=title, group=group, points=points, due=due,
                module=module, subtype=subtype, note=note)


plan = []
for s in C["schedule"]:
    wk = s.get("week")
    if not wk:
        continue
    mod = f"Week {wk:02d}"
    due = WEEK_DUE[wk]
    if s.get("study"):
        plan.append(A(f"study-w{wk}", "Weekly Study", "study", PTS["weeklyStudy"], due, mod))
    for p in s.get("performance", []):
        t = p["type"]
        if t == "peer-mock":
            plan.append(A(f"peer-mock-w{wk}", "Peer Mock Interview", "performance",
                          PTS["peerMock"], due, mod))
        elif t == "oa":
            grace = WEEK_DUE.get(wk + 1, due)   # OA accepted through the following week
            plan.append(A(f"oa-{p['topic']}", f"{TOPIC[p['topic']]['label']} — Online Assessment",
                          "performance", PTS["oa"], grace, mod, note="grace: +1 week"))
        elif t == "performance":
            plan.append(A(f"perf-{p['topic']}", f"{TOPIC[p['topic']]['label']} — Performance Exam",
                          "performance", PTS["performanceExam"], due, mod))
        elif t == "live-interview":
            plan.append(A(f"live-{p['index']}", f"Live Interview {p['index']}", "performance",
                          PTS["liveInterview"], due, mod))
        elif t == "professional-mock":
            plan.append(A("professional-mock", "Professional Mock Interview", "performance",
                          PTS["professionalMock"], due, mod))

for a in C["assignments"]:
    if a.get("tbd"):
        continue
    cat = a["category"]
    if cat == "extra-credit":
        plan.append(A(a["id"], a["title"], "extra-credit", a["points"], EC_DUE,
                      "Extra Credit", note="default score 0"))
    elif a["id"] == "connect-with-class":
        plan.append(A(a["id"], a["title"], "study", a["points"], WEEK_DUE[1], "Week 01"))
    elif a["id"] == "instructor-interview":
        plan.append(A(a["id"], a["title"], "performance", a["points"], None, "Milestones",
                      note="gate; no due date"))
    elif a["id"] == "final":
        plan.append(A(a["id"], a["title"], "final", a["points"],
                      due_iso(12, 17), "Milestones", subtype="on_paper", note="gate; proctored"))

# ---- build the deterministic plan artifact ----
mods = {}
for a in plan:
    mods.setdefault(a["module"], []).append(a["id"])

plan_doc = {
    "course": {"id": COURSE_ID, "host": CANVAS_HOST},
    "maxGradePct": sum(g["weight"] for g in GROUPS if g["id"] != "extra-credit") + ec_pts,
    "assignmentGroups": [{"id": g["id"], "name": g["name"], "weight": g["weight"]}
                         for g in GROUPS],
    "assignments": [
        {"id": a["id"], "title": a["title"], "group": a["group"], "points": a["points"],
         "due": a["due"], "module": a["module"], "submissionType": a["subtype"],
         "defaultScore": 0 if a["group"] == "extra-credit" else None,
         "note": a["note"] or None}
        for a in sorted(plan, key=lambda a: a["id"])
    ],
    "modules": [{"name": m, "items": sorted(items)} for m, items in sorted(mods.items())],
}

out = os.path.join(ROOT, "build", "canvas-plan.json")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    json.dump(plan_doc, f, indent=2, ensure_ascii=False)
    f.write("\n")

# ---- console summary ----
tot = plan_doc["maxGradePct"] - ec_pts
print(f"wrote build/canvas-plan.json — DRY RUN, no Canvas writes")
print(f"course {COURSE_ID} ({CANVAS_HOST})")
for g in GROUPS:
    tag = "extra credit, floats" if g["id"] == "extra-credit" else "pinned"
    print(f"  {g['name']:<14} {g['weight']:>3}%  ({tag})")
print(f"  max grade {plan_doc['maxGradePct']}%  |  {len(plan)} assignments  |  {len(mods)} modules")

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
if parser.parse_args().apply:
    sys.exit("apply mode not implemented yet — review build/canvas-plan.json first")
