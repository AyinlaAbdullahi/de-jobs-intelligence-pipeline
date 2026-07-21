import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.loader import generate_job_hash


def test_same_inputs_produce_same_hash():
    hash1 = generate_job_hash("Data Engineer", "Stripe", "https://example.com/job/1")
    hash2 = generate_job_hash("Data Engineer", "Stripe", "https://example.com/job/1")
    assert hash1 == hash2


def test_different_urls_produce_different_hashes():
    hash1 = generate_job_hash("Data Engineer", "Stripe", "https://example.com/job/1")
    hash2 = generate_job_hash("Data Engineer", "Stripe", "https://example.com/job/2")
    assert hash1 != hash2


def test_different_titles_produce_different_hashes():
    hash1 = generate_job_hash("Data Engineer", "Stripe", "https://example.com/job/1")
    hash2 = generate_job_hash("Senior Data Engineer", "Stripe", "https://example.com/job/1")
    assert hash1 != hash2


def test_case_insensitive_title_and_company():
    hash1 = generate_job_hash("Data Engineer", "Stripe", "https://example.com/job/1")
    hash2 = generate_job_hash("DATA ENGINEER", "STRIPE", "https://example.com/job/1")
    assert hash1 == hash2


def test_whitespace_is_stripped():
    hash1 = generate_job_hash("Data Engineer", "Stripe", "https://example.com/job/1")
    hash2 = generate_job_hash("  Data Engineer  ", "  Stripe  ", "https://example.com/job/1")
    assert hash1 == hash2


def test_hash_is_a_valid_sha256_hex_string():
    result = generate_job_hash("Data Engineer", "Stripe", "https://example.com/job/1")
    assert len(result) == 64
    assert all(c in "0123456789abcdef" for c in result)
