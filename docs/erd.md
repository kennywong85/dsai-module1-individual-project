# ERD Design

## 1 Purpose

This database design supports a career-coaching dashboard using Singapore job postings data.

The dashboard focuses on three use cases:

1. Identify market demand
2. Identify salary ranges
3. Identify experience requirements

## 2 Data Assumptions

The following assumptions are used:

1. Each row in the CSV represents one job posting.
2. Each job posting has one company.
3. Each job posting has one employment type.
4. Each job posting has one position level.
5. Each job posting has one salary range.
6. Each job posting can belong to multiple job categories.

The main field that needs special handling is `categories`, because one job posting can have more than one category.

## 3 ERD Design

The ERD was created using DBML and visualised in dbdiagram.io.

The database has one main table: `job_posting`.

The supporting lookup tables are:

- `company`
- `employment_type`
- `position_level`
- `category`

The `job_category` table is used as a bridge table because one job posting can belong to multiple categories.

The DBML source file is saved in:

`docs/erd.dbml`

An exported ERD image can be saved later in:

`outputs/erd.png`