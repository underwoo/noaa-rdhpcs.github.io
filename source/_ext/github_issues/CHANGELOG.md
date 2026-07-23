# Changelog

All notable changes to `sphinx-github-issues` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Version numbers follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

## [0.1.0] - 2026-07-23

Initial release.  All features developed in-tree as part of the
NOAA RDHPCS documentation project before extraction as a standalone
package.

### Added

#### Core (Phase 1)
- `.. github-issues:: <label>` Sphinx directive
- Client-side rendering via `github-issues.js`; no rebuild required
  when issues change
- `github_issues_config` in `conf.py` for site-wide defaults
- Per-directive overrides for `:repo:`, `:approved-label:`,
  `:filter-labels:`, `:empty-message:`, `:show-github-link:`
- `localStorage` caching; cache key includes all filter parameters
  so different filter combinations never share an entry
- Graceful `<noscript>` fallback with auto-generated link to GitHub
- Dark mode support via `prefers-color-scheme`
- Packaging groundwork: `pyproject.toml`, `LICENSE`, `README.md`

#### Date Filtering (Phase 2)
- `:date-filter:` option with four modes:
  - `none` — no date filtering (default)
  - `past` — issues within past `display-days` days
  - `future` — upcoming issues (plus recent linger window)
  - `window` — issues within `display-days` in either direction
- `:date-field:` option to override which body field is used as date
- `:display-days:` option to set window width
- Issues with no parseable date always pass the filter
- `date_filter` and `display_days` global defaults in `conf.py`
- Date and display-days included in cache key

#### Severity Badges (Phase 3)
- `:show-severity:` option (default: `false`)
- `severity` sub-dict in `github_issues_config`:
  - `label_pattern` — JavaScript/Python regex; capture group 1
    extracts the severity level name
  - `levels` — ordered list of level names (index 0 = most severe)
  - `colors` — optional CSS color overrides per level
- Positional CSS classes (`github-issues-severity-level-N`) so
  stylesheets work without hardcoding level names
- Inline `style` attribute added when `colors` are configured,
  allowing the badge to render correctly without the bundled CSS
- `github-issues-severity-unknown` class for unrecognised levels

#### Advanced Options (Phase 4)
- `:max-items:` — cap displayed items after filtering (`0` = unlimited)
- `:hide-fields:` — comma-separated list of body field names to
  suppress from rendering; applies to both known and custom fields
- `:cache-minutes:` — per-directive cache TTL override (previously
  only configurable globally)

[Unreleased]: https://github.com/NOAA-RDHPCS/noaa-rdhpcs.github.io/compare/sphinx-github-issues-v0.1.0...HEAD
[0.1.0]: https://github.com/NOAA-RDHPCS/noaa-rdhpcs.github.io/releases/tag/sphinx-github-issues-v0.1.0
