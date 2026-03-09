"""Shared pytest fixtures for the ATLAS test suite.

The `no_memory_persistence` fixture (autouse) prevents any test from writing
to atlas_data/memory.json.  Tests that explicitly exercise the save/load
implementation should be marked with @pytest.mark.uses_real_memory_io to
opt out of the mock.
"""
import pytest
from unittest.mock import patch


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "uses_real_memory_io: test calls ConversationMemory.save/load directly "
        "and must not have those methods mocked.",
    )


@pytest.fixture(autouse=True)
def no_memory_persistence(request):
    """Mock ConversationMemory file I/O for every test that does not opt out."""
    if request.node.get_closest_marker("uses_real_memory_io"):
        yield  # let the test exercise the real implementation
        return

    with patch("projrvt.memory.ConversationMemory.save"), \
         patch("projrvt.memory.ConversationMemory.load"):
        yield
