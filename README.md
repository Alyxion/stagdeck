# StagDeck

A NiceGUI-based presentation tool for creating and displaying slide decks.

## Setup

```bash
poetry install
```

## Run

```bash
poetry run python main.py
```

Then open http://localhost:8080 in your browser.

## Features

- Create slide decks with multiple slides
- Navigate between slides with keyboard arrows or buttons
- Support for titles, content, and markdown
- Custom slide builders for complex layouts
- Fullscreen presentation mode (press F)
- Responsive scaling to fit any screen

## Usage

```python
from stagdeck import SlideDeck

deck = SlideDeck(title='My Presentation')
deck.add(title='Hello World', content='My first slide!')
deck.build()
```

## License

Copyright © 2025 Michael Ikemann. Licensed under the AGPL-3.0 License.
