# Contributing to the project

This is a student team repository. Keep changes small enough for a teammate to review and explain.

## Start a change

1. If you do not have a local checkout, clone the repository using the command in `README.md`.
2. Update your local `main` branch from GitHub.
3. Create a branch such as `docs/project-plan`, `feat/category-filter` or `fix/import-validation`.
4. Make one focused change and note any verified project status in `docs/WORK_LOG.md`.
5. Open a pull request to `main`. Include what changed, how you checked it, and any data or environment limitation.
6. Ask a teammate to review before merging. Keep course submission claims and source counts tied to evidence.

## Commit messages

Use a short type and description, for example `docs: add database diagram`, `feat: add location filter`, or `fix: hold workbook row without detail URL`. These examples are a team convention, not an automatic rule.

## Data and credentials

- Do not commit `.env`, database dumps, reviewed workbooks, raw capture files, screenshots of session URLs, or browser profiles.
- Keep the small, non-sensitive sample in `data/sample_tenders.json` source-labeled.
- Preserve missing values and record source/correction evidence. Do not merge suspected duplicates by title alone.
- Before committing a new file, check it for passwords, tokens, personal contact details and session query values.

## Pull-request checklist

- [ ] The change has one clear purpose and its paths/names are understandable to a teammate.
- [ ] Setup, audit or plan documentation was updated when the behavior or evidence changed.
- [ ] Source labels, missing fields and limitations remain visible.
- [ ] I have described what I checked and what remains unverified.
- [ ] No private workbook, database dump, credential or session-bearing URL is included.
