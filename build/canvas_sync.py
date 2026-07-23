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
import json, os, re, argparse, subprocess, urllib.request, urllib.error
import canvas_content as content

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
ASSIGN_BY_ID = {a["id"]: a for a in C["assignments"]}
WEEK_TITLE = {w["week"]: w["title"] for w in C["weeks"]}

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
_ec_cat = next(g for g in C["grading"]["categories"] if g["id"] == "extra-credit")
EC_DUE = due_iso(*(int(x) for x in _ec_cat["due"].split("-")[1:]))   # from grading config

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

# ---- pages: one per week, in the module of that week's study assignment ----
study_module = {a["week"]: a["module"] for a in plan if a["type"] == "study"}
PAGES = [{"id": f"week-{w}", "title": f"Week {w:02d} — {WEEK_TITLE[w]}", "week": w,
          "module": study_module[w]} for w in sorted(study_module)]

# ---- module items (assignments + week pages), ordered ----
module_items = {}
for a in plan:
    module_items.setdefault(a["module"], []).append(
        {"kind": "assignment", "id": a["id"], "week": a["week"],
         "rank": ITEM_ORDER.get(a["type"], 99)})
for p in PAGES:
    module_items.setdefault(p["module"], []).append(
        {"kind": "page", "id": p["id"], "week": p["week"], "rank": -1})   # page first


def _item_key(it):
    return (it["week"] if it["week"] is not None else 99, it["rank"], it["id"])


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
    "pages": [{"id": p["id"], "title": p["title"], "module": p["module"]} for p in PAGES],
    "modules": [{"name": m, "items": [{"kind": it["kind"], "id": it["id"]}
                                      for it in sorted(module_items.get(m, []), key=_item_key)]}
                for m in MODULE_ORDER if m in module_items],
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

# ---- apply (idempotent Canvas writes, recorded in deploy map) ----
DEPLOY = os.path.join(ROOT, "build", "deploy.fall-2026.json")


def get_token():
    t = os.environ.get("CANVAS_TOKEN")
    if t and t.strip():
        return t.strip()
    r = subprocess.run("gcloud secrets versions access latest "
                       "--secret=CANVAS_API_TOKEN --project=personal-automation-mt",
                       capture_output=True, text=True, shell=True)
    if r.returncode or not r.stdout.strip():
        raise SystemExit("set CANVAS_TOKEN env var (or ensure gcloud is on PATH)")
    return r.stdout.strip()


def canvas(tok, method, path, payload=None):
    url = f"https://{CANVAS_HOST}/api/v1{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {path} -> {e.code}: {e.read().decode()[:300]}")
    return json.loads(body) if body.strip() else None   # 204 No Content -> None


def canvas_list(tok, path):
    sep = "&" if "?" in path else "?"
    url = f"https://{CANVAS_HOST}/api/v1{path}{sep}per_page=100"
    out = []
    while url:
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
        with urllib.request.urlopen(req) as r:
            out += json.load(r)
            link = r.headers.get("Link", "")
        m = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = m.group(1) if m else None
    return out


def load_dm():
    if os.path.exists(DEPLOY):
        dm = json.load(open(DEPLOY, encoding="utf-8"))
        dm.setdefault("pages", {})
        return dm
    return {"course": COURSE_ID, "host": CANVAS_HOST, "groups": {}, "assignments": {},
            "pages": {}, "modules": {}}


def save_dm(dm):
    with open(DEPLOY, "w", encoding="utf-8", newline="\n") as f:
        json.dump(dm, f, indent=2, ensure_ascii=False)
        f.write("\n")


def has_student_work(a):
    return bool(a.get("has_submitted_submissions") or a.get("graded_submissions_exist"))


