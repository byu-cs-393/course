#!/usr/bin/env python3
"""Render course markdown into Canvas HTML (assignment descriptions, pages, syllabus).

Internal repo links (relative .md) are rewritten to GitHub blob URLs on the public
course repo, so they resolve for students. Absolute links are left untouched.
"""
import os, re, posixpath, html, markdown

REPO_BLOB = "https://github.com/byu-cs-393/course/blob/main/"


def _read(root, path):
    with open(os.path.join(root, path), encoding="utf-8") as f:
        return f.read()


def _blob(src_path, target):
    if target.startswith(("http://", "https://", "#", "mailto:")):
        return None
    path, _, anchor = target.partition("#")
    if not path:
        return None
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(src_path), path))
    return REPO_BLOB + resolved + (("#" + anchor) if anchor else "")


def _rewrite_links(md, src_path):
    def inline(m):
        url = _blob(src_path, m.group(1).strip())
        return f"]({url})" if url else m.group(0)

    def ref(m):
        url = _blob(src_path, m.group(2).strip())
        return m.group(1) + url if url else m.group(0)

    md = re.sub(r"\]\(([^)]+)\)", inline, md)              # inline [x](url)
    md = re.sub(r"(?m)^(\[[^\]]+\]:\s*)(\S+)", ref, md)    # reference [x]: url
    return md


def _to_html(md_text):
    return markdown.markdown(md_text, extensions=["extra", "sane_lists"])


def _strip_h1(md):
    return re.sub(r"^#\s+.*\n", "", md, count=1)


def render_file(root, path, strip_h1=False):
    md = _read(root, path)
    if strip_h1:
        md = _strip_h1(md)
    return _to_html(_rewrite_links(md, path))


def _slug(s):
    s = re.sub(r"[^\w\s-]", "", s.lower())
    return re.sub(r"-+", "-", re.sub(r"\s+", "-", s.strip()))


def render_section(root, path, anchor):
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
    return _to_html(_rewrite_links("\n".join(out).strip(), path))


def description_html(root, a, assign_by_id):
    """HTML description for a plan assignment (dict with id, type)."""
    typ, aid = a["type"], a["id"]
    if typ == "oa":
        return render_file(root, f"topic-exams/{aid[3:]}/online-assessment.md", strip_h1=True)
    if typ == "performance":
        return render_file(root, f"topic-exams/{aid[5:]}/live-performance-exam.md", strip_h1=True)
    if typ == "live-interview":
        return render_file(root, "topic-exams/live-interview-exam.md", strip_h1=True)
    if typ in ("peer-mock", "professional-mock"):
        return render_file(root, "mock-interviews/README.md", strip_h1=True)
    if typ == "study":
        return render_file(root, "weekly/README.md", strip_h1=True)
    if typ == "final":
        return render_file(root, "final/README.md", strip_h1=True)
    aj = assign_by_id.get(aid, {})
    doc = aj.get("doc", "")
    if "#" in doc:
        f, anchor = doc.split("#", 1)
        return render_section(root, f, anchor)
    if aj.get("desc"):
        return "<p>" + html.escape(aj["desc"]) + "</p>"
    return ""


def page_html(root, source):
    return render_file(root, source, strip_h1=True)


def syllabus_html(root):
    return render_file(root, "syllabus.md", strip_h1=True)
