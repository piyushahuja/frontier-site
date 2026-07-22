# Frontier site

Static site, content-driven. **Edit the files in `data/`, never edit `index.html` by hand.**

## To change content
1. Edit a file in `data/`:
   - `meta.yaml` — name, tagline, eyebrow, hero line, contact email, `noindex`
   - `manifesto.md` — the manifesto prose (`*word*` = italic accent; `%% lead` / `%% statement` mark the intro line and the pull-quote)
   - `series.yaml` — lecture-series text + the six tracks
   - `speakers.yaml` — the speaker calendar (one block per speaker)
   - `projects.yaml` — live projects + the timeline ladder
   - `people.yaml` — organisers / advisors / friends + supporters
2. Rebuild:
   ```
   python3 code/build.py
   ```
3. Open `index.html` to check, then deploy.

## Speaker photos
Drop a square headshot at `assets/speakers/<name>.jpg` — e.g. `ashish-kapoor.jpg`
(lowercase, hyphenated). Missing photos fall back to initials automatically.

## Deploy
Drag the whole `frontier-site` folder onto https://app.netlify.com/drop.
Remove `noindex: true` from `meta.yaml` (and rebuild) when ready to go public.

`institutional.html` and `mockups/` are alternate designs kept for reference —
exclude them from the public deploy if you want a clean folder.
