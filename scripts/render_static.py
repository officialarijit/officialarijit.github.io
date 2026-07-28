"""
Injects static HTML for publications and blog posts into index.html so that
Google can index this content without executing JavaScript.

Run automatically by the process-blogs workflow on each deploy.
"""

import json
import html
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def render_publications(publications):
    items = []
    for pub in publications:
        title = html.escape(pub.get("title", ""))
        authors = html.escape(pub.get("authors", ""))
        journal = html.escape(pub.get("journal", ""))
        year = html.escape(str(pub.get("year", "")))
        citations = pub.get("citations", 0)
        paper_url = pub.get("links", {}).get("paper") or "#"

        citation_text = f'<span class="pub-citations">{citations} citation{"s" if citations != 1 else ""}</span>' if citations else ""

        items.append(f"""<div class="publication-item static-pub">
  <div class="pub-content">
    <h3 class="pub-title"><a href="{html.escape(paper_url)}" target="_blank" rel="noopener">{title}</a></h3>
    <p class="pub-authors">{authors}</p>
    <p class="pub-journal">{journal} ({year})</p>
    {citation_text}
  </div>
</div>""")

    return "\n".join(items)


def render_blog_previews(posts):
    items = []
    for post in posts[:3]:
        title = html.escape(post.get("title", ""))
        excerpt = html.escape(post.get("excerpt", ""))
        date = html.escape(post.get("date", ""))
        category = html.escape(post.get("category", ""))
        slug = html.escape(post.get("slug", post.get("id", "")))
        image = html.escape(post.get("image", "assets/images/slide2.jpg"))

        items.append(f"""<div class="blog-preview-card static-blog">
  <img src="{image}" alt="{title}" loading="lazy" width="400" height="250">
  <div class="blog-preview-content">
    <span class="post-category">{category}</span>
    <h3><a href="blog.html#{slug}">{title}</a></h3>
    <p>{excerpt}</p>
    <span class="post-date">{date}</span>
  </div>
</div>""")

    return "\n".join(items)


def inject_between(content, start_marker, end_marker, replacement):
    pattern = re.compile(
        re.escape(start_marker) + ".*?" + re.escape(end_marker),
        re.DOTALL,
    )
    return pattern.sub(start_marker + replacement + end_marker, content)


def main():
    index_path = ROOT / "index.html"
    pubs_path = ROOT / "data" / "publications.json"
    blogs_path = ROOT / "data" / "blog_posts.json"

    if not index_path.exists():
        print("index.html not found — skipping static injection")
        return

    content = index_path.read_text(encoding="utf-8")

    # Inject publications
    if pubs_path.exists():
        data = load_json(pubs_path)
        publications = data.get("publications", [])
        pub_html = "\n<noscript>\n" + render_publications(publications) + "\n</noscript>\n"
        content = inject_between(
            content,
            "<!-- STATIC_PUBLICATIONS_START -->",
            "<!-- STATIC_PUBLICATIONS_END -->",
            pub_html,
        )
        print(f"Injected {len(publications)} publications into index.html")

    # Inject blog previews
    if blogs_path.exists():
        data = load_json(blogs_path)
        posts = data.get("posts", [])
        blog_html = "\n<noscript>\n" + render_blog_previews(posts) + "\n</noscript>\n"
        content = inject_between(
            content,
            "<!-- STATIC_BLOGS_START -->",
            "<!-- STATIC_BLOGS_END -->",
            blog_html,
        )
        print(f"Injected {len(posts)} blog previews into index.html")

    index_path.write_text(content, encoding="utf-8")
    print("Static injection complete.")


if __name__ == "__main__":
    main()
