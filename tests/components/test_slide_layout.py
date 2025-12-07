"""Tests for slide layout system."""

import pytest

from stagdeck.components.slide_layout import (
    LayoutMode,
    LayoutConfig,
    ContentMetrics,
    detect_layout_mode,
    analyze_content,
    calculate_content_scale,
    DEFAULT_CONFIG,
)
from stagdeck.slide import Slide


class TestLayoutModeDetection:
    """Test automatic layout mode detection."""
    
    def test_title_only(self):
        """Slide with just title is TITLE_ONLY."""
        slide = Slide(title='Hello World')
        assert detect_layout_mode(slide) == LayoutMode.TITLE_ONLY
    
    def test_title_subtitle_only(self):
        """Slide with title and subtitle (no content) is TITLE_ONLY."""
        slide = Slide(title='Main Title', subtitle='Subtitle')
        assert detect_layout_mode(slide) == LayoutMode.TITLE_ONLY
    
    def test_content_only(self):
        """Slide with just content is CONTENT_ONLY."""
        slide = Slide(content='Some markdown content')
        assert detect_layout_mode(slide) == LayoutMode.CONTENT_ONLY
    
    def test_title_content(self):
        """Slide with title and content is TITLE_CONTENT."""
        slide = Slide(title='Title', content='Content here')
        assert detect_layout_mode(slide) == LayoutMode.TITLE_CONTENT
    
    def test_title_subtitle_small_content(self):
        """Slide with title, subtitle, and small content is TITLE_CENTERED."""
        slide = Slide(title='Title', subtitle='Sub', content='Small content')
        assert detect_layout_mode(slide) == LayoutMode.TITLE_CENTERED
    
    def test_title_subtitle_large_content(self):
        """Slide with title, subtitle, and large content is TITLE_CONTENT."""
        large_content = '\n'.join([f'- Item {i}' for i in range(10)])
        slide = Slide(title='Title', subtitle='Sub', content=large_content)
        assert detect_layout_mode(slide) == LayoutMode.TITLE_CONTENT
    
    def test_title_subtitle_table_content(self):
        """Slide with title, subtitle, and table is TITLE_CONTENT."""
        table = '| A | B |\n|---|---|\n| 1 | 2 |'
        slide = Slide(title='Title', subtitle='Sub', content=table)
        assert detect_layout_mode(slide) == LayoutMode.TITLE_CONTENT
    
    def test_custom_builder_as_content(self):
        """Slide with custom builder counts as having content."""
        slide = Slide(builder=lambda: None)
        assert detect_layout_mode(slide) == LayoutMode.CONTENT_ONLY
    
    def test_title_with_builder(self):
        """Slide with title and builder is TITLE_CONTENT."""
        slide = Slide(title='Title', builder=lambda: None)
        assert detect_layout_mode(slide) == LayoutMode.TITLE_CONTENT


class TestLayoutConfig:
    """Test layout configuration."""
    
    def test_default_config_values(self):
        """Default config has sensible values."""
        config = DEFAULT_CONFIG
        
        # Margins should be small percentages
        assert 0 < config.margin_top < 10
        assert 0 < config.margin_bottom < 10
        assert 0 < config.margin_left < 10
        assert 0 < config.margin_right < 10
        
        # Title region should be reasonable
        assert 10 < config.title_height < 30
        
        # Font sizes should be reasonable rem values
        assert config.title_only_size > config.title_size
        assert config.title_size > 0
    
    def test_custom_config(self):
        """Can create custom config."""
        config = LayoutConfig(
            margin_top=10.0,
            margin_bottom=10.0,
            title_height=25.0,
        )
        
        assert config.margin_top == 10.0
        assert config.margin_bottom == 10.0
        assert config.title_height == 25.0


class TestSlideFinalContent:
    """Test final_content for animation-stable sizing."""
    
    def test_get_sizing_content_default(self):
        """get_sizing_content returns content when final_content is None."""
        slide = Slide(content='Current content')
        assert slide.get_sizing_content() == 'Current content'
    
    def test_get_sizing_content_with_final(self):
        """get_sizing_content returns final_content when set."""
        slide = Slide(
            content='- Point 1',
            final_content='- Point 1\n- Point 2\n- Point 3',
        )
        assert slide.get_sizing_content() == '- Point 1\n- Point 2\n- Point 3'
    
    def test_final_content_empty_string(self):
        """Empty string final_content is used (not None)."""
        slide = Slide(content='Some content', final_content='')
        assert slide.get_sizing_content() == ''


