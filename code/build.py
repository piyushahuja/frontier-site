#!/usr/bin/env python3
"""
Frontier site builder.

Edit the content files in ../data/ and run:  python3 build.py
It regenerates ../index.html from the design in ../code/. Never edit index.html
by hand — your changes are overwritten on the next build.

Content lives in data/:
  meta.yaml       name, title, eyebrow, hero headline + lede, nav, password, noindex
  manifesto.md    the manifesto prose (format notes below)
  series.yaml     talks lead/body + the six tracks (name + body)
  speakers.yaml   the schedule (one block per event)
  projects.yaml   projects prose + the timeline steps
  people.yaml     supporters (name, aff, url) — the rising bubbles in the footer

Design lives in code/:
  template.html   page shell, CSS, and the supporter animation
  figure.html     the hand-built data-figure (an infographic); its numbers are
                  content-adjacent — edit them there, they are not in data/.

manifesto.md format:
  - Blank-line-separated paragraphs.
  - "%% lead"   marks the next paragraph as the large serif intro line.
  - "%% pull"   marks the next block as the pull-quote:
        first line(s) = the quote, a line starting with "—" = the attribution.
  - "%% figure" drops the data-figure (code/figure.html) in at that point.
  - *asterisks* -> italic accent (<em>); **double** -> bold (<strong>).
  - Every other paragraph flows into a .prose block automatically.
"""
import os, re, html
import yaml

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
CODE = os.path.join(BASE, "code")
OUT  = os.path.join(BASE, "index.html")


