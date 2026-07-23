#!/usr/bin/env python3
"""
Frontier site builder.

Edit the plain-text files in ../data/ and run:  python3 build.py
It regenerates ../index.html from ../code/template.html. Never edit index.html by hand.

Data files:
  data/meta.yaml       site name, tagline, eyebrow, hero line, contact email, noindex
  data/manifesto.md    the manifesto prose (see format notes below)
  data/series.yaml     lecture-series lead/body + the six tracks
  data/speakers.yaml   the speaker calendar (one block per speaker)
  data/projects.yaml   live projects + the timeline ladder
  data/people.yaml     organisers / advisors / friends + supporters

manifesto.md format:
  - Blank-line-separated paragraphs.
  - A line "%% lead" marks the next paragraph as the large intro line.
  - A line "%% statement" marks the next block as the pull-quote:
        first line = the quote, a line starting with "—" = the attribution.
  - Wrap emphasis in *asterisks* -> renders italic accent, e.g. *atmanirbharta*.
  - Every other paragraph flows into the two-column body automatically.
"""
import os, re, html, sys, random
import yaml

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
CODE = os.path.join(BASE, "code")
OUT  = os.path.join(BASE, "index.html")

ROMAN = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]


def load_yaml(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return yaml.safe_load(f)


def read(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return f.read()


def fmt(s):
    """Escape HTML, then turn *emphasis* into <em>…</em>."""
    s = html.escape(str(s), quote=False)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    return s


def fmt_breaks(s):
    return fmt(s).replace("\n", "<br>")


def slugify(name):
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def initials(name):
    parts = [p for p in re.split(r"\s+", name) if p]
    letters = [p[0] for p in parts[:2]]
    return "".join(letters).upper()


# ---- tracks ----------------------------------------------------------------
def build_tracks(tracks):
    cells = []
    for t in tracks:
        if isinstance(t, str):          # legacy: bare label
            t = {"name": t}
        name = fmt(t["name"])
        who = fmt(t.get("who", ""))
        covers = fmt(t.get("covers", ""))
        parts = ['      <div class="tname">%s</div>' % name]
        if who:
            parts.append('      <div class="twho">%s</div>' % who)
        if covers:
            parts.append('      <div class="tcov"><b>Covers</b> %s</div>' % covers)
        cells.append('    <div class="track">\n%s\n    </div>' % "\n".join(parts))
    return "\n".join(cells)


# ---- manifesto -------------------------------------------------------------
def build_manifesto(text):
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    out, cols = [], []

    def flush_cols():
        if cols:
            paras = "".join("    <p>%s</p>\n" % fmt(p) for p in cols)
            out.append('  <div class="cols">\n%s  </div>' % paras)
            cols.clear()

    pending = None
    for b in blocks:
        role, body = None, b
        if b.lstrip().startswith("%%"):
            first, _, rest = b.partition("\n")
            role = first.strip()[2:].strip().lower()
            body = rest.strip()
            if not body:            # marker alone -> applies to the next block
                pending = role
                continue
        elif pending:
            role, pending = pending, None

        if role == "lead":
            flush_cols()
            out.append('  <p class="lead-serif">%s</p>' % fmt(body))
        elif role == "statement":
            flush_cols()
            lines = [l for l in body.splitlines() if l.strip()]
            quote = " ".join(l for l in lines if not l.lstrip().startswith("—"))
            attr = next((l.lstrip("— ").strip() for l in lines
                         if l.lstrip().startswith("—")), "")
            out.append(
                '  <div class="statement">\n'
                '    <div class="s" style="font-style:italic">%s</div>\n'
                '    <div class="t">%s</div>\n'
                '  </div>' % (fmt(quote), fmt(attr))
            )
        else:
            cols.append(body)
    flush_cols()
    return "\n".join(out)


# ---- speakers --------------------------------------------------------------
def build_speakers(speakers):
    rows = []
    for s in speakers:
        date = fmt(s.get("date", ""))
        day = fmt(s.get("day", "") or "")
        name = fmt(s["name"])
        bio = fmt(s.get("bio", ""))
        cls = "sp tbd" if s.get("tbd") else "sp"
        rows.append(
            '    <div class="%s">\n'
            '      <div class="date"><b>%s</b>%s</div>\n'
            '      <div class="who"><b>%s</b><div>%s</div></div>\n'
            '    </div>' % (cls, date, day, name, bio)
        )
    return "\n".join(rows)


# ---- projects + timeline ---------------------------------------------------
def build_projects(projects):
    cards = []
    for p in projects:
        cards.append(
            '    <div class="p"><h3>%s</h3><p>%s</p></div>'
            % (fmt(p["name"]), fmt(p["body"]))
        )
    return "\n".join(cards)


def build_ladder(steps):
    return "\n".join(
        '    <div><div class="yr">%s</div><div class="t">%s</div></div>'
        % (fmt(s["year"]), fmt(s["label"])) for s in steps
    )


# ---- people ----------------------------------------------------------------
def build_people(groups):
    members = []
    for g in groups:
        members.extend(g.get("members", []))

    random.shuffle(members)
    chips = []
    for m in members:
        name = fmt(m["name"])
        sub = fmt(m.get("sub", ""))
        chips.append(
            '    <span class="supporter-chip">%s<span class="tooltip">%s</span></span>' % (name, sub)
        )
    return "\n".join(chips)


def build_logos(supporters):
    n = int(supporters.get("logos", 0))
    return "".join('<div class="slot">logo</div>' for _ in range(n))


# ---- main ------------------------------------------------------------------
def main():
    meta = load_yaml("meta.yaml")
    series = load_yaml("series.yaml")
    speakers = load_yaml("speakers.yaml")
    projects = load_yaml("projects.yaml")
    people = load_yaml("people.yaml")

    with open(os.path.join(CODE, "template.html"), encoding="utf-8") as f:
        tpl = f.read()

    repl = {
        "{{ROBOTS}}": '<meta name="robots" content="noindex">' if meta.get("noindex") else "",
        "{{TITLE}}": fmt(meta.get("title", meta["name"])),
        "{{NAME}}": fmt(meta["name"]),
        "{{EYEBROW}}": fmt(meta["eyebrow"]),
        "{{TAGLINE}}": fmt_breaks(meta["tagline"]),
        "{{HERO_LEDE}}": fmt(meta["hero_lede"]),
        "{{MANIFESTO}}": build_manifesto(read("manifesto.md")),
        "{{SERIES_LEAD}}": fmt(series["lead"]),
        "{{SERIES_BODY}}": fmt(series["body"]),
        "{{TRACKS}}": build_tracks(series["tracks"]),
        "{{SPEAKERS}}": build_speakers(speakers),
        "{{PROJECTS}}": build_projects(projects["projects"]),
        "{{TIMELINE_TITLE}}": fmt(projects["timeline"]["title"]),
        "{{TIMELINE_INTRO}}": fmt(projects["timeline"]["intro"]),
        "{{LADDER}}": build_ladder(projects["timeline"]["steps"]),
        "{{PEOPLE}}": build_people(people["groups"]),
        "{{SUPPORTERS_LABEL}}": fmt(people["supporters"]["label"]),
        "{{SUPPORTERS_LOGOS}}": build_logos(people["supporters"]),
        "{{FOOTER_LEFT}}": fmt(meta["footer_left"]),
        "{{EMAIL}}": fmt(meta["contact_email"]),
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(tpl)
    print("Built index.html  (%d bytes)" % len(tpl))


if __name__ == "__main__":
    main()