def prune(tok, dm):
    """Delete Canvas objects not in the deploy map (mirror), but NEVER delete an
    assignment that has student work — and never cascade-delete a group holding one."""
    keep_a = set(dm["assignments"].values())
    protected_groups = set()
    blocked = 0
    for a in canvas_list(tok, f"/courses/{COURSE_ID}/assignments"):
        if a["id"] in keep_a:
            protected_groups.add(a["assignment_group_id"])
            continue
        if has_student_work(a):
            protected_groups.add(a["assignment_group_id"])
            blocked += 1
            print(f"  BLOCKED prune (has submissions): {a['name']}")
            continue
        canvas(tok, "DELETE", f"/courses/{COURSE_ID}/assignments/{a['id']}")
        print(f"  pruned assignment  {a['name']}")

    keep_pg = set(dm.get("pages", {}).values())
    for pg in canvas_list(tok, f"/courses/{COURSE_ID}/pages"):
        if pg["url"] not in keep_pg:
            canvas(tok, "DELETE", f"/courses/{COURSE_ID}/pages/{pg['url']}")
            print(f"  pruned page        {pg['title']}")

    keep_m = set(dm["modules"].values())
    for m in canvas_list(tok, f"/courses/{COURSE_ID}/modules"):
        if m["id"] not in keep_m:                       # module items are just links; safe
            canvas(tok, "DELETE", f"/courses/{COURSE_ID}/modules/{m['id']}")
            print(f"  pruned module      {m['name']}")

    keep_g = set(dm["groups"].values())
    for g in canvas_list(tok, f"/courses/{COURSE_ID}/assignment_groups"):
        if g["id"] in keep_g:
            continue
        if g["id"] in protected_groups:                 # would cascade-delete a protected assignment
            print(f"  BLOCKED prune group (holds protected work): {g['name']}")
            continue
        canvas(tok, "DELETE", f"/courses/{COURSE_ID}/assignment_groups/{g['id']}")
        print(f"  pruned group       {g['name']}")

    if blocked:
        print(f"\n  ⚠ {blocked} assignment(s) kept despite not being in the plan "
              f"(student work present) — resolve manually if intentional.")


def set_missing_policy(tok):
    """Missing submissions (past due, nothing submitted) → 0. No late penalty.
    Applies to online-submission assignments; on_paper/none (the final) are exempt."""
    url = f"/courses/{COURSE_ID}/late_policy"
    try:
        urllib.request.urlopen(urllib.request.Request(
            f"https://{CANVAS_HOST}/api/v1{url}", headers={"Authorization": "Bearer " + tok}))
        exists = True
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        exists = False
    canvas(tok, "PATCH" if exists else "POST", url,
           {"late_policy": {"missing_submission_deduction_enabled": True,
                            "missing_submission_deduction": 100,
                            "late_submission_deduction_enabled": False}})
    print("  missing-submission policy: 0 for missing after due (no late penalty)")


def set_ec_defaults(tok, dm):
    """Set a default grade of 0 on Extra Credit assignments, ONLY for ungraded
    submissions — so EC counts toward its group's points (1 pt = 1%) without ever
    clobbering a grade a student has already earned."""
    ec_ids = [dm["assignments"][a["id"]] for a in plan if a["group"] == "extra-credit"]
    students = [u["id"] for u in
                canvas_list(tok, f"/courses/{COURSE_ID}/users?enrollment_type[]=student")]
    if not students:
        print("  (no students enrolled yet — skipped EC defaults)")
        return
    touched = 0
    for acid in ec_ids:
        subs = canvas_list(tok, f"/courses/{COURSE_ID}/assignments/{acid}/submissions")
        graded = {s["user_id"] for s in subs
                  if s.get("score") is not None or s.get("grade") is not None}
        ungraded = [u for u in students if u not in graded]
        if ungraded:
            canvas(tok, "POST",
                   f"/courses/{COURSE_ID}/assignments/{acid}/submissions/update_grades",
                   {"grade_data": {str(u): {"posted_grade": 0} for u in ungraded}})
            touched += 1
    print(f"  set default 0 on {touched}/{len(ec_ids)} EC assignments (ungraded only)")


