# StagDeck Samples

Example presentations demonstrating StagDeck features.

## Available Samples

| Sample | Description |
|--------|-------------|
| [default_deck_showcase](./default_deck_showcase/) | Markdown-first syntax, media folders, all layouts |

## Running Samples

Each sample can be run directly:

```bash
cd samples/<sample_name>
python main.py
```

Then open http://localhost:8080 in your browser.

## Features Demonstrated

### Markdown-First Syntax

```python
deck.add('''
![background](#1a1a2e)

# Slide Title
## Subtitle

Content with **markdown** support.
''')
```

### Media Folders

```python
deck.add_media_folder('./media', '/media')

deck.add('''
# Local Images

![inline](/media/photo.jpg)
''')
```

## Creating Your Own

Use these samples as starting points for your own presentations:

1. Copy a sample directory
2. Modify `main.py` with your content
3. Add images to the `media/` folder
4. Run with `python main.py`
