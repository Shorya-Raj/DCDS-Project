# Interface design and verification

Updated 20 October 2026.

## Design direction

The explorer is a research workspace for civil and infrastructure records. Its architectural illustration, forest-green header, editorial heading, and muted sage surfaces give it a distinct public-works identity. All illustration and styling are local; no external font service or image download is required. The user specifically requested softer surfaces instead of pure white.

The first styling pass was expanded into a layout redesign following user feedback:

- Tenders: central search, summary metrics, a searchable/exportable result table, and a record inspector alongside it on wide screens.
- Overview: the existing category chart, source provenance notes, and data-model explanation.
- Query studio: the actual dashboard queries, SQL editor, MongoDB filter editor, results, and guide.
- Narrow screens: result and inspector columns stack; the decorative illustration is hidden; native controls remain available.

The source selector and category/location/date filters retain their existing behavior. Source URL sanitization, query validation, data calculations, and database writes/imports were not changed. Sample mode continues to identify its third-party records.

## Research used

- Streamlit's official theming guidance: use supported configuration for widget, table, code, and sidebar colors. https://docs.streamlit.io/develop/concepts/configuration/theming
- Streamlit's color and border documentation: use consistent surface, border, and interaction colors. https://docs.streamlit.io/develop/concepts/configuration/theming-customize-colors-and-borders
- GOV.UK Design System color guidance: keep functional color use consistent and maintain readable contrast. This project has its own visual identity and does not claim government affiliation. https://design-system.service.gov.uk/styles/colour/

## Checks

- All 13 existing unit tests passed using the project's Python environment.
- Streamlit AppTest exercised the redesigned layout with local MySQL and MongoDB: 1,572 records, a changed listing selection, 46 Nashik matches, 20 SQL example results, 100 capped MongoDB results, no-match state, and 129 sample records.
- Browser checks covered workspace navigation, the query guide, desktop layout, and a 390-pixel viewport. The narrow layout had no page-wide horizontal overflow; data tables retain their own scrolling.
- These checks cover the local coursework app. They do not constitute an exhaustive accessibility audit or a deployment test.
