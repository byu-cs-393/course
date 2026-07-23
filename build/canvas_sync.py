#!/usr/bin/env python3
"""Plan (and later apply) the Canvas course from course.json.

Default mode is DRY-RUN: it computes the full plan (assignment groups,
assignments with points/due-dates, module layout) and writes
build/canvas-plan.json, making ZERO Canvas calls. Re-run after any course.json
edit to see the Canvas-level delta as a git diff.

Module layout + ordering come from course.json's `canvas` block (Canvas
presentation), routed off the shared structural facts (week `topic`, assignment
`category`/`type`). `--apply` (not yet implemented) will create the objects and
write build/deploy.fall-2026.json mapping each stable id -> Canvas id.
"""
import json, os, re, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT, "data", "course.json"), encoding="utf-8") as f:
    C = json.load(f)

CFG = C["canvas"]
COURSE_ID = CFG["courseId"]
CANVAS_HOST = CFG["host"]
MODULES_CFG = CFG["modules"]
MODULE_ORDER = [m["name"] for m in MODULES_CFG]
ITEM_ORDER = {t: i for i, t in enumerate(CFG["itemOrder"])}
TOPIC = {t["id"]: t for t in C["topics"]}
PTS = C["points"]

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


def end_date(dates):
    """Last calendar day of a schedule 'dates' range, as (month, day) in 2026."""
    tail = dates.split("–")[-1].strip()
    m = re.match(r"([A-Z][a-z]{2})?\s*(\d+)", tail)
    mon = m.group(1) or dates.split()[0]
    return MONTHS[mon], int(m.group(2))


def due_iso(mon, day):
    """23:59 America/Denver on 2026-mon-day (DST ends Nov 1 2026)."""
    off = "-06:00" if (mon, day) < (11, 1) else "-07:00"
    return f"2026-{mon:02d}-{day:02d}T23:59:00{off}"


WEEK_DUE = {s["week"]: due_iso(*end_date(s["dates"])) for s in C["schedule"] if "week" in s}
EC_DUE = due_iso(8, 31)

# ---- assignment groups (pinned weights; EC = sum of its points) ----
ec_pts = sum(a["points"] for a in C["assignments"]
             if a["category"] == "extra-credit" and not a.get("tbd"))
GROUPS = []
for g in C["grading"]["categories"]:
    w = ec_pts if g["weightMode"] == "sum-of-points" else g["weight"]
    GROUPS.append({"id": g["id"], "name": g["label"], "weight": w})


# ---- assignments (structural: type/topic/week; module is routed later) ----
def A(id, title, group, points, due, type, week=None, topic=None,
      subtype="online_text_entry", note=""):
    return dict(id=id, title=title, group=group, points=points, due=due, type=type,
                week=week, topic=topic, subtype=subtype, note=note)


plan = []
for s in C["schedule"]:
    wk = s.get("week")
    if not wk:
        continue
    tp = s.get("topic")
    due = WEEK_DUE[wk]
    if s.get("study"):
        plan.append(A(f"study-w{wk}", "Weekly Study", "study", PTS["weeklyStudy"], due,
                      "study", week=wk, topic=tp))
    for p in s.get("performance", []):
        t = p["type"]
        if t == "peer-mock":
            plan.append(A(f"peer-mock-w{wk}", "Peer Mock Interview", "performance",
                          PTS["peerMock"], due, "peer-mock", week=wk, topic=tp))
        elif t == "oa":
            grace = WEEK_DUE.get(wk + 1, due)   # OA accepted through the following week
            plan.append(A(f"oa-{p['topic']}", f"{TOPIC[p['topic']]['label']} — Online Assessment",
                          "performance", PTS["oa"], grace, "oa", week=wk, topic=p["topic"],
                          note="grace: +1 week"))
        elif t == "performance":
            plan.append(A(f"perf-{p['topic']}", f"{TOPIC[p['topic']]['label']} — Performance Exam",
                          "performance", PTS["performanceExam"], due, "performance",
                          week=wk, topic=p["topic"]))
        elif t == "live-interview":  # topic-agnostic
            plan.append(A(f"live-{p['index']}", f"Live Interview {p['index']}", "performance",
                          PTS["liveInterview"], due, "live-interview", week=wk))
        elif t == "professional-mock":
            plan.append(A("professional-mock", "Professional Mock Interview", "performance",
                          PTS["professionalMock"], due, "professional-mock", week=wk))

