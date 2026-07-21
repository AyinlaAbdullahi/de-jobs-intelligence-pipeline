import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.cleaner import parse_salary, is_accessible_from_nigeria, infer_experience_level


def test_parse_salary_with_range():
    salary_min, salary_max, currency = parse_salary("50000-70000 USD")
    assert salary_min == 50000
    assert salary_max == 70000
    assert currency == "USD"


def test_parse_salary_with_k_suffix():
    salary_min, salary_max, currency = parse_salary("80k-100k")
    assert salary_min == 80000
    assert salary_max == 100000


def test_parse_salary_single_value():
    salary_min, salary_max, currency = parse_salary("60000")
    assert salary_min == 60000
    assert salary_max == 60000


def test_parse_salary_empty_string():
    salary_min, salary_max, currency = parse_salary("")
    assert salary_min is None
    assert salary_max is None
    assert currency == "USD"


def test_parse_salary_none_input():
    salary_min, salary_max, currency = parse_salary(None)
    assert salary_min is None
    assert salary_max is None


def test_parse_salary_detects_gbp():
    salary_min, salary_max, currency = parse_salary("£40000-£60000")
    assert currency == "GBP"


def test_parse_salary_detects_eur():
    salary_min, salary_max, currency = parse_salary("€40000-€60000")
    assert currency == "EUR"


def test_parse_salary_ignores_unrealistic_numbers():
    # numbers outside the sane 10000-1000000 range should be dropped
    salary_min, salary_max, currency = parse_salary("5-10")
    assert salary_min is None
    assert salary_max is None


def test_accessible_empty_location_defaults_true():
    assert is_accessible_from_nigeria("") is True
    assert is_accessible_from_nigeria(None) is True


def test_accessible_rejects_onsite():
    assert is_accessible_from_nigeria("Onsite - New York") is False


def test_accessible_rejects_hybrid():
    assert is_accessible_from_nigeria("Hybrid - London") is False


def test_accessible_accepts_remote():
    assert is_accessible_from_nigeria("Remote - US") is True


def test_infer_experience_level_junior():
    assert infer_experience_level("Junior Data Engineer") == "junior"


def test_infer_experience_level_senior():
    assert infer_experience_level("Senior Data Engineer") == "senior"


def test_infer_experience_level_manager():
    assert infer_experience_level("Engineering Manager") == "manager"


def test_infer_experience_level_intern():
    assert infer_experience_level("Data Engineering Intern") == "intern"


def test_infer_experience_level_default_is_mid():
    assert infer_experience_level("Data Engineer") == "mid"
