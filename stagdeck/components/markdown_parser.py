"""Markdown Parser for StagDeck presentations.

Parses Markdown source into structured deck and slide information.
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

# Slide separator - must be on its own line
SLIDE_SEPARATOR = '---'


class SlideContentType(Enum):
    """Types of content that can appear on a slide."""
    TITLE = auto()           # Title-only slide
    TITLE_SUBTITLE = auto()  # Title with subtitle
    TITLE_CONTENT = auto()   # Title with body content
    TITLE_BULLETS = auto()   # Title with bullet list
    TITLE_CODE = auto()      # Title with code block
    TITLE_TABLE = auto()     # Title with table
    TITLE_IMAGE = auto()     # Title with image
    TITLE_QUOTE = auto()     # Title with blockquote
    CONTENT_ONLY = auto()    # Body content without title
    IMAGE_ONLY = auto()      # Full-slide image
    SECTION = auto()         # Section divider (large centered title)


@dataclass
class MarkdownDeckInfo:
    """Information extracted from Markdown that affects the whole deck.
    
    :ivar title: Deck title (from first H1 or frontmatter).
    :ivar author: Author name (from frontmatter).
    :ivar date: Presentation date (from frontmatter).
    :ivar theme: Theme name or reference (from frontmatter).
    :ivar footer: Footer text for all slides.
    :ivar slide_numbers: Whether to show slide numbers.
    :ivar build_lists: Whether to progressively reveal list items.
    :ivar aspect_ratio: Slide aspect ratio (e.g., '16:9', '4:3').
    :ivar custom_css: Custom CSS to apply to the deck.
    :ivar metadata: Additional metadata from frontmatter.
    """
    title: str = ''
    author: str = ''
    date: str = ''
    theme: str = ''
    footer: str = ''
    slide_numbers: bool = False
    build_lists: bool = False
    aspect_ratio: str = '16:9'
    custom_css: str = ''
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MarkdownSlideInfo:
    """Information extracted for a single slide.
    
    :ivar title: Slide title (from heading).
    :ivar subtitle: Slide subtitle (from second heading or emphasis).
    :ivar content: Main content (paragraphs, lists, etc.).
    :ivar content_type: Detected content type for layout selection.
    :ivar presenter_notes: Private notes for presenter view.
    :ivar code_blocks: List of (language, code) tuples.
    :ivar images: List of image references (url, alt, size).
    :ivar tables: List of table data (headers, rows).
    :ivar quotes: List of blockquotes.
    :ivar bullets: List of bullet points (can be nested).
    :ivar numbered_items: List of numbered items.
    :ivar background: Background image or color.
    :ivar build_list: Override build-lists for this slide.
    :ivar transition: Slide transition effect.
    :ivar classes: Additional CSS classes.
    :ivar raw_markdown: Original markdown source for this slide.
    """
    title: str = ''
    subtitle: str = ''
    content: str = ''
    content_type: SlideContentType = SlideContentType.TITLE_CONTENT
    presenter_notes: str = ''
    code_blocks: list[tuple[str, str]] = field(default_factory=list)
    images: list[dict[str, str]] = field(default_factory=list)
    tables: list[dict[str, Any]] = field(default_factory=list)
    quotes: list[str] = field(default_factory=list)
    bullets: list[str | list] = field(default_factory=list)
    numbered_items: list[str | list] = field(default_factory=list)
    background: str = ''
    build_list: bool | None = None
    transition: str = ''
    classes: list[str] = field(default_factory=list)
    raw_markdown: str = ''


class MarkdownParser:
    """Parser for Markdown presentation source.
    
    Splits Markdown into deck-level and slide-level information.
    
    Example:
        >>> parser = MarkdownParser()
        >>> deck_info, slides = parser.parse(markdown_source)
        >>> print(deck_info.title)
        >>> for slide in slides:
        ...     print(slide.title, slide.content_type)
    """
    
    # Regex patterns
    FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    SLIDE_SEPARATOR = re.compile(r'\n---\s*\n')
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    H1_PATTERN = re.compile(r'^#\s+(.+)$', re.MULTILINE)
    H2_PATTERN = re.compile(r'^##\s+(.+)$', re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r'```(\w*)\n(.*?)```', re.DOTALL)
    IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)(?:\s*\{([^}]+)\})?')
    # Background image pattern: ![background](color_or_url) or ![](url) at start
    BACKGROUND_IMAGE_PATTERN = re.compile(
        r'^!\[(background|fit|left|right|original)?[^\]]*\]\(([^)]+)\)\s*$',
        re.MULTILINE
    )
    TABLE_PATTERN = re.compile(r'^\|(.+)\|\s*\n\|[-:\s|]+\|\s*\n((?:\|.+\|\s*\n?)+)', re.MULTILINE)
    QUOTE_PATTERN = re.compile(r'^>\s*(.+)$', re.MULTILINE)
    BULLET_PATTERN = re.compile(r'^(\s*)[-*+]\s+(.+)$', re.MULTILINE)
    NUMBERED_PATTERN = re.compile(r'^(\s*)\d+\.\s+(.+)$', re.MULTILINE)
    PRESENTER_NOTE_PATTERN = re.compile(r'^\^\s*(.+)$', re.MULTILINE)
    DIRECTIVE_PATTERN = re.compile(r'^(\w[\w-]*):\s*(.+)$', re.MULTILINE)
    SLIDE_DIRECTIVE_PATTERN = re.compile(r'^\[\.(\w[\w-]*):\s*([^\]]+)\]$', re.MULTILINE)
    
    def __init__(self, headers_as_slides: bool = False):
        """Initialize the parser.
        
        :param headers_as_slides: If True, treat H1 headings as slide boundaries.
        """
        self.headers_as_slides = headers_as_slides
    
    def parse(self, source: str) -> tuple[MarkdownDeckInfo, list[MarkdownSlideInfo]]:
        """Parse Markdown source into deck and slide information.
        
        :param source: Markdown source text.
        :return: Tuple of (deck_info, list of slide_info).
        """
        deck_info = MarkdownDeckInfo()
        
        # Extract frontmatter
        source = self._parse_frontmatter(source, deck_info)
        
        # Extract deck-level directives
        source = self._parse_deck_directives(source, deck_info)
        
        # Split into slides
        raw_slides = self._split_slides(source)
        
        # Parse each slide
        slides = [self._parse_slide(raw) for raw in raw_slides if raw.strip()]
        
        # Infer deck title from first slide if not set
        if not deck_info.title and slides and slides[0].title:
            deck_info.title = slides[0].title
        
        return deck_info, slides
    
    def _parse_frontmatter(self, source: str, deck_info: MarkdownDeckInfo) -> str:
        """Extract YAML frontmatter from source.
        
        :param source: Markdown source.
        :param deck_info: DeckInfo to populate.
        :return: Source with frontmatter removed.
        """
        match = self.FRONTMATTER_PATTERN.match(source)
        if not match:
            return source
        
        frontmatter = match.group(1)
        
        # Simple YAML parsing (key: value)
        for line in frontmatter.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace('-', '_')
                value = value.strip().strip('"\'')
                
                if key == 'title':
                    deck_info.title = value
                elif key == 'author':
                    deck_info.author = value
                elif key == 'date':
                    deck_info.date = value
                elif key == 'theme':
                    deck_info.theme = value
                elif key == 'footer':
                    deck_info.footer = value
                elif key == 'slidenumbers' or key == 'slide_numbers':
                    deck_info.slide_numbers = value.lower() in ('true', 'yes', '1')
                elif key == 'build_lists' or key == 'buildlists':
                    deck_info.build_lists = value.lower() in ('true', 'yes', '1')
                elif key == 'aspect_ratio' or key == 'aspectratio':
                    deck_info.aspect_ratio = value
                else:
                    deck_info.metadata[key] = value
        
        return source[match.end():]
    
    def _parse_deck_directives(self, source: str, deck_info: MarkdownDeckInfo) -> str:
        """Extract deck-level directives from source.
        
        :param source: Markdown source.
        :param deck_info: DeckInfo to populate.
        :return: Source with directives removed.
        """
        lines = []
        for line in source.split('\n'):
            match = self.DIRECTIVE_PATTERN.match(line)
            if match and not line.startswith('#'):
                key = match.group(1).lower().replace('-', '_')
                value = match.group(2).strip()
                
                if key == 'footer':
                    deck_info.footer = value
                elif key == 'slidenumbers':
                    deck_info.slide_numbers = value.lower() in ('true', 'yes', '1')
                elif key == 'build_lists':
                    deck_info.build_lists = value.lower() in ('true', 'yes', '1')
                elif key == 'theme':
                    deck_info.theme = value
                else:
                    # Keep non-deck directives
                    lines.append(line)
            else:
                lines.append(line)
        
        return '\n'.join(lines)
    
    def _split_slides(self, source: str) -> list[str]:
        """Split source into individual slides.
        
        :param source: Markdown source.
        :return: List of raw slide content strings.
        """
        if self.headers_as_slides:
            # Split on H1 headings
            parts = re.split(r'(?=^#\s+)', source, flags=re.MULTILINE)
            return [p for p in parts if p.strip()]
        else:
            # Split on --- separators
            return self.SLIDE_SEPARATOR.split(source)
    
    def _parse_slide(self, raw: str) -> MarkdownSlideInfo:
        """Parse a single slide's content.
        
        :param raw: Raw markdown for one slide.
        :return: SlideInfo with extracted data.
        """
        slide = MarkdownSlideInfo(raw_markdown=raw)
        content = raw.strip()
        
        # Extract presenter notes (lines starting with ^)
        notes = []
        content_lines = []
        for line in content.split('\n'):
            note_match = self.PRESENTER_NOTE_PATTERN.match(line)
            if note_match:
                notes.append(note_match.group(1))
            else:
                content_lines.append(line)
        slide.presenter_notes = '\n'.join(notes)
        content = '\n'.join(content_lines)
        
        # Extract slide-level directives [.key: value]
        for match in self.SLIDE_DIRECTIVE_PATTERN.finditer(content):
            key = match.group(1).lower().replace('-', '_')
            value = match.group(2).strip()
            
            if key == 'background':
                slide.background = value
            elif key == 'build_lists':
                slide.build_list = value.lower() in ('true', 'yes', '1')
            elif key == 'transition':
                slide.transition = value
            elif key == 'class':
                slide.classes.extend(value.split())
        
        content = self.SLIDE_DIRECTIVE_PATTERN.sub('', content).strip()
        
        # Extract code blocks
        for match in self.CODE_BLOCK_PATTERN.finditer(content):
            lang = match.group(1) or 'text'
            code = match.group(2).strip()
            slide.code_blocks.append((lang, code))
        
        # Extract images
        for match in self.IMAGE_PATTERN.finditer(content):
            alt = match.group(1)
            url = match.group(2)
            attrs = match.group(3) or ''
            slide.images.append({'url': url, 'alt': alt, 'attrs': attrs})
        
        # Extract tables
        for match in self.TABLE_PATTERN.finditer(content):
            header_row = match.group(1)
            body = match.group(2)
            
            headers = [h.strip() for h in header_row.split('|') if h.strip()]
            rows = []
            for row_line in body.strip().split('\n'):
                cells = [c.strip() for c in row_line.split('|') if c.strip()]
                if cells:
                    rows.append(cells)
            
            slide.tables.append({'headers': headers, 'rows': rows})
        
        # Extract blockquotes
        for match in self.QUOTE_PATTERN.finditer(content):
            slide.quotes.append(match.group(1))
        
        # Extract bullet lists
        slide.bullets = self._extract_list(content, self.BULLET_PATTERN)
        
        # Extract numbered lists
        slide.numbered_items = self._extract_list(content, self.NUMBERED_PATTERN)
        
        # Extract headings for title/subtitle
        headings = self.HEADING_PATTERN.findall(content)
        if headings:
            # First heading is title
            slide.title = headings[0][1]
            # Second heading (if H2 or lower) is subtitle
            if len(headings) > 1 and len(headings[1][0]) >= 2:
                slide.subtitle = headings[1][1]
        
        # Remove headings from content for body text
        body = self.HEADING_PATTERN.sub('', content)
        body = self.CODE_BLOCK_PATTERN.sub('', body)
        body = self.TABLE_PATTERN.sub('', body)
        body = self.IMAGE_PATTERN.sub('', body)
        body = self.QUOTE_PATTERN.sub('', body)
        body = self.BULLET_PATTERN.sub('', body)
        body = self.NUMBERED_PATTERN.sub('', body)
        slide.content = body.strip()
        
        # Determine content type
        slide.content_type = self._detect_content_type(slide)
        
        return slide
    
    def _extract_list(self, content: str, pattern: re.Pattern) -> list[str | list]:
        """Extract list items with nesting.
        
        :param content: Content to search.
        :param pattern: Regex pattern for list items.
        :return: List of items (nested lists represented as sublists).
        """
        items: list[str | list] = []
        current_indent = -1  # Start at -1 so first item (indent 0) is added
        stack: list[list] = [items]
        
        for match in pattern.finditer(content):
            indent = len(match.group(1))
            text = match.group(2)
            
            if current_indent == -1:
                # First item
                current_indent = indent
            elif indent > current_indent:
                # Start nested list
                new_list: list = []
                stack[-1].append(new_list)
                stack.append(new_list)
                current_indent = indent
            elif indent < current_indent:
                # End nested list(s)
                while len(stack) > 1 and indent < current_indent:
                    stack.pop()
                    current_indent = max(0, current_indent - 4)
            
            stack[-1].append(text)
        
        return items
    
    def _detect_content_type(self, slide: MarkdownSlideInfo) -> SlideContentType:
        """Detect the content type for layout selection.
        
        :param slide: Slide info with extracted content.
        :return: Detected content type.
        """
        has_title = bool(slide.title)
        has_subtitle = bool(slide.subtitle)
        has_content = bool(slide.content)
        has_code = bool(slide.code_blocks)
        has_table = bool(slide.tables)
        has_image = bool(slide.images)
        has_quote = bool(slide.quotes)
        has_bullets = bool(slide.bullets)
        has_numbered = bool(slide.numbered_items)
        
        # Image-only slide (no title, just image)
        if has_image and not has_title and not has_content:
            return SlideContentType.IMAGE_ONLY
        
        # Title-only slides
        if has_title and not any([has_content, has_code, has_table, has_image, 
                                   has_quote, has_bullets, has_numbered]):
            if has_subtitle:
                return SlideContentType.TITLE_SUBTITLE
            return SlideContentType.TITLE
        
        # Content without title
        if not has_title:
            return SlideContentType.CONTENT_ONLY
        
        # Prioritize by primary content type
        if has_code:
            return SlideContentType.TITLE_CODE
        if has_table:
            return SlideContentType.TITLE_TABLE
        if has_image:
            return SlideContentType.TITLE_IMAGE
        if has_quote:
            return SlideContentType.TITLE_QUOTE
        if has_bullets or has_numbered:
            return SlideContentType.TITLE_BULLETS
        
        return SlideContentType.TITLE_CONTENT
    
    def parse_slide_markdown(self, markdown: str) -> dict[str, Any]:
        """Parse a single slide's markdown into components.
        
        Extracts title, subtitle, background, and content from markdown.
        Follows Deckset conventions:
        - `# Heading` = title
        - `## Heading` immediately after title = subtitle
        - `![background](color_or_url)` = background
        - `![](image.jpg)` at start (no text before) = background image
        - `![inline](image.jpg)` = inline image (kept in content)
        - Everything else = content
        
        :param markdown: Markdown source for a single slide.
        :return: Dict with keys: title, subtitle, background, content, images
        
        Example:
            >>> parser = MarkdownParser()
            >>> result = parser.parse_slide_markdown('''
            ... ![background](#1a1a2e)
            ... 
            ... # My Title
            ... ## My Subtitle
            ... 
            ... Some content here.
            ... ''')
            >>> result['title']
            'My Title'
            >>> result['background']
            '#1a1a2e'
        """
        result: dict[str, Any] = {
            'title': '',
            'subtitle': '',
            'background': '',
            'background_modifiers': '',  # Raw modifier string for ImageView
            'background_position': '',  # 'left', 'right', 'top', 'bottom', or '' for full
            'overlay_opacity': None,  # None = no overlay, 0.0-1.0 for opacity
            'blur_radius': None,  # None = no blur, value in pixels
            'content': '',
            'images': [],
            'notes': '',
            'text_style': {},  # Slide-level text style overrides
            'name': '',  # Slide name from [name: ...] directive
        }
        
        lines = markdown.strip().split('\n')
        content_lines: list[str] = []
        found_title = False
        found_subtitle = False
        title_line_idx = -1
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Check for slide name directive: [name: slidename]
            name_match = re.match(r'^\[name:\s*([^\]]+)\]$', stripped, re.IGNORECASE)
            if name_match:
                result['name'] = name_match.group(1).strip()
                i += 1
                continue
            
            # Check for presenter notes
            if stripped.startswith('^'):
                if result['notes']:
                    result['notes'] += '\n'
                result['notes'] += stripped[1:].strip()
                i += 1
                continue
            
            # Check for element style directives: [.element:property: value]
            # Examples: [.title:shadow: 2px 2px 4px black], [.text:color: white], [.subtitle:class: italic]
            style_match = re.match(r'^\[\.(\w+):(\w+):\s*(.+)\]$', stripped)
            if style_match:
                element = style_match.group(1).lower()  # title, subtitle, text, etc.
                prop = style_match.group(2).lower()     # shadow, color, class, etc.
                value = style_match.group(3).strip()
                
                # Initialize element dict if needed
                if element not in result['text_style']:
                    result['text_style'][element] = {}
                result['text_style'][element][prop] = value
                i += 1
                continue
            
            # Check for background image: ![modifiers](url)
            # Modifiers: background, left, right, top, bottom, overlay, overlay:N, blur, blur:N
            # Use a more permissive pattern that handles nested parentheses (for gradients)
            bg_match = re.match(r'^!\[([^\]]*)\]\((.+)\)\s*$', stripped)
            if bg_match:
                alt_text = bg_match.group(1).lower()
                value = bg_match.group(2)
                
                # Parse modifiers from alt text
                modifiers = alt_text.split()
                
                # Position modifiers
                is_background = 'background' in modifiers
                is_left = any(m == 'left' or m.startswith('left:') for m in modifiers)
                is_right = any(m == 'right' or m.startswith('right:') for m in modifiers)
                is_top = any(m == 'top' or m.startswith('top:') for m in modifiers)
                is_bottom = any(m == 'bottom' or m.startswith('bottom:') for m in modifiers)
                is_split = is_left or is_right or is_top or is_bottom
                
                # Filter modifiers: overlay, overlay:N, blur, blur:N
                overlay_opacity = None
                blur_radius = None
                
                for mod in modifiers:
                    if mod == 'overlay':
                        overlay_opacity = -1.0  # Sentinel for "use theme default"
                    elif mod.startswith('overlay:'):
                        try:
                            overlay_opacity = float(mod.split(':')[1])
                        except (ValueError, IndexError):
                            overlay_opacity = -1.0
                    elif mod == 'blur':
                        blur_radius = -1.0  # Sentinel for "use theme default"
                    elif mod.startswith('blur:'):
                        try:
                            blur_radius = float(mod.split(':')[1])
                        except (ValueError, IndexError):
                            blur_radius = -1.0
                
                # If it's explicitly "background" or positioned, or at start with no content
                if is_background or is_split or (not content_lines and not found_title and not alt_text.startswith('inline')):
                    # Check if it's a color (starts with # or contains gradient)
                    if value.startswith('#') or 'gradient' in value.lower():
                        result['background'] = value
                    else:
                        # It's an image URL
                        result['background'] = f'url({value})'
                    
                    # Store raw modifiers string for ImageView
                    result['background_modifiers'] = alt_text
                    
                    # Set filter values (for backward compatibility)
                    result['overlay_opacity'] = overlay_opacity
                    result['blur_radius'] = blur_radius
                    
                    # Set position for split layouts
                    if is_left:
                        result['background_position'] = 'left'
                    elif is_right:
                        result['background_position'] = 'right'
                    elif is_top:
                        result['background_position'] = 'top'
                    elif is_bottom:
                        result['background_position'] = 'bottom'
                    
                    i += 1
                    continue
                else:
                    # It's an inline/positioned image, keep track of it
                    result['images'].append({
                        'modifier': alt_text,
                        'url': value,
                        'line': i,
                    })
                    content_lines.append(line)
                    i += 1
                    continue
            
            # Check for inline images ![inline](...) - keep in content
            inline_match = re.match(r'^!\[inline[^\]]*\]\(([^)]+)\)', stripped)
            if inline_match:
                content_lines.append(line)
                i += 1
                continue
            
            # Check for H1 title
            h1_match = re.match(r'^#\s+(.+)$', stripped)
            if h1_match and not found_title:
                result['title'] = h1_match.group(1).strip()
                found_title = True
                title_line_idx = i
                i += 1
                
                # Check if next non-empty line is H2 (subtitle)
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                if i < len(lines):
                    h2_match = re.match(r'^##\s+(.+)$', lines[i].strip())
                    if h2_match:
                        result['subtitle'] = h2_match.group(1).strip()
                        found_subtitle = True
                        i += 1
                continue
            
            # Regular content line
            content_lines.append(line)
            i += 1
        
        # Join remaining content
        result['content'] = '\n'.join(content_lines).strip()
        
        return result
    
    def parse_multi_region_markdown(self, markdown: str) -> dict[str, Any]:
        """Parse markdown with multiple image/content regions.
        
        Splits markdown into regions, where each region starts with an image tag.
        Supports horizontal (left/right or multiple columns) and vertical (top/bottom) layouts.
        
        Example horizontal split:
            ![left](image1.jpg)
            # Left Title
            Content for left side
            
            ![right](image2.jpg)
            # Right Title
            Content for right side
        
        Example triple column:
            ![](image1.jpg)
            * Point A
            ![](image2.jpg)
            # Topic
            ![](image3.jpg)
            ## Other topic
        
        :param markdown: Markdown source with multiple regions.
        :return: Dict with 'regions' list and 'direction' ('horizontal' or 'vertical').
        """
        result: dict[str, Any] = {
            'regions': [],
            'direction': 'horizontal',
            'notes': '',
            'name': '',  # Slide name from [name: ...] directive
        }
        
        lines = markdown.strip().split('\n')
        
        # First pass: detect if this is a multi-region slide
        image_pattern = re.compile(r'^!\[([^\]]*)\]\((.+)\)\s*$')
        image_lines: list[tuple[int, str, str]] = []  # (line_idx, modifiers, url)
        
        name_pattern = re.compile(r'^\[name:\s*([^\]]+)\]$', re.IGNORECASE)
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Check for slide name directive
            name_match = name_pattern.match(stripped)
            if name_match:
                result['name'] = name_match.group(1).strip()
                continue
            
            # Skip presenter notes
            if stripped.startswith('^'):
                if result['notes']:
                    result['notes'] += '\n'
                result['notes'] += stripped[1:].strip()
                continue
            
            match = image_pattern.match(stripped)
            if match:
                modifiers = match.group(1).lower()
                url = match.group(2)
                # Skip inline images
                if 'inline' not in modifiers:
                    image_lines.append((i, modifiers, url))
        
        # If 0 or 1 images, use standard single-region parsing
        if len(image_lines) <= 1:
            single = self.parse_slide_markdown(markdown)
            if single.get('background'):
                result['regions'] = [{
                    'image': single['background'],
                    'overlay_opacity': single['overlay_opacity'],
                    'blur_radius': single['blur_radius'],
                    'content': single['content'],
                    'title': single['title'],
                    'subtitle': single['subtitle'],
                }]
            else:
                result['regions'] = [{
                    'image': '',
                    'overlay_opacity': None,
                    'blur_radius': None,
                    'content': single['content'],
                    'title': single['title'],
                    'subtitle': single['subtitle'],
                }]
            result['notes'] = single.get('notes', '')
            result['name'] = single.get('name', '')
            # Detect direction from position modifiers
            if single.get('background_position') in ('top', 'bottom'):
                result['direction'] = 'vertical'
            return result
        
        # Determine direction from modifiers
        has_left_right = any('left' in m or 'right' in m for _, m, _ in image_lines)
        has_top_bottom = any('top' in m or 'bottom' in m for _, m, _ in image_lines)
        
        if has_top_bottom and not has_left_right:
            result['direction'] = 'vertical'
        else:
            result['direction'] = 'horizontal'
        
        # Split content into regions based on image positions
        # Each region starts at an image line and ends before the next image
        for idx, (line_idx, modifiers, url) in enumerate(image_lines):
            # Find end of this region (start of next image or end of file)
            if idx + 1 < len(image_lines):
                end_idx = image_lines[idx + 1][0]
            else:
                end_idx = len(lines)
            
            # Extract content lines for this region (excluding the image line)
            region_lines = []
            for j in range(line_idx + 1, end_idx):
                stripped = lines[j].strip()
                # Skip presenter notes (already extracted)
                if not stripped.startswith('^'):
                    region_lines.append(lines[j])
            
            region_content = '\n'.join(region_lines).strip()
            
            # Parse title/subtitle from region content
            region_title = ''
            region_subtitle = ''
            final_content_lines = []
            
            content_started = False
            for line in region_lines:
                stripped = line.strip()
                
                # Check for H1 title
                h1_match = re.match(r'^#\s+(.+)$', stripped)
                if h1_match and not region_title and not content_started:
                    region_title = h1_match.group(1).strip()
                    continue
                
                # Check for H2 subtitle (only right after title)
                h2_match = re.match(r'^##\s+(.+)$', stripped)
                if h2_match and region_title and not region_subtitle and not content_started:
                    if not stripped or h2_match:
                        region_subtitle = h2_match.group(1).strip()
                        continue
                
                # Everything else is content
                if stripped:
                    content_started = True
                final_content_lines.append(line)
            
            # Determine image URL
            is_color = url.startswith('#') or 'gradient' in url.lower()
            image_url = url if is_color else f'url({url})'
            
            # Parse filter and position modifiers from this region's modifiers
            mod_list = modifiers.split()
            overlay_opacity = None
            blur_radius = None
            position = ''  # left, right, top, bottom
            
            for mod in mod_list:
                if mod == 'overlay':
                    overlay_opacity = -1.0  # Sentinel for "use theme default"
                elif mod.startswith('overlay:'):
                    try:
                        overlay_opacity = float(mod.split(':')[1])
                    except (ValueError, IndexError):
                        overlay_opacity = -1.0
                elif mod == 'blur':
                    blur_radius = -1.0  # Sentinel for "use theme default"
                elif mod.startswith('blur:'):
                    try:
                        blur_radius = float(mod.split(':')[1])
                    except (ValueError, IndexError):
                        blur_radius = -1.0
                elif mod in ('left', 'right', 'top', 'bottom'):
                    position = mod
            
            result['regions'].append({
                'image': image_url,
                'modifiers': modifiers,  # Raw modifier string for ImageView
                'overlay_opacity': overlay_opacity,
                'blur_radius': blur_radius,
                'position': position,
                'content': '\n'.join(final_content_lines).strip(),
                'title': region_title,
                'subtitle': region_subtitle,
            })
        
        return result
