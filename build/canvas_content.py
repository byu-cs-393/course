#!/usr/bin/env python3
"""Render course markdown into Canvas HTML (assignment descriptions, pages, syllabus).

Assignment descriptions are TAILORED per assignment: the relevant content, then a
fill-in submission template (a greyed code block) telling the student exactly what
to submit. Internal .md links resolve to real Canvas objects via `link_map`
(else GitHub blob). Headings get extra top margin so sections breathe in Canvas.
"""
import os, re, posixpath, markdown

REPO_BLOB = "https://github.com/byu-cs-393/course/blob/main/"


def _read(root, path):
    with open(os.path.join(root, path), encoding="utf-8") as f:
        return f.read()


def _resolve(src_path, target, link_map):
    if target.startswith(("http://", "https://", "#", "mailto:")):
        return None
    path, _, anchor = target.partition("#")
    if not path:
        return None
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(src_path), path))
    base = (link_map or {}).get(resolved, REPO_BLOB + resolved)
    return base + (("#" + anchor) if anchor else "")


def _rewrite_links(md, src_path, link_map=None):
    def inline(m):
        url = _resolve(src_path, m.group(1).strip(), link_map)
        return f"]({url})" if url else m.group(0)

    def ref(m):
        url = _resolve(src_path, m.group(2).strip(), link_map)
        return m.group(1) + url if url else m.group(0)

    md = re.sub(r"\]\(([^)]+)\)", inline, md)
    md = re.sub(r"(?m)^(\[[^\]]+\]:\s*)(\S+)", ref, md)
    return md


def _to_html(md_text):
    html = markdown.markdown(md_text, extensions=["extra", "sane_lists"])
    html = html.replace("<h2>", '<h2 style="margin-top:1.6em">')   # let sections breathe
    html = html.replace("<h3>", '<h3 style="margin-top:1.2em">')
    return html


def _strip_h1(md):
    return re.sub(r"^#\s+.*\n", "", md, count=1)


def render_file(root, path, strip_h1=False, link_map=None):
    md = _read(root, path)
    if strip_h1:
        md = _strip_h1(md)
    return _to_html(_rewrite_links(md, path, link_map))


def _slug(s):
    s = re.sub(r"[^\w\s-]", "", s.lower())
    return re.sub(r"-+", "-", re.sub(r"\s+", "-", s.strip()))


def _section_md(root, path, anchor):
    out, grab = [], False
    for ln in _read(root, path).splitlines():
        h = re.match(r"^##\s+(.*)", ln)
        if h:
            if grab:
                break
            if _slug(h.group(1)) == anchor:
                grab = True
            continue
        if grab:
            out.append(ln)
    return "\n".join(out).strip()


def render_section(root, path, anchor, link_map=None):
    return _to_html(_rewrite_links(_section_md(root, path, anchor), path, link_map))


def page_html(root, source, link_map=None):
    return render_file(root, source, strip_h1=True, link_map=link_map)


def syllabus_html(root, link_map=None):
    return render_file(root, "syllabus.md", strip_h1=True, link_map=link_map)


# ---------------------------------------------------------------- descriptions
def _block(title, lines):
    return f"**{title}**\n\n```\n" + "\n".join(lines) + "\n```"


def _booking_ta():
    return "📅 **Book a time with a TA** — the TA booking links are in the course syllabus."


def _connect_content(a):
    url = a.get("teamsUrl", "")
    join = f" ([join]({url}))" if url else ""
    return ("Get connected with the class. Do each step, then fill in the template below.\n\n"
            f"- **Join** the class Microsoft Teams team{join}\n"
            "- **Update your profile picture** to one that looks like you\n"
            "- **Post an intro** in the **networking-and-jobs** channel: who you are, your career "
            "interests, and any past CS-related jobs\n"
            "- **React** (emoji or a reply) to **3** classmates' intros\n"
            "- **Direct-message** at least **1** classmate to set up a mock interview (online or in person)\n"
            "- **Share your LeetCode profile URL** below")


def _content_md(root, a, assign_by_id, ctx):
    """(markdown, src_path) for the content above the template."""
    typ, aid = a["type"], a["id"]
    if typ == "oa":
        src = f"topic-exams/{aid[3:]}/online-assessment.md"
        return _strip_h1(_read(root, src)), src
    if typ == "performance":
        src = f"topic-exams/{aid[5:]}/live-performance-exam.md"
        return _strip_h1(_read(root, src)), src
    if typ == "live-interview":
        src = "topic-exams/live-interview-exam.md"
        return _strip_h1(_read(root, src)), src
    if typ in ("peer-mock", "professional-mock"):
        src = "mock-interviews/README.md"
        return _strip_h1(_read(root, src)), src
    if typ == "final":
        return _strip_h1(_read(root, "final/README.md")), "final/README.md"
    if typ == "study":
        reduced = a.get("week") in ctx.get("reducedWeeks", set())
        target = ("**~4.5 hours** — this is a half week, so everything is at half load"
                  if reduced else "**~9 hours** (class counts as 3)")
        return (f"Log your study for the week — target {target}. "
                "Paste the URL of your *accepted* LeetCode submission (open the problem → "
                "**Submissions** → your accepted attempt → copy the address) after each problem below."), ""
    if typ == "connect-with-class":
        return _connect_content(assign_by_id.get(aid, {})), ""
    if typ == "instructor-interview":
        book = ctx.get("booking", {}).get("instructor", "")
        book_line = f"\n\n📅 **Book your interview:** [{book}]({book})" if book else ""
        return ("**Required to pass the course.** A live interview with the instructor on a random "
                "topic from what we've covered. Be caught up on your topic exams and have passed at "
                "least one performance exam first. If you don't pass, learn, practice, and try again "
                "until you do." + book_line), ""
    aj = assign_by_id.get(aid, {})
    doc = aj.get("doc", "")
    if "#" in doc:
        f, anchor = doc.split("#", 1)
        return _section_md(root, f, anchor), f
    if aj.get("desc"):
        return aj["desc"], ""
    return "", ""


