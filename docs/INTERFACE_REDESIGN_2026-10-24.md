# Works Atlas interface update

**Updated:** 24 October 2026
**Project:** Maharashtra Works Tender Explorer

## Design direction

The interface presents the project as a practical works-tender atlas. It uses dark charcoal surfaces, ivory text, amber accents, and original bridge linework. The page keeps the main tasks visible: search listings, narrow the results, inspect a record, and review database queries.

The redesign uses the existing Streamlit app and project CSS. It adds no remote fonts, image assets, or third-party code.

## What changed

- Added a compact project masthead with original bridge artwork.
- Kept the three workspaces: **Tenders**, **Overview**, and **Query studio**.
- Added a card view with six records per page and a full-table option with the native CSV toolbar.
- Added sorting by closing date, reported estimate, and title.
- Moved source, category, location, and closing-date filters into expandable controls.
- Kept the selected record by its source-prefixed key when filters or page state change.
- Added an inspector for reported estimate, EMD, source metadata, safe source links, and the matching MongoDB details.
- Kept the Overview charts and the Query studio's SQL/MongoDB examples, guide, and safety limits.

## How a search reaches the databases

~~~mermaid
flowchart TD
    A[Choose Sample or MySQL + MongoDB] --> B[Enter a search and optional filters]
    B --> C{Selected mode}
    C -->|Sample| D[Filter the bundled 129 records in Python]
    C -->|MySQL + MongoDB| E[Build a parameterized SQL query]
    E --> F[MySQL returns matching listing fields]
    D --> G[Show cards or the full table]
    F --> G
    G --> H[Select a listing]
    H --> I{Selected mode}
    I -->|Sample| J[Read the bundled detail]
    I -->|MySQL + MongoDB| K[Find the MongoDB document by tender key]
    J --> L[Show details and a sanitized source link]
    K --> L
~~~

The Query studio is a separate, user-started path. SQL searches are limited to read-only queries, and MongoDB searches use the project's field/operator checks. Results are capped before display.

## Verification recorded on 24 October

- All 13 existing normalization and query-safety tests passed.
- The [UI verification script](../scripts/verify_atlas_ui.py) used Streamlit AppTest to check the 1,572-record database render, card selection, a second page, search and pagination reset, estimate sorting, the table view, empty search, an empty category selection, SQL search, MongoDB search, the 129-record sample mode, sample cards, and return to database mode.
- The app health endpoint returned ok.
- The recorded AppTest run is functional evidence. It does not prove how the page looks at desktop or narrow-screen widths.

## Still to check

A refreshed screenshot review of the redesigned dashboard has not been completed. Before using screenshots as final presentation evidence, inspect the Tenders, Overview, and Query studio workspaces at desktop and narrow widths. Check card/table readability, the inspector, keyboard focus, and contrast, then save updated screenshots under the evidence folder. Do not describe the visual review as complete until that evidence exists.

## Design references

These references informed layout and component research; the implementation remains in the project files.

- [Refero design prompts](https://styles.refero.design/ai-agents/design-prompts)
- [Linear: behind the latest design refresh](https://linear.app/now/behind-the-latest-design-refresh)
- [Carbon Design System: data table usage](https://v10.carbondesignsystem.com/components/data-table/usage/)