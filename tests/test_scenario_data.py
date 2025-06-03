import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scenario_data import load_scenario, Scenario


def test_load_scenario_spionage01():
    scenario = load_scenario("SPIONAGE01")
    assert isinstance(scenario, Scenario)
    assert scenario.title
    assert len(scenario.suspects) == 3
    assert scenario.culprit_id == "B"


def test_get_suspect_case_insensitive():
    scenario = load_scenario("SPIONAGE01")
    suspect = scenario.get_suspect("a")
    assert suspect is not None
    assert suspect.name == "Peter Schmidt"
    assert scenario.get_suspect("B").is_culprit


def test_get_suspect_invalid():
    scenario = load_scenario("SPIONAGE01")
    assert scenario.get_suspect("Z") is None