for a in C["assignments"]:
    if a.get("tbd"):
        continue
    if a["category"] == "extra-credit":
        plan.append(A(a["id"], a["title"], "extra-credit", a["points"], EC_DUE,
                      "extra-credit", note="default score 0"))
    elif a["id"] == "connect-with-class":
        plan.append(A(a["id"], a["title"], "study", a["points"], WEEK_DUE[1],
                      "connect-with-class", week=1, topic="data-structures"))
    elif a["id"] == "instructor-interview":
        plan.append(A(a["id"], a["title"], "performance", a["points"], None,
                      "instructor-interview", note="gate; no due date"))
    elif a["id"] == "final":
        plan.append(A(a["id"], a["title"], "final", a["points"], due_iso(12, 17),
                      "final", subtype="on_paper", note="gate; proctored"))


# ---- route each assignment to a module (first matching rule wins) ----
def route(a):
    for m in MODULES_CFG:
        if "topic" in m and a["topic"] == m["topic"]:
            return m["name"]
        if "category" in m and a["group"] == m["category"]:
            return m["name"]
        inc = m.get("include")
        if inc and (a["type"] in inc.get("types", [])
                    or a["week"] in inc.get("weeks", [])
                    or a["id"] in inc.get("ids", [])):
            return m["name"]
    return None


for a in plan:
    a["module"] = route(a)

# ---- build the deterministic plan artifact ----
mods = {}
for a in plan:
    mods.setdefault(a["module"], []).append(a)


def _item_key(a):
    return (a["week"] if a["week"] is not None else 99, ITEM_ORDER.get(a["type"], 99), a["id"])


plan_doc = {
    "course": {"id": COURSE_ID, "host": CANVAS_HOST},
    "maxGradePct": sum(g["weight"] for g in GROUPS if g["id"] != "extra-credit") + ec_pts,
    "assignmentGroups": [{"id": g["id"], "name": g["name"], "weight": g["weight"]}
                         for g in GROUPS],
    "assignments": [
        {"id": a["id"], "title": a["title"], "group": a["group"], "type": a["type"],
         "points": a["points"], "due": a["due"], "module": a["module"], "week": a["week"],
         "submissionType": a["subtype"],
         "defaultScore": 0 if a["group"] == "extra-credit" else None,
         "note": a["note"] or None}
        for a in sorted(plan, key=lambda a: a["id"])
    ],
    "modules": [{"name": m, "items": [x["id"] for x in sorted(mods[m], key=_item_key)]}
                for m in MODULE_ORDER if m in mods],
}

out = os.path.join(ROOT, "build", "canvas-plan.json")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    json.dump(plan_doc, f, indent=2, ensure_ascii=False)
    f.write("\n")

# ---- console summary ----
unrouted = [a["id"] for a in plan if a["module"] is None]
print("wrote build/canvas-plan.json — DRY RUN, no Canvas writes")
print(f"course {COURSE_ID} ({CANVAS_HOST})")
for g in GROUPS:
    tag = "extra credit, floats" if g["id"] == "extra-credit" else "pinned"
    print(f"  {g['name']:<14} {g['weight']:>3}%  ({tag})")
print(f"  max grade {plan_doc['maxGradePct']}%  |  {len(plan)} assignments  |  "
      f"{len(plan_doc['modules'])} modules")
if unrouted:
    print("  WARNING unrouted assignments:", unrouted)

parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true")
if parser.parse_args().apply:
    raise SystemExit("apply mode not implemented yet — review build/canvas-plan.json first")
