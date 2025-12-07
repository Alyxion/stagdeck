"""Server runner for integration tests.

Run this module directly to start a test server:
    python -m tests._server_runner 8080
"""

import os
import sys


def run_test_server(port: int) -> None:
    """Run a StagDeck test server using the default showcase deck."""
    # Ensure clean environment for subprocess
    os.environ['NICEGUI_STORAGE_PATH'] = f'/tmp/nicegui_test_{port}'
    
    # Use the actual showcase deck for realistic testing
    from samples.default_deck_showcase.main import create_showcase_deck
    from stagdeck import App
    from stagdeck.renderer import setup_render_endpoint
    
    App.create_page(create_showcase_deck, path='/')
    setup_render_endpoint(path='/render')
    
    from nicegui import ui
    ui.run(port=port, show=False, reload=False, storage_secret='test')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python -m tests._server_runner <port>')
        sys.exit(1)
    port = int(sys.argv[1])
    run_test_server(port)
