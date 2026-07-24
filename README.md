# Frontier site

Static, content-driven site. The page you deploy — `index.html` — is **generated**
from the content in `data/` and the design in `code/`. **Never edit `index.html`
by hand; the next build overwrites it.**

```
data/            content you edit (prose, lists, settings)
code/template.html   page shell, CSS, supporter animation
code/figure.html     the hand-built data-figure (an infographic)
code/build.py        assembles data/ + code/ -> index.html
index.html       generated output — commit it, it is what gets served
```

## To change content
1. Edit a file in `data/`:
   - `meta.yaml` — name, title, eyebrow, hero headline + lede, nav links, gate password, `noindex`
   - `manifesto.md` — the manifesto prose (`*word*` = italic, `**word**` = bold; `%% lead` = intro line, `%% pull` = pull-quote, `%% figure` = drops in the data-figure)
   - `series.yaml` — Talks lead/body + the six tracks (`name` + `body`)
   - `speakers.yaml` — the schedule (one block per event; `nodate: true` for a month-only slot, `tbd: true` to dim a placeholder)
   - `projects.yaml` — projects prose paragraphs + the timeline steps (`dest: true` marks the final node)
   - `people.yaml` — supporters (`name`, `aff`, `url`) — the rising bubbles in the footer
2. Rebuild:
   ```
   python3 code/build.py
   ```
3. Open `index.html` to check, commit it, then deploy.

The data-figure (the "1 in 7" infographic and capital-flow bars) is a hand-built
illustration; its numbers live in `code/figure.html`, next to the SVG geometry
they must stay consistent with. Edit them there.

## Deploy
`index.html` is served as-is (see `netlify.toml`) — Netlify does **not** run the
build. So always run `python3 code/build.py` and commit the regenerated
`index.html` before deploying. Remove `noindex: true` from `meta.yaml` (and
rebuild) when ready to go public.

`institutional.html` and `mockups/` are alternate designs kept for reference —
exclude them from the public deploy if you want a clean folder.
