"""Showcase of slide layouts using markdown file + Python hybrid approach.

This sample demonstrates:
- Loading slides from markdown or PPTX with `add_from_file()`
- Named slides using `[name: slidename]` directive
- Inserting at position with `add_from_file(..., after='name')`
- Page selection with `pages='1,3-5'` or `pages=[1,3,4,5]`
- Custom Python slides by subclassing Slide and overriding build_content()
- Layout helpers: add_content_area(), add_section()

Run with: python main.py

For PPTX support:
- Install LibreOffice: brew install --cask libreoffice
- Install pdf2image: pip install pdf2image
- Install poppler: brew install poppler
"""

from dataclasses import dataclass
from pathlib import Path
import random

from nicegui import ui
import plotly.graph_objects as go

from stagdeck import SlideDeck, App
from stagdeck.slide import Slide


# =============================================================================
# Custom Slide Classes - subclass Slide and override build_content()
# =============================================================================

@dataclass
class PlotlyChartSlide(Slide):
    """📊 Slide with an interactive Plotly chart.
    
    Uses add_content_area() to center the chart in the slide.
    Background color is set via the background_color field.
    """
    
    def __post_init__(self):
        self.title = '📊 Interactive Analytics'
        self.background_color = '#1a1a2e'
    
    async def build_content(self, step: int = 0):
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        revenue = [12, 19, 15, 25, 22, 30]
        users = [150, 230, 180, 310, 280, 420]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Revenue ($k)', x=months, y=revenue, marker_color='#6366f1'))
        fig.add_trace(go.Scatter(
            name='Users', x=months, y=users, yaxis='y2',
            line=dict(color='#22d3ee', width=3), mode='lines+markers', marker=dict(size=10),
        ))
        
        fig.update_layout(
            title=dict(text='Monthly Performance', font=dict(size=24, color='white'), x=0.5),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=14),
            legend=dict(orientation='h', y=-0.15, xanchor='center', x=0.5),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(title='Revenue ($k)', gridcolor='rgba(255,255,255,0.1)'),
            yaxis2=dict(title='Users', overlaying='y', side='right'),
            margin=dict(l=60, r=60, t=60, b=80),
        )
        
        with self.add_content_area():
            ui.plotly(fig).classes('w-full').style('height: 450px;')


@dataclass
class SplitImageSlide(Slide):
    """📐 Split slide with image on left, content on right.
    
    Uses background_position='left' for the split layout.
    The image is set via background_color='url(...)'.
    """
    
    def __post_init__(self):
        self.title = 'Project Progress'
        self.subtitle = "Track your team's progress with live indicators."
        self.background_color = 'url(/media/mountain.jpg)'
        self.background_position = 'left'  # Image on left, content on right
    
    async def build_content(self, step: int = 0):
        with self.add_content_area():
            with ui.column().classes('gap-6 w-full max-w-md'):
                ui.label('Project Status').classes('text-2xl font-bold text-white')
                
                for name, value, color in [
                    ('Frontend', 85, '#6366f1'),
                    ('Backend', 70, '#22d3ee'),
                    ('Testing', 45, '#f59e0b'),
                    ('Deployment', 30, '#10b981'),
                ]:
                    with ui.column().classes('w-full gap-1'):
                        with ui.row().classes('w-full justify-between'):
                            ui.label(name).classes('text-white')
                            ui.label(f'{value}%').classes('text-white/70')
                        ui.linear_progress(value=value/100, color=color).classes('w-full')


@dataclass
class BackgroundImageSlide(Slide):
    """🌌 Slide with full background image and overlay.
    
    Uses background_modifiers='overlay:0.6' for readability.
    """
    
    def __post_init__(self):
        self.title = 'Live Metrics'
        self.background_color = 'url(/media/stars.jpg)'
        self.background_modifiers = 'overlay:0.6'
    
    async def build_content(self, step: int = 0):
        with self.add_content_area():
            with ui.column().classes('gap-4'):
                for label, base, unit, icon in [
                    ('Active Users', 1247, '', '👥'),
                    ('Response Time', 42, 'ms', '⚡'),
                    ('Uptime', 99.97, '%', '✅'),
                    ('Requests/sec', 3842, '', '📊'),
                ]:
                    value = base + random.randint(-50, 50) if unit != '%' else base + random.uniform(-0.1, 0.1)
                    with ui.card().classes('bg-white/10 p-4 w-64'):
                        with ui.row().classes('items-center gap-3'):
                            ui.label(icon).classes('text-3xl')
                            with ui.column().classes('gap-0'):
                                ui.label(label).classes('text-white/70 text-sm')
                                ui.label(f'{value:.2f}{unit}' if unit == '%' else f'{int(value):,}{unit}').classes('text-2xl font-bold text-white')


# =============================================================================
# Deck Factory
# =============================================================================

def create_showcase_deck() -> SlideDeck:
    """Create a presentation from markdown file with Python enhancements."""
    
    deck = SlideDeck(title='StagDeck Showcase')
    
    # Register media folder - images become accessible at /media/filename
    media_dir = Path(__file__).parent / 'media'
    deck.add_media_folder(media_dir, '/media')
    
    # Load all slides from markdown file
    # Each slide can have [name: slidename] for later reference
    slides_file = Path(__file__).parent / 'slides.md'
    deck.add_from_file(slides_file)
    
    # Example: Insert a Python-generated slide after 'comparison'
    # deck.insert('''
    # # Dynamic Slide
    # This was inserted via Python!
    # ''', after='comparison')
    
    # Example: Replace a placeholder slide with custom builder
    # deck.replace('chart_placeholder', builder=my_chart_builder)
    
    # Insert PPTX slides (requires LibreOffice + pdf2image + poppler for first conversion)
    # Cached images in media/ppt_sample_slides/ can be committed to git
    pptx_file = Path(__file__).parent / 'media' / 'ppt_sample.pptx'
    deck.add_from_file(pptx_file, after='intro')
    
    # ==========================================================================
    # Custom Python slides - subclass Slide and override build_content()
    # ==========================================================================
    
    # 1. Full-screen slide with background color + Plotly chart
    deck.slides.append(PlotlyChartSlide(name='plotly_chart'))
    
    # 2. Split layout: background image on left, content on right
    deck.slides.append(SplitImageSlide(name='split_image_demo'))
    
    # 3. Full background image with overlay
    deck.slides.append(BackgroundImageSlide(name='metrics_demo'))
    
    return deck


if __name__ in {'__main__', '__mp_main__'}:
    App.run(create_showcase_deck, title='StagDeck Showcase')
