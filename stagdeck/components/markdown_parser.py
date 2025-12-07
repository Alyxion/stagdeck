"""Markdown Parser for StagDeck presentations.

Parses Markdown source into structured deck and slide information.
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


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
    CODE_BLOCK_PATTERN = re.compile(r'```(\w*)\n(.*?)```', re.DOTALL)
    IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)(?:\s*\{([^}]+)\})?')
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
