from __future__ import annotations

import socket
import urllib.request

import pytest


@pytest.fixture(autouse=True, scope="session")
def block_real_network_calls() -> None:
    patcher = pytest.MonkeyPatch()

    def blocked_connect(*args: object, **kwargs: object) -> None:
        raise AssertionError("network access blocked during tests")

    def blocked_urlopen(*args: object, **kwargs: object) -> None:
        raise AssertionError("network access blocked during tests")

    patcher.setattr(socket.socket, "connect", blocked_connect)
    patcher.setattr(urllib.request, "urlopen", blocked_urlopen)
    yield
    patcher.undo()
