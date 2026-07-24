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
| `citation.txt` | Google Scholar export (update `_data/scholar.yml` manually or via script) |

## Deploy

Pushes to `main`/`master` run `.github/workflows/deploy.yml`, which builds Jekyll and publishes `_site/` to the `gh-pages` branch.