def load_yaml(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_data(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return f.read()


def read_code(name):
    with open(os.path.join(CODE, name), encoding="utf-8") as f:
        return f.read()


def fmt(s):
    """Escape HTML, then *emphasis* -> <em>, **strong** -> <strong>."""
    s = html.escape(str(s), quote=False)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    return s


def fmt_breaks(s):
    return fmt(s).replace("\n", "<br>")


def js_str(s):
    """Escape a value for use inside a single-quoted JS string literal."""
    s = str(s).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
    return s.replace("</", "<\\/")   # never let content close the <script>


# ---- nav -------------------------------------------------------------------
def build_nav(links):
    return "\n".join(
        '    <a href="%s">%s</a>' % (html.escape(l["href"]), fmt(l["label"]))
        for l in links
    )


# ---- manifesto -------------------------------------------------------------
def build_manifesto(text, figure_html):
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    out, prose = [], []

    def flush_prose():
        if prose:
            paras = "".join("    <p>%s</p>\n" % fmt(p) for p in prose)
            out.append('  <div class="prose">\n%s  </div>' % paras)
            prose.clear()

    pending = None
    for b in blocks:
        role, body = None, b
        if b.lstrip().startswith("%%"):
            first, _, rest = b.partition("\n")
            role = first.strip()[2:].strip().lower()
            body = rest.strip()
            if not body:                 # marker alone -> applies to the next block
                if role == "figure":     # ...except the figure, which has no body
                    flush_prose()
                    out.append(figure_html.rstrip("\n"))
                    continue
                pending = role
                continue
        elif pending:
            role, pending = pending, None

        if role == "lead":
            flush_prose()
            out.append('  <p class="lead-serif">%s</p>' % fmt(body))
        elif role == "pull":
            flush_prose()
            lines = [l for l in body.splitlines() if l.strip()]
            quote = " ".join(l for l in lines if not l.lstrip().startswith("—"))
            attr = next((l.lstrip("— ").strip() for l in lines
                         if l.lstrip().startswith("—")), "")
            out.append(
                '  <div class="pull">\n'
                '    <div class="s">%s</div>\n'
                '    <div class="t">%s</div>\n'
                '  </div>' % (fmt(quote), fmt(attr))
            )
        else:
            prose.append(body)
    flush_prose()
    return "\n".join(out)


# ---- schedule --------------------------------------------------------------
def build_speakers(events):
    rows = []
    for e in events:
        ev_cls = "ev tbd" if e.get("tbd") else "ev"
        cal_cls = "cal nodate" if e.get("nodate") else "cal"
        track = e.get("track", "")
        # Only emit the track cell when set; the fixed grid keeps the column
        # aligned for rows without one, and no empty cell clutters mobile.
        trk = ('\n      <div class="trk">%s</div>' % fmt(track)) if track else ""
        rows.append(
            '    <div class="%s">\n'
            '      <div class="%s"><span class="day">%s</span><span class="mon">%s</span></div>\n'
            '      <div class="who"><b>%s</b>%s</div>%s\n'
            '    </div>'
            % (ev_cls, cal_cls, fmt(e["day"]), fmt(e.get("mon", "")),
               fmt(e["name"]), fmt(e.get("detail", "")), trk)
        )
    return "\n".join(rows)


# ---- projects prose + timeline ---------------------------------------------
def para_to_html(p):
    """Convert a prose paragraph to HTML, handling `* bullet` lists."""
    lines = p.split('\n')
    if any(l.startswith('* ') for l in lines):
        first_bullet = next(i for i, l in enumerate(lines) if l.startswith('* '))
        intro = ' '.join(lines[:first_bullet]).strip()
        bullets = [l[2:] for l in lines if l.startswith('* ')]
        parts = []
        if intro:
            parts.append('    <p>%s</p>' % fmt(intro))
        items = '\n'.join('      <li>%s</li>' % fmt(b) for b in bullets)
        parts.append('    <ul>\n%s\n    </ul>' % items)
        return '\n'.join(parts)
    return '    <p>%s</p>' % fmt(p)


def build_prose(paras):
    return "\n".join(para_to_html(p) for p in paras)


def build_timeline(steps):
    nodes = []
    for s in steps:
        cls = "node dest" if s.get("dest") else "node"
        nodes.append(
            '      <div class="%s">\n'
            '        <div class="yr">%s</div>\n'
            '        <div class="t">%s</div>\n'
            '        <div class="d">%s</div>\n'
            '      </div>' % (cls, fmt(s["year"]), fmt(s["title"]), fmt(s["desc"]))
        )
    return "\n".join(nodes)


# ---- supporters (injected into the footer animation) -----------------------
def build_supporters(supporters):
    rows = []
    for s in supporters:
        rows.append(
            "    { name: '%s', aff: '%s', url: '%s' }"
            % (js_str(s["name"]), js_str(s["aff"]), js_str(s["url"]))
        )
    return ",\n".join(rows)


# ---- main ------------------------------------------------------------------
def main():
    meta = load_yaml("meta.yaml")
    series = load_yaml("series.yaml")
    speakers = load_yaml("speakers.yaml")
    projects = load_yaml("projects.yaml")
    people = load_yaml("people.yaml")

    figure_html = read_code("figure.html")
    tpl = read_code("template.html")

    repl = {
        "{{ROBOTS}}": '<meta name="robots" content="noindex">' if meta.get("noindex") else "",
        "{{TITLE}}": fmt(meta.get("title", meta["name"])),
        "{{GATE_LABEL}}": fmt(meta.get("gate_label", "")),
        "{{PASSWORD}}": js_str(meta.get("password", "")),
        "{{NAV}}": build_nav(meta.get("nav", [])),
        "{{EYEBROW}}": fmt(meta["eyebrow"]),
        "{{HERO_HEADLINE}}": fmt_breaks(meta["hero_headline"]),
        "{{HERO_LEDE}}": fmt(meta["hero_lede"]),
        "{{MANIFESTO}}": build_manifesto(read_data("manifesto.md"), figure_html),
        "{{SERIES_LEAD}}": fmt(series["lead"]),
        "{{SERIES_BODY}}": fmt(series["body"]),
        "{{SPEAKERS}}": build_speakers(speakers),
        "{{PROJECTS_PROSE}}": build_prose(projects["prose"]),
        "{{TIMELINE_TITLE}}": fmt(projects["timeline"]["title"]),
        "{{TIMELINE_INTRO}}": fmt(projects["timeline"]["intro"]),
        "{{TIMELINE_STEPS}}": build_timeline(projects["timeline"]["steps"]),
        "{{FIGURE}}": figure_html.rstrip("\n"),
        "{{SUPPORTERS}}": build_supporters(people["supporters"]),
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(tpl)
    print("Built index.html  (%d bytes)" % len(tpl))


if __name__ == "__main__":
    main()
