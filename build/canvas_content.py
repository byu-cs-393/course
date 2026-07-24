#!/usr/bin/env python3
"""Render course markdown into Canvas HTML (assignment descriptions, pages, syllabus).

Internal repo links (relative .md) resolve to real Canvas objects when a `link_map`
(repo path -> Canvas URL, from the deploy map) is supplied; otherwise they fall back
to GitHub blob URLs on the public course repo. Absolute links are left untouched.
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
    base = (link_map or {}).get(resolved, REPO_BLOB + resolved)   # Canvas link or GitHub blob
    return base + (("#" + anchor) if anchor else "")


def _rewrite_links(md, src_path, link_map=None):
    def inline(m):
        url = _resolve(src_path, m.group(1).strip(), link_map)
        return f"]({url})" if url else m.group(0)

    def ref(m):
        url = _resolve(src_path, m.group(2).strip(), link_map)
        return m.group(1) + url if url else m.group(0)

    md = re.sub(r"\]\(([^)]+)\)", inline, md)              # inline [x](url)
    md = re.sub(r"(?m)^(\[[^\]]+\]:\s*)(\S+)", ref, md)    # reference [x]: url
    return md


def _to_html(md_text):
    return markdown.markdown(md_text, extensions=["extra", "sane_lists"])


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


def render_section(root, path, anchor, link_map=None):
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
    return _to_html(_rewrite_links("\n".join(out).strip(), path, link_map))


def description_html(root, a, assign_by_id, link_map=None):
    """HTML description for a plan assignment (dict with id, type)."""
    typ, aid = a["type"], a["id"]
    if typ == "oa":
        return render_file(root, f"topic-exams/{aid[3:]}/online-assessment.md", True, link_map)
    if typ == "performance":
        return render_file(root, f"topic-exams/{aid[5:]}/live-performance-exam.md", True, link_map)
    if typ == "live-interview":
        return render_file(root, "topic-exams/live-interview-exam.md", True, link_map)
    if typ in ("peer-mock", "professional-mock"):
        return render_file(root, "mock-interviews/README.md", True, link_map)
    if typ == "study":
        return render_file(root, "weekly/README.md", True, link_map)
    if typ == "final":
        return render_file(root, "final/README.md", True, link_map)
    aj = assign_by_id.get(aid, {})
    doc = aj.get("doc", "")
    if "#" in doc:
        f, anchor = doc.split("#", 1)
        return render_section(root, f, anchor, link_map)
    if aj.get("desc"):
        return _to_html(_rewrite_links(aj["desc"], "", link_map))   # inline md + links
    return ""


def page_html(root, source, link_map=None):
    return render_file(root, source, strip_h1=True, link_map=link_map)


def syllabus_html(root, link_map=None):
    return render_file(root, "syllabus.md", strip_h1=True, link_map=link_map)
