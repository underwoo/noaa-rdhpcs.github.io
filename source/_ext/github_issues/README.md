# sphinx-github-issues

A reusable Sphinx extension that renders GitHub Issues dynamically as
collapsible dropdowns using client-side JavaScript.  No rebuild is
needed when issues are created, updated, or closed — the page fetches
fresh content on every load (subject to a configurable browser cache).

## Features

- Fetches issues at page-load time via the GitHub REST API
- Configurable label filtering with AND logic
- Optional approval-label gate (e.g. `approved`)
- Date-based filtering: `none`, `past`, `future`, or `window`
- Severity badges driven by a configurable regex matched against labels
- Per-directive field suppression (`:hide-fields:`)
- Per-directive item limit (`:max-items:`)
- Per-directive cache TTL override (`:cache-minutes:`)
- Graceful `<noscript>` fallback with auto-generated link to GitHub
- Dark mode support via `prefers-color-scheme`
- Browser-side `localStorage` caching; cache key includes all filter
  parameters so different filter combinations never share a cache entry
- Portable — no assumptions about repository structure, label names,
  or severity level names

## Requirements

- Python 3.9+
- Sphinx 5.0+

## Installation

### In-tree (current)

The extension lives in `source/_ext/github_issues/`.  No installation
is needed; Sphinx discovers it via `sys.path` in `conf.py`.

### Future: pip install

```bash
pip install sphinx-github-issues
```

## Quick Start

Add to `conf.py`:

```python
extensions = [
    ...
    "github_issues",
]

github_issues_config = {
    "repo": "owner/repo",   # required
}
```

Use in any `.rst` file:

```rst
Known Issues
============

.. github-issues:: known-issue
   :show-severity: true
   :empty-message: There are no known issues at this time.
```

## Configuration (conf.py)

All keys in `github_issues_config` are optional; unset keys use the
built-in defaults shown below.

```python
github_issues_config = {
    # ---------- Required ---------------------------------------------------
    "repo": "owner/repo",

    # ---------- Approval ---------------------------------------------------
    # Label that must be present for an issue to be displayed.
    # Set to "" or None to disable the approval requirement.
    "approved_label": "approved",

    # ---------- Display ----------------------------------------------------
    "empty_message": "There are no items in this section at this time.",
    "show_github_link": True,
    "cache_minutes": 5,

    # ---------- Date filtering ---------------------------------------------
    # Default filter mode for all directives unless overridden per-directive.
    # Values: "none" | "past" | "future" | "window"
    "date_filter": "none",
    # Width of the date window in days.
    "display_days": 60,

    # ---------- Field name mapping ----------------------------------------
    # Each value is tried in order; first matching field wins.
    "fields": {
        "title":         ["title", "change-title", "issue-title"],
        "date":          ["effective-date", "planned-effective-date",
                          "date-identified"],
        "description":   "description",
        "documentation": ["documentation-link", "documentation"],
    },

    # ---------- Severity badges -------------------------------------------
    "severity": {
        # Python/JS regex; capture group 1 extracts the level name.
        "label_pattern": r"^severity:(.+)$",
        # Ordered from most to least severe.  Position determines the
        # CSS modifier class (level-0, level-1, ...).
        "levels": ["critical", "high", "medium", "low"],
        # Optional inline color overrides (CSS color values).
        # When absent, the bundled github-issues.css supplies colors.
        "colors": {
            "critical": "#b60205",
            "high":     "#d93f0b",
            "medium":   "#e4e669",
            "low":      "#0e8a16",
        },
    },
}
```

## Directive Reference

```rst
.. github-issues:: <label>
   :repo: owner/repo
   :approved-label: approved
   :filter-labels: system:gaea, component:storage
   :date-filter: past
   :date-field: effective-date
   :display-days: 60
   :show-severity: true
   :max-items: 5
   :hide-fields: workaround, user-action-required
   :cache-minutes: 10
   :empty-message: No items at this time.
   :show-github-link: true
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `<label>` | arg | (required) | Primary GitHub label to filter by |
| `:repo:` | string | `conf.py` value | Repository `owner/repo` |
| `:approved-label:` | string | `approved` | Additional required label; `""` to disable |
| `:filter-labels:` | string | — | Comma-separated extra labels, AND logic |
| `:date-filter:` | enum | `conf.py` value | `none` / `past` / `future` / `window` |
| `:date-field:` | string | `conf.py` fields.date | Body field name(s) for date, comma-separated |
| `:display-days:` | int | `60` | Window width in days |
| `:show-severity:` | bool | `false` | Show severity badge |
| `:max-items:` | int | `0` (unlimited) | Cap displayed items after filtering |
| `:hide-fields:` | string | — | Comma-separated field names to suppress |
| `:cache-minutes:` | int | `conf.py` value | Per-container cache TTL |
| `:empty-message:` | string | `conf.py` value | Message when no issues match |
| `:show-github-link:` | bool | `true` | Show "View on GitHub" link per item |

### Date Filter Modes

| Mode | Shows issues where… |
|------|---------------------|
| `none` | All issues (no date check) |
| `past` | Date ≤ today AND date ≥ today − `display-days` |
| `future` | Date > today OR date ≥ today − `display-days` |
| `window` | Date within `display-days` of today in either direction |

Issues with no parseable date always pass the filter.

## Issue Body Format

The directive uses GitHub's issue form format, where each field is
introduced by a `### Heading` marker.

