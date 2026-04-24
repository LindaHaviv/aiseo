"""Map failed checks to actionable fix recommendations."""

from __future__ import annotations

from app.models import CheckResult, CheckStatus, Fix

FIX_LIBRARY: dict[str, dict] = {
    "robots_exists": {
        "title": "Create a robots.txt file",
        "description": "Add a robots.txt at your site root that explicitly allows AI crawlers.",
        "priority": "critical",
        "effort": "easy",
        "score_lift": 8.0,
        "code_snippet": (
            "# /robots.txt\n"
            "User-agent: *\n"
            "Allow: /\n\n"
            "User-agent: GPTBot\n"
            "Allow: /\n\n"
            "User-agent: Google-Extended\n"
            "Allow: /\n\n"
            "User-agent: ChatGPT-User\n"
            "Allow: /\n\n"
            "Sitemap: https://yourdomain.com/sitemap.xml"
        ),
    },
    "robots_ai_bots": {
        "title": "Unblock AI bots in robots.txt",
        "description": (
            "Remove Disallow rules targeting AI crawlers (GPTBot, Google-Extended, etc.)."
        ),
        "priority": "critical",
        "effort": "easy",
        "score_lift": 10.0,
        "code_snippet": (
            "# Replace restrictive rules with:\n"
            "User-agent: GPTBot\n"
            "Allow: /\n\n"
            "User-agent: Google-Extended\n"
            "Allow: /\n"
        ),
    },
    "llms_txt": {
        "title": "Add an llms.txt file",
        "description": (
            "Create /llms.txt — a plain-text summary of your site"
            " optimised for LLM context windows. "
            "Include your site name, purpose, key pages, and important content."
        ),
        "priority": "high",
        "effort": "medium",
        "score_lift": 8.0,
        "code_snippet": (
            "# /llms.txt\n"
            "# Your Site Name\n\n"
            "> Brief one-line description of your site.\n\n"
            "## Key Pages\n"
            "- [About](/about): Company overview\n"
            "- [Docs](/docs): Technical documentation\n"
            "- [Blog](/blog): Latest articles\n"
        ),
    },
    "llms_full_txt": {
        "title": "Add an llms-full.txt file",
        "description": (
            "Create /llms-full.txt with comprehensive site content for deep LLM context."
        ),
        "priority": "medium",
        "effort": "medium",
        "score_lift": 4.0,
        "code_snippet": None,
    },
    "sitemap_exists": {
        "title": "Add a sitemap.xml",
        "description": (
            "Create an XML sitemap listing all public pages"
            " to help AI crawlers discover your content."
        ),
        "priority": "high",
        "effort": "easy",
        "score_lift": 6.0,
        "code_snippet": (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            "  <url>\n"
            "    <loc>https://yourdomain.com/</loc>\n"
            "    <lastmod>2024-01-01</lastmod>\n"
            "  </url>\n"
            "</urlset>"
        ),
    },
    "structured_data": {
        "title": "Add JSON-LD structured data",
        "description": (
            "Embed Schema.org JSON-LD in your page <head>"
            " so AI agents understand your content type."
        ),
        "priority": "high",
        "effort": "medium",
        "score_lift": 8.0,
        "code_snippet": (
            '<script type="application/ld+json">\n'
            "{\n"
            '  "@context": "https://schema.org",\n'
            '  "@type": "WebSite",\n'
            '  "name": "Your Site",\n'
            '  "url": "https://yourdomain.com",\n'
            '  "description": "Brief description"\n'
            "}\n"
            "</script>"
        ),
    },
    "meta_title": {
        "title": "Add a descriptive page title",
        "description": (
            "Set a meaningful <title> tag — this is one of the first things AI models read."
        ),
        "priority": "critical",
        "effort": "easy",
        "score_lift": 5.0,
        "code_snippet": "<title>Your Site — Clear, Descriptive Title</title>",
    },
    "meta_description": {
        "title": "Add a meta description",
        "description": "Write a 150-160 character meta description summarising the page content.",
        "priority": "high",
        "effort": "easy",
        "score_lift": 5.0,
        "code_snippet": (
            '<meta name="description" content="Your concise page description here (150-160 chars)">'
        ),
    },
    "og_tags": {
        "title": "Add Open Graph tags",
        "description": (
            "Add og:title, og:description, and og:image meta tags for richer AI context."
        ),
        "priority": "medium",
        "effort": "easy",
        "score_lift": 4.0,
        "code_snippet": (
            '<meta property="og:title" content="Your Page Title">\n'
            '<meta property="og:description" content="Your page description">\n'
            '<meta property="og:image" content="https://yourdomain.com/og-image.png">\n'
            '<meta property="og:url" content="https://yourdomain.com/">'
        ),
    },
    "text_html_ratio": {
        "title": "Improve text-to-HTML ratio",
        "description": (
            "Add more meaningful text content. Reduce boilerplate HTML, inline styles, and scripts."
        ),
        "priority": "medium",
        "effort": "hard",
        "score_lift": 5.0,
        "code_snippet": None,
    },
    "heading_structure": {
        "title": "Add proper heading structure",
        "description": (
            "Use H1-H6 headings to create a clear content hierarchy AI agents can parse."
        ),
        "priority": "medium",
        "effort": "easy",
        "score_lift": 4.0,
        "code_snippet": None,
    },
    "semantic_html": {
        "title": "Use semantic HTML elements",
        "description": (
            "Replace generic <div> containers with <article>, <section>, <nav>, <main>, etc."
        ),
        "priority": "medium",
        "effort": "medium",
        "score_lift": 5.0,
        "code_snippet": (
            "<!-- Instead of: -->\n"
            '<div class="content">...</div>\n\n'
            "<!-- Use: -->\n"
            "<article>\n"
            "  <header><h1>Title</h1></header>\n"
            "  <section>...</section>\n"
            "</article>"
        ),
    },
    "x_robots_tag": {
        "title": "Remove restrictive X-Robots-Tag header",
        "description": "Remove noindex/nofollow from the X-Robots-Tag HTTP header.",
        "priority": "critical",
        "effort": "easy",
        "score_lift": 6.0,
        "code_snippet": None,
    },
    "http_status": {
        "title": "Fix HTTP error status",
        "description": (
            "Ensure your page returns HTTP 200. Check server configuration and redirects."
        ),
        "priority": "critical",
        "effort": "medium",
        "score_lift": 3.0,
        "code_snippet": None,
    },
    "https": {
        "title": "Enable HTTPS",
        "description": "Switch to HTTPS — AI agents and search engines prefer secure sites.",
        "priority": "critical",
        "effort": "medium",
        "score_lift": 5.0,
        "code_snippet": None,
    },
    "canonical_url": {
        "title": "Set a canonical URL",
        "description": ("Add a <link rel='canonical'> tag to prevent duplicate content confusion."),
        "priority": "low",
        "effort": "easy",
        "score_lift": 3.0,
        "code_snippet": '<link rel="canonical" href="https://yourdomain.com/your-page">',
    },
}

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def generate_fixes(checks: list[CheckResult]) -> list[Fix]:
    fixes: list[Fix] = []
    for check in checks:
        if check.status in (CheckStatus.FAIL, CheckStatus.WARN):
            template = FIX_LIBRARY.get(check.id)
            if template:
                fixes.append(
                    Fix(
                        id=f"fix_{check.id}",
                        check_id=check.id,
                        **template,
                    )
                )

    fixes.sort(key=lambda f: (PRIORITY_ORDER.get(f.priority, 9), -f.score_lift))
    return fixes