def apply():
    """Mirror course.json to Canvas: create/update everything in the plan, prune the rest."""
    tok = get_token()
    old = load_dm()
    dm = {"course": COURSE_ID, "host": CANVAS_HOST, "groups": {}, "assignments": {},
          "pages": {}, "modules": {}}

    canvas(tok, "PUT", f"/courses/{COURSE_ID}",
           {"course": {"apply_assignment_group_weights": True,
                       "syllabus_body": content.syllabus_html(ROOT)}})
    print("enabled weighted groups + set syllabus")
    set_missing_policy(tok)

    for pos, g in enumerate(GROUPS, 1):
        body = {"name": g["name"], "group_weight": g["weight"], "position": pos}
        cid = old["groups"].get(g["id"])
        if cid:
            canvas(tok, "PUT", f"/courses/{COURSE_ID}/assignment_groups/{cid}", body); act = "updated"
        else:
            cid = canvas(tok, "POST", f"/courses/{COURSE_ID}/assignment_groups", body)["id"]; act = "created"
        dm["groups"][g["id"]] = cid
        print(f"  group  {g['name']:<26} {g['weight']:>3}%  {act}")

    for a in sorted(plan, key=lambda a: a["id"]):
        body = {"assignment": {"name": a["title"], "points_possible": a["points"],
                               "assignment_group_id": dm["groups"][a["group"]],
                               "submission_types": [a["subtype"]],
                               "due_at": a["due"], "published": True,
                               "description": content.description_html(ROOT, a, ASSIGN_BY_ID)}}
        cid = old["assignments"].get(a["id"])
        if cid:
            canvas(tok, "PUT", f"/courses/{COURSE_ID}/assignments/{cid}", body)
        else:
            cid = canvas(tok, "POST", f"/courses/{COURSE_ID}/assignments", body)["id"]
        dm["assignments"][a["id"]] = cid
    print(f"  synced {len(plan)} assignments (with descriptions)")

    for p in PAGES:
        wp = {"wiki_page": {"title": p["title"], "body": content.page_html(ROOT, p["week"]),
                            "published": True}}
        slug = old["pages"].get(p["id"])
        r = (canvas(tok, "PUT", f"/courses/{COURSE_ID}/pages/{slug}", wp) if slug
             else canvas(tok, "POST", f"/courses/{COURSE_ID}/pages", wp))
        dm["pages"][p["id"]] = r["url"]
    print(f"  synced {len(PAGES)} weekly pages")

    for pos, m in enumerate(plan_doc["modules"], 1):
        mcid = old["modules"].get(m["name"])
        body = {"module": {"name": m["name"], "position": pos, "published": True}}
        if mcid:
            canvas(tok, "PUT", f"/courses/{COURSE_ID}/modules/{mcid}", body)
        else:
            mcid = canvas(tok, "POST", f"/courses/{COURSE_ID}/modules", body)["id"]
        dm["modules"][m["name"]] = mcid
        desired = [("Assignment", dm["assignments"][it["id"]]) if it["kind"] == "assignment"
                   else ("Page", dm["pages"][it["id"]]) for it in m["items"]]
        have = {}
        for e in canvas_list(tok, f"/courses/{COURSE_ID}/modules/{mcid}/items"):
            if e.get("type") == "Assignment":
                have[("Assignment", e.get("content_id"))] = e["id"]
            elif e.get("type") == "Page":
                have[("Page", e.get("page_url"))] = e["id"]
        for key, iid in have.items():           # remove items no longer in the plan
            if key not in desired:
                canvas(tok, "DELETE", f"/courses/{COURSE_ID}/modules/{mcid}/items/{iid}")
        for ipos, (kind, ref) in enumerate(desired, 1):
            if (kind, ref) in have:
                canvas(tok, "PUT", f"/courses/{COURSE_ID}/modules/{mcid}/items/{have[(kind, ref)]}",
                       {"module_item": {"position": ipos}})
            else:
                mi = {"type": kind, "position": ipos}
                mi["content_id" if kind == "Assignment" else "page_url"] = ref
                canvas(tok, "POST", f"/courses/{COURSE_ID}/modules/{mcid}/items", {"module_item": mi})
        print(f"  module {m['name']:<26} {len(desired)} items")

    set_ec_defaults(tok, dm)
    prune(tok, dm)          # delete any Canvas group/assignment/page/module not in the plan
    save_dm(dm)
    print(f"\ndeploy map: build/deploy.fall-2026.json ({len(dm['groups'])} groups, "
          f"{len(dm['assignments'])} assignments, {len(dm['pages'])} pages, {len(dm['modules'])} modules)")


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true",
                    help="mirror course.json to Canvas (create/update in plan, prune the rest)")
if parser.parse_args().apply:
    print(f"\nAPPLY -> Canvas course {COURSE_ID} (mirror)\n")
    apply()
