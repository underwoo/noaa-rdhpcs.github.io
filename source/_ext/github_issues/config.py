"""Configuration handling for the github-issues Sphinx extension.

Provides defaults and merging logic for the ``github_issues_config``
dictionary in ``conf.py``.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Built-in defaults
# ---------------------------------------------------------------------------

#: Valid values for the ``date_filter`` option.
DATE_FILTER_VALUES = frozenset({"none", "past", "future", "window"})

#: Default configuration values. Every key here is optional in the user's
#: ``github_issues_config`` dict; missing keys fall back to these values.
DEFAULTS: dict[str, Any] = {
    # GitHub repository in "owner/repo" format.  No built-in default —
    # must be supplied in conf.py or per-directive.
    "repo": None,
    # Label that must be present for an issue to be displayed.
    # Set to an empty string or None to disable the approval requirement.
    "approved_label": "approved",
    # Default message shown when a section has no matching issues.
    "empty_message": "There are no items in this section at this time.",
    # Browser-side localStorage cache duration, in minutes.
    "cache_minutes": 5,
    # Field names to look for in the issue body (tried in order).
    # Values may be a single string or a list of strings.
    "fields": {
        "title": ["title", "change-title", "issue-title"],
        "date": ["effective-date", "planned-effective-date", "date-identified"],
        "description": "description",
        "documentation": ["documentation-link", "documentation"],
    },
    # Whether to show a "View on GitHub" link at the bottom of each item.
    "show_github_link": True,
    # ---------------------------------------------------------------------------
    # Date filtering defaults (Phase 2)
    # ---------------------------------------------------------------------------
    # How to filter issues by the date field.
    # Values: "none" | "past" | "future" | "window"
    #
    #   none   — no date filtering; show all matching issues
    #   past   — date <= today AND date >= (today - display_days)
    #   future — date > today OR  date >= (today - display_days)
    #   window — date >= (today - display_days) AND
    #            date <= (today + display_days)
    "date_filter": "none",
    # Width of the display window in days (used by "past", "future", "window").
    "display_days": 60,
    # ---------------------------------------------------------------------------
    # Severity display defaults (Phase 3)
    # ---------------------------------------------------------------------------
    # Severity configuration.  Controls whether and how severity badges are
    # rendered.  All sub-keys are optional; unrecognised levels receive a
    # neutral grey style.
    #
    # label_pattern: Python/JavaScript regex with one capture group that
    #   extracts the severity level string from a GitHub label name.
    #   Example: r"^severity:(.+)$"  matches "severity:high" → "high"
    #
    # levels: ordered list from most-severe to least-severe.  Position
    #   determines the CSS modifier class index (level-0, level-1, …).
    #   Any label that matches the pattern but whose captured value is NOT
    #   in this list is still displayed with a fallback "unknown" style.
    #
    # colors: optional dict mapping level name → CSS background colour.
    #   When absent the CSS classes (github-issues-severity-level-N) in
    #   github-issues.css supply the colours.  Providing colours here
    #   injects inline styles, allowing per-project overrides without
    #   editing CSS.
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


def get_config(app_config: Any) -> dict[str, Any]:
    """Return a fully-merged configuration dict.

    Merges the user's ``github_issues_config`` value from ``conf.py``
    over the built-in :data:`DEFAULTS`.  Nested dicts (``fields`` and
    ``severity``) are merged shallowly so the user only needs to override
    the keys they care about.

    Parameters
    ----------
    app_config:
        The Sphinx ``app.config`` object.  The function reads the
        ``github_issues_config`` attribute from it.

    Returns
    -------
    dict
        Merged configuration dictionary.
    """
    user: dict[str, Any] = getattr(app_config, "github_issues_config", {}) or {}

    merged: dict[str, Any] = dict(DEFAULTS)
    for key, value in user.items():
        if key in ("fields", "severity") and isinstance(value, dict):
            merged[key] = {**DEFAULTS.get(key, {}), **value}
        else:
            merged[key] = value

    return merged


def normalise_field_names(fields_config: dict[str, Any]) -> dict[str, list[str]]:
    """Normalise field-name config values to lists.

    Ensures every entry in the ``fields`` sub-dict is a ``list[str]``
    so the JavaScript serialisation is uniform.

    Parameters
    ----------
    fields_config:
        The ``fields`` sub-dict from the merged configuration.

    Returns
    -------
    dict
        The same keys, with every value guaranteed to be a list.
    """
    result: dict[str, list[str]] = {}
    for key, value in fields_config.items():
        if isinstance(value, str):
            result[key] = [value]
        else:
            result[key] = list(value)
    return result
