#!/usr/bin/env python3
"""Generate course markdown from data/course.json using Jinja2 templates.

course.json is the single source of truth. This renders:
  weekly/week-NN.md, topic-exams/<topic>/online-assessment.md,
  topic-exams/<topic>/live-performance-exam.md

Derived weekly sections ("This week", "Online Assessment from last week") are
reconstructed here from `schedule` + `oas` -- they are NOT stored in the JSON.
"""
import json, os, re
from jinja2 import Environment, FileSystemLoader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, "build", "templates")

with open(os.path.join(ROOT, "data", "course.json"), encoding="utf-8") as f:
    C = json.load(f)

TOPIC = {t["id"]: t for t in C["topics"]}
OA_BY_TOPIC = {o["topic"]: o for o in C["oas"]}
SCHED_BY_WEEK = {s["week"]: s for s in C["schedule"] if "week" in s}
# week number -> topic whose OA is assigned that week (for "OA from last week")
OA_WEEK = {s["week"]: p["topic"]
           for s in C["schedule"] if "week" in s
           for p in s.get("performance", []) if p.get("type") == "oa"}

PLACEMENT_ORDER = [("class", "Class"), ("class1", "Class 1"),
                   ("class2", "Class 2"), ("outside", "Outside of Class")]

# reminder/ref rendering for the "This week" list
REF = {
    "professional-mock": {"label": "professional mock",
                          "link": "../mock-interviews/linkedin-outreach.md"},
    "instructor-interview": {"label": "instructor interview",
                             "link": "../fix-your-timezone.md"},
    "connect-with-class": {"label": "Connect with class"},  # plain text, no link
}


def render_item(it):
    """`[name](url) notes *(tag)*` with every part optional."""
    parts = []
    if it.get("name"):
        parts.append(f"[{it['name']}]({it['url']})")
    if it.get("notes"):
        parts.append(it["notes"])
    s = " ".join(parts)
    if it.get("tag"):
        s = (s + " " if s else "") + f"*({it['tag']})*"
    return s


def this_week_lines(week):
    s = SCHED_BY_WEEK.get(week, {})
    out = []
    for p in s.get("performance", []):
        t = p.get("type")
        if t == "peer-mock":
            out.append("📅 [Peer Mock](../mock-interviews/README.md)")
        elif t == "oa":
            tp = TOPIC[p["topic"]]
            out.append(f"🖥️ [{tp['label']} Online Assessment]"
                       f"(../topic-exams/{tp['id']}/online-assessment.md)")
        elif t == "performance":
            tp = TOPIC[p["topic"]]
            out.append(f"📅 [{tp['label']} Performance]"
                       f"(../topic-exams/{tp['id']}/live-performance-exam.md)")
        elif t == "live-interview":
            out.append(f"📅 [Live Interview {p['index']}]"
                       "(../topic-exams/live-interview-exam.md)")
        elif t == "professional-mock":
            out.append("📅 [Professional Mock](../mock-interviews/linkedin-outreach.md)")
    for o in s.get("other", []):
        if o.get("type") == "reading":
            out.append(f"📖 {o['label']}")
        elif o.get("type") == "reminder" and o.get("action") == "schedule":
            r = REF[o["ref"]]
            out.append(f"📅 Schedule your [{r['label']}]({r['link']})")
        elif "ref" in o:
            r = REF[o["ref"]]
            out.append(r["label"] if "link" not in r
                       else f"[{r['label']}]({r['link']})")
    return out


def prev_oa_problems(week):
    topic = OA_WEEK.get(week - 1)
    if not topic:
        return None
    oa = OA_BY_TOPIC[topic]
    return [p for a in oa["attempts"] for p in a["problems"]]


env = Environment(loader=FileSystemLoader(TPL), trim_blocks=True, lstrip_blocks=True,
                  keep_trailing_newline=True)
env.filters["item"] = render_item


def normalize(text):
    """Collapse 3+ blank lines to one, strip trailing ws, end with single newline."""
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.rstrip() + "\n"


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(normalize(text))
    print("wrote", path)


# ---- weeks ----
wk_tpl = env.get_template("week.md.j2")
for w in C["weeks"]:
    placements = [(label, w["placements"][key])
                  for key, label in PLACEMENT_ORDER if key in w["placements"]]
    write(f"weekly/week-{w['week']:02d}.md", wk_tpl.render(
        w=w, placements=placements,
        prev_oa=prev_oa_problems(w["week"]),
        journaling=C["static"]["journalingPrompt"],
        this_week=this_week_lines(w["week"]),
        objectives=w.get("objectives", [])))

# ---- OAs ----
oa_tpl = env.get_template("oa.md.j2")
for oa in C["oas"]:
    write(f"topic-exams/{oa['topic']}/online-assessment.md",
          oa_tpl.render(oa=oa, topic=TOPIC[oa["topic"]]))

# ---- performance ----
perf_tpl = env.get_template("performance.md.j2")
for p in C["performance"]:
    write(f"topic-exams/{p['topic']}/live-performance-exam.md",
          perf_tpl.render(q=p["question"], topic=TOPIC[p["topic"]],
                          objectives=p.get("objectives", [])))

print("done")
