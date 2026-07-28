# Arijit Nandi — Portfolio (Jekyll)

Personal site for [officialarijit.github.io](https://officialarijit.github.io), built with Jekyll.

## Local preview (Docker)

```bash
docker run --rm -it \
  -p 4000:4000 \
  -v "$(pwd):/srv/jekyll" \
  -w /srv/jekyll \
  jekyll/jekyll:4.2.2 \
  jekyll serve --host 0.0.0.0 --livereload
```

Open **http://localhost:4000**

## Build

```bash
bundle install
bundle exec jekyll build
```

Output: `_site/`

## Content

| Path | Purpose |
|------|---------|
| `_data/` | Site content (navigation, skills, projects, scholar metrics) |
| `_posts/` | Blog posts |
| `_includes/dossier/` | Homepage sections |
| `css/theme-dossier.css` | Site theme |
| `data/publications.json` | Publications (linked from `_data/publications.json`) |
| `citation.txt` | Google Scholar export (fallback input for `scripts/update_scholar.py`) |
| `publications.txt` | Optional Scholar publications HTML export (fallback for `scripts/update_publications.py`) |
| `scripts/` | Scholar update scripts (see below) |

## Google Scholar updates

Citation metrics and publications can be refreshed automatically or manually.

### Automatic (GitHub Actions)

`.github/workflows/update-scholar.yml` runs weekly (Mondays 06:00 UTC) and on manual dispatch. It:

1. Tries to fetch live data from Google Scholar via `scripts/fetch_scholar.py`
2. Falls back to parsing `citation.txt` / `publications.txt` if the fetch fails
3. Updates `_data/scholar.yml` and `data/publications.json`
4. Commits changes when data changes

Trigger manually: **Actions → Update Google Scholar data → Run workflow**.

### Local update

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/update_all.py
```

Fallback only (no live fetch):

```bash
python scripts/update_all.py --skip-fetch
```

Individual scripts:

```bash
python scripts/fetch_scholar.py              # live fetch → scholar.yml + publications.json
python scripts/update_scholar.py             # citation.txt → _data/scholar.yml
python scripts/update_publications.py        # publications.txt → data/publications.json
```

**Source of truth:** aggregate metrics in the About sidebar come from `_data/scholar.yml` (Google Scholar's official totals). Per-paper citation counts come from `data/publications.json`.

## Deploy

Pushes to `main`/`master` run `.github/workflows/deploy.yml`, which builds Jekyll and publishes `_site/` to the `gh-pages` branch.
