# Default Deck Showcase

This sample demonstrates all available slide layouts in the StagDeck default master deck.

## Running

```bash
cd samples/default_deck_showcase
python main.py
```

Then open http://localhost:8080 in your browser.

## Layouts Demonstrated

| Layout | Description |
|--------|-------------|
| `title` | Opening slide with centered title and subtitle |
| `section` | Section header/divider |
| `content` | Standard content with title and markdown body |
| `two_column` | Side-by-side columns |
| `comparison` | Two columns with headers |
| `three_column` | Three columns |
| `picture` | Full-bleed image |
| `picture_caption` | Image with caption |
| `text_picture` | Text on left, image on right |
| `quote` | Centered quote with attribution |
| `name_card` | Person introduction card |
| `blank` | Empty slide for custom content |
| `end` | Closing slide with contact info |

## Usage Pattern

```python
from stagdeck import SlideDeck, DeckViewer
from stagdeck.templates.decks.default import create_default_master

# Get the default master deck
master = create_default_master()

# Create your presentation
deck = SlideDeck(title='My Talk', master=master)

# Add slides using layout names
deck.add(layout='title', title='Hello World', subtitle='A demo')
deck.add(layout='content', title='Introduction', body='...')
deck.add(layout='end', title='Thank You!')

# Run the viewer
DeckViewer.run(deck)
```
