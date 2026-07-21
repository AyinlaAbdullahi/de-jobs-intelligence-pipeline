import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_config.role_skills import get_role_type, role_skills


def test_identifies_data_engineer_title():
    assert get_role_type("Senior Data Engineer") == "data engineering"


def test_identifies_analytics_engineer_as_de():
    assert get_role_type("Analytics Engineer, Growth") == "data engineering"


def test_identifies_product_manager_title():
    assert get_role_type("Product Manager, Growth") == "product management"


def test_identifies_product_management_phrase():
    assert get_role_type("Head of Product Management") == "product management"


def test_unmatched_title_defaults_to_data_engineering():
    assert get_role_type("Executive Assistant") == "data engineering"


def test_empty_title_does_not_crash():
    assert get_role_type("") == "data engineering"
    assert get_role_type(None) == "data engineering"


def test_is_case_insensitive():
    assert get_role_type("SENIOR PRODUCT MANAGER") == "product management"


def test_all_roles_have_required_keys():
    for role_name, config in role_skills.items():
        assert "match_keywords" in config
        assert "skills" in config
        assert "priority_skills" in config
        assert len(config["skills"]) > 0
