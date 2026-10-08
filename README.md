# sanjanamaini.github.io

Static portfolio site, generated from one content file per project.

- `content/site.json`: home page text, contact links, the Google Analytics measurement ID (`ga_measurement_id`, empty until set).
- `content/projects/*.json`: one file per project page (finding, question, data, method, figure, limits, checks).
- `python3 build.py`: rebuilds every page. Each number on a page is listed under `checks` and compared with the project repo's results file (the repos sit next to this one in `GitHub/`); the build stops if one no longer matches. `--cards` also renders the 1200x630 link-preview cards (needs Google Chrome); `--no-verify` skips the checks.
- `assets/`: stylesheet, scripts and figures. Generated pages (`index.html`, `<project>/index.html`, `links/`, `og/`, `sitemap.xml`) are committed because GitHub Pages serves them as they are.

Tagged links for the job search: `/links/` builds them (`utm_source`, `utm_medium`, `utm_campaign`).
