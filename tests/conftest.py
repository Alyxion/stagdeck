"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path


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
