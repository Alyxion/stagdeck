"""Pytest configuration and fixtures."""

import atexit
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest


# Track server process globally for cleanup
_server_process: subprocess.Popen | None = None


def _cleanup_server():
    """Cleanup function registered with atexit."""
    global _server_process
    if _server_process is not None:
        try:
            _server_process.terminate()
            _server_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _server_process.kill()
            _server_process.wait(timeout=2)
        except Exception:
            pass
        finally:
            _server_process = None


# Register cleanup at interpreter exit
atexit.register(_cleanup_server)


def _wait_for_server(port: int, timeout: float = 30.0) -> bool:
    """Wait for server to be ready."""
    import httpx
    
    start = time.time()
    while time.time() - start < timeout:
        try:
            # Use 127.0.0.1 explicitly to avoid IPv6 delays
            response = httpx.get(f'http://127.0.0.1:{port}/', timeout=2.0)
            if response.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def _is_port_in_use(port: int) -> bool:
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


@pytest.fixture(scope='session')
def stagdeck_server(request):
    """Start a StagDeck server for integration tests.
    
    This fixture starts a real server in a subprocess before integration
    tests run and tears it down afterwards.
    """
    global _server_process
    
    port = 8080
    
    # Check if port is free - fail with clear message if not
    if _is_port_in_use(port):
        pytest.fail(
            f'Port {port} is already in use. '
            f'Please stop any running server before running integration tests.\n'
            f'Run: lsof -ti:{port} | xargs kill -9'
        )
    
    # Start server as subprocess with clean environment
    # Remove pytest-related env vars that confuse NiceGUI
    env = os.environ.copy()
    for key in list(env.keys()):
        if 'PYTEST' in key or 'NICEGUI' in key:
            del env[key]
    
    _server_process = subprocess.Popen(
        [sys.executable, '-m', 'tests._server_runner', str(port)],
        cwd=Path(__file__).parent.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    
    # Wait for server to be ready
    if not _wait_for_server(port):
        # Capture output for debugging
        stdout, stderr = b'', b''
        try:
            stdout, stderr = _server_process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            pass
        _cleanup_server()
        error_msg = f'Server failed to start on port {port}'
        if stderr:
            error_msg += f'\nstderr: {stderr.decode()[:500]}'
        pytest.fail(error_msg)
    
    yield {'port': port, 'base_url': f'http://localhost:{port}'}
    
    # Teardown: terminate server
    _cleanup_server()


@pytest.fixture
def themes_dir() -> Path:
    """Path to the built-in themes directory."""
    return Path(__file__).parent.parent / 'stagdeck' / 'templates' / 'themes'


@pytest.fixture
def aurora_theme_path(themes_dir: Path) -> Path:
    """Path to aurora theme file."""
    return themes_dir / 'aurora.json'


@pytest.fixture
def midnight_theme_path(themes_dir: Path) -> Path:
    """Path to midnight theme file."""
    return themes_dir / 'midnight.json'
