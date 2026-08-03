# Zed Configuration for NOAA-RDHPCS Documentation

This directory contains Zed editor settings for the NOAA-RDHPCS documentation project, migrated from the original VS Code `.vscode/` configuration.

## Files

- **settings.json** — Project-specific editor settings (line length, trailing whitespace, reStructuredText config, Sphinx language server)
- **tasks.json** — Build tasks for Sphinx documentation (build, link check, dev server, linting)

## Usage

### Build Tasks

Open the command palette (`Cmd+Shift+P`) and search for "task" to see available build commands:

- **Sphinx: Build HTML** — Full Sphinx build to `build/html`
- **Sphinx: Link Check** — Validate all internal/external links
- **Sphinx: Start Dev Server** — Local HTTP server at `http://localhost:8000`
- **doc8: Lint RST files** — Check RST markup quality

### Language Server

If you have the `esbonio` language server installed globally or in `.venv/`, Zed will use it for reStructuredText files with Sphinx support.

## Differences from VS Code

1. **Extensions** — Zed has fewer RST extensions. Install what's available from Extensions panel (`Cmd+Shift+X`)
2. **Spell Check** — VS Code used cSpell with custom dictionaries. Zed has built-in spell check; you may need to add custom words via settings
3. **Tasks** — Zed's task runner is simpler than VS Code's. Tasks run as shell commands, not integrated builds
4. **Problem Matchers** — Zed doesn't support VS Code-style problem matchers; errors appear in terminal output

## Migrated Settings

| VS Code Setting | Zed Equivalent |
|----------------|----------------|
| `terminal.integrated.defaultProfile.windows` | Not needed (macOS project) |
| `esbonio.sphinx.confDir` | `lsp.esbonio.initialization_options` |
| `esbonio.sphinx.pythonCommand` | `lsp.esbonio.initialization_options` |
| `files.trimTrailingWhitespace` | `files.trim_trailing_whitespace` |
| `rewrap.wrappingColumn` | `preferred_line_length` |
| `makefile.configureOnOpen` | Not applicable |
| `[restructuredtext]` overrides | `language_overrides.reStructuredText` |
| `cSpell.words` | Use Zed's spell checker settings |

## Notes

- Tasks use explicit `.venv/bin/` paths (no shell activation needed)
- The Sphinx language server requires `esbonio` installed in `.venv/`
- Custom spell check dictionaries from VS Code's cSpell are not automatically migrated
