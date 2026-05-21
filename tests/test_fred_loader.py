"""Tests for FRED data loader."""
from econ_fragility.fred_loader import FRED_SERIES, DOMAIN_MAP

def test_all_series_mapped():
    mapped = set()
    for sl in DOMAIN_MAP.values():
        mapped.update(sl)
    for sid in FRED_SERIES:
        assert sid in mapped, f"{sid} not mapped"

def test_domain_count():
    assert len(DOMAIN_MAP) == 6

def test_series_count():
    assert len(FRED_SERIES) == 45
