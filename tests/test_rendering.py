"""Unit tests for Plotsiris rendering and application factory."""

from plotsiris.services.data_manager import DataManager
from plotsiris.rendering.map_builder import MapBuilder
from plotsiris.rendering.graph_builder import EntityGraphBuilder
from plotsiris.app import create_app


def test_map_builder():
    dm = DataManager()
    entities = dm.get_all_entities()
    routes = dm.get_route_paths()
    fig = MapBuilder.build_map(entities, routes, theme="ghost")
    assert fig is not None
    assert len(fig.data) > 0


def test_entity_graph_builder():
    fig = EntityGraphBuilder.build_graph(theme="ghost")
    assert fig is not None
    assert len(fig.data) >= 2  # edge trace, background star nodes, and core node trace


def test_create_app():
    app = create_app()
    assert app is not None
    assert app.title.startswith("Plotsiris")
    assert app.layout is not None
