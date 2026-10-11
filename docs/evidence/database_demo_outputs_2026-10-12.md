# Database demo outputs — 12 October 2026

Captured: `2026-10-12T02:57:07+05:30`

- MySQL records: **1572**
- MongoDB documents: **1572**
- The source-plan consistency check passed separately immediately before this capture.
- No source URL or raw workbook row is included in this evidence file.

## SQL examples

### SQL 1: Category join + grouping

8 category groups

```sql
SELECT c.name AS category, COUNT(*) AS tender_count,
       SUM(t.estimated_value_inr) AS total_estimated_value_inr
FROM tenders AS t
JOIN categories AS c ON c.category_id = t.category_id
GROUP BY c.category_id, c.name
ORDER BY tender_count DESC;
```

| category | tender_count | total_estimated_value_inr |
| --- | --- | --- |
| Civil Works | 1344 | 23656758121.00 |
| Civil Works - Others | 90 | 413275704.00 |
| Civil Works - Buildings | 34 | 1483975078.00 |
| Civil Works - Roads | 33 | 2506258909.00 |
| Civil Works - Water Works | 30 | 313092940.00 |
| Electrical and Maintenance Works | 23 | 150267604.00 |
| Construction Works | 13 | 9591748.00 |
| Civil Works - Bridges | 5 | 335344097.00 |

### SQL 2: Above-average estimated value subquery

75 matching tenders; first 5 shown

```sql
SELECT t.tender_key, t.title, t.estimated_value_inr
FROM tenders AS t
WHERE t.estimated_value_inr > (
    SELECT AVG(estimated_value_inr) FROM tenders
    WHERE estimated_value_inr IS NOT NULL
)
ORDER BY t.estimated_value_inr DESC;
```

| tender_key | title | estimated_value_inr |
| --- | --- | --- |
| mahatenders:2026_TMC_1342205_1 | Design, Engineering, Procurement and Construction (EPC) of 3,084 EWS Dwelling Units with allied Infrastructure, Amenities and Services on land bearing S.No. 15/1 and .No.78, Village Betawade, Thane, under Pradhan Mantri Awas Yojana (Urban) 2.0. | 5120643082.00 |
| mahatenders:2026_MSIDC_1339226_1 | Plot 1 Vidhanbhavan | 4400000000.00 |
| mahatenders:2026_MSIDC_1339232_1 | Plot 2 Vidhanbhavan | 2300000000.00 |
| mahatenders:2026_MMRDA_1336820_1 | ARCHITECTURAL FINISHING INCLUDING DESIGN FABRICATION SUPPLY ERECTION AND ROOF SHEETING OF PEB STRUCTURES AND DESIGN AND CONSTRUCTION OF EXTERNAL FACADE WATER SUPPLY SANITARY INSTALLATION DRAINAGE SITE DEVELOPMENT WORKS AT SIX 06 ELEVATED STATIONS | 1669098609.00 |
| mahatenders:2026_MMRDA_1336754_1 | ARCHITECTURAL FINISHING INCLUDING DESIGN FABRICATION SUPPLY ERECTION AND ROOF SHEETING OF PEB STRUCTURES AND DESIGN AND CONSTRUCTION OF EXTERNAL FACADE WATER SUPPLY SANITARY INSTALLATION DRAINAGE SITE DEVELOPMENT WORKS AT FIVE 05 ELEVATED STATIONS | 1341059610.00 |

### SQL 3: GROUP BY + HAVING location-label query

113 source-reported labels; first 10 shown

```sql
SELECT l.name AS location, COUNT(*) AS tender_count
FROM tenders AS t
JOIN locations AS l ON l.location_id = t.location_id
GROUP BY l.location_id, l.name
HAVING COUNT(*) >= 3
ORDER BY tender_count DESC, location;
```

| location | tender_count |
| --- | --- |
| Work | 69 |
| At Nagpur. | 67 |
| EE/EAST/MSIB | 62 |
| Under EE/East/MSIB | 53 |
| DE TURBHE | 39 |
| NMMC Zone-2 Dep Koparkhairane | 37 |
| Ahilyanagar | 30 |
| DE AIROLI | 29 |
| KW Ward | 27 |
| DAHISAR (E) | 24 |

## MongoDB examples

### Read one imported document

The projection intentionally excludes `source_url` and `raw_source_row`.

```json
{
  "_id": "mahatenders:2026_NMC_1342575_23",
  "source_record_id": "2026_NMC_1342575_23",
  "source_type": "MahaTenders official detail page",
  "title": "Repairing and Related Work at Vihitgaon Smashanbhoomi Bed P.No.22 in Nashik road Division.",
  "category": "Civil Works",
  "location": "P.No.22 in Nashik road Division",
  "scope": "Repairing and Related Work at Vihitgaon Smashanbhoomi Bed P.No.22 in Nashik road Division.",
  "eligibility": "Please refer Tender documents."
}
```

### Category aggregation (8 groups)

| category | tender_count |
| --- | --- |
| Civil Works | 1344 |
| Civil Works - Others | 90 |
| Civil Works - Buildings | 34 |
| Civil Works - Roads | 33 |
| Civil Works - Water Works | 30 |
| Electrical and Maintenance Works | 23 |
| Construction Works | 13 |
| Civil Works - Bridges | 5 |

### Temporary CRUD check

A schema-valid `demo:crud:*` record was created, read, updated, deleted, and checked absent. The cleanup ran even if a check failed; no imported tender was changed.

| Operation | Result |
| --- | --- |
| create | passed |
| read | passed |
| update | passed |
| delete | passed |
| final absence check | passed |

Interpret the third SQL query as a count of source-reported labels. Labels such as `Work` and `EE/EAST/MSIB` are not necessarily standardized geographic locations.

Estimates are published estimates, not awards or actual spending; missing estimates remain NULL.
