-- Join + grouping: category counts and total estimated tender value.
SELECT c.name AS category, COUNT(*) AS tender_count,
       SUM(t.estimated_value_inr) AS total_estimated_value_inr
FROM tenders AS t
JOIN categories AS c ON c.category_id = t.category_id
GROUP BY c.category_id, c.name
ORDER BY tender_count DESC;

-- Subquery: works tenders with an estimated value above the works average.
SELECT t.tender_key, t.title, t.estimated_value_inr
FROM tenders AS t
WHERE t.estimated_value_inr > (
    SELECT AVG(estimated_value_inr) FROM tenders
    WHERE estimated_value_inr IS NOT NULL
)
ORDER BY t.estimated_value_inr DESC;

-- GROUP BY + HAVING: source-reported location labels with at least three tenders.
SELECT l.name AS location, COUNT(*) AS tender_count
FROM tenders AS t
JOIN locations AS l ON l.location_id = t.location_id
GROUP BY l.location_id, l.name
HAVING COUNT(*) >= 3
ORDER BY tender_count DESC, location;
