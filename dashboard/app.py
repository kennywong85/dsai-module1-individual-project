from pathlib import Path

import duckdb
import streamlit as st


# -----------------------------
# Page setup
# -----------------------------

st.set_page_config(
    page_title="Career Coach - Job Market Navigator",
    layout="wide"
)

st.title("Career Coach - Job Market Navigator")

st.write(
    """
    This dashboard helps career coaches explore Singapore job postings by
    market demand, salary range, experience requirements, and career opportunity signals.
    """
)


# -----------------------------
# Database path
# -----------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "db" / "jobs.duckdb"

st.caption(f"Database path: `{DB_PATH}`")


if not DB_PATH.exists():
    st.error("Database not found. Run `python src/create_database.py` first.")
    st.stop()


# -----------------------------
# Query helper
# -----------------------------

@st.cache_data
def run_query(query):
    """
    Run a SQL query against the local DuckDB database
    and return the result as a DataFrame.
    """
    con = duckdb.connect(str(DB_PATH), read_only=True)
    result = con.execute(query).df()
    con.close()
    return result


# -----------------------------
# Dataset summary
# -----------------------------

summary_query = """
SELECT
    COUNT(DISTINCT job_post_id) AS total_unique_job_postings,
    COUNT(DISTINCT category_name) AS total_categories,
    COUNT(DISTINCT company_name) AS total_companies,
    MIN(new_posting_date) AS earliest_posting_date,
    MAX(new_posting_date) AS latest_posting_date
FROM vw_career_coach_jobs;
"""

summary_df = run_query(summary_query)

st.subheader("Dataset Summary")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Unique Job Postings",
    f"{summary_df.loc[0, 'total_unique_job_postings']:,}"
)

col2.metric(
    "Categories",
    f"{summary_df.loc[0, 'total_categories']:,}"
)

col3.metric(
    "Companies",
    f"{summary_df.loc[0, 'total_companies']:,}"
)

st.caption(
    f"Posting date range: {summary_df.loc[0, 'earliest_posting_date']} "
    f"to {summary_df.loc[0, 'latest_posting_date']}"
)


# -----------------------------
# Dashboard tabs
# -----------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Market Demand",
        "Salary Ranges",
        "Experience Requirements",
        "Opportunity Score"
    ]
)


# -----------------------------
# Tab 1: Market Demand
# -----------------------------

with tab1:
    st.header("Market Demand")

    st.write(
        """
        This section helps career coaches identify job categories with stronger
        visible market demand.
        """
    )

    postings_query = """
    SELECT
        category_name,
        COUNT(DISTINCT job_post_id) AS total_job_postings
    FROM vw_career_coach_jobs
    WHERE category_name IS NOT NULL
    GROUP BY category_name
    ORDER BY total_job_postings DESC
    LIMIT 10;
    """

    top_categories_by_postings = run_query(postings_query)

    vacancies_query = """
    SELECT
        category_name,
        SUM(number_of_vacancies) AS total_vacancies
    FROM vw_career_coach_jobs
    WHERE category_name IS NOT NULL
    GROUP BY category_name
    ORDER BY total_vacancies DESC
    LIMIT 10;
    """

    top_categories_by_vacancies = run_query(vacancies_query)

    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Top Categories by Job Postings")
        st.dataframe(top_categories_by_postings, use_container_width=True)

        chart_data = top_categories_by_postings.set_index("category_name")
        st.bar_chart(chart_data["total_job_postings"])

    with right_col:
        st.subheader("Top Categories by Vacancies")
        st.dataframe(top_categories_by_vacancies, use_container_width=True)

        chart_data = top_categories_by_vacancies.set_index("category_name")
        st.bar_chart(chart_data["total_vacancies"])


# -----------------------------
# Tab 2: Salary Ranges
# -----------------------------

