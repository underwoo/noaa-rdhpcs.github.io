"""``github-issues`` Sphinx directive.

Emits a client-side-rendered container that the companion JavaScript
(``github-issues.js``) fills with issues fetched from the GitHub API.

Directive syntax
----------------

.. code-block:: rst

   .. github-issues:: <label>
      :repo: owner/repo
      :approved-label: approved
      :filter-labels: system:gaea, component:storage
      :empty-message: No items at this time.
      :show-github-link: true

Options
-------

label (positional argument)
    The primary GitHub label to filter by (e.g. ``known-issue``).

:repo:
    GitHub repository in ``owner/repo`` format.  Defaults to the
    ``repo`` key in ``github_issues_config`` from ``conf.py``.

:approved-label:
    Additional label that must be present for an issue to be shown.
    Pass an empty string to disable.  Defaults to ``approved``.

:filter-labels:
    Comma-separated list of extra labels that must ALL be present
    (AND logic).  Example: ``system:gaea, component:storage``.

:empty-message:
    Text displayed when no issues match the filters.

:show-github-link:
    Whether to show a "View on GitHub" link per item.  Accepts
    ``true`` / ``false`` (case-insensitive).  Default: ``true``.
"""

from __future__ import annotations

import json
from typing import Any

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

from .config import get_config, normalise_field_names


class GithubIssuesDirective(SphinxDirective):
    """Sphinx directive: ``.. github-issues:: <label>``."""

    has_content = False
    required_arguments = 1   # the primary label
    optional_arguments = 0
    final_argument_whitespace = False

    option_spec = {
        "repo": directives.unchanged,
        "approved-label": directives.unchanged,
        "filter-labels": directives.unchanged,
        "empty-message": directives.unchanged,
        "show-github-link": directives.unchanged,
    }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _bool(value: str | None, default: bool = True) -> bool:
        """Coerce a directive option string to a bool."""
        if value is None:
            return default
        return value.strip().lower() not in {"false", "0", "no", "off"}

    @staticmethod
    def _labels(value: str) -> list[str]:
        """Split a comma-separated label string into a cleaned list."""
        return [lbl.strip() for lbl in value.split(",") if lbl.strip()]

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(self) -> list[nodes.Node]:
        cfg = get_config(self.env.app.config)

        primary_label: str = self.arguments[0].strip()

        # --- resolve options, falling back to conf.py defaults ----------
        repo: str | None = self.options.get("repo") or cfg.get("repo")
        if not repo:
            raise self.error(
                "github-issues: no repository specified. "
                "Set 'repo' as a directive option or set "
                "'github_issues_config[\"repo\"]' in conf.py."
            )

        approved_label: str = self.options.get(
            "approved-label",
            cfg.get("approved_label", "approved"),
        )

        filter_labels: list[str] = self._labels(
            self.options.get("filter-labels", "")
        )

        empty_message: str = self.options.get(
            "empty-message",
            cfg.get("empty_message", "There are no items in this section at this time."),
        )

        show_github_link: bool = self._bool(
            self.options.get("show-github-link"),
            default=bool(cfg.get("show_github_link", True)),
        )

        cache_minutes: int = int(cfg.get("cache_minutes", 5))
        fields: dict[str, list[str]] = normalise_field_names(cfg.get("fields", {}))

        # --- build data-* payload passed to JavaScript ------------------
        data: dict[str, Any] = {
            "label": primary_label,
            "repo": repo,
            "approved-label": approved_label,
            "filter-labels": filter_labels,
            "empty-message": empty_message,
            "show-github-link": json.dumps(show_github_link),
            "cache-minutes": str(cache_minutes),
            "fields": json.dumps(fields),
        }

        # Build HTML attribute string
        attrs = "".join(
            f' data-{key}="{_escape(str(val) if not isinstance(val, list) else json.dumps(val))}"'
            for key, val in data.items()
        )

        # Noscript fallback URL
        noscript_url = (
            f"https://github.com/{repo}/issues"
            f"?q=is%3Aissue+is%3Aopen+label%3A{primary_label}"
        )

        html = (
            f'<div class="github-issues-container"{attrs}>'
            f'<p class="github-issues-loading">Loading...</p>'
            f"</div>"
            f"<noscript>"
            f"<p>JavaScript is required to view dynamic content. "
            f'See <a href="{noscript_url}">issues on GitHub</a>.</p>'
            f"</noscript>"
        )

        return [nodes.raw("", html, format="html")]


def _escape(value: str) -> str:
    """Escape double-quotes and angle brackets for HTML attribute values."""
    return value.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
