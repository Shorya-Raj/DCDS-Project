# Query explorer guide

Open the dashboard, choose **MySQL + MongoDB** in the sidebar, then use the **Query explorer and guide** link. The Query explorer is below the tender details. Open **Queries used by the dashboard** to see the exact SQL used by the current sidebar filters, the values bound to its placeholders, and the MongoDB lookup for the selected listing.

## Use the sidebar query display

1. Change Category, Location, Search, or Closing today or later.
2. Open Queries used by the dashboard.
3. Read the SQL and the bound values together. Each %s placeholder receives the value in the matching position. Search text is sent as a value, not assembled into SQL code.
4. Select a different listing to see its MongoDB find_one lookup by the shared tender key.

The category and location choices come from two small SQL queries shown in the nested expander. Their lists may be cached for up to 60 seconds. The tender result query and selected MongoDB detail lookup run when the app reruns.

## Write your own SQL search

Choose **Write SQL**, load an example, edit it, and press **Run SQL search**. Use one SELECT statement with no trailing semicolon. The editor accepts joins, filters, grouping, sorting, and limits. The available project tables are tenders, categories, and locations.

    SELECT t.source_record_id, t.title, c.name AS category, l.name AS location
    FROM tenders AS t
    JOIN categories AS c ON c.category_id = t.category_id
    JOIN locations AS l ON l.location_id = t.location_id
    WHERE c.name = 'Civil Works'
    ORDER BY t.closing_date DESC
    LIMIT 20

Useful columns in tenders include source_record_id, title, closing_date, estimated_value_inr, and emd_inr. Category and location names are in their separate tables. Put text in single quotes. Dates use YYYY-MM-DD.

The SQL search runs in a read-only transaction and has a three-second server time limit. The page shows at most 100 result rows. Write queries that narrow the data before joining or sorting large sets. Commands that change the database, comments, variables, and multiple statements are rejected.

## Write your own MongoDB search

Choose **Write MongoDB filter**, load an example, edit its JSON, and press **Run MongoDB search**. This runs a find on tender_details and displays selected summary fields.

    {"category": "Civil Works"}

    {"$and": [{"category": "Civil Works"}, {"closing_date": {"$gte": "2026-10-01"}}]}

Use double quotes around JSON field names and text. Use null for a missing value, and true or false for an exists check. Supported comparisons are $eq, $ne, $gt, $gte, $lt, $lte, $in, and $exists. Combine conditions with $and or $or. Searches are limited to 100 displayed rows and three seconds. The editor rejects commands, JavaScript expressions, raw source fields, and unsupported operators.

## How the two databases connect

MySQL stores the main searchable fields and joins the category and location tables. MongoDB stores source-specific details. Both use the same source-prefixed tender key. The dashboard's listing selector uses that key to find the matching MongoDB document.

All tender data is a saved snapshot. An estimated value is not an award or actual expenditure. The full captured source URL and raw source rows are not shown in the query result tables because source links may include session parameters.