with tab2:
    st.header("Salary Ranges")

    st.write(
        """
        This section compares median salary ranges across job categories.

        Median salary is used instead of average salary because salary data can contain
        outliers. This gives career coaches a more stable reference point for salary
        expectation discussions.
        """
    )

    salary_query = """
    SELECT
        category_name,
        COUNT(DISTINCT job_post_id) AS total_job_postings,
        MEDIAN(salary_minimum) AS median_salary_minimum,
        MEDIAN(salary_maximum) AS median_salary_maximum,
        MEDIAN(average_salary) AS median_average_salary
    FROM vw_career_coach_jobs
    WHERE category_name IS NOT NULL
      AND average_salary IS NOT NULL
    GROUP BY category_name
    ORDER BY median_average_salary DESC
    LIMIT 10;
    """

    salary_by_category = run_query(salary_query)

    st.subheader("Top Categories by Median Average Salary")

    st.dataframe(
        salary_by_category,
        use_container_width=True
    )

    chart_data = salary_by_category.set_index("category_name")

    st.bar_chart(chart_data["median_average_salary"])

    st.caption(
        """
        Note: Higher salary categories may also require more specialised skills,
        stronger experience, or higher qualifications. Career coaches should compare
        salary together with demand and experience requirements.
        """
    )

# -----------------------------
# Tab 3: Experience Requirements
# -----------------------------

with tab3:
    st.header("Experience Requirements")

    st.write(
        """
        This section helps career coaches identify job categories with lower
        experience requirements and stronger entry-level availability.

        This is useful when advising fresh graduates, early-career jobseekers,
        or mid-career switchers.
        """
    )

    experience_query = """
    SELECT
        category_name,
        COUNT(DISTINCT job_post_id) AS total_job_postings,
        MEDIAN(minimum_years_experience) AS median_min_years_experience,
        AVG(minimum_years_experience) AS average_min_years_experience
    FROM vw_career_coach_jobs
    WHERE category_name IS NOT NULL
      AND minimum_years_experience IS NOT NULL
    GROUP BY category_name
    ORDER BY median_min_years_experience ASC, total_job_postings DESC
    LIMIT 10;
    """

    experience_by_category = run_query(experience_query)

    entry_level_query = """
    SELECT
        category_name,
        COUNT(DISTINCT job_post_id) AS entry_level_job_postings,
        MEDIAN(average_salary) AS median_average_salary,
        MEDIAN(minimum_years_experience) AS median_min_years_experience
    FROM vw_career_coach_jobs
    WHERE category_name IS NOT NULL
      AND minimum_years_experience <= 1
    GROUP BY category_name
    ORDER BY entry_level_job_postings DESC
    LIMIT 10;
    """

    entry_level_friendly_categories = run_query(entry_level_query)

    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("Lower Experience Requirement Categories")

        st.dataframe(
            experience_by_category,
            use_container_width=True
        )

        chart_data = experience_by_category.set_index("category_name")

        st.bar_chart(chart_data["median_min_years_experience"])

    with right_col:
        st.subheader("Entry-Level Friendly Categories")

        st.dataframe(
            entry_level_friendly_categories,
            use_container_width=True
        )

        chart_data = entry_level_friendly_categories.set_index("category_name")

        st.bar_chart(chart_data["entry_level_job_postings"])

    st.caption(
        """
        Note: Lower experience requirements do not automatically mean a role is easy
        to obtain. Career coaches should still consider skills, qualifications,
        competition, and jobseeker fit.
        """
    )

    # -----------------------------
# Tab 4: Career Opportunity Score
# -----------------------------