### Recognised fields

| Role | Default names tried (in order) |
|------|-------------------------------|
| Title | `title`, `change-title`, `issue-title` |
| Date | `effective-date`, `planned-effective-date`, `date-identified` |
| Description | `description` |
| Documentation | `documentation-link`, `documentation` |
| Affected systems | `affected-systems` (checkbox list) |

Field names are configurable via `github_issues_config["fields"]` in
`conf.py` and can be overridden per-directive with `:date-field:`.

### Custom fields

Any `### Heading` that appears **after** the Description section and is
not one of the recognised fields above is rendered as a custom field in
body order.  Use `:hide-fields:` to suppress specific ones.

Fields that appear **before** Description are not rendered; they are
available to GitHub Actions workflows (e.g. for auto-labelling).

## Severity Badges

Severity is read from GitHub labels, not from the issue body, so it can
be set by repository maintainers independently of issue content.

Configure via `github_issues_config["severity"]`:

```python
"severity": {
    # Regex with one capture group that extracts the level string.
    "label_pattern": r"^severity:(.+)$",
    # Levels in priority order (index 0 = most severe).
    "levels": ["critical", "high", "medium", "low"],
    # Optional color overrides (any valid CSS color value).
    "colors": { "critical": "#b60205", ... },
}
```

Severity levels not in the `levels` list are still displayed with a
neutral "unknown" style.  The regex can be changed to match any label
naming scheme; the capture group extracts the display name.

### Example: Custom severity scheme

```python
"severity": {
    "label_pattern": r"^priority-(.+)$",
    "levels": ["p0", "p1", "p2", "p3"],
    "colors": {
        "p0": "#b60205",
        "p1": "#d93f0b",
        "p2": "#fbca04",
        "p3": "#0e8a16",
    },
}
```

## Approval Workflow

By default, issues must have both the primary label and the `approved`
label to be displayed.  This lets contributors create draft issues that
are reviewed before publication.

- **Members with write access** can add the `approved` label themselves.
- **External contributors** can trigger a notification workflow that
  pings reviewers; a reviewer adds `approved` after verifying content.

Set `"approved_label": ""` in `conf.py` (or `:approved-label: ""` on a
directive) to disable the requirement entirely.

## System Label Filtering

To show only issues affecting a specific system, use `:filter-labels:`:

```rst
.. github-issues:: known-issue
   :filter-labels: system:gaea
   :show-severity: true
   :empty-message: There are no known issues affecting Gaea at this time.
```

System labels can be added manually or automatically via a GitHub
Actions workflow that reads the checkbox selections from the issue body.

## FAQ Page Example

```rst
Upcoming Changes
================

.. github-issues:: upcoming-change
   :date-filter: future
   :empty-message: There are no upcoming changes at this time.


Known Issues
============

.. github-issues:: known-issue
   :date-filter: none
   :show-severity: true
   :empty-message: There are no known issues at this time.


Recent Changes
==============

.. github-issues:: recent-change
   :date-filter: past
   :empty-message: There are no recent changes at this time.
```

## CSS Customisation

All class names use the `github-issues-` prefix.  The bundled
`github-issues.css` provides default styling.  To override colors or
layout, add rules to your project's own stylesheet that target these
classes:

| Class | Element |
|-------|---------|
| `.github-issues-container` | Wrapper div |
| `.github-issues-loading` | "Loading..." paragraph |
| `.github-issues-empty` | Empty-state paragraph |
| `.github-issues-error` | Error message div |
| `.github-issues-item` | Individual issue dropdown |
| `.github-issues-severity` | Severity badge base |
| `.github-issues-severity-level-N` | Severity badge for level N (0 = most severe) |
| `.github-issues-severity-unknown` | Severity badge for unrecognised levels |
| `.github-issues-systems` | "Affects: ..." line |
| `.github-issues-system-tag` | Individual system pill |
| `.github-issues-date` | Date line |
| `.github-issues-description` | Description block |
| `.github-issues-field` | Custom field block |
| `.github-issues-doc-link` | Documentation link |
| `.github-issues-issue-link` | "View on GitHub" link |

## Future Roadmap

- GitHub Actions workflow for auto-applying system labels from checkbox
  selections in the issue body
- OR logic for `:filter-labels:`
- Standalone pip package (`sphinx-github-issues`)
