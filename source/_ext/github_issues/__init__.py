"""github-issues — Sphinx extension for rendering GitHub Issues dynamically.

This extension provides the ``.. github-issues::`` directive, which
generates a client-side-rendered container.  The companion JavaScript
file (``github-issues.js``) fetches matching issues from the GitHub
REST API at page-load time and renders them as collapsible dropdowns.

Configuration
-------------

Add to ``conf.py``::

    extensions = [
        ...
        "github_issues",
    ]

    github_issues_config = {
        "repo": "owner/repo",          # required
        "approved_label": "approved",  # default
        "empty_message": "There are no items in this section at this time.",
        "cache_minutes": 5,
        "show_github_link": True,
        "fields": {
            "title": ["title", "change-title", "issue-title"],
            "date": ["effective-date", "planned-effective-date"],
            "description": "description",
            "documentation": ["documentation-link", "documentation"],
        },
    }

Usage
-----

.. code-block:: rst

   .. github-issues:: known-issue
      :empty-message: No known issues at this time.

   .. github-issues:: known-issue
      :repo: owner/other-repo
      :filter-labels: system:gaea
      :empty-message: No Gaea known issues at this time.
"""

from __future__ import annotations

import os
from pathlib import Path

from sphinx.application import Sphinx

from .directive import GithubIssuesDirective

# Path to the static assets bundled with this extension
_STATIC_DIR = Path(__file__).parent / "static"


def _add_static_assets(app: Sphinx) -> None:
    """Register the extension's JS and CSS with Sphinx."""
    # Add the extension's static directory so Sphinx copies its contents
    app.config.html_static_path = list(app.config.html_static_path or [])
    app.config.html_static_path.append(str(_STATIC_DIR))

    # Register JS and CSS files (Sphinx deduplicates automatically)
    app.add_js_file("github-issues.js")
    app.add_css_file("github-issues.css")


def setup(app: Sphinx) -> dict:
    """Sphinx extension entry point."""
    # Register the conf.py configuration value
    app.add_config_value("github_issues_config", default={}, rebuild="html")

    # Register the directive
    app.add_directive("github-issues", GithubIssuesDirective)

    # Hook to add static assets after the builder is initialised
    app.connect("builder-inited", lambda app: _add_static_assets(app))

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
