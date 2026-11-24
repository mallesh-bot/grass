import os

import pytest

import grass.script as gs
from grass.tools import ToolError, Tools


@pytest.fixture
def session(tmp_path):
    """Active session in an XY project with a 3D raster"""
    project = tmp_path / "xy_test"
    gs.create_project(project)
    with (
        gs.setup.init(project, env=os.environ.copy()) as session,
        Tools(session=session) as tools,
    ):
        tools.g_region(s=0, n=2, w=0, e=2, b=0, t=2, res=1, res3=1)
        tools.r3_mapcalc(expression="volume = 1")
        tools.r3_support(map="volume", title="Original title", vunit="meters")
        yield session


def test_unknown_vertical_unit_is_rejected(session):
    """An unknown vertical unit fails before any metadata is changed"""
    tools = Tools(session=session)

    with pytest.raises(ToolError):
        tools.r3_support(map="volume", title="New title", vunit="nanometers")

    info = tools.r3_info(map="volume", format="json")
    assert info["vertical_units"] == "meters"
    assert info["title"] == "Original title"