def _template_md(a):
    """The fill-in submission template (greyed code block), or '' for none."""
    typ, aid = a["type"], a["id"]
    if typ == "oa":
        return _block("Submit this:", [
            "Attempt you passed (1 / 2 / 3):",
            "Accepted-solution URLs for every problem in that attempt:",
            "  - ", "  - ", "  - "])
    if typ == "performance":
        return _booking_ta() + "\n\n" + _block("Submit this:", [
            "Date you did it:",
            "Who you worked with (TA / instructor):",
            "How long it took:",
            "Attempt you passed on:",
            "Link to your passing solution:"])
    if typ == "live-interview":
        return _booking_ta() + "\n\n" + _block("Submit this:", [
            "Date you did it:",
            "How it went (a few sentences):",
            "Self-rating (1-3):",
            "Link to your solution:"])
    if typ in ("peer-mock", "professional-mock"):
        return _block("Submit this:", [
            "Who you interviewed with:",
            "When:",
            "Problem(s) you worked on:",
            "Feedback you received:",
            "Self-rating (1-3):"])
    if typ == "instructor-interview":
        return _block("Submit this:", [
            "Date you did it:",
            "Link to your passing solution:",
            "How did it go?"])
    if typ == "connect-with-class":
        return _block("Submit this:", [
            "Joined Teams: (Did it! / Not yet — why?)",
            "Updated my photo: (Did it! / Not yet — why?)",
            "Posted my intro: (Did it! / Not yet — why?)",
            "Reacted to 3 intros: (Did it! / Not yet — why?)",
            "DM'd a classmate for a mock: (Did it! / Not yet — why?)",
            "My LeetCode profile URL:",
            "How I plan to connect with others and network this semester:"])
    if aid == "ec-interview-ready":
        return _block("Submit this:", [
            "All categories green? (Yes / No)",
            "Total problems solved:",
            "Anything you learned using the extension:"])
    if aid.startswith("ec-real-interview-report"):
        return _block("Post this in the \"Real Interview\" Teams channel, then paste it here:", [
            "Where did you interview?",
            "What types of questions were you asked?",
            "How was your experience? Would you recommend them?"])
    if aid.startswith("ec-real-offer-report"):
        return _block("Post this in the \"Real Offer\" Teams channel, then paste it here:", [
            "What did you do to prepare?",
            "Who did you network with to get the interview/job?",
            "Tips for others:",
            "Was the offer over 50k/yr?   Full-time / Internship / Other:",
            "Did it meet your expectations? (1 = no … 10 = perfectly):"])
    if aid == "ec-friend-interview":
        return _block("Post this in the networking channel, then paste it here:", [
            "Friend's full name:",
            "Where they interviewed:",
            "How you helped them get the interview:"])
    if aid == "ec-friend-offer":
        return _block("Post this in the networking channel, then paste it here:", [
            "Friend's full name:",
            "Where they got the offer:",
            "How you helped them get the offer:"])
    if typ == "study":
        req, inclass = (a.get("_weekly") or ([], []))
        lines = ["Required problems (paste your accepted-submission URL after each):"]
        lines += [f"  - {r}: " for r in (req or ["(none assigned this week)"])]
        if inclass:
            lines.append("In-class problems (URL or \"done in class\"):")
            lines += [f"  - {r}: " for r in inclass]
        lines += ["Collaborative study: __ hrs (with whom?)",
                  "Personal study: __ hrs",
                  "For growth I (mark any): re-timed myself / re-did without lookups /",
                  "  studied others' solutions after / just finished / other:",
                  "Want a TA to review a solution? If yes, paste the submission link below:"]
        return _block("Submit this:", lines)
    return ""   # amazing projects (URL submission), final (no submission)


def description_html(root, a, assign_by_id, link_map=None, ctx=None):
    ctx = ctx or {}
    if a["type"] == "study":                       # attach this week's problems for the template
        a = dict(a, _weekly=ctx.get("weeklyProblems", {}).get(a.get("week")))
    content, src = _content_md(root, a, assign_by_id, ctx)
    template = _template_md(a)
    md = "\n\n".join(p for p in (content, template) if p)
    return _to_html(_rewrite_links(md, src, link_map))
