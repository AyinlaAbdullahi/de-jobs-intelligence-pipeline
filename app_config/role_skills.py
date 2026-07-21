role_skills = {
    "data engineering": {
        "match_keywords": ["data engineer", "analytics engineer", "etl", "data platform"],
        "skills": [
            "python", "sql", "airflow", "dbt", "docker",
            "postgresql", "postgres", "snowflake", "streamlit",
            "pandas", "git", "github", "azure", "databricks",
            "spark", "pyspark", "etl", "elt", "pipeline",
        ],
        "priority_skills": ["python", "sql", "airflow", "dbt", "spark", "azure"],
    },
    "product management": {
        "match_keywords": ["product manager", "product management"],
        "skills": [
            "roadmap", "product strategy", "stakeholder", "agile", "scrum",
            "user research", "customer discovery", "prioritization", "backlog",
            "cross-functional", "go-to-market", "product vision", "kpi",
            "a/b test", "analytics", "sql", "jira", "wireframe", "okr",
            "product launch", "user experience",
        ],
        "priority_skills": ["roadmap", "product strategy", "stakeholder", "cross-functional", "okr"],
    },
}


def get_role_type(title: str) -> str:
    title_lower = (title or "").lower()
    for role_name, config in role_skills.items():
        if any(keyword in title_lower for keyword in config["match_keywords"]):
            return role_name
    return "data engineering"