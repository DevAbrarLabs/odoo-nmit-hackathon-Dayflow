# Dayflow HRMS — Admin Console (Python / Streamlit port)

A Python conversion of the static site (`index.html` + `styles.css` + `data.js` +
`app.js`) that keeps the **same design system** — ink navy sidebar, paper
background, sunrise-gold accent, Space Grotesk / Inter / IBM Plex Mono type,
cards, badges, the "workday arc" motif, and the dependency-free bar charts —
rebuilt on [Streamlit](https://streamlit.io) instead of hash-routing + DOM.

## Run it

```bash
pip install streamlit pandas
streamlit run dayflow_hrms.py
```

The `.streamlit/config.toml` next to the script sets Streamlit's theme
(background/accent/text colors) to match the site palette, and the script
itself injects the same Google Fonts + custom CSS as `styles.css` so cards,
tables, and badges render pixel-close to the original.

A `dayflow_store.json` file is created next to the script on first run —
the same seeded data (24 employees, 45 days of attendance, 10 leave
requests) that `loadStore()` used to write to `localStorage`. Use the
**"🔄 Reset demo data"** button in the sidebar to reseed (equivalent of
`resetStore()`).

## What carried over 1:1

- **Design tokens** — every color, radius, and shadow from `:root` in
  `styles.css` is reproduced as a Python constant and injected as CSS.
- **Typography** — Space Grotesk for headings/metrics, Inter for body,
  IBM Plex Mono for codes/timestamps/currency — same as the site.
- **The workday arc** — the sunrise→sunset SVG with a dot marking "now" is
  computed in Python (`workday_arc_svg()`) with the exact same geometry
  and appears in every page header, just like `workdayArcSVG()` did.
- **Bar charts, badges, tables** — rendered as real HTML (`.df-bar-*`,
  `.df-badge`, `.df-table`) with the original CSS classes' styling, not
  generic Streamlit widgets, so they look the same.
- **Seed-data generation & business rules** — same salary formula (HRA 40%,
  allowances 15%, deductions 8% of basic), same weighted attendance
  distribution (78/6/10/6%), same weekend-skipping.
- **All 7 admin pages**, same rules: Dashboard, Employee List (search/filter/add),
  Employee Details (edit profile, salary tab, history tab), Attendance
  Overview (filters + manual override), Leave Approvals (approve/reject +
  comment), Payroll Management (edit + salary-slip download), Analytics &
  Reports (charts + CSV export).

## What changed (by necessity, given the platform swap)

- **Routing** — hash-based `#/route/param` became a sidebar radio list,
  styled with CSS to resemble the original `.nav-item` list. Clicking an
  employee row now uses a "Open employee details for…" picker instead of
  a clickable `<tr>`, since Streamlit doesn't support per-row click
  handlers on server-rendered HTML without a custom component.
- **Persistence** — `localStorage` → a JSON file on disk (`dayflow_store.json`).
- **Toasts** — the sliding bottom-right toast became Streamlit's built-in
  `st.success` / `st.warning` inline confirmations.
- **Native form controls** (text inputs, selects, sliders, date pickers) are
  Streamlit's own widgets, retinted via the theme + a few CSS overrides —
  they won't be pixel-identical to the site's custom `<input>`/`<select>`
  styling, since Streamlit owns that markup.

## Files

| File                        | Purpose                                              |
|-----------------------------|-------------------------------------------------------|
| `dayflow_hrms.py`           | Data layer, design system CSS, all 7 pages, router    |
| `.streamlit/config.toml`    | Streamlit theme (palette) for native widgets          |
| `dayflow_store.json`        | Generated on first run — your persisted data          |
