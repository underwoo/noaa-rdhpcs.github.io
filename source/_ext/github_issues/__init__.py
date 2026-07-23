"""github-issues -- Sphinx extension for rendering GitHub Issues dynamically.

This extension provides the ``.. github-issues::`` directive, which
generates a client-side-rendered container.  The companion JavaScript
file (``github-issues.js``) fetches matching issues from the GitHub
REST API at page-load time and renders them as collapsible dropdowns.

No site rebuild is required when issues are created, updated, or closed;
content refreshes on every page load (subject to a configurable browser
cache).

Configuration
-------------

Add to ``conf.py``::

    extensions = [
        ...
        "github_issues",
    ]

    github_issues_config = {
        # Required
        "repo": "owner/repo",

        # Optional (these are the built-in defaults)
        "approved_label": "approved",
        "empty_message": "There are no items in this section at this time.",
        "show_github_link": True,
        "cache_minutes": 5,
        "date_filter": "none",
        "display_days": 60,
        "fields": {
            "title":         ["title", "change-title", "issue-title"],
            "date":          ["effective-date", "planned-effective-date",
                              "date-identified"],
            "description":   "description",
            "documentation": ["documentation-link", "documentation"],
        },
        "severity": {
            "label_pattern": r"^severity:(.+)$",
            "levels": ["critical", "high", "medium", "low"],
            "colors": {
                "critical": "#b60205",
                "high":     "#d93f0b",
                "medium":   "#e4e669",
                "low":      "#0e8a16",
            },
        },
    }

Usage
-----

.. code-block:: rst

   .. github-issues:: known-issue
      :date-filter: none
      :show-severity: true
      :empty-message: No known issues at this time.

   .. github-issues:: upcoming-change
      :date-filter: future
      :empty-message: No upcoming changes at this time.

   .. github-issues:: known-issue
      :repo: owner/other-repo
      :filter-labels: system:gaea
      :show-severity: true
      :empty-message: No Gaea known issues at this time.

See ``README.md`` in this directory for full documentation.
"""

from __future__ import annotations

from pathlib import Path

from sphinx.application import Sphinx

from .directive import GithubIssuesDirective

#: Semantic version string, also used by pyproject.toml via hatch.version.
__version__ = "0.1.0"

# Path to the static assets bundled with this extension
_STATIC_DIR = Path(__file__).parent / "static"


def _add_static_assets(app: Sphinx) -> None:
    """Register the extension JavaScript and CSS files with Sphinx.

    Appends the extension ``static/`` directory to ``html_static_path``
    so Sphinx copies ``github-issues.js`` and ``github-issues.css`` into
    the output tree.  Both files are then added to every HTML page.
    Sphinx deduplicates asset registrations, so calling this function
    multiple times is safe.

    Parameters
    ----------
    app:
        The Sphinx application object, passed by the ``builder-inited``
        event hook.
    """
    app.config.html_static_path = list(app.config.html_static_path or [])
    app.config.html_static_path.append(str(_STATIC_DIR))
    app.add_js_file("github-issues.js")
    app.add_css_file("github-issues.css")


def setup(app: Sphinx) -> dict:
    """Sphinx extension entry point.

    Registers:

    - The ``github_issues_config`` configuration value (type ``dict``,
      default ``{}``, triggers an HTML rebuild when changed).
    - The ``.. github-issues::`` directive.
    - A ``builder-inited`` hook that copies static assets.

    Parameters
    ----------
    app:
        The Sphinx application object provided by Sphinx when loading
        the extension.

    Returns
    -------
    dict
        Extension metadata consumed by Sphinx.
    """
    app.add_config_value("github_issues_config", default={}, rebuild="html")
    app.add_directive("github-issues", GithubIssuesDirective)
    app.connect("builder-inited", lambda a: _add_static_assets(a))

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
