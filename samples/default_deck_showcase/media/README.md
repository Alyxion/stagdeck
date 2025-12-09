# Media Folder

This folder contains media assets for the StagDeck showcase presentation.

## Usage

Register this folder in your deck:

```python
from pathlib import Path
from stagdeck import SlideDeck

deck = SlideDeck()
deck.add_media_folder(Path(__file__).parent / 'media', '/media')
```

Then reference images in markdown:

```markdown
# Inline Image
![inline](/media/mountain.jpg)

# Background Image
![background](/media/stars.jpg)
```

## Image Sources

| File | Description | Source | Photographer |
|------|-------------|--------|--------------|
| `mountain.jpg` | Mountain landscape above clouds | [Unsplash](https://unsplash.com/photos/photo-1506905925346-21bda4d32df4) | Samuel Ferrara |
| `stars.jpg` | Night sky with Milky Way over mountains | [Unsplash](https://unsplash.com/photos/photo-1519681393784-d120267933ba) | Benjamin Voros |

## License

All images are from [Unsplash](https://unsplash.com) and are provided under the 
[Unsplash License](https://unsplash.com/license):

> Unsplash grants you an irrevocable, nonexclusive, worldwide copyright license 
> to download, copy, modify, distribute, perform, and use images from Unsplash 
> for free, including for commercial purposes, **without permission from or 
> attributing the photographer or Unsplash**.

### What this means:

- ✅ **Free for commercial use** - Use in any project, product, or presentation
- ✅ **No attribution required** - Credit is appreciated but not mandatory
- ✅ **Modification allowed** - Resize, crop, filter as needed
- ✅ **Redistribution allowed** - Include in your own projects
- ❌ **Cannot resell unmodified** - Don't sell the photos themselves
- ❌ **Cannot use in competing service** - Don't create a similar photo platform

For full terms, see: https://unsplash.com/license