with tab4:
    st.header("Career Opportunity Score")

    st.write(
        """
        This section creates a simple prototype score to compare job categories.

        The score combines three signals:

        1. Demand: job postings and vacancies
        2. Salary: median average salary
        3. Accessibility: lower experience requirements and more entry-level postings

        This is not a final recommendation engine. It is a simple scoring prototype
        to help career coaches compare job categories more easily.
        """
    )

    minimum_postings = st.slider(
        "Minimum job postings required for a category to be scored",
        min_value=0,
        max_value=1000,
        value=100,
        step=50
    )

    category_summary_query = f"""
    SELECT
        category_name,
        COUNT(DISTINCT job_post_id) AS total_job_postings,
        SUM(number_of_vacancies) AS total_vacancies,
        MEDIAN(average_salary) AS median_average_salary,
        MEDIAN(minimum_years_experience) AS median_min_years_experience,
        COUNT(DISTINCT CASE
            WHEN minimum_years_experience <= 1 THEN job_post_id
        END) AS entry_level_job_postings
    FROM vw_career_coach_jobs
    WHERE category_name IS NOT NULL
    GROUP BY category_name
    HAVING COUNT(DISTINCT job_post_id) >= {minimum_postings}
    ORDER BY total_job_postings DESC;
    """

    category_summary = run_query(category_summary_query)

    if category_summary.empty:
        st.warning(
            "No categories match the selected minimum job postings threshold."
        )

    else:
        category_summary["entry_level_share"] = (
            category_summary["entry_level_job_postings"]
            / category_summary["total_job_postings"]
        )

        score_df = category_summary.copy()

        score_df = score_df.dropna(
            subset=[
                "total_job_postings",
                "total_vacancies",
                "median_average_salary",
                "median_min_years_experience",
                "entry_level_share"
            ]
        )

        # Demand score rewards categories with more postings and vacancies.
        score_df["posting_score"] = (
            score_df["total_job_postings"].rank(pct=True) * 100
        )

        score_df["vacancy_score"] = (
            score_df["total_vacancies"].rank(pct=True) * 100
        )

        score_df["demand_score"] = (
            score_df["posting_score"] * 0.5
            + score_df["vacancy_score"] * 0.5
        )

        # Salary score rewards higher median salary.
        score_df["salary_score"] = (
            score_df["median_average_salary"].rank(pct=True) * 100
        )

        # Accessibility score rewards lower experience requirements
        # and higher entry-level share.
        score_df["low_experience_score"] = (
            score_df["median_min_years_experience"]
            .rank(pct=True, ascending=False) * 100
        )

        score_df["entry_level_score"] = (
            score_df["entry_level_share"].rank(pct=True) * 100
        )

        score_df["accessibility_score"] = (
            score_df["low_experience_score"] * 0.5
            + score_df["entry_level_score"] * 0.5
        )

        # Final opportunity score.
        score_df["opportunity_score"] = (
            score_df["demand_score"] * 0.4
            + score_df["salary_score"] * 0.3
            + score_df["accessibility_score"] * 0.3
        )

        opportunity_score = score_df.sort_values(
            "opportunity_score",
            ascending=False
        ).reset_index(drop=True)

        opportunity_score["entry_level_share_percent"] = (
            opportunity_score["entry_level_share"] * 100
        )

        display_columns = [
            "category_name",
            "total_job_postings",
            "total_vacancies",
            "median_average_salary",
            "median_min_years_experience",
            "entry_level_share_percent",
            "demand_score",
            "salary_score",
            "accessibility_score",
            "opportunity_score"
        ]

        st.subheader("Top Categories by Career Opportunity Score")

        st.dataframe(
            opportunity_score[display_columns].head(10),
            use_container_width=True
        )

        chart_data = (
            opportunity_score[["category_name", "opportunity_score"]]
            .head(10)
            .set_index("category_name")
        )

        st.bar_chart(chart_data["opportunity_score"])

        st.caption(
            """
            Score weights: Demand 40%, Salary 30%, Accessibility 30%.

            Accessibility rewards categories with lower median experience requirements
            and a higher share of entry-level job postings.
            """
        )

        st.subheader("How to Interpret This Score")

        st.write(
            """
            A high score means the category performs relatively well across the selected
            labour-market signals. It does not mean the category is suitable for every
            jobseeker.

            Career coaches should still consider the jobseeker's skills, background,
            interests, qualifications, and constraints before making recommendations.
            """
        )