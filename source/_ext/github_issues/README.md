# github-issues Sphinx Extension

A reusable Sphinx extension that renders GitHub Issues dynamically as
collapsible dropdowns using client-side JavaScript.

## Features

- Fetches issues at page-load time — no rebuild needed when issues change
- Configurable label filtering with AND logic
- Optional approval-label gate (e.g. `approved`)
- Configurable empty, loading, and error states
- Graceful `<noscript>` fallback with link to GitHub
- Dark mode support
- Browser-side caching with configurable TTL
- Portable — no assumptions about repository structure or label names

## Installation

### In-tree (current)

The extension lives in `source/_ext/github_issues/`. No installation needed.

### Future: pip install

```bash
pip install sphinx-github-issues
```

## Configuration

In `conf.py`:

```python
extensions = [
    ...
    "github_issues",
]

github_issues_config = {
    # Required
    "repo": "owner/repo",

    # Optional (these are the defaults)
    "approved_label": "approved",    # set to "" to disable
    "empty_message": "There are no items in this section at this time.",
    "cache_minutes": 5,
    "show_github_link": True,
    "fields": {
        # Each value is tried in order; first match wins
        "title":         ["title", "change-title", "issue-title"],
        "date":          ["effective-date", "planned-effective-date", "date-identified"],
        "description":   "description",
        "documentation": ["documentation-link", "documentation"],
    },
}
```

## Directive Syntax

```rst
.. github-issues:: <label>
   :repo: owner/repo
   :approved-label: approved
   :filter-labels: system:gaea, component:storage
   :empty-message: No items at this time.
   :show-github-link: true
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `<label>` | (required) | Primary GitHub label to filter by |
| `:repo:` | `conf.py` value | GitHub repository `owner/repo` |
| `:approved-label:` | `approved` | Additional required label; empty to disable |
| `:filter-labels:` | — | Comma-separated extra labels (AND logic) |
| `:empty-message:` | `conf.py` value | Message when no issues match |
| `:show-github-link:` | `true` | Show "View on GitHub" link per item |

## Issue Body Format

Issues use GitHub's issue form format. Sections are defined with
`### Heading` markers. The extension recognises these field names
(configurable via `fields` in `conf.py`):

| Role | Default field names |
|------|-------------------|
| Title | `title`, `change-title`, `issue-title` |
| Date | `effective-date`, `planned-effective-date`, `date-identified` |
| Description | `description` |
| Documentation | `documentation-link`, `documentation` |
| Affected Systems | `affected-systems` (checkbox format) |

Any `### Heading` that appears **after** the Description section and is
not one of the above is rendered as a custom field in the order it appears.

Fields that appear **before** Description are not rendered (they may be
used by GitHub Actions workflows).

## Approval Workflow

By default, issues must have both the primary label and the `approved`
label to be displayed. This allows contributors to create issues that
are reviewed before publication.

- Members with write access can add `approved` themselves.
- External contributors trigger a notification workflow; a reviewer
  adds `approved` after verifying the content.

Set `"approved_label": ""` in `conf.py` (or `:approved-label:` to `""`)
to disable the requirement.

## System Label Filtering

To show only issues affecting a specific system, use `:filter-labels:`:

```rst
.. github-issues:: known-issue
   :filter-labels: system:gaea
   :empty-message: There are no known issues affecting Gaea at this time.
```

This requires issues to have **both** `known-issue` and `system:gaea`.
System labels can be added manually or automatically via a GitHub Actions
workflow that reads checkbox selections from the issue body.

## Future Roadmap

- Phase 2: Configurable date filtering (`:date-filter:`, `:display-days:`)
- Phase 3: Severity badge display (`:show-severity:`)
- Phase 4: Advanced options (`:max-items:`, `:hide-fields:`, `:cache-minutes:`)
- Phase 5: Standalone pip package
