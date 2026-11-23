"""Test the units of m.measure in projected projects"""

import os

import pytest

import grass.script as gs
from grass.tools import Tools

# A square with sides of 10 map units
COORDINATES = [0, 0, 10, 0, 10, 10, 0, 10]
US_FOOT_IN_METERS = 1200 / 3937


def measure(tmp_path, epsg, **kwargs):
    """Measure the square in a new project and return the JSON output"""
    project = tmp_path / "test"
    gs.create_project(project, epsg=epsg)
    with (
        gs.setup.init(project, env=os.environ.copy()) as session,
        Tools(session=session) as tools,
    ):
        return tools.m_measure(coordinates=COORDINATES, format="json", **kwargs).json


def test_us_feet_default_units(tmp_path):
    """Without units, the result is in map units, not in meters"""
    data = measure(tmp_path, epsg="2240")
    assert data["length"] == pytest.approx(30)
    assert data["area"] == pytest.approx(100)
    assert data["units"] == {"length": "units", "area": "square units"}


def test_us_feet_meters(tmp_path):
    """With units, the map units are converted"""
    data = measure(tmp_path, epsg="2240", units="meters")
    assert data["length"] == pytest.approx(30 * US_FOOT_IN_METERS)
    assert data["area"] == pytest.approx(100 * US_FOOT_IN_METERS**2)
    assert data["units"] == {"length": "meters", "area": "square meters"}


def test_meters_default_units(tmp_path):
    """Without units, the result is in meters in a project in meters"""
    data = measure(tmp_path, epsg="3857")
    assert data["length"] == pytest.approx(30)
    assert data["area"] == pytest.approx(100)
    assert data["units"] == {"length": "meters", "area": "square meters"}