class TestContentAnalysis:
    """Test content analysis for scaling."""
    
    def test_analyze_empty_content(self):
        """Empty content returns default metrics."""
        metrics = analyze_content('')
        assert metrics.content_type == 'text'
        assert metrics.total_chars == 0
    
    def test_analyze_table(self):
        """Analyze table content."""
        table = '''| A | B | C |
|---|---|---|
| 1 | 2 | 3 |
| 4 | 5 | 6 |'''
        metrics = analyze_content(table)
        
        assert metrics.content_type == 'table'
        assert metrics.table_cols == 3
        assert metrics.table_rows == 3  # header + 2 data rows
    
    def test_analyze_large_table(self):
        """Analyze large table with many rows."""
        rows = ['| Col1 | Col2 | Col3 | Col4 | Col5 |']
        rows.append('|------|------|------|------|------|')
        for i in range(10):
            rows.append(f'| Row{i} | Data | More | Even | More |')
        table = '\n'.join(rows)
        
        metrics = analyze_content(table)
        assert metrics.content_type == 'table'
        assert metrics.table_rows == 11  # header + 10 data rows
        assert metrics.table_cols == 5
    
    def test_analyze_bullet_list(self):
        """Analyze bullet list content."""
        bullets = '''- First item
- Second item
- Third item'''
        metrics = analyze_content(bullets)
        
        assert metrics.content_type == 'bullets'
        assert metrics.bullet_count == 3
    
    def test_analyze_code_block(self):
        """Analyze code block content."""
        code = '''```python
def hello():
    print("Hello")
    return True
```'''
        metrics = analyze_content(code)
        
        assert metrics.content_type == 'code'
        assert metrics.code_lines == 4


class TestContentScaling:
    """Test programmatic content scaling."""
    
    def test_small_table_scales_up(self):
        """Small table should scale UP to fill space."""
        metrics = ContentMetrics(
            content_type='table',
            table_rows=3,
            table_cols=3,
            avg_cell_length=5,
        )
        font_size, scale = calculate_content_scale(metrics, DEFAULT_CONFIG)
        
        # Small tables (<=5 rows) scale up to 1.4
        assert scale > 1.0
        assert font_size > DEFAULT_CONFIG.base_table_size
    
    def test_large_table_scaled_appropriately(self):
        """Large table (10 rows) should have moderate scale."""
        metrics = ContentMetrics(
            content_type='table',
            table_rows=10,
            table_cols=5,
            avg_cell_length=15,
        )
        font_size, scale = calculate_content_scale(metrics, DEFAULT_CONFIG)
        
        # 10 rows = scale 1.0, with 5 cols adjustment (0.95) = 0.95
        assert 0.9 <= scale <= 1.1
    
    def test_very_large_table_scaled_down(self):
        """Very large table (>12 rows) should be scaled down."""
        metrics = ContentMetrics(
            content_type='table',
            table_rows=15,
            table_cols=5,
            avg_cell_length=15,
        )
        font_size, scale = calculate_content_scale(metrics, DEFAULT_CONFIG)
        
        assert scale < 0.8
    
    def test_many_bullets_scaled_down(self):
        """Many bullet points should be scaled down."""
        metrics = ContentMetrics(
            content_type='bullets',
            bullet_count=12,
            max_line_length=50,
        )
        font_size, scale = calculate_content_scale(metrics, DEFAULT_CONFIG)
        
        assert scale < 1.0
    
    def test_minimum_scale_enforced(self):
        """Scale should never go below minimum."""
        metrics = ContentMetrics(
            content_type='table',
            table_rows=20,
            table_cols=10,
            avg_cell_length=50,
        )
        font_size, scale = calculate_content_scale(metrics, DEFAULT_CONFIG)
        
        assert scale >= DEFAULT_CONFIG.min_scale
